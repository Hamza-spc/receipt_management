from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
import uuid

from ..database import get_db
from ..models.receipt import Receipt, ReceiptItem
from ..schemas.receipt import ReceiptResponse, ReceiptCreate, ReceiptUpdate, ReceiptItemCreate
from ..services.ocr_service import OCRService
from ..services.categorization_service import CategorizationService

router = APIRouter()

# Initialize services
ocr_service = OCRService()
categorization_service = CategorizationService()

@router.post("/upload", response_model=ReceiptResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a receipt image"""
    
    # Validate file type
    allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Process with OCR
        receipt_data = ocr_service.extract_receipt_data(file_content)
        
        # Categorize items
        categorized_data = categorization_service.categorize_receipt(receipt_data)
        
        # Create receipt record
        db_receipt = Receipt(
            filename=file.filename,
            file_path=file_path,
            total_amount=categorized_data.get("total_amount"),
            merchant_name=categorized_data.get("merchant_name"),
            purchase_date=datetime.fromisoformat(categorized_data.get("purchase_date")) if categorized_data.get("purchase_date") else None,
            raw_text=categorized_data.get("raw_text")
        )
        
        db.add(db_receipt)
        db.commit()
        db.refresh(db_receipt)
        
        # Create receipt items
        for item_data in categorized_data.get("items", []):
            db_item = ReceiptItem(
                receipt_id=db_receipt.id,
                item_name=item_data["item_name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
                category=item_data["category"],
                description=item_data.get("description")
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_receipt)
        
        return db_receipt
        
    except Exception as e:
        # Clean up uploaded file if processing failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process receipt: {str(e)}")

@router.get("/", response_model=List[ReceiptResponse])
async def get_receipts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all receipts with pagination"""
    receipts = db.query(Receipt).offset(skip).limit(limit).all()
    return receipts

@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific receipt by ID"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt

@router.put("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_id: int,
    receipt_update: ReceiptUpdate,
    db: Session = Depends(get_db)
):
    """Update a receipt"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Update receipt fields
    if receipt_update.total_amount is not None:
        receipt.total_amount = receipt_update.total_amount
    if receipt_update.merchant_name is not None:
        receipt.merchant_name = receipt_update.merchant_name
    if receipt_update.purchase_date is not None:
        receipt.purchase_date = receipt_update.purchase_date
    
    # Update items if provided
    if receipt_update.items is not None:
        # Delete existing items
        db.query(ReceiptItem).filter(ReceiptItem.receipt_id == receipt_id).delete()
        
        # Add new items
        for item_data in receipt_update.items:
            db_item = ReceiptItem(
                receipt_id=receipt_id,
                item_name=item_data.item_name,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_data.total_price,
                category=item_data.category,
                description=item_data.description
            )
            db.add(db_item)
    
    db.commit()
    db.refresh(receipt)
    return receipt

@router.delete("/{receipt_id}")
async def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db)
):
    """Delete a receipt and its associated file"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Delete file from filesystem
    if os.path.exists(receipt.file_path):
        os.remove(receipt.file_path)
    
    # Delete from database (items will be deleted due to cascade)
    db.delete(receipt)
    db.commit()
    
    return {"message": "Receipt deleted successfully"}
