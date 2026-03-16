from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Trajet(Base):
    __tablename__ = "trajet"

    trajet_id = Column(String(50), primary_key=True)

    gare_depart = Column(String(200))
    gare_arrivee = Column(String(200))

    heure_depart = Column(String(30))
    heure_arrivee = Column(String(30))

    id_ligne = Column(Integer, ForeignKey("ligne.id_ligne"))

    ligne = relationship("Ligne", back_populates="trajets")

    itineraires = relationship("Itineraire", back_populates="trajet")