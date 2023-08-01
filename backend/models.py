from enum import Enum
import re
from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, validator
from dateutil.parser import parse

class BatchStatus(Enum):
    UPLOADED = 'Uploaded' # Batch has been uploaded, entries are being processed.
    CREATED = 'Created' # Batch has been created, ready for payment invocation.
    COMPLETED = 'Completed' # Batch has been completed, all payments have been processed
    FAILED = 'Failed' # Batch has failed to process.

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Address(BaseModel):
    Line1: str
    City: str
    State: str
    Zip: str

class Employee(BaseModel):
    DunkinId: str
    DunkinBranch: str
    FirstName: str
    LastName: str
    DOB: str
    PhoneNumber: str

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Employee):
            return self.DunkinId == __value.DunkinId
        raise ValueError("Cannot compare Employee to non-Employee")
    
    @validator('DOB')
    def parse_dob(cls, value):
        # Use dateutil.parser.parse to automatically parse various date formats
        dob_date = parse(value)

        # Convert the datetime object back to the desired format "yyyy-mm-dd"
        return dob_date.strftime('%Y-%m-%d')

class Payor(BaseModel):
    DunkinId: str
    ABARouting: str
    AccountNumber: str
    Name: str
    DBA: str
    EIN: str
    Address: Address
    
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Payor):
            return self.DunkinId == __value.DunkinId
        raise ValueError("Cannot compare Payor to non-Payor")

class Payee(BaseModel):
    PlaidId: str
    LoanAccountNumber: str

class Transaction(BaseModel):
    Employee: Employee
    Payor: Payor
    Payee: Payee
    Amount: float
    status: Optional[str] = "Pending"

    @validator('Amount', pre=True)
    def parse_currency(cls, v):
        if isinstance(v, float):
            return v
        match = re.search(r'([^\d]*)([\d.,]+)', str(v))
        if match:
            return float(match.group(2).replace(',', '.'))
        else:
            raise ValueError('Invalid amount')

class TransactionBatchResponse(BaseModel):
    batch_name: str
    batch_id: str
    # Transaction: List[Transaction]
    total_transactions: int
    valid_transactions: int
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

class Payment(BaseModel):
    status: str
    source: Optional[str]
    destination: Optional[str]
    is_valid: bool
    
class TransactionSummary(BaseModel):
    batch_name: str
    batch_id: str
    status: str
    transaction: Transaction
    source: Optional[str]
    destination: Optional[str]
    payment : Optional[Dict[str,str]] = None
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        
class Batch(BaseModel):
    id : PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    batch_name: str
    status: str = BatchStatus.UPLOADED.value
    total_transactions: int
    valid_transactions: int
    invalid_transactions: int
    date_created: datetime = Field(default_factory=datetime.utcnow)
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            BatchStatus: lambda x: x.value
        }

def get_unique_employees(transactions:List[Transaction]):
    return list({tnx.Employee.DunkinId: tnx for tnx in transactions}.values())

def get_unique_payors(transactions:List[Transaction]):
    return list({tnx.Payor.DunkinId: tnx for tnx in transactions}.values())