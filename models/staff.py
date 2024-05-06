# SqlAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

# Database
from db import Base

#========================= Sección tablas Staff (Personal de trabajo) =====================================================

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key = True, index = True)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    rut = Column(String(13), nullable=False, unique=True)
    email = Column(String(30), nullable=False, unique=True)
    address_name = Column(String(20), nullable=False)
    address_number = Column(Integer, nullable=False)
    commune = Column(String, ForeignKey('commune.commune'), nullable=False)
    region = Column(String, ForeignKey('region.region'), nullable=False)
    country = Column(String,ForeignKey('country.country'), nullable=False)

class PhonePerson(Base):
    __tablename__ = 'phone_person'
    phone_id = Column(Integer, primary_key = True, index = True)
    phone = Column(Integer)
    person = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), nullable=False)

#=========================== Sección tablas Empleos ====================================================

class WorkArea(Base):
    __tablename__ = 'work_area'
    id = Column(Integer, primary_key = True, index = True)
    area = Column(String, nullable=False, unique=True)

class Employment(Base):
    __tablename__ = 'employment'
    id = Column(Integer, primary_key = True, index = True)
    employment = Column(String, nullable=False, unique=True)
    area = Column(String, ForeignKey('work_area.area'), nullable=False)

class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key = True, index = True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    person = Column(String, ForeignKey('person.rut', ondelete='CASCADE'), nullable=False)
    employment = Column(String, ForeignKey('employment.employment'), nullable=False)
    area = Column(String, ForeignKey('work_area.area'), nullable=False)
