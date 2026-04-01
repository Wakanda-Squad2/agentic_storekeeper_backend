"""Reconciliation Agent for matching transactions against existing records."""

import json
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from decimal import Decimal
from app.config import client, settings
from app.mcp_tools.database import DatabaseQueryTool
from sqlalchemy.orm import Session


class MatchResult(BaseModel):
    is_duplicate: bool
    confidence: float
    matched_transaction_id: Optional[int]
    matching_fields: List[str]
    reasoning: str
    action: str  # create_new, update_existing, flag_for_review


def reconcile_transaction(transaction: Dict[str, Any], potential_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Reconcile a new transaction against potential existing matches.

    Args:
        transaction: New transaction to reconcile
        potential_matches: Existing transactions from database

    Returns:
        Dict with reconciliation results
    """
    system_prompt = """You are a transaction reconciliation expert. Determin e if the new transaction is:
1. A duplicate of an existing transaction
2. A new transaction to create
3. An update to an existing transaction
4. Requires manual review

Match Criteria (in order of importance):
1. Exact date match (same day)
2. Amount match (within 1 NGN)
3. Vendor name match (exact or similar)
4. Reference number match (exact)
5. Description similarity

Response JSON:
{
  "is_duplicate": true|false,
  "confidence": 0.0-1.0,
  "matched_transaction_id": null|id,
  "matching_fields": ["list of fields that matched"],
  "reasoning": "explanation of match/no-match",
  "action": "create_new|update_existing|flag_for_review"
}

Rules:
- If 3+ criteria match with high confidence: likely duplicate
- If reference numbers match exactly: very likely duplicate
- If only amount matches but different date/vendor: likely new transaction
- If partial match on 2 criteria: flag for review
- Always err on side of caution - prefer flag_for_review over auto-match
"""

    try:
        context = {
            "new_transaction": transaction,
            "potential_matches": potential_matches
        }

        context_text = json.dumps(context, indent=2, default=str)

        response = client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        result = json.loads(response.choices[0].message.content)
        validated = MatchResult(**result)

        return {
            "success": True,
            "is_duplicate": validated.is_duplicate,
            "confidence": validated.confidence,
            "matched_transaction_id": validated.matched_transaction_id,
            "matching_fields": validated.matching_fields,
            "reasoning": validated.reasoning,
            "action": validated.action
        }

    except Exception as e:
        return {
            "success": False,
            "is_duplicate": False,
            "confidence": 0.0,
            "matched_transaction_id": None,
            "matching_fields": [],
            "reasoning": f"Reconciliation failed: {str(e)}",
            "action": "flag_for_review"
        }


def find_potential_matches(transaction: Dict[str, Any], db: Session, tenant_id: int) -> List[Dict[str, Any]]:
    """
    Find potential matches for a transaction in the database.

    Args:
        transaction: Transaction to find matches for
        db: Database session
        tenant_id: Tenant ID

    Returns:
        List of potential matching transactions (limited to top 10)
    """
    # Use DatabaseQueryTool to find recent transactions that might match
    filters = {
        "tenant_id": tenant_id,
        "transaction_type": transaction.get("type"),
    }

    # Add date range (±7 days from transaction date)
    if transaction.get("date"):
        txn_date = date.fromisoformat(transaction["date"])
        filters["start_date"] = (txn_date - datetime.timedelta(days=7)).isoformat()
        filters["end_date"] = (txn_date + datetime.timedelta(days=7)).isoformat()

    # Get recent transactions
    result = DatabaseQueryTool.run({
        "query_type": "list_transactions",
        "filters": filters,
        "limit": 50,
        "offset": 0
    }, db)

    if not result.get("success"):
        return []

    transactions = result.get("data", [])

    # Filter by vendor if provided
    if transaction.get("vendor"):
        transactions = [t for t in transactions if t.get("vendor") == transaction["vendor"]]

    # Filter by amount similarity (within ±1%)
    if transaction.get("amount"):
        amount = float(transaction["amount"])
        transactions = [
            t for t in transactions
            if abs(float(t.get("amount", 0)) - amount) / amount < 0.01
        ]

    # Sort by date and amount similarity, return top 10
    transactions.sort(key=lambda t: (
        float("inf") if not t.get("date") else abs((date.fromisoformat(t["date"]) - txn_date).days),
        abs(float(t.get("amount", 0)) - amount) if amount else 0
    ))

    return transactions[:10]
