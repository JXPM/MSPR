from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Operateur(Base):
    __tablename__ = "operateur"

    code_operateur = Column(String, primary_key=True)
    operateur_nom = Column(String, nullable=False)
    iso_pays = Column(String, ForeignKey("pays.iso_pays"))

    pays = relationship("Pays", back_populates="operateurs")
    lignes = relationship("Ligne", back_populates="operateur")