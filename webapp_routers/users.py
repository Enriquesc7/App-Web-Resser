# FastAPI 
from fastapi import APIRouter
from fastapi import Form, Depends
from fastapi import status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# Hash and password
from passlib.context import CryptContext

# Schemas
from schemas import schema

# Models
from models.model import User 

# SQLAlchemist
from sqlalchemy.orm import Session
 
# app
from routers.login import get_password_hash
from utils import get_db





# Templates
templates = Jinja2Templates(directory="templates")

# Seguridad autenticación y autorización
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")


router = APIRouter(
    prefix = "",
    tags = ["Register"],
    responses = {404: {"description": "Not found"}}, 
)



############# Register a user ####################


### Register
@router.get(
    path = "/register",
    status_code = status.HTTP_200_OK,
    summary = "Register a user",
    tags= ["Register"]
)
async def signup(request: Request):
    return templates.TemplateResponse("auth/signup.html",{"request":request})




### Register a user
@router.post(
    path = "/register",
    response_model = schema.User,
    status_code = status.HTTP_201_CREATED,
    summary = "Register a user confirmed",
    tags= ["Register"]
)
async def signup_confirmed(
    request: Request,
    db: Session=Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    password_confirmation: str = Form(...) 
):
    
    # Generamos los mensajes de validación
    mensaje = {
            "password": "Las contraseñas no son iguales.",
            "username": "Este username ya existe, intenta con otro.",
            "email": "Este correo ya existe, intenta con otro."
        }
    
    # Obtenemos el resultado del formulario
    results = await request.form()

    # Vemos si existe el username (no pueden haber 2 iguales)
    username_exist = db.query(User).filter_by(username = username).first()
    # Vemos si existe el correo (no pueden haber 2 iguales)
    email_exist = db.query(User).filter_by(email = results['email']).first()

    if username_exist:
        return templates.TemplateResponse("auth/signup.html",{
            "request":request,
            "mensaje":mensaje['username'],
            "username":username,
            "results":results})

    elif email_exist:
        return templates.TemplateResponse("auth/signup.html",{
            "request":request,
            "mensaje":mensaje["email"],
            "username":username,
            "results":results})


    elif password != password_confirmation:
        return templates.TemplateResponse("auth/signup.html",{
            "request":request,
            "mensaje":mensaje["password"],
            "username":username,
            "results":results})
    else:
        usuario = User(
            email = results["email"],
            hashed_password = get_password_hash(password),
            username= username,
            first_name = results["first_name"],
            last_name = results["last_name"],
            is_staff = 'off')      
  
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    
    return RedirectResponse("/login", status_code= status.HTTP_303_SEE_OTHER)
    