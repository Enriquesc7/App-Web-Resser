# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends, Path
from fastapi.templating import Jinja2Templates

# Python
from typing import List

# Schemas
from schemas import user

# SQLAlchemist
from sqlalchemy.orm import Session

# Managers
from managers.admin import AdminManager
from managers.front import FrontManager
from managers.team import TeamManager

# app
from utils import get_db
from .user import get_current_active_user


# Templates
templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "",
    tags = ["User-Service"],
    responses = {404: {"description": "Not found"}}, 
)


#===============================================================================================================
#============================ Update User ======================================================================

# MOSTRAMOS LOS SERVICIOS/PLANES AL POSIBLE CLIENTE
@router.get(
    path = "/planes",
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Go to Plans",
    tags= ["User-Service"]
)
async def plan_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        "users/plan.html",
        {"request":request,
        "user": await AdminManager.get_user_by_email(db, current_user.email),
        "plans": await FrontManager.get_plans(db)})


# PROCEDIMIENTO DE SUSCRIPCÍÓN
@router.get(
    path = "/planes/{plan}",
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Selected plan",
    tags= ["User-Service"]
)
async def plan_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
    plan: str = Path()
):
    return templates.TemplateResponse(
        "users/selected_plan.html",
        {"request":request,
        "user": await AdminManager.get_user_by_email(db, current_user.email),
        "plan": await FrontManager.get_plan_by_name(db, plan),
        'regions': await TeamManager.get_regions(db)})

