# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# Python
from typing import List
from os import getcwd, remove

# Schemas
from schemas import front, user

# SQLAlchemist
from sqlalchemy.orm import Session

# Managers
from managers.auth import get_current_active_user
from managers.admin import is_staff, AdminManager

# app
from utils import get_db



templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix = "/admin",
    tags = ["Admin-Service"],
    responses = {418: {"description": "I'm a teapot"}},)


#================================== Admin Front =======================================================

#===================== Go to Front ============================

## View all services
@router.get(
    response_model = List[front.Service],
    path = "/cloud",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_200_OK,
    summary = "Show all services",
    tags= ["Admin-Service"]
)
async def show_all_services(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        'admin/admin_cloud.html',
        {'request':request,
        'admin': await AdminManager.get_user_by_email(db, current_user.email)})












