"""room relationship

Revision ID: dd8727893878
Revises: b4da09fbdf7e
Create Date: 2020-05-20 08:56:21.677388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd8727893878'
down_revision = 'b4da09fbdf7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('inventory_object')
    op.create_table('room',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_name'), 'room', ['name'], unique=False)
    # ### end Alembic commands ###

    op.create_table('inventory_object',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article', sa.String(length=64), nullable=True),
    sa.Column('organisation', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('lend_to', sa.Integer(), nullable=True),
    sa.Column('room', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lend_to'], ['user.id'], ),
    sa.ForeignKeyConstraint(['organisation'], ['organisation.id'], ),
    sa.ForeignKeyConstraint(['room'], ['room.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_object_article'), 'inventory_object', ['article'], unique=False)
    op.create_index(op.f('ix_inventory_object_description'), 'inventory_object', ['description'], unique=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_room_name'), table_name='room')
    op.drop_table('room')
    op.drop_table('inventory_object')
    # ### end Alembic commands ###
    op.create_table('inventory_object',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article', sa.String(length=64), nullable=True),
    sa.Column('organisation', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('lend_to', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lend_to'], ['user.id'], ),
    sa.ForeignKeyConstraint(['organisation'], ['organisation.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_object_article'), 'inventory_object', ['article'], unique=False)
    op.create_index(op.f('ix_inventory_object_description'), 'inventory_object', ['description'], unique=False)
