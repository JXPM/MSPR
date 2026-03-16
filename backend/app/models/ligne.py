from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class Ligne(Base):
    __tablename__ = "ligne"

    id_ligne = Column(Integer, primary_key=True)
    nom_ligne = Column(String(100))
    distance = Column(Numeric(15,2))
    type_service = Column(String(50))

    trajets = relationship("Trajet", back_populates="ligne")