#!/usr/bin/env python3
"""
OCR Example Script for Scan&Track
Demonstrates how to use the OCR service independently
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import OCRService
from app.services.categorization_service import CategorizationService
import argparse

def main():
    """Main function to demonstrate OCR capabilities"""
    parser = argparse.ArgumentParser(description='OCR Receipt Processing Example')
    parser.add_argument('image_path', help='Path to the receipt image file')
    parser.add_argument('--output', '-o', help='Output file for results (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image_path):
        print(f"Error: Image file '{args.image_path}' not found")
        return 1
    
    try:
        # Initialize services
        ocr_service = OCRService()
        categorization_service = CategorizationService()
        
        print("🔍 Processing receipt with OCR...")
        
        # Read image file
        with open(args.image_path, 'rb') as f:
            image_data = f.read()
        
        # Extract text and data
        receipt_data = ocr_service.extract_receipt_data(image_data)
        
        # Categorize items
        categorized_data = categorization_service.categorize_receipt(receipt_data)
        
        # Display results
        print("\n📄 EXTRACTED DATA:")
        print("=" * 50)
        print(f"Merchant: {categorized_data.get('merchant_name', 'N/A')}")
        print(f"Total Amount: ${categorized_data.get('total_amount', 0):.2f}")
        print(f"Purchase Date: {categorized_data.get('purchase_date', 'N/A')}")
        
        print(f"\n📝 EXTRACTED TEXT:")
        print("-" * 30)
        print(categorized_data.get('raw_text', 'No text extracted'))
        
        print(f"\n🛒 ITEMS FOUND ({len(categorized_data.get('items', []))}):")
        print("-" * 30)
        for i, item in enumerate(categorized_data.get('items', []), 1):
            print(f"{i}. {item['item_name']}")
            print(f"   Price: ${item['total_price']:.2f}")
            print(f"   Category: {item.get('category', 'Uncategorized')}")
            print()
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(f"Receipt Analysis Results\n")
                f.write(f"=======================\n\n")
                f.write(f"Merchant: {categorized_data.get('merchant_name', 'N/A')}\n")
                f.write(f"Total: ${categorized_data.get('total_amount', 0):.2f}\n")
                f.write(f"Date: {categorized_data.get('purchase_date', 'N/A')}\n\n")
                f.write("Items:\n")
                for i, item in enumerate(categorized_data.get('items', []), 1):
                    f.write(f"{i}. {item['item_name']} - ${item['total_price']:.2f} ({item.get('category', 'Uncategorized')})\n")
            print(f"💾 Results saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error processing image: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
