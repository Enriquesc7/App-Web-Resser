# SQLAlchemist
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum

# Models
from models.enum import UserRoleEnum

# App
from db import Base

# Utils
from datetime import datetime

#========================== Sección tablas Usuarios ==========================================================

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True, index = True)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(64), nullable=False)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    path_img_profile = Column(String(100))
    create = Column(DateTime, default=datetime.now)
    update = Column(DateTime, onupdate=datetime.now)
    rol = Column(Enum(UserRoleEnum), default=UserRoleEnum.user.value, nullable=False)
    disabled = Column(Boolean, default=True, nullable=False)

# ALEMBIC
# Para gestionar las migraciones de la base de datos se utilizará 'alembic' (pip install alembic) que nos 
# sirve para agilizar y controlar los cambios realidados en la bbdd. Es como un git, pero para la bbdd.

# Debemos inicializarlo con: 
# 'alembic init alembic'

# Lo siguiente es modificar la variable 'sqlalchemy.url' indicandole la ruta de la bbdd en 'alembic.ini'

# # Luego vamos al archivo 'env.py' y modificamos la variable 'target_metadata' que esta en None, y ponemos
# la variable metadata ubicada en  'from config.database import metadata'

# Luego creamos una revisión automatica con el nombre 'Initial' y actualizamos con 'alembic upgrade head'
# alembic revision --autogenerate -m "Initial"
# alembic upgrade head

# Ahora, cualquier cambio que hagamos en la base de datos, creación de tablas u otro, debemos registralo aca...
# Para ello debemos ejecutar los mismos 2 comandos anteriores
# 
# alembic revision --autogenerate -m "texto identificador del cambio"
# alembic upgrade head
