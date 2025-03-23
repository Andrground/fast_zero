"""exercicio 02 aula 04

Revision ID: 6ae889faa592
Revises: 930cd03c4cdc
Create Date: 2025-03-23 13:02:45.644440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ae889faa592'
down_revision: Union[str, None] = '930cd03c4cdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   with op.batch_alter_table('users', schema=None) as batch_op:  

        batch_op.add_column(   
            sa.Column(
                'updated_at',
                sa.DateTime(),
                server_default=sa.text('(CURRENT_TIMESTAMP)'),
                nullable=False,
            )
        )


def downgrade() -> None:
     with op.batch_alter_table('users', schema=None) as batch_op:  
        batch_op.drop_column('updated_at')  
