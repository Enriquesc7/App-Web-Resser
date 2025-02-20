# FastAPI
from fastapi import APIRouter
from fastapi import status, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Python
from typing import List
import json

# Project modules
from schemas import front

# Models
from models.location import Country, Region, Commune
from models.enum import PlanEnum

# SQLAlchemist
from sqlalchemy.orm import Session

# App
from utils import get_db

# Managers
from managers.front import FrontManager


# Templates
templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix = "",
    tags = ["Front app"],
    responses = {404: {"description": "Not found"}}, 
)


########################## TEMPLATES FRONT ####################################################################


### Index
@router.get(
    path = "/",
    response_class=HTMLResponse,
    status_code = status.HTTP_200_OK,
    summary = "Index app",
    tags= ["Front app"]
)
async def home(
    request: Request,
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "front/index.html",
        {"request":request,
        "img_slider": await FrontManager.get_slider(db),
        "services": await FrontManager.get_services(db)})



### Nosotros
@router.get(
    path = "/nosotros",
    response_class=HTMLResponse,
    status_code = status.HTTP_200_OK,
    summary = "Show information this company",
    tags= ["Front app"]
)
async def blog(
    request: Request
):
    return templates.TemplateResponse("front/us.html",{"request":request})



########################################### TEMAS LEGALES ###################################################

### Politica de Privacidad
@router.get(
    path = "/politica",
    response_class=HTMLResponse,
    status_code = status.HTTP_200_OK,
    summary = "Show policy information",
    tags= ["Front app"]
)
async def politica(
    request: Request
):
    #with open('data/la_cuarta.json', 'r', encoding='utf-8') as f:
    #    content = json.load(f)
        
    return templates.TemplateResponse("politica/politica.html",{"request":request})


### Cookies
@router.get(
    path = "/cookies",
    response_class=HTMLResponse,
    status_code = status.HTTP_200_OK,
    summary = "Show cookies information",
    tags= ["Front app"]
)
async def cookie(
    request: Request,
    db: Session = Depends(get_db)
):
    #add_location(db)
    #add_work_horus(db)

    return templates.TemplateResponse("politica/cookies.html",{"request":request})


############################################################################################
############################################################################################


'''
def add_work_horus(db):
    with open('data/work.json', 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    for area in content:
        work_area = WorkArea(
            area = area
        )
        db.add(work_area)
        db.commit()
        db.refresh(work_area)

        for employment in content[area]:
            employ = Employment(
                employment = employment,
                area = work_area.area
            )
            db.add(employ)
            db.commit()
            db.refresh(employ)

'''



# Agregamos las regiones y comunas de Chile
def add_location(db):
    with open('data/location.json', 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    # Agregamos Chile a la bbdd
    chile = Country(
        country = "Chile"
    )
    db.add(chile)
    db.commit()
    db.refresh(chile)
    # Agregamos las regiones a la bbdd
    for reg in content:
        region = Region(
            region = reg,
            country = chile.country
        )
        db.add(region)
        db.commit()
        db.refresh(region)
        # Agregamos las comunas pertenecientes a esas regiones a la bbdd
        for com in content[reg]:
            comuna = Commune(
                commune = com,
                region = region.region,
                country = chile.country
            )
            db.add(comuna)
            db.commit()
            db.refresh(comuna)
