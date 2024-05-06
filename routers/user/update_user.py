# FastAPI 
from fastapi import APIRouter, UploadFile, File
from fastapi import status, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# Python
from typing import List
from os import getcwd, remove, makedirs

# Schemas
from schemas import schema

# Models
from models.model import User

# SQLAlchemist
from sqlalchemy.orm import Session

# app
from utils import get_db
from .user import get_current_active_user, verify_user




# Templates
templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "/profile",
    tags = ["Users"],
    responses = {404: {"description": "Not found"}}, 
)


#===============================================================================================================
#============================ Update User ======================================================================



@router.get(
    path = "/{username}/update",
    response_model = schema.User,
    status_code = status.HTTP_200_OK,
    summary = "Go to Update a profile",
    tags= ["Users"]
)
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_current_active_user)
):
    # Comprobamos si es usuario
    verify_user(request, db, current_user)
    # Obtenemos la información del path
    results = request.path_params
    # Controlamos que no vayan a otro usuario a traves del path
    if current_user.username != results['username']:
        return RedirectResponse("/profile/"+current_user.username+"/update", status_code=status.HTTP_303_SEE_OTHER)

    # Obtenemos el usuario de la ddbb
    user = db.query(User).filter_by(username = current_user.username).first()

    return templates.TemplateResponse(
        "users/update_data_user.html",
        {"request":request,
        "user":user})



@router.post(
    path = "/{username}/update",
    response_model = schema.User,
    status_code = status.HTTP_200_OK,
    summary = "Update a profile",
    tags= ["Users"]
)
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schema.User = Depends(get_current_active_user),
    img_profile: UploadFile = File(...)
):
    
    # Comprobamos si es usuario
    verify_user(request, db, current_user)

    # Encontramos al usuario dado su autenticación...
    user = db.query(User).filter_by(username = current_user.username).first()
    username = user.username
    # Cargamos los datos del formulario
    results = await request.form()
    print("Llegamos aca, y la ruta del getcwd() es: ", getcwd())
    # Creamos el directorio de img para el usuario
    makedirs(getcwd()+"/static/img/users/"+username, exist_ok=True)
    # Guardamos la imagen en el directorio correspondiente
    try:
        with open(getcwd() + "/static/img/users/"+username+"/"+img_profile.filename, "wb") as myfile:
            content = await img_profile.read()
            myfile.write(content)
            myfile.close()
    except PermissionError:
        print("No se cargo ningún archivo")
    # Idealmente que no puedan mofificar el username y correo... debe ser con un permiso especial...
    #user.username = results['username']
    user.first_name = results['first_name']
    user.last_name = results['last_name']
    #user.email = results['email']
    user.rut = None if results['rut'] == '' else results['rut']
    user.birthday = None if results['birthday'] == '' else results['birthday']
    user.address = None if results['address'] == '' else results['address']
    user.commune = None if results['commune'] == '' else results['commune']
    user.region = None if results['region'] == '' else results['region']
    user.country = None if results['country'] == '' else results['country']
    
    print("La wea rara, veamos: ", img_profile.filename)
    if user.path_img_profile == None and img_profile.filename != "":
        user.path_img_profile = "img/users/"+username+"/"+img_profile.filename

    elif img_profile.filename != "":
        try:
            # Eliminamos la imagen del directorio
            remove(getcwd() + "/static/" + user.path_img_profile)
            user.path_img_profile = "img/users/"+username+"/"+img_profile.filename
        except FileNotFoundError:
            print("No se encontro la ruta del archivo. No se pudo eliminar.")
    
    db.commit()
    db.refresh(user)

    return RedirectResponse("/profile/"+username, status_code=status.HTTP_303_SEE_OTHER)
