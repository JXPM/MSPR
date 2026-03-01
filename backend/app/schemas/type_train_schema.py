from pydantic import BaseModel

class TypeTrainResponse(BaseModel):
    id_type_train: int
    type_nom: str

    class Config:
        from_attributes = True