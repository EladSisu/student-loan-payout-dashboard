import csv
import io

from bson import ObjectId
from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from method_manager import MethodWrapper, TransactionService
from models import Batch, BatchStatus, TransactionBatchResponse
from pymongo import MongoClient, UpdateOne
from xml_parser import parse_rows_from_xml

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
uri = "mongodb+srv://eladhershkovitz:mika1992@payments.oy64vhq.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)

method = MethodWrapper()
db = client["payments"]

# Get cvs report of Total amount of funds paid out per unique source account.
@app.get("/reports/batches/{id}/source_account")
async def get_sum_transactions_per_source(id: str):
    transactions_collection = db["transactions"]

    pipeline = [
    {"$match": {"batch_id":id}},  # Filter by batch_name
    {"$group": {
        "_id": "$payment.source",  # Group by payment.source
        "totalAmount": {"$sum": "$transaction.Amount"}  # Sum the Amount
    }}
    ]
    results =  list(transactions_collection.aggregate(pipeline))
    results_list = [{"Source Account": result["_id"], "Total Amount": result["totalAmount"]} for result in results]

    # Define the fieldnames for the CSV
    fieldnames = ["Source Account", "Total Amount"]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results_list)

    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=report_total_spend_per_source_account.csv"

    return response

# Get csv report of Total amount of funds paid out per Dunkin branch.
@app.get("/reports/batches/{id}/branch")
async def get_sum_transactions_for_account(id: str):
    transactions_collection = db["transactions"]

    pipeline = [
    {"$match": {"batch_id":id}},  # Filter by batch_name
    {"$group": {
        "_id": "$transaction.Payor.DunkinId",  # Group by transaction.Payor.DunkinId
        "totalAmount": {"$sum": "$transaction.Amount"}  # Sum the Amount
    }}
    ]
    results =  list(transactions_collection.aggregate(pipeline))
    results_list = [{"Dunkin branch Id": result["_id"], "Total Amount": result["totalAmount"]} for result in results]

    # Define the fieldnames for the CSV
    fieldnames = ["Dunkin branch Id", "Total Amount"]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results_list)

    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=report_total_spend_per_branch.csv"

    return response

# Get csv report of all payments metadata for a given batch name.
@app.get("/reports/batches/{id}/payments")
async def get_payments_metadata(id: str):
    transactions_collection = db["transactions"]
    transactions = transactions_collection.find({"batch_id": id})
    breakpoint()
    payments_list = [tnx['payment'] for tnx in transactions if 'payment' in tnx]

    # Define the fieldnames for the CSV
    fieldnames = [col for col in payments_list[0].keys()]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(payments_list)

    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=report_all_payments.csv"

    return response

# Get all batches.
@app.get("/batches",response_model=list[Batch])
async def get_all_batches():
    batches_collection = db["batches"]
    results = []
    batches = batches_collection.find()
    for batch in batches:
        results.append(Batch(**batch))
    return results

# Upload an xml and create transactions.
@app.post("/upload/xml")
async def upload_file(background_tasks: BackgroundTasks,file: UploadFile=File(...)):
    try:
        breakpoint()
        filename = file.filename.split('.')[0]
        transactions = parse_rows_from_xml(file)
        total_transactions = len(transactions)
        batches_collection = db["batches"]
        batch = Batch(batch_name=filename,total_transactions=total_transactions,valid_transactions=0,invalid_transactions=0)
        batches_collection.insert_one(batch.dict(by_alias=True))
        background_tasks.add_task(create_transactions,filename, transactions, total_transactions, batches_collection, batch)
        return TransactionBatchResponse(batch_id=str(batch.id),batch_name=filename,total_transactions=total_transactions,valid_transactions=0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def create_transactions(filename, transactions, total_transactions, batches_collection, batch):
    transactions_summaries = await TransactionService(method,transactions,filename,str(batch.id)).create_batch()
    invalid_transactions_count = len([tnx for tnx in transactions_summaries if tnx.status =='failed'])
    valid_transactions_count = total_transactions - invalid_transactions_count
    if transactions_summaries:
        transactions_collection = db["transactions"]        
        transactions_collection.insert_many([tnx.dict() for tnx in transactions_summaries])
    batches_collection.update_one({"_id": batch.id}, {"$set": {"valid_transactions":valid_transactions_count,"invalid_transactions": invalid_transactions_count,'status':BatchStatus.CREATED.value}})
    return valid_transactions_count
    
# Invoke a payment for all transaction in a batch.
@app.post("/invoke-payment/{id}")
async def invoke_payment(id: str):
    batch_collection = db["batches"]
    batch = batch_collection.find_one({"_id": ObjectId(id)})
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    if batch['status'] != 'Created':
        raise HTTPException(status_code=400, detail="Cannot invoke payment for this batch at this time.")
    transactions_collection = db["transactions"]
    tnx_summaries = transactions_collection.find({"batch_id": id})
    updates = []
    for tnx_summary in tnx_summaries:
        try:
            payment = TransactionService.invoke_payment(tnx_summary['transaction']['Amount'],tnx_summary['source'],tnx_summary['destination'],method)
            updates.append(UpdateOne({"_id": tnx_summary["_id"]}, {"$set": {"status": 'success','payment':payment}}))
        except Exception:
            updates.append(UpdateOne({"_id": tnx_summary["_id"]}, {"$set": {"status": 'failed'}}))
            continue
    batch_collection.update_one({"_id": batch["_id"]}, {"$set": {"status":BatchStatus.COMPLETED.value}})
    if updates:
        transactions_collection.bulk_write(updates)
        return {"message": "Payouts created successfully!"}
    else:
         raise HTTPException(status_code=404, detail="No transactions found for this batch name.")

