# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# Python
from typing import List

# Schemas
from schemas import schema

# Models
from models.model import User, Service

# SQLAlchemist
from sqlalchemy.orm import Session

# app
from utils import get_db
from .user import get_current_active_user, verify_user




# Templates
templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "/profile",
    tags = ["Users"],
    responses = {404: {"description": "Not found"}}, 
)


#===============================================================================================================
#============================ Update User ======================================================================


# MOSTRAMOS LOS SERVICIOS/PLANES AL POSIBLE CLIENTE
@router.get(
    path = "/{username}/services",
    response_model = schema.User,
    status_code = status.HTTP_200_OK,
    summary = "Go to Plans User",
    tags= ["Users"]
)
async def plan_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_current_active_user)
):
    # Comprobamos si es usuario
    verify_user(request, db, current_user)
    # Obtenemos la información del path
    results = request.path_params
    # Controlamos que no vayan a otro usuario a traves del path
    if current_user.username != results['username']:
        return RedirectResponse("/profile/"+current_user.username+"/plans", status_code=status.HTTP_303_SEE_OTHER)


    # Obtenemos el usuario de la ddbb
    user = db.query(User).filter_by(username = current_user.username).first()
    # Obtenemos los servicios para mostrarlos...
    services = db.query(Service).all()

    return templates.TemplateResponse(
        "users/service.html",
        {"request":request,
        "user":user,
        "services":services})





# PROCEDIMIENTO DE SUSCRIPCÍÓN
@router.get(
    path = "/{username}/suscribe-to-service",
    response_model = schema.User,
    status_code = status.HTTP_200_OK,
    summary = "Go to Plans User",
    tags= ["Users"]
)
async def plan_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_current_active_user)
):
    # Comprobamos si es usuario
    verify_user(request, db, current_user)
    # Obtenemos la información del path
    results = request.path_params
    # Controlamos que no vayan a otro usuario a traves del path
    if current_user.username != results['username']:
        return RedirectResponse("/profile/"+current_user.username+"/suscribe-to-service", status_code=status.HTTP_303_SEE_OTHER)


    # Obtenemos el usuario de la ddbb
    user = db.query(User).filter_by(username = current_user.username).first()


    return templates.TemplateResponse(
        "users/suscribe_to_service.html",
        {"request":request,
        "user":user})

