from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class Itineraire(Base):
    __tablename__ = "itineraire"

    # Schéma réel DB:
    # PRIMARY KEY (trajet_id, id_itineraire)
    trajet_id = Column(String(50), ForeignKey("trajet.trajet_id"), primary_key=True)
    id_itineraire = Column(Integer, primary_key=True)
    chemin = Column(String(1000))
    code_uic = Column(String, ForeignKey("gare.code_uic"))

    trajet = relationship("Trajet", back_populates="itineraires")
    gare = relationship("Gare", back_populates="itineraires")