# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import File, UploadFile

# Python
from typing import List
from os import getcwd, remove

# Schemas
from schemas import schema

# Models
from models.model import Service, User

# SQLAlchemist
from sqlalchemy.orm import Session

# app
from .admin import get_db, get_staff_user, verify_staff



templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix = "/admin",
    tags = ["Admin-Service"],
    responses = {418: {"description": "I'm a teapot"}},)



######################################### UTILS ##############################################################


###################################### ADMIN - SERVICE #############################################################

## View all services
@router.get(
    response_model = List[schema.Service],
    path = "/{username}/service",
    status_code = status.HTTP_200_OK,
    summary = "Show all services",
    tags= ["Admin-Service"]
)
async def show_all_services(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_staff_user)
):
    # Comprobamos que el usuario sea un admin
    verify_staff(request, db, current_user)
    # Obtenemos la información del path
    results = request.path_params
    # Controlamos que no vayan a otro admin a traves del path
    if current_user.username != results['username']:
        return RedirectResponse("/admin/"+current_user.username+"/service", status_code=status.HTTP_303_SEE_OTHER)

    # Obtenemos el admin para el username
    admin = db.query(User).filter_by(username = current_user.username).first()
    # Obtenemos todos los post de la bbdd
    all_services = db.query(Service).all()

    return templates.TemplateResponse(
        'admin/service.html',
        {'request':request,
        'admin':admin, 
        'all_services':all_services})




### Modified a service



######################## CREATE SERVICE ########################################################

## Go to create new post
@router.get(
    response_model = schema.Service,
    path = "/{username}/new-service",
    status_code = status.HTTP_200_OK,
    summary = "Go to create a new service",
    tags= ["Admin-Service"]
)
async def new_service(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_staff_user)
):
    # Comprobamos que el usuario sea un admin
    verify_staff(request, db, current_user)
    # Obtenemos la información del path
    results = request.path_params
    # Controlamos que no vayan a otro admin a traves del path
    if current_user.username != results['username']:
        return RedirectResponse("/admin/"+current_user.username+"/new-service", status_code=status.HTTP_303_SEE_OTHER)

    # Obtenemos el user para el username
    admin = db.query(User).filter_by(username = current_user.username).first()

    return templates.TemplateResponse('admin/new_service.html',{
        'request':request,
        'admin':admin})




## Create new post
@router.post(
    response_model = schema.Service,
    path = "/{username}/new-service",
    status_code = status.HTTP_201_CREATED,
    summary = "Create a new service",
    tags= ["Admin-Service"]
)
async def new_service(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_staff_user),
    img_service: UploadFile = File(...)
):
    # Comprobamos que el usuario sea un admin
    verify_staff(request, db, current_user)
    
   # Obtenemos los resultados del formulario 
    results = await request.form()

    # Guardamos la imagen en el directorio correspondiente
    print("Aca tenemos el resultado de getcwd", getcwd())
    with open(getcwd() + "/static/img/front/img_services/" + img_service.filename, "wb") as myfile:
        content = await img_service.read()
        myfile.write(content)
        myfile.close()
    
    # Rescatamos la información y la almacenamos en la bbdd
    service = Service(
        title = results['title'],
        description = results['description'],
        content = results['content'],
        category = results['category'],
        path_img_service = "img/front/img_services/" + img_service.filename
    )

    db.add(service)
    db.commit()
    db.refresh(service)
    
    username = current_user.username

    return RedirectResponse("/admin/"+username+"/service", 303)



# ============================================================================================================
# ======================== Delete Service ====================================================================

# # Deberia ocuparse el método "delete", investigar más...
@router.get(
    path = "/{username}/service/{service_id}/delete",
    response_model = schema.Mensaje,
    status_code = status.HTTP_200_OK,
    summary = "Delete a service",
    tags= ["Admin-Service"]
)
async def delete_service(
    request:Request, 
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_staff_user)
):
    # Comprobamos que el usuario sea un admin
    verify_staff(request, db, current_user)

    # Obtenemos el id del usuario
    results = request.path_params["service_id"]
 
    # Lo buscamos en la bbdd
    service= db.query(Service).filter_by(service_id = results).first()
    db.delete(service)
    db.commit()
    
    # Eliminamos la imagen del directorio
    try:
        remove(getcwd() + "/static/" + service.path_img_service)
    except FileNotFoundError:
        print("No se encontro la ruta del archivo. No se pudo eliminar.")

    # Obtenemos el username para el path_parameter
    username = current_user.username

    return RedirectResponse("/admin/"+username+"/service", 303)