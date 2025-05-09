"""update asset

Revision ID: 49be840bd644
Revises: 206fda5ad761
Create Date: 2025-04-24 09:42:42.213276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49be840bd644'
down_revision = '206fda5ad761'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.add_column(sa.Column('model', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assets', schema=None) as batch_op:
        batch_op.drop_column('model')

    # ### end Alembic commands ###
