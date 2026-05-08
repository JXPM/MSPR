from pydantic import BaseModel


class OperateurBase(BaseModel):
    code_operateur: str
    nom_operateur: str
    iso_pays: str


class OperateurResponse(OperateurBase):
    class Config:
        from_attributes = True
