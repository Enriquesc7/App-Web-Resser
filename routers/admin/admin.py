# FastAPI 
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi import status, Request, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# Python
from typing import List
from os import getcwd, makedirs, remove

# Schemas
from schemas import user

# Models
from models.user import User

# SQLAlchemist
from sqlalchemy.orm import Session

# app
from utils import get_db

# Managers
from managers.admin import is_staff, AdminManager
from managers.auth import get_current_active_user

templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "/admin",
    tags = ["Admin"],
    responses = {418: {"description": "I'm a teapot"}},)

#================================ Admin ==============================================================


## Admin profile
@router.get(
    response_model = user.User,
    dependencies= [Depends(is_staff)],
    path = "/{first_name}-{last_name}",
    status_code = status.HTTP_200_OK,
    summary = "Home admin",
    tags= ["Admin"]
)
async def profile_admin(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        'admin/admin_profile.html',
        {'request':request,
         'admin': await AdminManager.get_user_by_email(db, current_user.email)})



## Go to update profile
@router.get(
    response_model = user.User,
    path = "/{first_name}-{last_name}/update",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_200_OK,
    summary = "Go to update admin",
    tags= ["Admin"]
)
async def profile_admin(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
):
    return templates.TemplateResponse(
        'admin/update_admin.html',
        {'request': request,
         'admin': await AdminManager.get_user_by_id(db, current_user.id)})



@router.post(
    path = "/{first_name}-{last_name}/update",
    dependencies= [Depends(is_staff)],
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Update Admin",
    tags= ["Admin"]
)
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
    img_profile: UploadFile = File(...)
):
    # Cargamos los datos del formulario
    results = await request.form()   
    # Actualizamos según la información ingresada 
    await AdminManager.update_info_admin(db, results, img_profile, current_user.id)
    # Obtenemos el admin actualizado
    admin = await AdminManager.get_user_by_id(db, current_user.id)
    
    return RedirectResponse("/admin/"+admin.first_name+"-"+admin.last_name, status_code=status.HTTP_303_SEE_OTHER)
