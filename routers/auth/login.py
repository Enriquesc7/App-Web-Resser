# FastAPI 
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status, Request
from fastapi.responses import Response, RedirectResponse
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

# Schemas
from schemas import user

# Models
from models.enum import UserRoleEnum

# SQLAlchemist
from sqlalchemy.orm import Session
 
# app
from utils import get_db
from managers.auth import AuthManager



# Templates
templates = Jinja2Templates(directory="templates")

# Ocupada dada la documentación -- De momento en STOP
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")



router = APIRouter(
    prefix = "/login",
    tags = ["Auth"],
    responses = {404: {"description": "Not found"}}, 
)


#=================== Go to Login ==================

# Go to Login
@router.get(
    path = "",
    status_code = status.HTTP_200_OK,
    summary = "Login a user",
    tags= ["Auth"]
)
async def login(
    request: Request
):
    return templates.TemplateResponse("auth/login.html",{"request":request})


#=================== Login User ===================
@router.post(
    path = "",
    status_code = status.HTTP_200_OK,
    response_model= user.Token,
    summary = "Login a user",
    tags= ["Auth"]
)
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    
    user_session = await AuthManager.login(form_data, db)
    
    try:
        message = user_session['message']
        return templates.TemplateResponse('auth/login.html',{'request':request,'message':message})   

    # TypeError ya que el resultado no fue un diccionario, sino una tupla...     
    except TypeError:
        access_token, user = user_session

    if user.rol.value == UserRoleEnum.admin.value or user.rol.value == UserRoleEnum.super_admin.value:
            response = RedirectResponse("admin/"+user.first_name+"-"+user.last_name, status_code= status.HTTP_302_FOUND)
            
    elif user.rol.value == UserRoleEnum.user.value:
        response = RedirectResponse("/home", status_code= status.HTTP_302_FOUND)

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response
    
    

# La solución podria estar en este video --> https://www.youtube.com/watch?v=3KjaJkGzpAU
