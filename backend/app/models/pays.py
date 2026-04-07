from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base

class Pays(Base):
    __tablename__ = "pays"

    iso_pays = Column(String, primary_key=True)
    nom_pays = Column(String, nullable=False)

    gares = relationship("Gare", back_populates="pays")
    operateurs = relationship("Operateur", back_populates="pays")