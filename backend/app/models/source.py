from sqlalchemy import Column, Integer, String
from app.database import Base

class Source(Base):
    __tablename__ = "source"

    id_source = Column(Integer, primary_key=True)
    url = Column(String)
    nom_fichier = Column(String)
    format = Column(String)
    nombre_fichier = Column(Integer)