# Pydantic
from pydantic import BaseModel, Field

# Python
from datetime import datetime

#================================== Schemas para Front ==========================================================

class Service(BaseModel):
    service_id: int = Field()
    title: str = Field(
        ...,
        max_length=50,
        example = 'Titulo de ejemplo'
    )
    description: str = Field(
        ...,
        max_length= 150,
        example = 'Descripción de algún proyecto de ejemplo'
    )
    content: str = Field(
        ...,
        max_length=2000,
        example = "Contenido de algún proyecto de ejemplo, podría ser cualquier cosa."
    )
    category: str = Field(
        ...,
        max_length=30,
        example = "categoriaX"
    )
    create_service: datetime = Field(
        ...,
        example = "24-01-2023"
    )
    path_img_service: str = Field(
        ...,
        max_length=100,
        example = "base/img/imagen.png"
    )

    class Config:
        orm_mode = True



########## Slider Post #############
class Slider(BaseModel):
    slide_id: int = Field()
    title: str = Field(
        ...,
        max_length=50,
        example = 'Titulo de ejemplo'
    )
    create: datetime = Field(
        ...,
        example = "24-01-2023"
    )
    path_img_slide: str = Field(
        ...,
        max_length=100,
        example = "base/img/imagen.png"
    )

    class Config:
        orm_mode = True

