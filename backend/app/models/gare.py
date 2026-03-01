from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Gare(Base):
    __tablename__ = "gare"

    code_uic = Column(String, primary_key=True)
    gare_nom = Column(String, nullable=False)
    longitude = Column(Float)
    latitude = Column(Float)
    iso_pays = Column(String, ForeignKey("pays.iso_pays"))

    pays = relationship("Pays", back_populates="gares")
    itineraires = relationship("Itineraire", back_populates="gare")