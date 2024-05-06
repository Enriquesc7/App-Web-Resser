# Python
from datetime import datetime
from typing import Optional

# Pydantics
from pydantic import BaseModel, EmailStr
from pydantic import Field

# Models
from models.enum import UserRoleEnum


# gt: greater than
# ge: greater than or equal
# lt: less than
# le: less than or equal

#============================== Schemas User ================================================

#========== Models User ===============
#from email_validator import validate_email as validate_e
#from email_validator import EmailNotValidError
#from pydantic import validator

# Creamos una clase para validar el email (actualmente ocupamos EmailStr de Pydantic)
#class EmailField(str):
#    @classmethod
#    def __get_validators__(cls):
#        yield cls.validate
#    
#    @classmethod
#    def valdate(cls, v) -> str:
#        try:
#            validate_e(v)
#            return v
#
#        except EmailNotValidError:
#            raise ValueError("Email no valido")


class UserBase(BaseModel):
    id : int = Field()
    email: EmailStr = Field(...)



class UserLogin(UserBase):
    password: str = Field(
        ..., 
        min_length=8,
        example= "Unacontraseñacualquiera"
    )

class User(UserBase): 
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example = "Zoro"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example = "Roronoa"
    )
    create_service: datetime = Field(
        ...,
        example = "24-01-2023"
    )
    update_info: datetime = Field(
        ...,
        example = "24-01-2023"
    )
    rol: UserRoleEnum = None
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True 
    



#================ JWT ======================

class UsernameLogin(BaseModel):
    username: str
    disabled: Optional[bool] = None
    class Config:
        orm_mode = True

class UserRegisterInDB(UsernameLogin):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


#========== Update info User =================
class UpdateUser(BaseModel): 
    username: str = Field(
        min_length=1,
        max_length=50,
        example = "RoronoaZoro"
    )
    class Config:
        orm_mode = True

########## Models Mensaje #############
class Mensaje(BaseModel):
    mensaje: str = "Registrado con exito"