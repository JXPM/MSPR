from fastapi import APIRouter
from typing import List
from app.schemas.gare_schema import GareResponse
from app.services import gare_service

router = APIRouter(prefix="/gares", tags=["Gares"])


@router.get("/", response_model=List[GareResponse])
def get_gares():
    return gare_service.get_all_gares()