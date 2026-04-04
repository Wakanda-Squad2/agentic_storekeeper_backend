from typing import List, Optional
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionSummary
)

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

# TODO: Add authentication and get tenant_id from token
CURRENT_TENANT_ID = 1


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a new transaction."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = CURRENT_TENANT_ID

    db_transaction = Transaction(
        tenant_id=tenant_id,
        **transaction.model_dump(exclude={'tenant_id'})
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    transaction_type: Optional[str] = Query(None, regex="^(income|expense)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    vendor: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all transactions for the tenant with optional filters."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = CURRENT_TENANT_ID

    query = db.query(Transaction).filter(Transaction.tenant_id == tenant_id)

    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    if category:
        query = query.filter(Transaction.category == category)

    if vendor:
        query = query.filter(Transaction.vendor == vendor)

    transactions = query.offset((page - 1) * size).limit(size).all()

    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific transaction."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = CURRENT_TENANT_ID

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.tenant_id == tenant_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update a transaction."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = CURRENT_TENANT_ID

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.tenant_id == tenant_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Update fields
    update_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Delete a transaction."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = CURRENT_TENANT_ID

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.tenant_id == tenant_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted successfully"}


@router.get("/summary/dashboard", response_model=TransactionSummary)
async def get_transaction_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get transaction summary for dashboard."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = CURRENT_TENANT_ID

    query = db.query(Transaction).filter(Transaction.tenant_id == tenant_id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    # Calculate summary
    income_result = query.filter(Transaction.type == "income").with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()

    expense_result = query.filter(Transaction.type == "expense").with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()

    total_income = Decimal(str(income_result or 0))
    total_expense = Decimal(str(expense_result or 0))
    net_flow = total_income - total_expense
    count = query.count()

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_flow": net_flow,
        "count": count,
    }