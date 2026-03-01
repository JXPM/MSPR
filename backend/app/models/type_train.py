from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class TypeTrain(Base):
    __tablename__ = "type_train"

    id_type_train = Column(Integer, primary_key=True)
    type_nom = Column(String, nullable=False)

    trajets = relationship("Trajet", back_populates="type_train")