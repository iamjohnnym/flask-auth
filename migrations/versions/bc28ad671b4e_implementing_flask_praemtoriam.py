"""implementing flask-praemtoriam

Revision ID: bc28ad671b4e
Revises: c4c636ce8c1e
Create Date: 2019-07-19 08:49:54.488051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc28ad671b4e'
down_revision = 'c4c636ce8c1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true'))
    op.add_column('users', sa.Column('roles', sa.String(), nullable=True))
    #op.drop_column('users', 'active')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('users', 'roles')
    op.drop_column('users', 'is_active')
    # ### end Alembic commands ###