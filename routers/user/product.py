# FastAPI 
from fastapi import APIRouter
from fastapi import status, Request, Depends, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse

# Python
from typing import List
import json

# Schemas
from schemas import user
from schemas.product import BarcodeData

# SQLAlchemist
from sqlalchemy.orm import Session

# Managers
from managers.admin import AdminManager


# app
from utils import get_db
from .user import get_current_active_user


# Templates
templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = "",
    tags = ["User-Products"],
    responses = {404: {"description": "Not found"}}, 
)


#===============================================================================================================
#============================ Products User ======================================================================

# Mostramos todos los productos
@router.get(
    path = "/products",
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Show all Products",
    tags= ["User-Products"]
)
async def products_user(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    with open('data/open_food.json', 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    return templates.TemplateResponse(
        "users/products.html",
        {"request":request,
        "user": await AdminManager.get_user_by_email(db, current_user.email),
        "products": products})



# Mostramos la información específica del producto
@router.get(
    path = "/products/{bar_code}",
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Show information about product",
    tags= ["User-Products"]
)
async def info_product(
    request: Request,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user),
    bar_code: str = Path()
):
    # Cargamos la información del archivo
    with open('data/open_food.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Identificamos el producto que queremos mostrar dado el código de barras
    product = next((product for product in products if product['basic_data']['bar_code'] == bar_code) , None)
    
    return templates.TemplateResponse(
        "users/info_product.html",
        {"request":request,
        "user": await AdminManager.get_user_by_email(db, current_user.email),
        'product': product})



# Petición Ajax para lectura de códigos de barra
@router.post(
    path = "/get_barcode",
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Show information with barcode",
    tags= ["User-Products"]
)
async def product_lookup(
    request: Request,
    barcode: BarcodeData,
    db: Session = Depends(get_db),
    current_user: user.User = Depends(get_current_active_user)
):
    # Cargamos la información del archivo
    with open('data/open_food-big.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    #Mostramos el valor por consola
    print("Codigo escaneado", barcode.barcode)

    # Identificamos el producto que queremos mostrar dado el código de barras
    product = next((product for product in products if product['basic_data']['bar_code'] == barcode.barcode) , None)
    
    print('Vemos si esta el producto:', product)

    message = "Este producto aún no se encuentra en nuestra base de datos. Lamentamos el inconveniente."


    if product is None:
        print(message)
        # Si el producto no se encuentra, devolver una respuesta JSON con el mensaje de no encontrado
        return JSONResponse(status_code=200, content={"message": message})
    else:
        # Si el producto se encuentra, devolver una respuesta JSON con la URL del producto
        return JSONResponse(status_code=200, content={"redirect": f"/products/{barcode.barcode}"})


    #if product is None:
    #    return templates.TemplateResponse(
    #        "users/profile.html",
    #        {"request":request,
    #        "user": await AdminManager.get_user_by_email(db, current_user.email)})
    #
    #else:
    #    return RedirectResponse(f"/products/{barcode.barcode}", status_code=status.HTTP_302_FOUND)
    
