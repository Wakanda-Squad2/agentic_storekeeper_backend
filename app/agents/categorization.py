"""Categorization Agent for assigning expense categories."""

import json
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.config import client, settings


class CategoryResult(BaseModel):
    category: str
    confidence: float
    subcategory: Optional[str]
    reasoning: str


CATEGORY_TAXONOMY = """
Expense Categories:
- rent: Office rent, property rental, lease payments
- fuel: Gasoline, diesel, vehicle fuel, transportation fuel
- office_supplies: Stationery, paper, pens, printer supplies, office materials
- payroll: Employee salaries, wages, benefits, contractor payments
- utilities: Electricity, water, gas, internet, phone bills
- travel: Business travel, hotels, flights, transportation
- meals: Business meals, entertainment, client entertainment
- subscriptions: SaaS subscriptions, software licenses, memberships
- maintenance: Equipment maintenance, repairs, servicing
- marketing: Advertising, promotions, marketing campaigns
- professional_services: Legal, accounting, consulting, professional fees
- insurance: Business insurance premiums, coverage payments
- equipment: Purchase of equipment, machinery, hardware
- shipping: Courier services, postage, delivery services
- training: Employee training, courses, certifications
"""


def categorize_transaction(transaction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Categorize a transaction based on description, vendor, and amount.

    Args:
        transaction: Transaction dictionary with description, vendor, amount, etc.

    Returns:
        Dict with category, confidence, and reasoning
    """
    system_prompt = f"""You are a financial categorization expert. Assign the most appropriate category to the transaction.

{CATEGORY_TAXONOMY}

Respond with a JSON object:
{{
  "category": "category_name",
  "subcategory": "optional_more_specific_category",
  "confidence": 0.0-1.0,
  "reasoning": "explanation for this categorization"
}}

Consider:
- Description keywords
- Vendor name/business type
- Amount patterns
- Date (regular vs one-time)
- Industry context

Return confidence based on certainty of categorization.
"""

    try:
        transaction_text = json.dumps(transaction, indent=2)

        response = client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transaction_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        result = json.loads(response.choices[0].message.content)
        validated = CategoryResult(**result)

        return {
            "success": True,
            "category": validated.category,
            "subcategory": validated.subcategory,
            "confidence": validated.confidence,
            "reasoning": validated.reasoning
        }

    except Exception as e:
        return {
            "success": False,
            "category": "uncategorized",
            "subcategory": None,
            "confidence": 0.0,
            "reasoning": f"Categorization failed: {str(e)}"
        }
