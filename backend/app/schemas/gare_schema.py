from pydantic import BaseModel
from typing import Optional


class GareResponse(BaseModel):
    code_uic: str
    nom_gare: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    iso_pays: Optional[str] = None

    class Config:
        from_attributes = True
