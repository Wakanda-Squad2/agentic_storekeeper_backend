from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.agents import get_insight

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# TODO: Add authentication and get tenant_id from token
CURRENT_TENANT_ID = 1


class ChatMessage(BaseModel):
    role: str # user or assistant or system
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    tenant_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    data: dict


@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Chat with AI assistant about financial data using natural language."""
    # TODO: Get tenant_id from authenticated user
    tenant_id = int(request.tenant_id) if request.tenant_id else CURRENT_TENANT_ID

    # Use InsightAgent to process the question
    insight_response = await get_insight(
        question=request.message,
        db=db,
        tenant_id=tenant_id
    )

    return ChatResponse(
        answer=insight_response.answer,
        data=insight_response.data
    )


# Additional endpoints preserved for future use
class AskDocumentRequest(BaseModel):
    document_id: int
    question: str


@router.post("/ask-about-document")
async def ask_about_document(request: AskDocumentRequest):
    """Ask specific questions about a document using AI."""
    tenant_id = CURRENT_TENANT_ID

    return {
        "answer": f"This would analyze document {request.document_id} and answer: {request.question}",
        "confidence": 0.85,
        "relevant_text": ["Document analysis feature coming soon"]
    }


@router.post("/analyze-trends")
async def analyze_trends(timeframe: str = "month", focus: Optional[str] = None):
    """Ask AI to analyze spending trends and patterns."""
    tenant_id = CURRENT_TENANT_ID

    return {
        "analysis": f"AI analysis of {timeframe} trends with focus on {focus}",
        "insights": [
            "Spending has increased 15% this month",
            "Category 'Utilities' shows unusual pattern",
            "Recommendations: Review vendor X for better rates"
        ],
        "visualization_suggestion": "line_chart"
    }


@router.get("/conversation-history")
async def get_conversation_history(limit: int = 50):
    """Get recent chat conversation history."""
    tenant_id = CURRENT_TENANT_ID

    # Mock data
    return {
        "conversations": [
            {
                "id": 1,
                "messages": [
                    {
                        "role": "user",
                        "content": "What were my top expenses last month?",
                        "timestamp": datetime.utcnow()
                    },
                    {
                        "role": "assistant",
                        "content": "Your top expenses were: Rent (₦500,000), Groceries (₦150,000), and Utilities (₦85,000).",
                        "timestamp": datetime.utcnow()
                    }
                ]
            }
        ]
    }
