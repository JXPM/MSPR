from pydantic import BaseModel


class PaysBase(BaseModel):
    iso_pays: str
    nom_pays: str


class PaysResponse(PaysBase):
    class Config:
        from_attributes = True