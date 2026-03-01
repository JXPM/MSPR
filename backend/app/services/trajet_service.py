from typing import List
from app.schemas.trajet_schema import TrajetResponse
from datetime import time


def get_all_trajets() -> List[TrajetResponse]:
    # MOCK TEMPORAIRE (sera remplacé par requête SQLAlchemy)
    return [
        TrajetResponse(
            trajet_id=1,
            ligne_id=10,
            gare_depart="LILLE",
            gare_arrivee="PARIS",
            heure_depart=time(8, 30),
            heure_arrivee=time(9, 45),
            type_train_id=2
        )
    ]


def get_trajet_by_id(trajet_id: int) -> TrajetResponse:
    return TrajetResponse(
        trajet_id=trajet_id,
        ligne_id=10,
        gare_depart="LILLE",
        gare_arrivee="PARIS",
        heure_depart=time(8, 30),
        heure_arrivee=time(9, 45),
        type_train_id=2
    )