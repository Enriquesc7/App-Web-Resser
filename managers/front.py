# FastAPI
from fastapi import HTTPException

# models
from models.front import Service, Slider, Plan

# Python
from os import getcwd, remove
from datetime import datetime


class FrontManager:
    @staticmethod   
    async def get_services(db):
        return db.query(Service).all()
    
    @staticmethod   
    async def get_slider(db):
        return db.query(Slider).all()
    
    @staticmethod   
    async def get_plans(db):
        return db.query(Plan).all()
    
    @staticmethod
    async def get_plan_by_name(db, name):
        return db.query(Plan).filter_by(name = name).first()
    
    @staticmethod
    async def add_promotion_slider(db, results, new_img, id):
        # Guardamos la imagen en el directorio correspondiente
        with open(getcwd() + "/static/img/front/slide_front/" + new_img.filename, "wb") as myfile:
            content = await new_img.read()
            myfile.write(content)
            myfile.close()
        
        # Rescatamos la información y la almacenamos en la bbdd
        new_img_slider = Slider(
            title = results['title'],
            path_img_slide = "img/front/slide_front/" + new_img.filename,
            admin = id
        )
        db.add(new_img_slider)
        db.commit()
        db.refresh(new_img_slider)


    @staticmethod
    async def delete_img_promotion(db, id):
        # Lo buscamos en la bbdd
        img_slider= db.query(Slider).filter_by(id = id).first()
        db.delete(img_slider)
        db.commit()
        # Eliminamos la imagen del directorio
        try:
            remove(getcwd() + "/static/" + img_slider.path_img_slide)
        except FileNotFoundError:
            print("No se encontro la ruta del archivo. No se pudo eliminar.")


    @staticmethod
    async def add_new_service(db, results, img_service, id):
        # Guardamos la imagen en el directorio correspondiente
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
            path_img_service = "img/front/img_services/" + img_service.filename,
            admin = id
        )
        db.add(service)
        db.commit()
        db.refresh(service)


    @staticmethod
    async def delete_service(db, id):
        # Lo buscamos en la bbdd
        service= db.query(Service).filter_by(id=id).first()
        db.delete(service)
        db.commit()
        # Eliminamos la imagen del directorio
        try:
            remove(getcwd() + "/static/" + service.path_img_service)
        except FileNotFoundError:
            print("No se encontro la ruta del archivo. No se pudo eliminar.")


    @staticmethod
    async def add_new_plan(db, results, id):
        # Rescatamos la información y la almacenamos en la bbdd
        plan = Plan(
            name = results['plan'],
            price = results['price'],
            renewal = results['renewal'],
            start_date = datetime.strptime(results['start_date'], "%m/%d/%Y"),
            end_date = datetime.strptime(results['end_date'], "%m/%d/%Y"),
            admin = id
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

    
    @staticmethod
    async def delete_plan(db, id):
        # Lo buscamos en la bbdd
        plan = db.query(Plan).filter_by(id=id).first()
        db.delete(plan)
        db.commit()