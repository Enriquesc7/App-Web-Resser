# Instalar las dependencias --> pip install -r requirements.txt
# Actualizar las dependencias en requirements.txt --> pip freeze > requirements.txt

#  Links importantes para esta parte del proyecto 
#
#    https://css-tricks.com/snippets/css/complete-guide-grid/
#    https://css-tricks.com/snippets/css/a-guide-to-flexbox/
#    https://htmx.org/docs/#ajax

# Buena pagina de imagenes --> https://fondosmil.com/
#
#    En conclusión, aún no puedo aplicar AJAX a la barra del nav, pero si 
#    al contenido html de cada una de las paginas. 

# Comandos que me permiten modificar el puerto y navegar desde otro dispositivo
# Puerto
# --> uvicorn main:app --reload --port "num_puerto"
# Navegar desde otro dispositivo (encontrandose en la misma red) -- IP pc --> 192.168.0.8
# --> uvicorn main:app --reload --host 192.168.0.8

# Repositorio curso Udemy - Ines (https://github.com/InesIvanova)
# https://github.com/InesIvanova/FastAPI-working-with-dbs
# https://github.com/InesIvanova/ComplaintSystemMainCourseAppFastAPI

# Repositorio curso Platzi - Pablo España
# https://github.com/platzi/curso-fastapi-sql/tree/11-refactorizacion-final

# Recomendaciones del curso: 
# Libreria "black": Nos servirá para ordenar, limpiar y mejorar nuestro código automaticamente con el comando
# black archivo.py (pip install black)

###############################################################################################################

# FastAPI
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Project modules
from db import engine, Base
from routers.auth import register, login
from routers.admin import admin, admin_cloud, admin_user, admin_front, admin_setting, admin_team
from routers.front import front
from routers.user import plan, user, setting


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.title = "App"
app.version = "0.0.1"

# Secciones de la app

app.include_router(login.router)
app.include_router(register.router)

app.include_router(front.router)

app.include_router(user.router)
app.include_router(plan.router)
app.include_router(setting.router)

app.include_router(admin.router)
app.include_router(admin_user.router)
app.include_router(admin_front.router)
app.include_router(admin_team.router)
app.include_router(admin_cloud.router)
app.include_router(admin_setting.router)

app.mount("/static", StaticFiles(directory="static"), name = "static")
templates = Jinja2Templates(directory="templates")
