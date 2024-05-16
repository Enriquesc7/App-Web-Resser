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
from utils import get_db
from managers.admin import AdminManager
from managers.auth import get_current_active_user


# Templates
templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "",
    tags = ["User"],
    responses = {404: {"description": "Not found"}}, 
)



#========================= Welcome User ===============================


@router.get(
    path = "/started",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Form Register",
    tags= ["User"]
)
async def profile(
    request: Request    
):
    return templates.TemplateResponse(
        "users/welcome/collect_data.html",{"request":request})



@router.post(
    path = "/started",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Form Register",
    tags= ["User"]
)
async def profile(
    request: Request    
):
    
    
    
    
    return templates.TemplateResponse(
        "users/welcome/collect_data.html",{"request":request})




@router.get(
    path = "/welcome_1",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Welcome 1",
    tags= ["User"]
)
async def profile(
    request: Request    
):
    return templates.TemplateResponse(
        "users/welcome/welcome_1.html",{"request":request})


@router.get(
    path = "/welcome_2",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Welcome 2",
    tags= ["User"]
)
async def profile(
    request: Request    
):
    return templates.TemplateResponse(
        "users/welcome/welcome_2.html",{"request":request})


@router.get(
    path = "/welcome_3",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Welcome 3",
    tags= ["User"]
)
async def profile(
    request: Request    
):
    return templates.TemplateResponse(
        "users/welcome/welcome_3.html",{"request":request})



@router.get(
    path = "/welcome_4",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Welcome 4",
    tags= ["User"]
)
async def profile(
    request: Request    
):
    return templates.TemplateResponse(
        "users/welcome/welcome_4.html",{"request":request})




@router.get(
    path = "/welcome_5",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Welcome 5",
    tags= ["User"]
)
async def profile(
    request: Request    
):
    return templates.TemplateResponse(
        "users/welcome/welcome_5.html",{"request":request})




@router.get(
    path = "/welcome_6",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Welcome 6",
    tags= ["User"]
)
async def profile(
    request: Request    
):
    return templates.TemplateResponse(
        "users/welcome/welcome_6.html",{"request":request})

















#========================= Go to User Profile ===============================

### Show profile - /profile
@router.get(
    path = "/home",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Home",
    tags= ["User"]
)
async def profile(
    request: Request 
):
    return templates.TemplateResponse(
        "users/profile.html", {"request":request})



@router.get(
    path = "/escanear",
    response_model = user.User,
    response_class= HTMLResponse, 
    status_code = status.HTTP_200_OK,
    summary = "Home",
    tags= ["User"]
)
async def profile(
    request: Request 
):
    
    


    return templates.TemplateResponse(
        "users/escanear.html", {"request":request})



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
    path = "/{first_name}-{last_name}/logout",
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
    
    response = RedirectResponse("/", status_code= status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    user.disabled = True
    db.commit()
    db.refresh(user)

    return response