from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    filename: str
    file_path: str
    file_type: str
    document_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    tenant_id: int


class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    document_type: Optional[str] = None
    status: Optional[str] = None


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class DocumentList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int
