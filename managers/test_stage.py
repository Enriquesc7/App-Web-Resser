# FastAPI
from fastapi import HTTPException

# models
from models.model import UserStage

# Python
from os import getcwd, remove
from datetime import datetime


class FrontManager:
    @staticmethod   
    async def create_user_stage(db, results):
        user = UserStage(
            name = results['name'],
            age = results['age'],
            genero = results['genero']
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    