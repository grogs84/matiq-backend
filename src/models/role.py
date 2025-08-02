from sqlalchemy import CheckConstraint, Column, String, DateTime, func

from src.core.database import Base


class Role(Base):
    __tablename__ = "role"

    role_id = Column(String, primary_key=True)
    person_id = Column(String, nullable=False)
    role_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "role_type IN ('wrestler', 'coach', 'admin', 'moderator', 'editor')", 
            name="role_type_check"
        ),
    )
