# FastAPI
from fastapi import status, Request, HTTPException
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

# Python
from typing import Optional, Dict

# data
from db import SessionLocal

# python-decouple
from decouple import config


# aiosmtplib (enviador de correos)
import aiosmtplib
from email.message import EmailMessage
import logging


#====================================================================================================================
#===============================================================================================================


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")  # Obtiene el token de las cookies

        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                detail="User not authenticated. Redirecting to login...",
                headers={"Location": "/login"}
            )
        
        # ⚠️ IMPORTANTE: Eliminar el prefijo "Bearer " si está presente
        if authorization.startswith("Bearer "):
            authorization = authorization[len("Bearer "):]  # Elimina "Bearer " del inicio
        
        return authorization  # Retorna el token limpio



# Access BBDD
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()



# Enviar información de Formulario de Contacto a correo electronico
async def send_email(name: str, user_email: str, message: str):
    """
    Envía un correo a tu bandeja de entrada con los datos del usuario.
    """
    msg = EmailMessage()
    msg["Subject"] = f"Nuevo mensaje de contacto de {name}"
    msg["From"] = config("SMTP_FROM")  # Tu correo autenticado (remitente)
    msg["To"] = config("SMTP_TO")  # Tu correo donde recibirás los mensajes
    msg["Reply-To"] = user_email  # Para que puedas responder al usuario fácilmente

    msg.set_content(
        f"Has recibido un nuevo mensaje de contacto:\n\n"
        f"Nombre: {name}\n"
        f"Correo electrónico: {user_email}\n\n"
        f"Mensaje:\n{message}"
    )

    try:
        await aiosmtplib.send(
            msg,
            hostname=config("SMTP_SERVER"),
            port=config("SMTP_PORT"),
            username=config("SMTP_USER"),
            password=config("SMTP_PASSWORD"),
            start_tls=True
        )
        logging.info(f"Correo enviado correctamente a {config('SMTP_TO')}")
        return True
    except Exception as e:
        logging.error(f"Error al enviar el correo: {e}")
        return False
