from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Dict
from datetime import datetime, timedelta

from ..database import get_db
from ..models.receipt import Receipt, ReceiptItem
from ..schemas.receipt import ReceiptResponse, AnalyticsResponse

router = APIRouter()

@router.get("/expenses", response_model=AnalyticsResponse)
async def get_expense_analytics(
    months: int = 12,
    db: Session = Depends(get_db)
):
    """Get expense analytics for the specified number of months"""
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    # Get total expenses
    total_expenses = db.query(func.sum(Receipt.total_amount)).filter(
        Receipt.total_amount.isnot(None),
        Receipt.created_at >= start_date
    ).scalar() or 0
    
    # Get monthly expenses
    monthly_data = db.query(
        extract('year', Receipt.created_at).label('year'),
        extract('month', Receipt.created_at).label('month'),
        func.sum(Receipt.total_amount).label('total')
    ).filter(
        Receipt.total_amount.isnot(None),
        Receipt.created_at >= start_date
    ).group_by(
        extract('year', Receipt.created_at),
        extract('month', Receipt.created_at)
    ).order_by('year', 'month').all()
    
    monthly_expenses = []
    for data in monthly_data:
        monthly_expenses.append({
            "year": int(data.year),
            "month": int(data.month),
            "total": float(data.total or 0)
        })
    
    # Get category breakdown
    category_data = db.query(
        ReceiptItem.category,
        func.sum(ReceiptItem.total_price).label('total')
    ).join(Receipt).filter(
        Receipt.created_at >= start_date,
        ReceiptItem.category.isnot(None)
    ).group_by(ReceiptItem.category).all()
    
    category_breakdown = []
    for data in category_data:
        category_breakdown.append({
            "category": data.category,
            "total": float(data.total or 0)
        })
    
    # Get recent receipts
    recent_receipts = db.query(Receipt).filter(
        Receipt.created_at >= start_date
    ).order_by(Receipt.created_at.desc()).limit(10).all()
    
    return AnalyticsResponse(
        total_expenses=float(total_expenses),
        monthly_expenses=monthly_expenses,
        category_breakdown=category_breakdown,
        recent_receipts=recent_receipts
    )

@router.get("/categories")
async def get_category_stats(
    months: int = 12,
    db: Session = Depends(get_db)
):
    """Get detailed category statistics"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    # Get category statistics
    category_stats = db.query(
        ReceiptItem.category,
        func.count(ReceiptItem.id).label('item_count'),
        func.sum(ReceiptItem.total_price).label('total_amount'),
        func.avg(ReceiptItem.total_price).label('avg_amount')
    ).join(Receipt).filter(
        Receipt.created_at >= start_date,
        ReceiptItem.category.isnot(None)
    ).group_by(ReceiptItem.category).all()
    
    return [
        {
            "category": stat.category,
            "item_count": stat.item_count,
            "total_amount": float(stat.total_amount or 0),
            "avg_amount": float(stat.avg_amount or 0)
        }
        for stat in category_stats
    ]

@router.get("/monthly-trends")
async def get_monthly_trends(
    months: int = 12,
    db: Session = Depends(get_db)
):
    """Get monthly spending trends"""
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    # Get monthly trends by category
    trends = db.query(
        extract('year', Receipt.created_at).label('year'),
        extract('month', Receipt.created_at).label('month'),
        ReceiptItem.category,
        func.sum(ReceiptItem.total_price).label('total')
    ).join(Receipt).filter(
        Receipt.created_at >= start_date,
        ReceiptItem.category.isnot(None)
    ).group_by(
        extract('year', Receipt.created_at),
        extract('month', Receipt.created_at),
        ReceiptItem.category
    ).order_by('year', 'month').all()
    
    # Organize data by month and category
    monthly_trends = {}
    for trend in trends:
        key = f"{int(trend.year)}-{int(trend.month):02d}"
        if key not in monthly_trends:
            monthly_trends[key] = {}
        monthly_trends[key][trend.category] = float(trend.total or 0)
    
    return monthly_trends
