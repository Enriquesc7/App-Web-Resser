# SQLAlchemist
from email.policy import default
from operator import index
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Enum

# App
from data import Base

# Utils
from datetime import datetime, date

# Models
from models.enum import Genero

# Models
# Información basica del usuario al momento de registrarse
class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key = True, index = True)
    username = Column(String(20))
    hashed_password = Column(String(30))
    email = Column(String(30))
    first_name = Column(String(30))
    last_name = Column(String(30))
    rut = Column(String(12))
    birthday = Column(DateTime)
    address = Column(String(20))
    commune = Column(String(20))
    region = Column(String(30))
    country = Column(String(20))
    path_img_profile = Column(String(100))
    create_user = Column(DateTime, default = datetime.now)
    update_user = Column(DateTime, onupdate = datetime.now)
    is_staff = Column(String(5))
    disabled = Column(Boolean, default=True)


#, onupdate = datetime.now

# Información más detallada luego de registrarse (Falta vinvularlo con un Foreing_key)
#class UserInfo(Base):
#    __tablename__ = 'info_user'


# Información del usuario tras convertirse en ciente (Esta puede ser la misma que UserInfo o no... depende...)
#class Customer(base):
#    __tablename__ = 'customer'
#    company = Column(String(30))
#    rut_company = Column(String(13))
#    business_name = Column(String(60))
#    address = Column(String(20))
#    Commune = Column(String(20))
#    #region = Column(String(30))
#    country = Column(String(20))
#    create_customer = Column(DateTime, default =datetime.now, onupdate = datetime.now)



class Service(Base):
    __tablename__ = 'service'
    service_id = Column(Integer, primary_key = True, index = True)
    title = Column(String(50))
    description = Column(String(250))
    content = Column(String(2000))
    category = Column(String(30))
    path_img_service = Column(String(100))
    create_service = Column(DateTime, default =datetime.now, onupdate = datetime.now)



class Slider(Base):
    __tablename__ = 'slider'
    slide_id = Column(Integer, primary_key = True, index = True)
    title = Column(String(50))
    path_img_slide = Column(String(100))
    create = Column(DateTime, default =datetime.now, onupdate = datetime.now)



# Información basica del usuario al momento de registrarse
class UserStage(Base):
    __tablename__ = 'user_stage'
    name = Column(String(20))
    age = Column(String(3))
    genero = Column(Enum(Genero), nullable=False)