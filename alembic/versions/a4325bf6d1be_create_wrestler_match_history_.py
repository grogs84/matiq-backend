"""create wrestler match history materialized view

Revision ID: [generated_id]
Revises: 81fcfa418034
Create Date: 2025-07-27 [timestamp]

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4325bf6d1be'
down_revision: Union[str, Sequence[str], None] = '81fcfa418034'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the wrestler_match_history materialized view
    op.execute("""
    CREATE MATERIALIZED VIEW wrestler_match_history AS
    SELECT
      per.slug as slug,
      part.year,
      part.weight_class,
      m.round,
      m.round_order,
      INITCAP(per.search_name) AS wrestler_name,
      per.person_id AS wrestler_person_id,
      ws.name wrestler_school_name,
      pm.is_winner,
      INITCAP(per2.search_name) AS opponent_name,
      os.name opponent_school_name,
      m.result_type,
      COALESCE(pm.score::text || ' - ' || pm1.score::text, m.fall_time) AS score
    FROM role
    JOIN person per ON per.person_id = role.person_id
    JOIN participant part ON role.role_id = part.role_id
    JOIN participant_match pm ON part.participant_id = pm.participant_id
    JOIN school ws on ws.school_id = part.school_id
    JOIN match m ON pm.match_id = m.match_id
    JOIN participant_match pm1 ON m.match_id = pm1.match_id
      AND pm.participant_id != pm1.participant_id
    JOIN participant part2 ON part2.participant_id = pm1.participant_id
    JOIN school os on os.school_id = part2.school_id
    JOIN role r2 ON part2.role_id = r2.role_id
    JOIN person per2 ON per2.person_id = r2.person_id;
    """)
    
    # Create indexes for better performance
    op.execute("""
    CREATE INDEX idx_wrestler_match_history_slug 
    ON wrestler_match_history (slug);
    """)
    
    op.execute("""
    CREATE INDEX idx_wrestler_match_history_person_year 
    ON wrestler_match_history (wrestler_person_id, year);
    """)
    
    op.execute("""
    CREATE INDEX idx_wrestler_match_history_weight_class 
    ON wrestler_match_history (weight_class);
    """)


def downgrade() -> None:
    # Drop the materialized view and its indexes
    op.execute("DROP MATERIALIZED VIEW IF EXISTS wrestler_match_history;")