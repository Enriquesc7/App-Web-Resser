# FastAPI
from fastapi import status, HTTPException
from fastapi import Depends

# models
from models.user import User
from models.enum import UserRoleEnum
# schemas
from schemas import user

# Managers
from managers.auth import get_current_active_user, get_password_hash

# Python
from os import makedirs, remove, getcwd



class AdminManager:

    @staticmethod
    async def get_user_by_email(db, email):
        return db.query(User).filter_by(email = email).first()
    

    @staticmethod
    async def get_user_by_id(db, id):
        return db.query(User).filter_by(id = id).first()


    @staticmethod   
    async def get_users_by_rol(db, rol:str):
        return db.query(User).filter_by(rol = rol).all()
    

    @staticmethod
    async def update_info_user(db, results, img_profile):
        user = await AdminManager.get_user_by_id(db, user.id)
        # Creamos el directorio y almacenamos la imagen si existe
        await AdminManager.save_img(user.id, img_profile)

        user.first_name = results['first_name']
        user.last_name = results['last_name']
    
        if user.path_img_profile == None and img_profile.filename != "":
            user.path_img_profile = "img/users/"+str(user.id)+"/"+img_profile.filename

        elif img_profile.filename != "":
            try:
                # Eliminamos la imagen del directorio
                remove(getcwd() + "/static/" + user.path_img_profile)
                user.path_img_profile = "img/users/"+str(user.id)+"/"+img_profile.filename
            except FileNotFoundError:
                print("No se encontro la ruta del archivo. No se pudo eliminar.")
        
        db.commit()
        db.refresh(user)


    @staticmethod
    async def create_user(db, results):
        # Vemos si existe el correo (no pueden haber 2 iguales)
        email_exist = await AdminManager.get_user_by_email(db, results['email'])
      
        if email_exist:
            alert =  HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                   detail= "Este correo ya existe, intenta con otro.")
            return alert
        
        elif results['password'] != results['password_confirmation']:
            alert =  HTTPException(status_code = status.HTTP_400_BAD_REQUEST,
                                   detail= "Las contraseñas no son iguales.")
            return alert
        
        else:
            user = User(
                email = results['email'],
                hashed_password = get_password_hash(results['password']),
                first_name = results["first_name"],
                last_name = results["last_name"],
                rol = results['rol'])
            
        db.add(user)
        db.commit()
        db.refresh(user)


    @staticmethod
    async def delete_user(db, id):
        user_delete = await AdminManager.get_user_by_id(db, id)
        db.delete(user_delete)
        db.commit()


    @staticmethod
    async def save_img(id, img_profile):
        # Creamos el directorio de img para el usuario
        makedirs(getcwd()+"/static/img/admins/"+ str(id), exist_ok=True)
        # Guardamos la imagen en el directorio correspondiente
        try:
            with open(getcwd() + "/static/img/admins/"+ str(id) +"/"+ img_profile.filename, "wb") as myfile:
                content = await img_profile.read()
                myfile.write(content)
                myfile.close()
        except PermissionError:
            print("No se cargo ningun archivo")


    @staticmethod
    async def update_info_admin(db, results, img_profile):

        admin = await AdminManager.get_user_by_id(db, admin.id)
        # Creamos el directorio y almacenamos la imagen si existe
        await AdminManager.save_img(admin.id, img_profile)

        admin.first_name = results['first_name']
        admin.last_name = results['last_name']
        
        # Si no tiene imagen de perfil, la guardamos
        if admin.path_img_profile == None and img_profile.filename != "":
            admin.path_img_profile = "img/admins/"+ str(admin.id)+ "/"+ img_profile.filename

        # En caso de que ya tenga, eliminamos la anterior y guardamos la nueva
        elif img_profile.filename != "":
            try:
                # Eliminamos la imagen del directorio
                remove(getcwd() + "/static/" + admin.path_img_profile)
                admin.path_img_profile = "img/admins/"+ str(admin.id) +"/"+ img_profile.filename
            except FileNotFoundError:
                print("No se encontro la ruta del archivo. No se pudo eliminar.")
        
        db.commit()
        db.refresh(admin)



# Revisamos si tiene permisos de administrador y superadmin (que ambos puedan acceder)
def is_staff(current_user: user.User = Depends(get_current_active_user)):
    if not (current_user.rol.value == UserRoleEnum.admin.value or current_user.rol.value == UserRoleEnum.super_admin.value):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

# Revisamos si tiene permisos de super admin (unicamente un superadmin puede acceder)
def is_super_admin(current_user: user.User = Depends(get_current_active_user)):
    if not current_user.rol.value == UserRoleEnum.super_admin.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


