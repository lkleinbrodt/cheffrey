"""update strs

Revision ID: a21a7a25d38c
Revises: 6f0270830bba
Create Date: 2024-02-01 09:36:43.500299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a21a7a25d38c'
down_revision = '6f0270830bba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=64),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.alter_column('canonical_url',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=256),
               existing_nullable=True)
        batch_op.alter_column('category',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=256),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('category',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
        batch_op.alter_column('canonical_url',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
        batch_op.alter_column('title',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=64),
               existing_nullable=True)

    # ### end Alembic commands ###
