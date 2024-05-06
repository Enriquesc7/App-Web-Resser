# FastAPI 
from fastapi import APIRouter
from fastapi import Form, Depends
from fastapi import status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse


# Hash and password
from passlib.context import CryptContext

# Schemas
from schemas import user

# SQLAlchemist
from sqlalchemy.orm import Session
 
# app
from utils import get_db

# Managers
from managers.auth import AuthManager



# Templates
templates = Jinja2Templates(directory="templates")

# Seguridad autenticación y autorización
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")


router = APIRouter(
    prefix = "",
    tags = ["Register"],
    responses = {404: {"description": "Not found"}}, 
)



#=============== Go to Register a user ======================

### Register
@router.get(
    path = "/register/",
    status_code = status.HTTP_200_OK,
    summary = "Go to register user",
    tags= ["Register"]
)
async def signup(request: Request):
    return templates.TemplateResponse("auth/signup.html",{"request":request})


#================ Register a user ==========================
@router.post(
    path = "/register/",
    status_code = status.HTTP_201_CREATED,
    summary = "User registration confirmed",
    tags= ["Register"]
)
async def signup_confirmed(
    request: Request,
    db: Session=Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    password_confirmation: str = Form(...)
):
    results = await request.form() # Tener en cuenta que los nombres recopilados en results, corresponden a los nombres de las etiquetas
    
    user_register = await AuthManager.register(results, email, password, password_confirmation, db)
    # Si hay algun mensaje de error (HTTPExeption)
    if user_register != None:
        message = user_register.detail
        print(f'El mensaje de error es: {message}')
        return JSONResponse(content={'message':message}, status_code=400)
    
    return JSONResponse(content={'redirect': '/login'}, status_code=status.HTTP_201_CREATED)
    
    