"""Classification Agent for document type classification."""

import json
from typing import Dict, Any
from pydantic import BaseModel
from app.config import client, settings


class ClassificationResult(BaseModel):
    document_type: str
    confidence: float


def classify_document(ocr_text: str) -> Dict[str, Any]:
    """
    Classify document type from OCR text.

    Args:
        ocr_text: Extracted text from OCR

    Returns:
        Dict with document_type and confidence score
    """
    system_prompt = """You are a document classification expert. Analyze the provided OCR text and classify it into one of these categories:

1. receipt - Proof of purchase, cash register receipts, payment confirmations
2. invoice - Business invoices, bills requesting payment, company invoices
3. bank_statement - Bank account statements, transaction summaries
4. credit_card_statement - Credit card bills and statements

Respond with a JSON object containing:
{
  "document_type": "receipt|invoice|bank_statement|credit_card_statement",
  "confidence": 0.0-1.0
}

Consider keywords, document structure, and patterns when classifying.
"""

    try:
        response = client.chat.completions.create(
            model=settings.ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ocr_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )

        result = json.loads(response.choices[0].message.content)
        validated = ClassificationResult(**result)

        return {
            "success": True,
            "document_type": validated.document_type,
            "confidence": validated.confidence
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Classification failed: {str(e)}"
        }
