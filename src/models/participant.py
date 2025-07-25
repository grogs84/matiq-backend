from sqlalchemy import CheckConstraint, Column, Integer, String

from src.core.database import Base


class Participant(Base):
    __tablename__ = "participant"

    participant_id = Column(String, primary_key=True)
    role_id = Column(String, nullable=False)
    tournament_id = Column(String, nullable=False)
    school_id = Column(String, nullable=False)
    person_id = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    weight_class = Column(String, nullable=True)
    seed = Column(String, nullable=True)

    def __repr__(self):
        return (
            f"<Participant(participant_id={self.participant_id}, role_id={self.role_id}, "
            f"tournament_id={self.tournament_id}, school_id={self.school_id}, "
            f"person_id={self.person_id}, year={self.year}, weight_class={self.weight_class}, "
            f"seed={self.seed})>"
        )

    __table_args__ = (
        CheckConstraint(
            "weight_class IS NULL OR weight_class != ''", name="weight_class_not_empty"
        ),
        CheckConstraint("seed IS NULL OR seed != ''", name="seed_not_empty"),
    )
