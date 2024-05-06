from sqlalchemy import Column, Integer, String, ForeignKey
from db import Base

#================= Location tables section ==============================

class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key = True, index = True)
    country = Column(String(30), nullable=False, unique=True)

class Region(Base):
    __tablename__ = 'region'
    id = Column(Integer, primary_key = True, index = True)
    region = Column(String(50), nullable=False, unique=True)
    country = Column(String, ForeignKey('country.country'), nullable=False)

class Commune(Base):
    __tablename__= 'commune'
    id = Column(Integer, primary_key = True, index = True)
    commune = Column(String(30), nullable=False, unique=True)
    region = Column(String, ForeignKey('region.region'), nullable=False)
    country = Column(String, ForeignKey('country.country'), nullable=False)