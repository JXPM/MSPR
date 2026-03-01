from pydantic import BaseModel

class GareResponse(BaseModel):
    code_uic: str
    gare_nom: str
    longitude: float
    latitude: float
    iso_pays: str

    class Config:
        from_attributes = True