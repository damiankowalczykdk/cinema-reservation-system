"""add group_id to reservations

Revision ID: 9e9e2bec64c9
Revises: 41b972b3c77e
Create Date: 2026-09-23 17:21:21.986282

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.ddl import CreateSequence, DropSequence

# revision identifiers, used by Alembic.
revision: str = '9e9e2bec64c9'
down_revision: Union[str, Sequence[str], None] = '41b972b3c77e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(CreateSequence(sa.Sequence("reservation_group_id_seq")))
    op.add_column('reservations', sa.Column('group_id', sa.Integer(), nullable=True))
    op.execute("UPDATE reservations SET group_id = nextval('reservation_group_id_seq')")
    op.alter_column('reservations', 'group_id', nullable=False)
    op.create_index(op.f('ix_reservations_group_id'), 'reservations', ['group_id'], unique=False)

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_reservations_group_id'), table_name='reservations')
    op.drop_column('reservations', 'group_id')
    op.execute(DropSequence(sa.Sequence("reservation_group_id_seq")))
