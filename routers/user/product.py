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
    current_user: user.User = Depends(get_current_active_user),
    page: int = 1,
    limit: int = 50
):
    with open('data/open_food-big.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    total_products = len(products)
    start = (page - 1)*limit
    end = start + limit
    paginated_products = products[start:end]
    total_pages = (total_products // limit) 
    total_pages = (total_products // limit) + (1 if total_products % limit > 0 else 0)
    pagination = get_pagination(page, total_pages)
    
    return templates.TemplateResponse(
        "users/products.html",
        {"request":request,
        "user": await AdminManager.get_user_by_email(db, current_user.email),
        "products": paginated_products,
        "page": page,
        "total_pages": total_pages,
        "pagination": pagination,})





# Mostramos la información específica del producto
@router.get(
    path = "/products/3179732326911",
    response_model = user.User,
    status_code = status.HTTP_200_OK,
    summary = "Show information about product",
    tags= ["User-Products"]
)
async def info_product(
    request: Request,
):

    f ={
    "url": "https://fr.openfoodfacts.org/produit/3179732326911/eau-vittel",
    "basic_data": {
        "title": "Eau Vittel - 1 l",
        "bar_code": "3179732326911",
        "image": "https://images.openfoodfacts.org/images/products/317/973/232/6911/front_fr.22.400.jpg",
        "generic_name": 'null',
        "quantity": "1 l",
        "packaging": [
            "Plastique"
        ],
        "brands": "Vittel",
        "categories": [
            "Boissons et préparations de boissons",
            "Boissons",
            "Eaux",
            "Eaux de sources",
            "Eaux minérales",
            "Boissons sans sucre ajouté",
            "Eaux minérales naturelles"
        ],
        "labels": {
            "name": [],
            "image": 'null'
        },
        "manufacturing": [],
        "countries": [
            "France"
        ]
    },
    "nutritional_data": {
        "nutriscore": {
            "image": "https://static.openfoodfacts.org/images/attributes/dist/nutriscore-a.svg",
            "grade": "Nutri-Score A",
            "content": "Très bonne qualité nutritionnelle"
        },
        "nova": {
            "image": "https://static.openfoodfacts.org/images/attributes/dist/nova-group-1.svg",
            "grade": "NOVA 1",
            "content": "Aliments non transformés ou minimalement transformés"
        }
    },
    "environment_data": {
        "ecoscore": {
            "image": "https://static.openfoodfacts.org/images/attributes/dist/ecoscore-not-applicable.svg",
            "grade": "\n                \n                Eco-Score n'est pas encore applicable\n            ",
            "content": "Pas encore applicable pour la catégorie : Eaux"
        },
        "packaging": {
            "image": "https://static.openfoodfacts.org/images/icons/dist/packaging.svg",
            "image_label": 'null',
            "content": "\n                \n                Emballage à impact moyen\n            ",
            "materials": {
                "columns": [
                    "\n                    Matière\n                ",
                    "\n                    %\n                ",
                    "\n                    Poids de l'emballage\n                ",
                    "\n                    Poids de l'emballage pour 100 g de produit\n                "
                ],
                "rows": [
                    "\n            Plastique\n        ",
                    "\n            \n        ",
                    "\n            \n        ",
                    "\n            \n        "
                ]
            }
        },
        "transport": {
            "image": "https://static.openfoodfacts.org/images/icons/dist/public.svg",
            "title_image": "\n                \n                Origines des ingrédients\n            ",
            "content": "Origines des ingrédients ayant un faible impact",
            "origins_table": {
                "columns": [
                    "\n                    Origine du produit et/ou de ses ingrédients\n                ",
                    "\n                    % d'ingrédients\n                ",
                    "\n                    Impact\n                "
                ],
                "rows": []
            }
        }
    }
}


    product = f

    
    
    return templates.TemplateResponse(
        "users/info_product.html",
        {"request":request,
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
    


# ===== Funciones varias ==========================0



def get_pagination(page: int, total_pages: int, delta: int = 6):
    if total_pages <= 1:
        return []

    pages = []
    for p in range(1, total_pages + 1):
        if p == 1 or p == total_pages or abs(p - page) <= delta:
            pages.append(p)
        elif pages and pages[-1] != '...':
            pages.append('...')
    
    return pages