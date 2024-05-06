# FastAPI
from fastapi import Depends
from fastapi import status, HTTPException

# Python
from typing import Optional
from datetime import datetime, timedelta

# jwt
# Hash and password
from jose import jwt, JWTError
from passlib.context import CryptContext

# SQLAlchemist
from sqlalchemy.orm import Session

# Models
from models.user import User

# Schemas
from schemas import user
from schemas.user import TokenData

# python-decoupler (.env) - (SECRET_KEY, ALGORITHM, ACCES_TOKEN_EXPIRE_MINUTES)
from decouple import config

# app
from utils import OAuth2PasswordBearerWithCookie, get_db


pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")
# Ocupada dado el compa de youtube
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


class AuthManager:

    @staticmethod
    async def register(results, email, password, password_confirmation, db):  
        # Vemos si existe el correo (no pueden haber 2 iguales)
        email_exist = db.query(User).filter_by(email = email).first()
        
        if email_exist:
            alert =  HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                   detail= "Cet e-mail existe déjà, essayez-en un autre.") # "Este correo ya existe, intenta con otro."
            return alert
        
        elif password != password_confirmation:
            alert =  HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                   detail= "Les mots de passe ne sont pas les mêmes.") # "Las contraseñas no son iguales."
            return alert
        
        else:
            user = User(
                email = email,
                hashed_password = get_password_hash(password),
                first_name = results["first_name"],
                last_name = results["last_name"])   
        db.add(user)
        db.commit()
        db.refresh(user)

    

    @staticmethod
    async def login(form_data, db):
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            message = "Nom d'utilisateur ou mot de passe incorrect." # "Nombre de usuario o contraseña incorrecto."
            return {'message':message}
        
        access_token_expires = timedelta(minutes= int(config('ACCES_TOKEN_EXPIRE_MINUTES')))
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires)

        return access_token, user
    



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def get_user_by_email(db, email: str):
    user = db.query(User).filter_by(email = email).first()
    if user:
        return user


def authenticate_user(db, username: str, password: str):
    user = get_user_by_email(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data:dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, config('SECRET_KEY'), algorithm=config('ALGORITHM'))

    return encode_jwt


# Funciones obtenidas de la documentación oficial
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials - get_current_user",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try: 
        payload = jwt.decode(token, config('SECRET_KEY'), algorithms=[config('ALGORITHM')])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception # --> Vemos si con RedirectResponse mejoramos la caida de session 
        token_data = TokenData(username=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    
    user.disabled = False
    db.commit()
    db.refresh(user)
    
    return user


async def get_current_active_user(current_user: user.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
    

# Función obtenida del men de youtube
#def get_user_from_token(db, token):
#    try:
#        print("Entramos en el try")
#        payload = jwt.decode(token, config('SECRET_KEY'), config('ALGORITHM'))
#        print("Creo que obtuvimos el payload")
#        username = payload.get("sub")
#        if not username:
#            raise HTTPException(
#                status_code=status.HTTP_401_UNAUTHORIZED,
#                detail="Could not validate Credentials",
#            )
#    except:
#        raise HTTPException(
#            status_code=status.HTTP_401_UNAUTHORIZED,
#            detail="Could not validate Credetials",
#        )
#    user = db.query(User).filter_by(username = username).first()
#    if user is None:
#        raise HTTPException(
#            status_code=status.HTP_401_UNAUTHORIZED,
#            detail="Could not validate credentials - get_user_from_token",
#        )
#    return user