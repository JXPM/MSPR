from pydantic import BaseModel, Field


class TrajetBase(BaseModel):
    id_ligne: int
    gare_depart: str = Field(min_length=1, max_length=255)
    gare_arrivee: str = Field(min_length=1, max_length=255)
    heure_depart: str = Field(max_length=32)
    heure_arrivee: str = Field(max_length=32)


class TrajetResponse(TrajetBase):
    trajet_id: str = Field(min_length=1, max_length=64)

    class Config:
        from_attributes = True
