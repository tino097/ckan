"""Add new column last_active in User model

Revision ID: d65b0ae235c0
Revises: ccd38ad5fced
Create Date: 2021-08-17 22:16:39.626233

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd65b0ae235c0'
down_revision = 'ccd38ad5fced'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('last_active', sa.TIMESTAMP))


def downgrade():
    op.drop_column('user', 'last_active')

