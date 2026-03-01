from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Ligne(Base):
    __tablename__ = "ligne"

    id_ligne = Column(Integer, primary_key=True)
    ligne_nom = Column(String, nullable=False)
    distance = Column(Float)
    type_service = Column(String)

    code_operateur = Column(String, ForeignKey("operateur.code_operateur"))

    operateur = relationship("Operateur", back_populates="lignes")
    trajets = relationship("Trajet", back_populates="ligne")