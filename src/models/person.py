from sqlalchemy import Column, DateTime, String

from src.core.database import Base


class Person(Base):
    __tablename__ = "person"

    person_id = Column(String, primary_key=True)
    slug = Column(String, unique=True) 
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    search_name = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    city_of_origin = Column(String, nullable=True)
    state_of_origin = Column(String, nullable=True)

    def __repr__(self):
        return f"<Person(person_id={self.person_id}, first_name={self.first_name}, last_name={self.last_name})>"
