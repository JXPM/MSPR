from fastapi import APIRouter
from typing import List
from app.schemas.ligne_schema import LigneResponse
from app.services import ligne_service

router = APIRouter(prefix="/lignes", tags=["Lignes"])


@router.get("/", response_model=List[LigneResponse])
def get_lignes():
    return ligne_service.get_all_lignes()
