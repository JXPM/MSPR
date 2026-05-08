from pydantic import BaseModel
from typing import Optional


class LigneResponse(BaseModel):
    id_ligne: int
    nom_ligne: str
    distance: Optional[float] = None
    type_service: Optional[str] = None

    class Config:
        from_attributes = True
