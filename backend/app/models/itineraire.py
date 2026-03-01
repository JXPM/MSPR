from sqlalchemy import Column, Integer, ForeignKey, String, Time
from sqlalchemy.orm import relationship
from app.database import Base

class Itineraire(Base):
    __tablename__ = "itineraire"

    id_itineraire = Column(Integer, primary_key=True)
    ordre_passage = Column(Integer)

    heure_depart = Column(Time)
    heure_arrivee = Column(Time)

    trajet_id = Column(Integer, ForeignKey("trajet.trajet_id"))
    code_uic = Column(String, ForeignKey("gare.code_uic"))

    trajet = relationship("Trajet", back_populates="itineraires")
    gare = relationship("Gare", back_populates="itineraires")