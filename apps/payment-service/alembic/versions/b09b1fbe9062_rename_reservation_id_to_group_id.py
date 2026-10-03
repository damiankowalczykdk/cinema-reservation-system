"""rename reservation_id to group_id

Revision ID: b09b1fbe9062
Revises: 77668c6ac945
Create Date: 2026-09-27 18:41:17.545587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b09b1fbe9062'
down_revision: Union[str, Sequence[str], None] = '77668c6ac945'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('uq_payment_reservation_active', table_name='payments')
    op.alter_column('payments', 'reservation_id', new_column_name='group_id')
    op.create_index(
        'uq_payment_group_active', 'payments', ['group_id'],
        unique=True, postgresql_where=sa.text("status != 'FAILED'"),
    )


def downgrade() -> None:
    op.drop_index('uq_payment_group_active', table_name='payments')
    op.alter_column('payments', 'group_id', new_column_name='reservation_id')
    op.create_index(
        'uq_payment_reservation_active', 'payments', ['reservation_id'],
        unique=True, postgresql_where=sa.text("status != 'FAILED'"),
    )
