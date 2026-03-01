from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.trajet_schema import TrajetResponse
from app.services import trajet_service

router = APIRouter(prefix="/trajets", tags=["Trajets"])


@router.get("/", response_model=List[TrajetResponse])
def get_trajets():
    return trajet_service.get_all_trajets()


@router.get("/{trajet_id}", response_model=TrajetResponse)
def get_trajet(trajet_id: int):
    trajet = trajet_service.get_trajet_by_id(trajet_id)
    if not trajet:
        raise HTTPException(status_code=404, detail="Trajet not found")
    return trajet