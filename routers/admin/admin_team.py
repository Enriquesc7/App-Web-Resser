# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

# Python
from typing import List, Optional
import json
from datetime import datetime

# Schemas
from schemas import front, user

# SQLAlchemist
from sqlalchemy.orm import Session

# Managers
from managers.auth import get_current_active_user
from managers.admin import is_staff, is_super_admin ,AdminManager
from managers.team import TeamManager

# app
from utils import get_db



templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix = "/admin",
    tags = ["Admin-Service"],
    responses = {418: {"description": "I'm a teapot"}},)



#===================== Go to Team ============================

@router.get(
    response_model = List[front.Service],
    path = "/team",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_200_OK,
    summary = "Go to Team",
    tags= ["Admin-Team"]
)
async def go_to_team(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        'admin/admin_team.html',
        {'request':request,
        'admin': await AdminManager.get_user_by_email(db, current_user.email),
        'regions': await TeamManager.get_regions(db),
        'work_areas': await TeamManager.get_work_areas(db),
        'team': await TeamManager.get_team(db),
        'permission': current_user.rol.value})


# Get commnes by region with Ajax
@router.get(
    path = "/team/ajax",
    status_code = status.HTTP_200_OK,
    summary = "Go to Team",
    tags= ["Admin-Team"]
)
async def communes_and_employments(
    region: Optional[str] = None,
    area: Optional[str] = None,
    db: Session = Depends(get_db),
):
    response = {}
    
    if region:
        # Obtenemos las comunas dada una region
        get_communes = await TeamManager.get_communes_by_region(db, region)
        communes = [commune.commune for commune in get_communes]
        response['communes'] = communes
    
    if area:
        # Obtenemos los empleos dada un area de trabajo
        get_employments = await TeamManager.get_employment_by_work_area(db, area)
        employments = [employment.employment for employment in get_employments]
        response['employments'] = employments

    return response


#================ Create new staff =================================

@router.post(
    path = "/team/new-staff/ajax",
    dependencies= [Depends(is_staff)],
    status_code = status.HTTP_201_CREATED,
    summary = "Create new staff",
    tags= ["Admin-Team"]
)
async def create_user(
    request:Request,
    db: Session = Depends(get_db)
):
    results = await request.form()
    await TeamManager.create_new_staff(db, results)

    return RedirectResponse('/admin/team', status_code=status.HTTP_303_SEE_OTHER)


#================ Delete Team Member ====================================

@router.get(
    path = "/team/{person_id}/delete",
    response_model = user.Mensaje,
    dependencies = [Depends(is_super_admin)],
    status_code = status.HTTP_200_OK,
    summary = "Delete Team Member",
    tags= ["Admin-Team"]
)
async def delete_team_member(
    db: Session = Depends(get_db),
    person_id: int = Path()
):
    await TeamManager.delete_team_member(db, person_id)

    return RedirectResponse("/admin/team", status_code=status.HTTP_303_SEE_OTHER)





