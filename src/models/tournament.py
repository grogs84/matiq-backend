from sqlalchemy import Column, Date, Integer, String

from src.core.database import Base


class Tournament(Base):
    __tablename__ = "tournament"

    tournament_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    year = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
