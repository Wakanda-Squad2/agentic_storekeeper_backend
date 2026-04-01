"""Validation Agent for verifying extracted transaction data."""

import json
from typing import Dict, Any, Optional
from pydantic import BaseModel
from decimal import Decimal
from app.config import client, settings


class ValidationResult(BaseModel):
    valid: bool
    errors: list
    warnings: list
    calculated_total: float
    stated_total: Optional[float]
    discrepancies: list


def validate_transactions(parsed_data: Dict[str, Any], original_ocr_text: str) -> Dict[str, Any]:
    """
    Validate parsed transaction data against original OCR text and business rules.

    Args:
        parsed_data: Data from parsing agent containing transactions
        original_ocr_text: Original OCR text for cross-reference

    Returns:
        Dict with validation results
    """
    system_prompt = """You are a validation expert for financial data. Verify the parsed transaction data against the original OCR text.

Check for:
1. Mathematical accuracy (individual amounts sum to total)
2. Amount consistency between line items and totals
3. Missing required fields (date, description, amount)
4. Suspicious amounts (negative values, unrealistic large amounts)
5. Currency consistency
6. Vendor name consistency
7. Date format validity

Respond with a JSON object:
{
  "valid": true|false,
  "errors": ["list of critical errors"],
  "warnings": ["list of warnings"],
  "calculated_total": 0.0,
  "stated_total": 0.0,
  "discrepancies": ["list of specific discrepancies found"]
}

Validation Rules:
- If calculated total doesn't match stated total: ERROR
- If individual line items don't sum to total: ERROR
- If required fields missing: ERROR
- If amounts > 10 million NGN: WARNING (verify)
- If negative amounts: WARNING
- If confidence < 0.6: WARNING
"""

    try:
        content = json.dumps(parsed_data, indent=2)

        response = client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Parsed Data:\n{content}\n\nOriginal OCR:\n{original_ocr_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        result = json.loads(response.choices[0].message.content)
        validated = ValidationResult(**result)

        return {
            "success": True,
            "valid": validated.valid,
            "errors": validated.errors,
            "warnings": validated.warnings,
            "calculated_total": float(validated.calculated_total),
            "stated_total": float(validated.stated_total) if validated.stated_total else None,
            "discrepancies": validated.discrepancies
        }

    except Exception as e:
        return {
            "success": False,
            "valid": False,
            "errors": [f"Validation failed: {str(e)}"],
            "warnings": [],
            "calculated_total": 0.0,
            "stated_total": None,
            "discrepancies": []
        }
