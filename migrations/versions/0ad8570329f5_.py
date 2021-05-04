"""empty message

Revision ID: 0ad8570329f5
Revises: 1d6431bfb896
Create Date: 2021-04-13 15:11:30.032623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ad8570329f5'
down_revision = '1d6431bfb896'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'movies', 'categories', ['category_id'], ['id'])
    op.add_column('questions', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'questions', 'categories', ['category_id'], ['id'])
    op.drop_column('questions', 'category')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions', sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'questions', type_='foreignkey')
    op.drop_column('questions', 'category_id')
    op.drop_constraint(None, 'movies', type_='foreignkey')
    op.drop_column('movies', 'category_id')
    # ### end Alembic commands ###
