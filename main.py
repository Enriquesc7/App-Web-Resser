# Instalar las dependencias --> pip install -r requirements.txt
# Actualizar las dependencias en requirements.txt --> pip freeze > requirements.txt

#  Links importantes para el proyecto:
#
# CSS:
#       https://css-tricks.com/snippets/css/complete-guide-grid/
#       https://css-tricks.com/snippets/css/a-guide-to-flexbox/
#       https://htmx.org/docs/#ajax

# Transiciones CSS
#       https://www.transition.style/

# Ilustraciones, iconos, colores e inspiración...
#       https://www.toools.design/
#       https://freesets.vercel.app/
#       https://blush.design/es
#       https://colorhunt.co/
#       https://webkul.github.io/coolhue/
#       https://www.pixeltrue.com/packs
#       https://fontawesome.com/

# Soporte y compatibilidad
#       https://caniuse.com/

# Imágenes
#       https://fondosmil.com/

# Python
#       https://aprendepython.es/

# Comandos que me permiten modificar el puerto y navegar desde otro dispositivo
# Puerto (desde cmd, escribir ipconfig para encontrar el número de puerto)
# --> uvicorn main:app --reload --port "num_puerto"
# Navegar desde otro dispositivo (encontrandose en la misma red) -- IP pc --> 192.168.0.8
# --> uvicorn main:app --reload --host 192.168.23.27


# Repositorio curso Udemy - Ines (https://github.com/InesIvanova)
# https://github.com/InesIvanova/FastAPI-working-with-dbs
# https://github.com/InesIvanova/ComplaintSystemMainCourseAppFastAPI

# Repositorio curso Platzi - Pablo España
# https://github.com/platzi/curso-fastapi-sql/tree/11-refactorizacion-final


# Recomendaciones del curso: 
# Libreria "black": Nos servirá para ordenar, limpiar y mejorar nuestro código automaticamente con el comando
# black archivo.py (pip install black)


## Ngrok - https://dashboard.ngrok.com/login ##
#para poder crear servidores seguros y gratis. 

# Como usar QuaggaJS para escanear códigos de barras (en nuestro caso 'ean_reader'= EAN-13)
# https://scanbot.io/developer/techblog/quagga-js-tutorial/
# https://github.com/ericblade/quagga2?tab=readme-ov-file#decoder

# Para usarlo debo correr el proyecto de forma normal. En este caso nunca específicamos puerto
# pero uvicorn considera de forma predeterminada el 8000. Si quisiesemos especificar uno 
# Lo hacamos con
        #       uvicorn main:app --reload --port 8080

# Luego de ejecutar el proyecto, debemos iniciar Ngrok desde la aplicación y luego
# ejecutar el comando de acuerdo al puerto donde esté corriendo el proyecto

        #       ngrok http 8080

# Esto generará un enlace seguro (https) y podrá acceder quien sea independiente de la red. 




###############################################################################################################

# FastAPI
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Project modules
from db import engine, Base
from routers.auth import register, login
from routers.admin import admin, admin_cloud, admin_user, admin_front, admin_setting
from routers.front import front
from routers.user import product, user, setting


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.title = "App"
app.version = "0.0.1"

# Secciones de la app

app.include_router(login.router)
app.include_router(register.router)

app.include_router(front.router)

app.include_router(user.router)
app.include_router(product.router)
app.include_router(setting.router)

app.include_router(admin.router)
app.include_router(admin_user.router)
app.include_router(admin_front.router)
app.include_router(admin_cloud.router)
app.include_router(admin_setting.router)

app.mount("/static", StaticFiles(directory="static"), name = "static")
templates = Jinja2Templates(directory="templates")
