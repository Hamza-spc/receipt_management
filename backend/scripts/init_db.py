#!/usr/bin/env python3
"""
Database initialization script
Creates tables and optionally seeds with sample data
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, SessionLocal
from app.models.receipt import Receipt, ReceiptItem
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

def create_tables():
    """Create all database tables"""
    from app.models.receipt import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def seed_sample_data():
    """Add sample data for testing"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Receipt).count() > 0:
            print("⚠️  Sample data already exists, skipping...")
            return

        # Sample merchants
        merchants = [
            "Starbucks Coffee",
            "Whole Foods Market",
            "Shell Gas Station",
            "CVS Pharmacy",
            "Target Store",
            "McDonald's",
            "Amazon",
            "Walmart",
            "Home Depot",
            "Best Buy"
        ]

        # Sample items by category
        sample_items = {
            "Food & Dining": [
                {"name": "Coffee", "price_range": (3.50, 6.00)},
                {"name": "Sandwich", "price_range": (8.00, 15.00)},
                {"name": "Salad", "price_range": (7.00, 12.00)},
                {"name": "Pizza Slice", "price_range": (2.50, 4.50)},
                {"name": "Burger", "price_range": (5.00, 12.00)},
            ],
            "Transportation": [
                {"name": "Gas", "price_range": (25.00, 60.00)},
                {"name": "Uber Ride", "price_range": (8.00, 25.00)},
                {"name": "Parking", "price_range": (5.00, 15.00)},
                {"name": "Toll Fee", "price_range": (2.00, 8.00)},
            ],
            "Shopping": [
                {"name": "T-Shirt", "price_range": (15.00, 30.00)},
                {"name": "Jeans", "price_range": (40.00, 80.00)},
                {"name": "Shoes", "price_range": (50.00, 120.00)},
                {"name": "Electronics", "price_range": (100.00, 500.00)},
            ],
            "Healthcare": [
                {"name": "Prescription", "price_range": (10.00, 50.00)},
                {"name": "Vitamins", "price_range": (15.00, 40.00)},
                {"name": "First Aid", "price_range": (5.00, 20.00)},
            ],
            "Entertainment": [
                {"name": "Movie Ticket", "price_range": (12.00, 18.00)},
                {"name": "Netflix Subscription", "price_range": (15.00, 20.00)},
                {"name": "Gym Membership", "price_range": (30.00, 60.00)},
            ],
            "Utilities": [
                {"name": "Electric Bill", "price_range": (80.00, 150.00)},
                {"name": "Internet", "price_range": (50.00, 80.00)},
                {"name": "Phone Bill", "price_range": (40.00, 70.00)},
            ]
        }

        # Create sample receipts
        for i in range(20):
            merchant = random.choice(merchants)
            purchase_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            # Create receipt
            receipt = Receipt(
                filename=f"receipt_{i+1}.jpg",
                file_path=f"uploads/sample_receipt_{i+1}.jpg",
                merchant_name=merchant,
                purchase_date=purchase_date,
                raw_text=f"Sample receipt text for {merchant} on {purchase_date.strftime('%Y-%m-%d')}",
                total_amount=0.0  # Will be calculated from items
            )
            
            db.add(receipt)
            db.flush()  # Get the receipt ID
            
            # Add items to receipt
            num_items = random.randint(1, 5)
            total_amount = 0.0
            
            for j in range(num_items):
                category = random.choice(list(sample_items.keys()))
                item_template = random.choice(sample_items[category])
                
                quantity = random.randint(1, 3)
                unit_price = round(random.uniform(*item_template["price_range"]), 2)
                total_price = round(unit_price * quantity, 2)
                total_amount += total_price
                
                item = ReceiptItem(
                    receipt_id=receipt.id,
                    item_name=item_template["name"],
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    category=category,
                    description=f"Sample {category.lower()} item"
                )
                
                db.add(item)
            
            # Update receipt total
            receipt.total_amount = round(total_amount, 2)
        
        db.commit()
        print("✅ Sample data created successfully")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {e}")
    finally:
        db.close()

def main():
    """Main function"""
    print("🚀 Initializing database...")
    
    # Create tables
    create_tables()
    
    # Ask if user wants sample data
    if len(sys.argv) > 1 and sys.argv[1] == "--with-sample-data":
        seed_sample_data()
    else:
        response = input("Do you want to create sample data? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            seed_sample_data()
    
    print("✅ Database initialization complete!")

if __name__ == "__main__":
    main()
