# Pydantic
from pydantic import BaseModel, Field

#============================== Schemas para Ubicación ======================================================

class Country(BaseModel):
    id: int = Field()
    country_name: str = Field(
        ...,
        max_length= 15,
        example = 'Chile'
    )

class Region(BaseModel):
    id: int = Field(),
    region_name: str = Field(
        ...,
        max_length=20,
        example = 'Metropolitana'
    )

class Commune(BaseModel):
    id: int = Field(),
    commune_name: str = Field(
        ...,
        max_length=20,
        example = 'Recoleta'
    ),
    postal_code: str = Field(
        ...,
        max_length=15,
        example = '80004300'
    )
