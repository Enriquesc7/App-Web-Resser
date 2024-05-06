# SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey

# App
from db import Base


#================== Customer tables section ===================================

class PersonalCustomer(Base):
    __tablename__ = 'personal_customer'
    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(13), nullable=False, unique=True)
    address_name = Column(String(20), nullable=False)
    address_number = Column(Integer, nullable=False)
    user = Column(Integer, ForeignKey('user.id'), nullable=False)
    commune = Column(String, ForeignKey('commune.commune'), nullable=False)
    region = Column(String, ForeignKey('region.region'), nullable=False)
    country = Column(String,ForeignKey('country.country'), nullable=False)


class PhonePC(Base):
    __tablename__ = 'phone_pc'
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(Integer)
    person = Column(Integer, ForeignKey('personal_customer.id', ondelete='CASCADE'), nullable=False)


#================= Company Customer tables section ============================

class BusinessCustomer(Base):
    __tablename__ = 'business_customer'
    id = Column(Integer, primary_key=True, index=True)
    rut = Column(String(13), nullable=False, unique=True)
    company_name = Column(String(50), nullable=False)
    legal_name = Column(String(100), nullable=False)
    commercial_business = Column(String(100), nullable=False)
    address_name = Column(String(20), nullable=False)
    address_number = Column(Integer, nullable=False)
    user = Column(Integer, ForeignKey('user.id'), nullable=False)
    commune = Column(String, ForeignKey('commune.commune'), nullable=False)
    region = Column(String, ForeignKey('region.region'), nullable=False)
    country = Column(String,ForeignKey('country.country'), nullable=False)


class PhoneBC(Base):
    __tablename__ = 'phone_bc'
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(Integer)
    person = Column(Integer, ForeignKey('business_customer.id', ondelete='CASCADE'), nullable=False)