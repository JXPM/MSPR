from pydantic import BaseModel


class EmissionBase(BaseModel):
    transporteur: str
    distance_train_km: float
    empreinte_train_kg: float
    distance_avion_km: float
    empreinte_avion_kg: float


class EmissionResponse(EmissionBase):
    id_emission: int

    class Config:
        from_attributes = True