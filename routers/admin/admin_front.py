# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import File, UploadFile

# Python
from typing import List

# Schemas
from schemas import user, front

# SQLAlchemist
from sqlalchemy.orm import Session

# Managers
from managers.auth import get_current_active_user
from managers.admin import is_staff, is_super_admin, AdminManager
from managers.front import FrontManager

# app
from utils import get_db



templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix = "/admin",
    tags = ["Admin-Front"],
    responses = {418: {"description": "I'm a teapot"}},)


#============================ Admin Front ==============================================================

#============================== Go to Admin Front ====================================
@router.get(
    path = "/front",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_200_OK,
    summary = "Go to Admin Front",
    tags= ["Admin-Front"]
)
async def admin_front(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        'admin/admin_front.html',{
            'request':request,
            'admin': await AdminManager.get_user_by_email(db, current_user.email),
            'img_slider': await FrontManager.get_slider(db),
            'services': await FrontManager.get_services(db),
            'plans': await FrontManager.get_plans(db),
            'permission':current_user.rol.value})


#================================= Section for Create things Front =====================================

#=============== New Promotion (img) for the slider ================

## Create a new image for Slider
@router.post(
    response_model = front.Slider,
    path = "/front/img-slider",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_201_CREATED,
    summary = "Add promotion in Slider",
    tags= ["Admin-Front"]
)
async def new_img_slider(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
    new_img: UploadFile = File(...)
):
   # Obtenemos los resultados del formulario 
    results = await request.form()
    await FrontManager.add_promotion_slider(db, results, new_img, current_user.id)

    return RedirectResponse("/admin/front", status_code=status.HTTP_303_SEE_OTHER)



#=============== New service for the Services ================

## Create new service
@router.post(
    response_model = front.Service,
    path = "/front/new-service",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_201_CREATED,
    summary = "Create a new service",
    tags= ["Admin-Front"]
)
async def new_service(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
    img_service: UploadFile = File(...)
):
   # Obtenemos los resultados del formulario 
    results = await request.form()
    await FrontManager.add_new_service(db, results, img_service, current_user.id)

    return RedirectResponse("/admin/front", status_code=status.HTTP_303_SEE_OTHER)


#=============== New plan for the Plans ================

## Create new post
@router.post(
    path = "/front/new-plan",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_201_CREATED,
    summary = "Create a new plan",
    tags= ["Admin-Front"]
)
async def new_service(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
): 
   # Obtenemos los resultados del formulario 
    results = await request.form()
    await FrontManager.add_new_plan(db, results, current_user.id)

    return RedirectResponse("/admin/front", status_code=status.HTTP_303_SEE_OTHER)


#=======================================================================================================
#================================= Section for Delete things Front =====================================

#============== Delete image Slider =================

@router.get(
    path = "/front/{slide_id}/delete-img",
    dependencies= [Depends(is_super_admin)],
    response_model = user.Mensaje,
    status_code = status.HTTP_200_OK,
    summary = "Delete img slider",
    tags= ["Admin-Front"]
)
async def delete_service(
    db: Session = Depends(get_db),
    slide_id: int = Path()
):
    await FrontManager.delete_img_promotion(db, slide_id)
    return RedirectResponse("/admin/front", status_code=status.HTTP_303_SEE_OTHER)


#==================== Delete service  ==========================

@router.get(
    path = "/{username}/front/{service_id}/delete-service",
    dependencies= [Depends(is_super_admin)],
    response_model = user.Mensaje,
    status_code = status.HTTP_200_OK,
    summary = "Delete a service",
    tags= ["Admin-Service"]
)
async def delete_service(
    db: Session = Depends(get_db),
    service_id: int = Path()
):
    await FrontManager.delete_service(db, service_id)
    return RedirectResponse("/admin/front", status_code=status.HTTP_303_SEE_OTHER)


#============== Delete Plan =================

@router.get(
    path = "/front/{plan_id}/delete-plan",
    dependencies= [Depends(is_super_admin)],
    status_code = status.HTTP_200_OK,
    summary = "Delete plan",
    tags= ["Admin-Front"]
)
async def delete_service(
    db: Session = Depends(get_db),
    plan_id: int = Path()
):
    await FrontManager.delete_plan(db, plan_id)
    return RedirectResponse("/admin/front", status_code=status.HTTP_303_SEE_OTHER)
