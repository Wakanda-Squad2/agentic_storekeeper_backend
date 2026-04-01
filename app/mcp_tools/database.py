from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, date
from decimal import Decimal
import json
from app.models.transaction import Transaction
from app.models.document import Document


class DatabaseQueryTool:
    """Database query tool with predefined query types (no raw SQL)."""

    name = "database_query_tool"
    description = "Execute predefined database queries for financial data analysis"

    input_schema = {
        "type": "object",
        "properties": {
            "query_type": {
                "type": "string",
                "enum": [
                    "list_transactions",
                    "sum_by_category",
                    "monthly_totals",
                    "vendor_breakdown",
                    "pending_invoices"
                ],
                "description": "Type of query to execute"
            },
            "filters": {
                "type": "object",
                "description": "Filters for the query",
                "properties": {
                    "tenant_id": {"type": "integer"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "category": {"type": "string"},
                    "vendor": {"type": "string"},
                    "transaction_type": {"type": "string", "enum": ["income", "expense"]},
                    "min_amount": {"type": "number"},
                    "max_amount": {"type": "number"},
                    "document_id": {"type": "integer"}
                }
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 100
            },
            "offset": {
                "type": "integer",
                "description": "Number of results to skip",
                "default": 0
            }
        },
        "required": ["query_type", "filters"]
    }

    @staticmethod
    def run(input_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Execute a predefined database query.

        Args:
            input_data: Dictionary with query_type, filters, and optional limit/offset
            db: SQLAlchemy database session

        Returns:
            Dictionary with query results
        """
        query_type = input_data.get("query_type")
        filters = input_data.get("filters", {})
        limit = input_data.get("limit", 100)
        offset = input_data.get("offset", 0)

        if not query_type or not filters:
            raise ValueError("query_type and filters are required")

        tenant_id = filters.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required in filters")

        try:
            if query_type == "list_transactions":
                return DatabaseQueryTool._list_transactions(db, filters, limit, offset)
            elif query_type == "sum_by_category":
                return DatabaseQueryTool._sum_by_category(db, filters)
            elif query_type == "monthly_totals":
                return DatabaseQueryTool._monthly_totals(db, filters)
            elif query_type == "vendor_breakdown":
                return DatabaseQueryTool._vendor_breakdown(db, filters, limit)
            elif query_type == "pending_invoices":
                return DatabaseQueryTool._pending_invoices(db, filters, limit, offset)
            else:
                raise ValueError(f"Invalid query type: {query_type}")

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def _build_base_query(db: Session, filters: Dict[str, Any]):
        """Build the base query with common filters."""
        query = db.query(Transaction).filter(Transaction.tenant_id == filters["tenant_id"])

        if filters.get("start_date"):
            query = query.filter(Transaction.date >= filters["start_date"])

        if filters.get("end_date"):
            query = query.filter(Transaction.date <= filters["end_date"])

        if filters.get("category"):
            query = query.filter(Transaction.category == filters["category"])

        if filters.get("vendor"):
            query = query.filter(Transaction.vendor == filters["vendor"])

        if filters.get("transaction_type"):
            query = query.filter(Transaction.type == filters["transaction_type"])

        if filters.get("min_amount"):
            query = query.filter(Transaction.amount >= filters["min_amount"])

        if filters.get("max_amount"):
            query = query.filter(Transaction.amount <= filters["max_amount"])

        if filters.get("document_id"):
            query = query.filter(Transaction.document_id == filters["document_id"])

        return query

    @staticmethod
    def _list_transactions(db: Session, filters: Dict[str, Any], limit: int, offset: int) -> Dict[str, Any]:
        """List transactions with filters."""
        query = DatabaseQueryTool._build_base_query(db, filters)
        total = query.count()
        transactions = query.offset(offset).limit(limit).all()

        return {
            "success": True,
            "data": [
                {
                    "id": t.id,
                    "tenant_id": t.tenant_id,
                    "document_id": t.document_id,
                    "date": t.date.isoformat(),
                    "description": t.description,
                    "amount": float(t.amount),
                    "currency": t.currency,
                    "type": t.type,
                    "category": t.category,
                    "vendor": t.vendor,
                    "reference": t.reference,
                    "confidence": t.confidence,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in transactions
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    @staticmethod
    def _sum_by_category(db: Session, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Sum amounts grouped by category."""
        query = DatabaseQueryTool._build_base_query(db, filters)

        results = query.with_entities(
            Transaction.category,
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        ).filter(
            Transaction.category.isnot(None)
        ).group_by(
            Transaction.category,
            Transaction.type
        ).all()

        return {
            "success": True,
            "data": [
                {
                    "category": result.category,
                    "type": result.type,
                    "total": float(result.total or 0),
                    "count": result.count
                }
                for result in results
            ]
        }

    @staticmethod
    def _monthly_totals(db: Session, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get monthly totals for income and expenses."""
        query = DatabaseQueryTool._build_base_query(db, filters)

        results = query.with_entities(
            extract('year', Transaction.date).label('year'),
            extract('month', Transaction.date).label('month'),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count")
        ).group_by(
            extract('year', Transaction.date),
            extract('month', Transaction.date),
            Transaction.type
        ).order_by('year', 'month').all()

        return {
            "success": True,
            "data": [
                {
                    "year": int(result.year),
                    "month": int(result.month),
                    "type": result.type,
                    "total": float(result.total or 0),
                    "count": result.count
                }
                for result in results
            ]
        }

    @staticmethod
    def _vendor_breakdown(db: Session, filters: Dict[str, Any], limit: int) -> Dict[str, Any]:
        """Get breakdown by vendor."""
        query = DatabaseQueryTool._build_base_query(db, filters)

        results = query.with_entities(
            Transaction.vendor,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
            Transaction.type
        ).filter(
            Transaction.vendor.isnot(None)
        ).group_by(
            Transaction.vendor,
            Transaction.type
        ).order_by(
            func.sum(Transaction.amount).desc()
        ).limit(limit).all()

        return {
            "success": True,
            "data": [
                {
                    "vendor": result.vendor,
                    "type": result.type,
                    "total": float(result.total or 0),
                    "count": result.count
                }
                for result in results
            ]
        }

    @staticmethod
    def _pending_invoices(db: Session, filters: Dict[str, Any], limit: int, offset: int) -> Dict[str, Any]:
        """Get pending invoices (transactions with reference)."""
        query = DatabaseQueryTool._build_base_query(db, filters)

        # Filter for transactions with reference numbers (potential invoices)
        query = query.filter(
            Transaction.reference.isnot(None),
            Transaction.reference != ""
        )

        total = query.count()
        transactions = query.order_by(Transaction.date.desc()).offset(offset).limit(limit).all()

        return {
            "success": True,
            "data": [
                {
                    "id": t.id,
                    "date": t.date.isoformat(),
                    "description": t.description,
                    "amount": float(t.amount),
                    "currency": t.currency,
                    "reference": t.reference,
                    "vendor": t.vendor,
                    "type": t.type
                }
                for t in transactions
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
