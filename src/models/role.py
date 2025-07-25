from sqlalchemy import Column, String, CheckConstraint
from src.core.database import Base

class Role(Base):
    __tablename__ = "role"
    
    role_id = Column(String, primary_key=True)
    person_id = Column(String, nullable=False)
    role_type = Column(String, nullable=False)
    
    __table_args__ = (
        CheckConstraint("role_type IN ('wrestler', 'coach')", name='role_type_check'),
    )