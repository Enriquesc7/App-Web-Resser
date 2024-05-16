# Pydantic 
from pydantic import BaseModel

#=================================== Schemas para Person ===================================================

class BarcodeData(BaseModel):
    barcode: str