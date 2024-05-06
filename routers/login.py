# FastAPI 
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status, Request, HTTPException
from fastapi.responses import Response
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

# Hash and password
from jose import jwt, JWTError
from passlib.context import CryptContext

# Python
from typing import Optional
from datetime import datetime, timedelta

# Schemas
from schemas import schema

# Models
from models.model import User 

# SQLAlchemist
from sqlalchemy.orm import Session
 
# app
from utils import OAuth2PasswordBearerWithCookie, get_db




# openssl rand -hex 32
SECRET_KEY = "446816f40461c86a6b3e20679c794d3d3d315fb554c16cceb82fe46b957136a3"
ALGORITHM = "HS256"
ACCES_TOKEN_EXPIRE_MINUTES = 30


# Templates
templates = Jinja2Templates(directory="templates")

# Seguridad autenticación y autorización
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")

# Ocupada dada la documentación -- De momento en STOP
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

# Ocupada dado el compa de youtube
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")

router = APIRouter(
    prefix = "/login",
    tags = ["Auth"],
    responses = {404: {"description": "Not found"}}, 
)



############################# Autenticación ###################################################################



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    usuario = db.query(User).filter_by(username = username).first()
    if usuario:
        return usuario


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data:dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt


################################### AUTH LOGIN ################################################################

@router.post(
    path = "/token",
    status_code = status.HTTP_200_OK,
    response_model= schema.Token,
    summary = "Login a user",
    tags= ["Auth"]
)
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        alert = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        return templates.TemplateResponse("auth/login.html",{"request":request, "alert":alert})

    access_token_expires = timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES)
    # Creamos/obtenemos el token jwt con la función create_access_token().
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires)

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    
    return {"access_token": access_token, "token_type": "bearer"}