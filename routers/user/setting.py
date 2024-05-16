# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends
from fastapi.templating import Jinja2Templates

# Python
from typing import List

# Schemas
from schemas import user

# Managers
from managers.admin import AdminManager

# SQLAlchemist
from sqlalchemy.orm import Session

# app
from utils import get_db
from .user import get_current_active_user




# Templates
templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "",
    tags = ["User-Setting"],
    responses = {404: {"description": "Not found"}}, 
)


#===============================================================================================================
#============================ Update User ======================================================================



@router.get(
    path = "/setting",
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Go to Setting",
    tags= ["User-Setting"]
)
async def setting(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        "users/setting.html",
        {"request":request,
        "user": await AdminManager.get_user_by_email(db, current_user.email) })
