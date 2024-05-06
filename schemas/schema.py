# Python
from datetime import date, datetime
from doctest import Example
from uuid import UUID
from typing import Optional, List

# Pydantics
from pydantic import BaseModel, EmailStr
from pydantic import Field    


###############################################################################################
#################### Models ###################################################################

# gt: greater than
# ge: greater than or equal
# lt: less than
# le: less than or equal


########## Models Users #############
class UserBase(BaseModel):
    user_id : int = Field()
    email: EmailStr = Field(...)

class UserLogin(UserBase):
    password: str = Field(
        ..., 
        min_length=8,
        example= "Unacontraseñacualquiera"
    )

class User(UserBase): 
    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example = "RoronoaZoro"
    )
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
    is_staff: Optional[str] = 'off'
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True 

    
class UserInfo(User):
    rut: str = Field(
        ...,
        max_lenght = 12,
        example = "19.515.158-k"
    )
    birthday: datetime = Field(
        ...,
        example = "24-01-2023"
    )
    address: str = Field(
        ...,
        max_length = 20,
        example = "El Roble 799"
    )
    commune: str = Field(
        ...,
        max_lenght = 20,
        example = "Recoleta"
    )
    region: str = Field(
        ...,
        max_length = 30,
        example = "Región Metropolitana"
    )
    country: str = Field(
        ...,
        max_length = 20,
        example = "Chile"
    )
    path_img_profile: str = Field(
        ...,
        max_length=100,
        example = "base/img/imagen.png"
    )
    class Config:
        orm_mode = True 


############## Authentication User #############################

class UserRegister(User, UserLogin):
    password_confirmation: str = Field(
        ..., 
        min_length=8,
        example= "Unacontraseñacualquiera"
    )


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


class UserSignup(BaseModel):
    username: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example = "RoronoaZoro"
    )
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

    class Config:
        orm_mode = True



############# Customer Info ##############################
class CustomerInfo(UserInfo):
    company: str = Field(
        ...,
        max_length = 30,
        example = "Horus SPA"
    )
    rut_company: str = Field(
        ...,
        max_lenght = 13,
        example = "105.515.158-k"
    )
    business_name: str = Field(
        ...,
        max_length = 50,
        example = "Comercializadora de..."
    )
    address: str = Field(
        ...,
        max_length = 20,
        example = "El Roble 799"
    )
    commune: str = Field(
        ...,
        max_lenght = 20,
        example = "Recoleta"
    )
    region: str = Field(
        ...,
        max_length = 30,
        example = "Región Metropolitana"
    )
    country: str = Field(
        ...,
        max_length = 20,
        example = "Chile"
    )
    create_customer: datetime = Field(
        ...,
        example = "24-01-2023"
    )


############ Update info User ###########################
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
    mensaje: str = Field(...)




########## Models Service #############
class Service(BaseModel):
    service_id: int = Field()
    title: str = Field(
        ...,
        max_length=50,
        example = 'Titulo de ejemplo'
    )
    description: str = Field(
        ...,
        max_length= 150,
        example = 'Descripción de algún proyecto de ejemplo'
    )
    content: str = Field(
        ...,
        max_length=2000,
        example = "Contenido de algún proyecto de ejemplo, podría ser cualquier cosa."
    )
    category: str = Field(
        ...,
        max_length=30,
        example = "categoriaX"
    )
    create_service: datetime = Field(
        ...,
        example = "24-01-2023"
    )
    path_img_service: str = Field(
        ...,
        max_length=100,
        example = "base/img/imagen.png"
    )

    class Config:
        orm_mode = True



########## Slider Post #############
class Slider(BaseModel):
    slide_id: int = Field()
    title: str = Field(
        ...,
        max_length=50,
        example = 'Titulo de ejemplo'
    )
    create: datetime = Field(
        ...,
        example = "24-01-2023"
    )
    path_img_slide: str = Field(
        ...,
        max_length=100,
        example = "base/img/imagen.png"
    )

    class Config:
        orm_mode = True