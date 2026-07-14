# FastAPI 
from fastapi import APIRouter, UploadFile, File
from fastapi import status, Request, Depends
from fastapi.responses import RedirectResponse, Response, HTMLResponse
from fastapi.templating import Jinja2Templates

# Schemas
from schemas import user

# SQLAlchemist
from sqlalchemy.orm import Session

# app
from utils import get_db, send_email
from managers.admin import AdminManager
from managers.auth import get_current_active_user, get_optional_current_user

# Python
from typing import Optional



# Templates
templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "",
    tags = ["User"],
    responses = {404: {"description": "Not found"}}, 
)



#================= Go to Home ==================

@router.get(
    path="/home",
    response_class=HTMLResponse, 
    status_code=status.HTTP_200_OK,
    summary="Home",
    tags=["User"]
)
async def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[user.User] = Depends(get_optional_current_user)  # Ahora es opcional
):
    return templates.TemplateResponse(
        "users/profile.html", {"request": request, "user": current_user}
    )



# ============== Validamos la información enviada por el Form contact ===========




@router.post("/contact")
async def contact_form(form: user.ContactForm, db: Session = Depends(get_db)):
    """
    Procesa el formulario de contacto.
    """
    email_sent = await send_email(form.name, form.email, form.message)

    if email_sent:
        return {"message": "Mensaje enviado correctamente"}
    else:
        return {"message": "Error al enviar el mensaje. Inténtalo más tarde"}



#================= Go to Recycling Point ==================

# Ir a la sección de puntos de reciclaje
@router.get(
    path = "/recycling_point",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Recycling Point",
    tags= ["User"]
)
async def recycling_point(
    request: Request 
):
    return templates.TemplateResponse(
        "users/recycling_point.html", {"request":request})


# Ir al punto de collecta más cercano
@router.get(
    path = "/point_collector",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Find Point Collect",
    tags= ["User"]
)
async def recycling_point(
    request: Request 
):
    return templates.TemplateResponse(
        "users/point_collector.html", {"request":request})


# Primera interacción para reciclar
@router.get(
    path = "/action_recycling_1",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Find Point Collect",
    tags= ["User"]
)
async def recycling_point(
    request: Request 
):
    return templates.TemplateResponse(
        "users/action_recycling_1.html", {"request":request})



# Ganando puntos por reciclar
@router.get(
    path = "/win_resser_point",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Win Resser Point",
    tags= ["User"]
)
async def win_resser_point(
    request: Request 
):
    return templates.TemplateResponse(
        "users/resser_point.html", {"request":request})



# Ganando puntos por reciclar
@router.get(
    path = "/resser",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Win Resser Point",
    tags= ["User"]
)
async def resser(
    request: Request 
):
    return templates.TemplateResponse(
        "users/resser.html", {"request":request})


#================= Go to Shopping ==================

@router.get(
    path = "/shopping",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Section Shopping",
    tags= ["User"]
)
async def shopping(
    request: Request 
):
    return templates.TemplateResponse(
        "users/shopping.html", {"request":request})



#================= Go to Libraries ==================


# Sección global de como reciclar los diferentes residuos
@router.get(
    path = "/library",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Section Libraries",
    tags= ["User"]
)
async def shopping(
    request: Request 
):
    return templates.TemplateResponse(
        "users/library/library.html", {"request":request})



# Sección plastico
@router.get(
    path = "/library/plastic",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Section Libraries",
    tags= ["User"]
)
async def shopping(
    request: Request,
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        "users/library/library_plastic.html", {"request":request})


# Sección Papel
@router.get(
    path = "/library/paper",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Section Libraries",
    tags= ["User"]
)
async def shopping(
    request: Request,
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        "users/library/library_paper.html", {"request":request})


# Sección Vidrio
@router.get(
    path = "/library/glass",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Section Libraries",
    tags= ["User"]
)
async def shopping(
    request: Request,
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        "users/library/library_glass.html", {"request":request})


# Sección Compostaje
@router.get(
    path = "/library/composting",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Section Libraries",
    tags= ["User"]
)
async def shopping(
    request: Request,
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        "users/library/library_composting.html", {"request":request})










#=================== Go to Update User ============================

@router.get(
    path = "/{first_name}-{last_name}",
    response_model = user.User,
    response_class= HTMLResponse,
    status_code = status.HTTP_200_OK,
    summary = "Go to Profile",
    tags= ["User"]
)
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    return templates.TemplateResponse(
        "users/update_data_user.html",
        {"request":request,
        "user": await AdminManager.get_user_by_email(db, current_user.email)})

#==================== Update Info User ============================

@router.post(
    path = "/{first_name}-{last_name}/update",
    response_model = user.User,
    response_class= RedirectResponse,
    status_code = status.HTTP_200_OK,
    summary = "Update Profile",
    tags= ["User"]
)
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
    img_profile: UploadFile = File(...)
):
    # Cargamos los datos del formulario
    results = await request.form()
    await AdminManager.update_info_user(db, results, img_profile)

    # Obtenemos el usuario actualizado
    user = await AdminManager.get_user_by_id(db, current_user.id)
    
    return RedirectResponse("/"+user.first_name+"-"+user.last_name, status_code=status.HTTP_303_SEE_OTHER)



#======================= LogOut =====================================

# LogOut
@router.get(
    path = "/logout",
    response_model = user.User,
    response_class= RedirectResponse,
    status_code = status.HTTP_200_OK,
    summary = "LogOut",
    tags= ["User"]
)
async def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    # Obtenemos el usuario
    user = await AdminManager.get_user_by_email(db, current_user.email)
    
    response = RedirectResponse("/home", status_code= status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    user.disabled = True
    db.commit()
    db.refresh(user)

    return response