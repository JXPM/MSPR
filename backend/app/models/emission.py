from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Emission(Base):
    __tablename__ = "emission"

    id_emission = Column(Integer, primary_key=True)
    transporteur = Column(String)
    origine = Column(String)
    destination = Column(String)

    distance_train_km = Column(Float)
    empreinte_train_kg = Column(Float)
    distance_route_km = Column(Float)
    distance_avion_km = Column(Float)
    empreinte_avion_kg = Column(Float)