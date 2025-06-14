"""empty message

Revision ID: f20cce325fca
Revises: 4f9e17df04bf
Create Date: 2025-06-02 08:59:04.137160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f20cce325fca'
down_revision = '4f9e17df04bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_index('ix_notification_message')
        batch_op.create_index(batch_op.f('ix_notification_message'), ['message'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notification_message'))
        batch_op.create_index('ix_notification_message', ['message'], unique=True)

    # ### end Alembic commands ###
