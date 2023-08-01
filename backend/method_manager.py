import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from fastapi.logger import logger
from method import Method
from models import (
    Employee,
    Payee,
    Payment,
    Payor,
    Transaction,
    TransactionSummary,
    get_unique_employees,
    get_unique_payors,
)
from ratelimit import limits, sleep_and_retry

PHONE_NUMBER = '15121231111'


class MethodOperation(Enum):
    CREATE_PAYMENT = 1
    CREATE_ACCOUNT = 2
    CREATE_ENTITY = 3
class MethodWrapper(Method):
    "class to wrap the Method class and add functionality to avoid overuse of the method api"
    def __init__(self):
        super().__init__(env='dev', api_key='sk_mgUJmVYiezQWypikbFrrJPPP')
    @sleep_and_retry
    @limits(calls=599, period=60)
    def invoke_method_api(self,request,method_operation:MethodOperation):
        logger.info("invoking method api for : %s",method_operation)
        match method_operation:
            case MethodOperation.CREATE_PAYMENT:
                return self.payments.create(request)
            case MethodOperation.CREATE_ACCOUNT:
                return self.accounts.create(request)
            case MethodOperation.CREATE_ENTITY:
                return self.entities.create(request)
            case _:
                raise Exception('Invalid Method Operation')
@dataclass
class TransactionService:
    method_client : MethodWrapper
    transactions:List[Transaction]
    batch_name:str
    batch_id:str

    @property
    async def employees_entities(self) -> Dict[str, str]:
        unique_employees = get_unique_employees(self.transactions)
        return {tnx.Employee.DunkinId:self.get_employee_account_async(tnx) for tnx in unique_employees}
        # unique_employees = get_unique_employees(self.transactions)
        # tasks = [self.get_employee_account_async(tnx) for tnx in unique_employees]
        # result = await asyncio.gather(*tasks)
        # return {tnx.Employee.DunkinId: payment_account for tnx, payment_account in zip(unique_employees, result)}

    def get_employee_account_async(self, tnx):    
        # loop = asyncio.get_event_loop()
        # account = IndividualAccount(tnx.Payee, tnx.Employee, self.method_client)
        # return await loop.run_in_executor(None, account.payment_account)
        return IndividualAccount(tnx.Payee, tnx.Employee, self.method_client).payment_account()

    @property
    async def corporate_entities(self) -> Dict[str, str]:
        unique_payors = get_unique_payors(self.transactions)
        tasks = [self.get_corp_account_async(tnx) for tnx in unique_payors]
        result = await asyncio.gather(*tasks)
        return {tnx.Payor.DunkinId: payment_account for tnx, payment_account in zip(unique_payors, result)}

    async def get_corp_account_async(self, tnx):
        loop = asyncio.get_event_loop()
        account =  CorporationAccount(tnx.Payor, self.method_client)
        return await loop.run_in_executor(None, account.payment_account)
    
    async def create_batch(self) -> List[TransactionSummary]:
        result = []
        sources = await self.corporate_entities
        destinations = await self.employees_entities
        for tnx in self.transactions:
            destination = destinations[tnx.Employee.DunkinId]
            source = sources[tnx.Payor.DunkinId]
            payment = TransactionService.create_payment(source=source,destination=destination)
            tnx_summary = TransactionSummary(transaction=tnx,
                                             source=payment.source,
                                             destination=payment.destination,
                                             status='created' if payment.is_valid else 'failed',
                                             batch_id=self.batch_id,
                                             batch_name=self.batch_name)
            result.append(tnx_summary)
        return result

    @staticmethod
    def create_payment(source:str,destination:str)-> Payment:
        try:
            return Payment(status='pending',is_valid=True,source=source,destination=destination)
        except BaseException as e:
            logger.error("Error creating payment",e)
            return Payment(status='failed',is_valid=False,source=None,destination=None)
        
    @staticmethod
    def invoke_payment(amount:float,source:str,destination:str,method_client:MethodWrapper):
        return method_client.invoke_method_api(request = {
                # amount is in cents so multiply by 100.
                'amount': amount*100,
                'source': source,
                'destination': destination,
                'description': 'Loan Pmt'
                },
                method_operation=MethodOperation.CREATE_PAYMENT)

class Account(ABC):
    @abstractmethod
    def create_account(self):
        pass
    @abstractmethod
    def create_entity(self):
        pass
    

@dataclass
class IndividualAccount(Account):
    payee:Payee
    employee:Employee
    method_client:MethodWrapper

    
    def payment_account(self) -> str:
        try:
            holder_id = self.create_entity()['id']
            account = self.create_account(holder_id,self.payee.PlaidId,self.payee.LoanAccountNumber)
            return account['id']
        except BaseException as e:
            logger.error(f"Error creating Individual Account {e}")
            return 'N/A'

    def create_account(self, holder_id,plaid_id:str, number:str):
        mch_id = self.get_individual_mch_id(plaid_id)
        return self.method_client.invoke_method_api(request={
        'holder_id': holder_id,
        'liability': {
            'mch_id': mch_id,
            'number': number,
        }
        },
        method_operation=MethodOperation.CREATE_ACCOUNT)
    
    def create_entity(self):
        return self.method_client.invoke_method_api(request ={
            'type': 'individual',
            'individual': {
                'first_name': self.employee.FirstName,
                'last_name': self.employee.LastName,
                'phone': PHONE_NUMBER,
                'dob': self.employee.DOB,
            }},
            method_operation=MethodOperation.CREATE_ENTITY)
    
    def get_individual_mch_id(self,plaid_id:str) -> str:
        """
        This method is used to get the Method Merchant ID for an individual.
        Assume the first merchant is the correct one.
        """
        return self.method_client.merchants.list({'provider_ids.plaid_id': plaid_id})[0]['mch_id']


@dataclass
class CorporationAccount(Account):
    payor:Payor
    method_client:MethodWrapper
    
    def payment_account(self) -> str:
        try:
            holder_id = self.create_entity()['id']
            account = self.create_account(holder_id,self.payor.ABARouting,self.payor.AccountNumber)
            return account['id']
        except BaseException as e:
            logger.error(f"Error creating Corporation Account {e}",e)
            return 'N/A'
    
    def create_entity(self):
        return self.method_client.invoke_method_api(request ={
                'type': 'c_corporation',
                'corporation': {
                    'name': self.payor.Name,
                    'dba': self.payor.DBA,
                    'ein': self.payor.EIN,
                    'owners': []
                },
                'address': {
                    'line1': self.payor.Address.Line1,
                    'city': self.payor.Address.City,
                    'state': self.payor.Address.State,
                    'zip': '50001',
                }
                },
                method_operation=MethodOperation.CREATE_ENTITY)

    def create_account(self, holder_id:str,routing:str, number:str, type:str = 'checking'):
        return self.method_client.invoke_method_api(request ={
        'holder_id': holder_id,
        'ach': {
            'routing': routing,
            'number': number,
            'type': type,
        }
        },
        method_operation=MethodOperation.CREATE_ACCOUNT)
    