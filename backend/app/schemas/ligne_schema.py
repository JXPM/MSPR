from pydantic import BaseModel
from typing import Optional

class LigneBase(BaseModel):
    ligne_nom: str
    distance: float
    type_service: Optional[str]


class LigneResponse(LigneBase):
    id_ligne: int

    class Config:
        from_attributes = True