"""organisation table and relationship user

Revision ID: af3b3a98d193
Revises: b113af53175f
Create Date: 2020-05-07 14:31:55.625511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af3b3a98d193'
down_revision = 'b113af53175f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organisation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organisation_name'), 'organisation', ['name'], unique=True)
    op.create_table('organisation_user',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('organisation_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['organisation_id'], ['organisation.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'organisation_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('organisation_user')
    op.drop_index(op.f('ix_organisation_name'), table_name='organisation')
    op.drop_table('organisation')
    # ### end Alembic commands ###