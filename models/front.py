from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from db import Base
from datetime import datetime
from models.enum import PlanEnum

#================ Front tables section ===================================

class Slider(Base):
    __tablename__ = 'slider'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    path_img_slide = Column(String(100), nullable=False)
    admin = Column(Integer, ForeignKey('user.id'), nullable=False)
    create = Column(DateTime, default =datetime.now)
    update = Column(DateTime, onupdate=datetime.now)

class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(String(250), nullable=False)
    content = Column(String(2000), nullable=False)
    category = Column(String(30), nullable=False)
    path_img_service = Column(String(100), nullable=False)
    admin = Column(Integer, ForeignKey('user.id'), nullable=False)
    create = Column(DateTime, default =datetime.now)
    update = Column(DateTime, onupdate=datetime.now)

class Plan(Base):
    __tablename__ = 'plan'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(PlanEnum), nullable = False)
    price = Column(Integer, nullable=False)
    renewal = Column(String(10), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    create = Column(DateTime, default =datetime.now)
    update = Column(DateTime, onupdate=datetime.now)
    admin = Column(Integer, ForeignKey('user.id'), nullable=False)