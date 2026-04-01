"""Initial migration - add all models

Revision ID: 001
Revises:
Create Date: 2026-04-01 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False, index=True),
        sa.Column('name', sa.String(length=200), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False, index=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False, index=True),
        sa.Column('document_id', sa.Integer(), nullable=True, index=True),
        sa.Column('date', sa.Date(), nullable=False, index=True),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='NGN'),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True, index=True),
        sa.Column('vendor', sa.String(length=200), nullable=True, index=True),
        sa.Column('reference', sa.String(length=200), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_transactions_category', 'transactions', ['category'])
    op.create_index('ix_transactions_date', 'transactions', ['date'])
    op.create_index('ix_documents_status', 'documents', ['status'])
    op.create_index('ix_documents_tenant_id', 'documents', ['tenant_id'])
    op.create_index('ix_documents_updated_at', 'documents', ['updated_at'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_documents_updated_at', table_name='documents')
    op.drop_index('ix_documents_tenant_id', table_name='documents')
    op.drop_index('ix_documents_status', table_name='documents')
    op.drop_index('ix_transactions_date', table_name='transactions')
    op.drop_index('ix_transactions_category', table_name='transactions')

    # Drop tables in reverse order
    op.drop_table('transactions')
    op.drop_table('documents')
    op.drop_table('vendors')
    op.drop_table('categories')
