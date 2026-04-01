from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.transaction import Transaction

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

# TODO: Add authentication and get tenant_id from token
CURRENT_TENANT_ID = 1


@router.get("/summary")
async def get_dashboard_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard summary."""
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

    count = query.count()

    # Category breakdown
    category_breakdown = query.with_entities(
        Transaction.category,
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).group_by(Transaction.category, Transaction.type).all()

    # Vendor breakdown
    vendor_breakdown = query.with_entities(
        Transaction.vendor,
        func.sum(Transaction.amount).label("total")
    ).filter(Transaction.vendor.isnot(None)).group_by(Transaction.vendor).limit(10).all()

    return {
        "summary": {
            "total_income": income_result or 0,
            "total_expense": expense_result or 0,
            "net_flow": (income_result or 0) - (expense_result or 0),
            "total_transactions": count,
        },
        "category_breakdown": [
            {
                "category": item.category,
                "type": item.type,
                "total": item.total
            } for item in category_breakdown
        ],
        "top_vendors": [
            {
                "vendor": item.vendor,
                "total": item.total
            } for item in vendor_breakdown
        ],
    }


@router.get("/category-breakdown")
async def get_category_breakdown(
    transaction_type: Optional[str] = Query(None, regex="^(income|expense)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get category breakdown for pie chart."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = CURRENT_TENANT_ID

    query = db.query(Transaction).filter(Transaction.tenant_id == tenant_id)

    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    results = query.with_entities(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(Transaction.category.isnot(None)).group_by(Transaction.category).all()

    return [
        {
            "category": item.category,
            "total": item.total
        } for item in results
    ]


@router.get("/trend-data")
async def get_trend_data(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get trend data for line chart."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = CURRENT_TENANT_ID

    query = db.query(Transaction).filter(Transaction.tenant_id == tenant_id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    # Group by date
    income_trend = query.filter(Transaction.type == "income").with_entities(
        Transaction.date,
        func.sum(Transaction.amount).label("total")
    ).group_by(Transaction.date).order_by(Transaction.date).all()

    expense_trend = query.filter(Transaction.type == "expense").with_entities(
        Transaction.date,
        func.sum(Transaction.amount).label("total")
    ).group_by(Transaction.date).order_by(Transaction.date).all()

    return {
        "income": [
            {
                "date": item.date.isoformat(),
                "total": item.total
            } for item in income_trend
        ],
        "expenses": [
            {
                "date": item.date.isoformat(),
                "total": item.total
            } for item in expense_trend
        ],
    }