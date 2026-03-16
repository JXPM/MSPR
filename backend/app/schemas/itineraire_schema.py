from pydantic import BaseModel


class ItineraireBase(BaseModel):
    chemin: str


class ItineraireResponse(ItineraireBase):
    id_itineraire: int

    class Config:
        from_attributes = True