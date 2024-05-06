from sqlalchemy import Column, Integer, DateTime, ForeignKey
from db import Base
from datetime import datetime

#================= Customer sales and bills tables section =========================================

class BillPC(Base):
    __tablename__ = 'bill_pc'
    id = Column(Integer, primary_key = True, index = True)
    date = Column(DateTime, default = datetime.now)
    client = Column(Integer, ForeignKey('personal_customer.id'), nullable=False)

class SalePC(Base):
    __tablename__ = 'sale_pc'
    id = Column(Integer, primary_key = True, index = True)
    date = Column(DateTime, default = datetime.now)
    plan = Column(Integer, ForeignKey('plan.id'), nullable=False)
    bill = Column(Integer, ForeignKey('bill_pc.id'), nullable=False) 

#================ Company Customer sales and bills tables section ==================================

class BillBC(Base):
    __tablename__ = 'bill_bc'
    id = Column(Integer, primary_key = True, index = True)
    date = Column(DateTime, default = datetime.now)
    client = Column(Integer, ForeignKey('business_customer.id'))

class SaleBC(Base):
    __tablename__ = 'sale_bc'
    id = Column(Integer, primary_key = True, index = True)
    date = Column(DateTime, default = datetime.now)
    plan = Column(Integer, ForeignKey('plan.id'), nullable=False)
    bill = Column(Integer, ForeignKey('bill_bc.id'), nullable=False) 