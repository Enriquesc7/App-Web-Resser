# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends
from fastapi.templating import Jinja2Templates

# Python
from typing import List

# Schemas
from schemas import user

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
    tags = ["Admin-Setting"],
    responses = {418: {"description": "I'm a teapot"}},)



######################################### UTILS ##############################################################


###################################### ADMIN - SERVICE #############################################################

## View all services
@router.get(
    response_model = user.User,
    path = "/setting",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_200_OK,
    summary = "Go to Setting",
    tags= ["Admin-Setting"]
)
async def admin_setting(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        'admin/admin_setting.html',
        {'request':request,
        'admin': await AdminManager.get_user_by_email(db, current_user.email)})
