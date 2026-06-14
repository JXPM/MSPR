from pydantic import BaseModel, Field


class EmissionsRequest(BaseModel):
    """Corps de requete pour la prediction d'empreinte CO2 ferroviaire."""

    distance_km: float = Field(gt=0, description="Distance du trajet en km")
    operateur: str = Field(description="Nom de l'operateur ferroviaire")
    type_service: str = Field(
        pattern=r"^(JOUR|NUIT)$",
        description="Type de service: JOUR ou NUIT",
    )
    duree_trajet_min: float = Field(gt=0, description="Duree du trajet en minutes")


class EmissionsResponse(BaseModel):
    """Reponse de prediction d'empreinte CO2 ferroviaire."""

    empreinte_train_kg: float
    unite: str = "kg CO2"
    operateur: str
    distance_km: float
    type_service: str


class ClusterRequest(BaseModel):
    """Corps de requete pour l'identification du cluster de substitution."""

    distance_km: float = Field(gt=0, description="Distance du trajet en km")
    empreinte_train_kg: float = Field(gt=0, description="Empreinte CO2 du train en kg")
    empreinte_avion_kg: float = Field(gt=0, description="Empreinte CO2 de l'avion en kg")
    ratio_co2: float = Field(gt=0, description="Ratio empreinte train / empreinte avion")


class ClusterResponse(BaseModel):
    """Reponse d'identification du cluster de substitution avion/train."""

    cluster: int
    label: str
    description: str


class PredictFullRequest(BaseModel):
    """Corps de requete pour la prediction complete (emissions + cluster) en un seul appel."""

    distance_km: float = Field(gt=0, description="Distance du trajet en km")
    operateur: str = Field(description="Nom de l'operateur ferroviaire")
    type_service: str = Field(
        pattern=r"^(JOUR|NUIT)$",
        description="Type de service: JOUR ou NUIT",
    )
    duree_trajet_min: float = Field(gt=0, description="Duree du trajet en minutes")


class PredictFullResponse(BaseModel):
    """Reponse combinee: empreinte CO2 et cluster de substitution."""

    empreinte_train_kg: float
    unite: str = "kg CO2"
    operateur: str
    distance_km: float
    type_service: str
    cluster: int
    label: str
    description: str
