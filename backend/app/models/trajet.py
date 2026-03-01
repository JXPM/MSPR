from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.database import Base

class Trajet(Base):
    __tablename__ = "trajet"

    trajet_id = Column(Integer, primary_key=True)

    ligne_id = Column(Integer, ForeignKey("ligne.id_ligne"))
    gare_depart = Column(String, ForeignKey("gare.code_uic"))
    gare_arrivee = Column(String, ForeignKey("gare.code_uic"))

    heure_depart = Column(Time)
    heure_arrivee = Column(Time)

    ligne = relationship("Ligne", back_populates="trajets")
    type_train_id = Column(Integer, ForeignKey("type_train.id_type_train"))
    type_train = relationship("TypeTrain", back_populates="trajets")

    itineraires = relationship("Itineraire", back_populates="trajet")