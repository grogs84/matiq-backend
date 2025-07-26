"""populate slugs for person, school, tournament

Revision ID: 81fcfa418034
Revises: 2d51d664b8cf
Create Date: 2025-07-26 07:23:30.819527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81fcfa418034'
down_revision: Union[str, Sequence[str], None] = '2d51d664b8cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Person
    op.execute("""
    WITH base AS (
        SELECT person_id,
               lower(regexp_replace(search_name, '[^a-z0-9]+', '-', 'g')) AS base_slug
        FROM person
    ),
    ranked AS (
        SELECT person_id,
               base_slug,
               ROW_NUMBER() OVER (PARTITION BY base_slug ORDER BY person_id) AS rn
        FROM base
    ),
    final AS (
        SELECT person_id,
               CASE
                   WHEN rn = 1 THEN base_slug
                   ELSE base_slug || '-' || rn
               END AS unique_slug
        FROM ranked
    )
    UPDATE person
    SET slug = final.unique_slug
    FROM final
    WHERE person.person_id = final.person_id;
    """)

    # School
    op.execute("""
    WITH base AS (
        SELECT school_id,
               lower(regexp_replace(name, '[^a-z0-9]+', '-', 'g')) AS base_slug
        FROM school
    ),
    ranked AS (
        SELECT school_id,
               base_slug,
               ROW_NUMBER() OVER (PARTITION BY base_slug ORDER BY school_id) AS rn
        FROM base
    ),
    final AS (
        SELECT school_id,
               CASE
                   WHEN rn = 1 THEN base_slug
                   ELSE base_slug || '-' || rn
               END AS unique_slug
        FROM ranked
    )
    UPDATE school
    SET slug = final.unique_slug
    FROM final
    WHERE school.school_id = final.school_id;
    """)

    # Tournament (name + year)
    op.execute("""
    WITH base AS (
        SELECT tournament_id,
               lower(regexp_replace(name, '[^a-z0-9]+', '-', 'g')) || '-' || year AS base_slug
        FROM tournament
    ),
    ranked AS (
        SELECT tournament_id,
               base_slug,
               ROW_NUMBER() OVER (PARTITION BY base_slug ORDER BY tournament_id) AS rn
        FROM base
    ),
    final AS (
        SELECT tournament_id,
               CASE
                   WHEN rn = 1 THEN base_slug
                   ELSE base_slug || '-' || rn
               END AS unique_slug
        FROM ranked
    )
    UPDATE tournament
    SET slug = final.unique_slug
    FROM final
    WHERE tournament.tournament_id = final.tournament_id;
    """)


def downgrade():
    op.execute("UPDATE person SET slug = NULL;")
    op.execute("UPDATE school SET slug = NULL;")
    op.execute("UPDATE tournament SET slug = NULL;")
