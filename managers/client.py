# Customer information
from models.client import PersonalCustomer, PhonePC
from models.client import BusinessCustomer, PhoneBC

# Sales and bills information
from models.sale_and_bill import BillPC, SalePC, BillBC, SaleBC

class ClientManager:

    @staticmethod
    async def get_personal_customer(db):
        return db.query(PersonalCustomer, PhonePC).join(PersonalCustomer, PersonalCustomer.id == PhonePC.person).all()
    
    @staticmethod
    async def get_business_customer(db):
        return db.query(BusinessCustomer, PhoneBC).join(BusinessCustomer, BusinessCustomer.id == PhoneBC.person).all()
    
    @staticmethod
    async def get_bill_and_sales_pc(db):
        return db.query(BillPC, SalePC).join(BillPC, BillPC.id == SalePC.bill)
    
    @staticmethod
    async def get_bill_and_sales_bc(db):
        return db.query(BillBC, SaleBC).join(BillBC, BillBC.id == SaleBC.bill)