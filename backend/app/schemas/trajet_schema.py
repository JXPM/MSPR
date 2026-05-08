from pydantic import BaseModel


class TrajetBase(BaseModel):
    id_ligne: int
    gare_depart: str
    gare_arrivee: str
    heure_depart: str
    heure_arrivee: str


class TrajetResponse(TrajetBase):
    trajet_id: str

    class Config:
        from_attributes = True
