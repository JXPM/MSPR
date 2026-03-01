from pydantic import BaseModel
from datetime import time
from typing import Optional

class TrajetBase(BaseModel):
    ligne_id: int
    gare_depart: str
    gare_arrivee: str
    heure_depart: time
    heure_arrivee: time
    type_train_id: int


class TrajetResponse(TrajetBase):
    trajet_id: int

    class Config:
        from_attributes = True