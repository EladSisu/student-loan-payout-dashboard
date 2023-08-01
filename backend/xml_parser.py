import xml.etree.ElementTree as ET
from typing import List, Optional

from fastapi import UploadFile

from models import Address, Employee, Payee, Payor, Transaction


def parse_address(element: ET.Element) -> Optional[Address]:
    if element is None:
        return None

    return Address(
        Line1=element.find('Line1').text,
        City=element.find('City').text,
        State=element.find('State').text,
        Zip=element.find('Zip').text,
    )

def parse_employee(element: ET.Element) -> Optional[Employee]:
    if element is None:
        return None

    return Employee(
        DunkinId=element.find('DunkinId').text,
        DunkinBranch=element.find('DunkinBranch').text,
        FirstName=element.find('FirstName').text,
        LastName=element.find('LastName').text,
        DOB=element.find('DOB').text,
        PhoneNumber=element.find('PhoneNumber').text,
    )

def parse_payor(element: ET.Element) -> Optional[Payor]:
    if element is None:
        return None

    return Payor(
        DunkinId=element.find('DunkinId').text,
        ABARouting=element.find('ABARouting').text,
        AccountNumber=element.find('AccountNumber').text,
        Name=element.find('Name').text,
        DBA=element.find('DBA').text,
        EIN=element.find('EIN').text,
        Address=parse_address(element.find('Address')),
    )

def parse_payee(element: ET.Element) -> Optional[Payee]:
    if element is None:
        return None

    return Payee(
        PlaidId=element.find('PlaidId').text,
        LoanAccountNumber=element.find('LoanAccountNumber').text,
    )

def parse_rows_from_xml(file: UploadFile) -> List[Transaction]:
    tree = ET.parse(file.file)
    root = tree.getroot()
    rows = []
    for row_element in root.findall('row'):
        try:
            row = Transaction(
                Employee=parse_employee(row_element.find('Employee')),
                Payor=parse_payor(row_element.find('Payor')),
                Payee=parse_payee(row_element.find('Payee')),
                Amount=row_element.find('Amount').text,
            )
            rows.append(row)
        except Exception as e:
            continue
    return rows