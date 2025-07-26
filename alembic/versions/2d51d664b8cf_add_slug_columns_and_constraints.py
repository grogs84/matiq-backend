"""add slug columns and constraints

Revision ID: 2d51d664b8cf
Revises: 
Create Date: 2025-07-26 07:17:37.843960
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2d51d664b8cf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add slug columns to person, school, tournament"""
    op.add_column('person', sa.Column('slug', sa.String(), nullable=True))
    op.create_unique_constraint('person_slug_key', 'person', ['slug'])

    op.add_column('school', sa.Column('slug', sa.String(), nullable=True))
    op.create_unique_constraint('school_slug_key', 'school', ['slug'])

    op.add_column('tournament', sa.Column('slug', sa.String(), nullable=True))
    op.create_unique_constraint('tournament_slug_key', 'tournament', ['slug'])


def downgrade() -> None:
    """Downgrade schema: remove slug columns"""
    op.drop_constraint('tournament_slug_key', 'tournament', type_='unique')
    op.drop_column('tournament', 'slug')

    op.drop_constraint('school_slug_key', 'school', type_='unique')
    op.drop_column('school', 'slug')

    op.drop_constraint('person_slug_key', 'person', type_='unique')
    op.drop_column('person', 'slug')
