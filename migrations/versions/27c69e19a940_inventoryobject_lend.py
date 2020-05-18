"""inventoryobject lend

Revision ID: 27c69e19a940
Revises: eb83a82b3601
Create Date: 2020-05-18 08:04:57.642972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27c69e19a940'
down_revision = 'eb83a82b3601'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inventory_object', sa.Column('description', sa.String(length=128), nullable=True))
    op.add_column('inventory_object', sa.Column('lend_to', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_inventory_object_description'), 'inventory_object', ['description'], unique=False)
    op.create_foreign_key(None, 'inventory_object', 'user', ['lend_to'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'inventory_object', type_='foreignkey')
    op.drop_index(op.f('ix_inventory_object_description'), table_name='inventory_object')
    op.drop_column('inventory_object', 'lend_to')
    op.drop_column('inventory_object', 'description')
    # ### end Alembic commands ###