from sqlalchemy import Column, String

from src.core.database import Base


class School(Base):
    __tablename__ = "school"

    school_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    mascot = Column(String, nullable=True)
    school_type = Column(String, nullable=True)
    school_url = Column(String, nullable=True)

    def __repr__(self):
        return f"<School(id={self.school_id}, name={self.name})>"
