from sqlalchemy import Column, Integer, String
from app.database import Base


class TypeTrain(Base):
    __tablename__ = "type_train"

    id_type_train = Column(Integer, primary_key=True)
    type_nom = Column(String)
