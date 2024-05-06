# FastAPI
from fastapi import APIRouter
from fastapi import status, Request, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, Response

# Python
from typing import List

# Schemas
from schemas import user

# Models
from models.user import User

# SQLAlchemist
from sqlalchemy.orm import Session

# Managers
from managers.auth import get_current_active_user
from managers.admin import is_staff, is_super_admin, AdminManager

# app
from utils import get_db

templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "/admin",
    tags = ["Admin-User"],
    responses = {418: {"description": "I'm a teapot"}},)


#================================== USER =====================================================================

#============== Shorw all Users =============================
@router.get(
    response_model = List[user.User],
    path = "/users",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_200_OK,
    summary = "Show all users",
    tags= ["Admin-User"]
)
async def show_all_users(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
):
    return templates.TemplateResponse(
        'admin/admin_users.html',{
            'request':request,
            'admin': await AdminManager.get_user_by_email(db, current_user.email),
            'users':await AdminManager.get_users_by_rol(db, 'user'),
            'admins':await AdminManager.get_users_by_rol(db, 'admin'),
            'super_admins': await AdminManager.get_users_by_rol(db, 'super_admin'),
            'permission':current_user.rol.value})


#============= Create User ==============================


@router.post(
    path = "/users/create/ajax",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_201_CREATED,
    summary = "Create a User",
    tags= ["Admin-User"]
)
async def create_user(
    request:Request,
    db: Session = Depends(get_db)
):
    results = await request.form()
    user_created = await AdminManager.create_user(db, results)
    # Si se creo con exito no retorna nada, en caso contrario (existe o password_confirmation) retorna un alert
    if user_created != None:
        message = user_created.detail
        return {'message': message}
    message = "El usuario fue creado con exito"
    new_user = await AdminManager.get_user_by_email(db, results['email'])
    return {'message': message, 'new_user':new_user} 




#============= Update a User =============================
@router.get(
    path = "/users/{user_id}",
    dependencies= [Depends(is_staff)],
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Go to update a User",
    tags= ["Admin-User"]
)
async def go_update_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
    user_id: int = Path()
):
    return templates.TemplateResponse("admin/update_user.html",{
        "request":request, 
        "admin": await AdminManager.get_user_by_id(db, current_user.id),
        "user": await AdminManager.get_user_by_id(db, id = user_id)})


### Update a user // Deberia ser PUT ... investigar.
@router.post(
    path = "/users/{user_id}",
    dependencies= [Depends(is_staff)],
    response_model = user.Mensaje,
    status_code = status.HTTP_200_OK,
    summary = "Update a user",
    tags= ["Admin-User"]
)
async def update_user(
    request:Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
    username: str = Path(),
    user_id: str = Path()
):
    pass 




# ======================================================================================================
# ============================ DELETE USER =============================================================

### Delete a user  // Deberia ocuparse el método "delete", investigar más...
@router.get(
    path = "/users/{user_id}/delete",
    response_model = user.Mensaje,
    dependencies = [Depends(is_super_admin)],
    status_code = status.HTTP_200_OK,
    summary = "Delete a user",
    tags= ["Admin-User"]
)
async def delete_user(
    db: Session = Depends(get_db),
    user_id: int = Path()
):
    await AdminManager.delete_user(db, user_id)

    return RedirectResponse("/admin/users", status_code=status.HTTP_303_SEE_OTHER)