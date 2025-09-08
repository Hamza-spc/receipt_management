from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReceiptItemBase(BaseModel):
    item_name: str
    quantity: float = 1.0
    unit_price: float
    total_price: float
    category: Optional[str] = None
    description: Optional[str] = None

class ReceiptItemCreate(ReceiptItemBase):
    pass

class ReceiptItemResponse(ReceiptItemBase):
    id: int
    receipt_id: int
    
    class Config:
        from_attributes = True

class ReceiptBase(BaseModel):
    filename: str
    total_amount: Optional[float] = None
    merchant_name: Optional[str] = None
    purchase_date: Optional[datetime] = None
    raw_text: Optional[str] = None

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptUpdate(BaseModel):
    total_amount: Optional[float] = None
    merchant_name: Optional[str] = None
    purchase_date: Optional[datetime] = None
    items: Optional[List[ReceiptItemCreate]] = None

class ReceiptResponse(ReceiptBase):
    id: int
    file_path: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ReceiptItemResponse] = []
    
    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    total_expenses: float
    monthly_expenses: List[dict]
    category_breakdown: List[dict]
    recent_receipts: List[ReceiptResponse]
