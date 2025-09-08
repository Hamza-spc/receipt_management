#!/usr/bin/env python3
"""
Data Export Utility for Scan&Track
Export receipt data to various formats (CSV, JSON, Excel)
"""

import csv
import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Excel export will be disabled.")

from app.database import SessionLocal
from app.models.receipt import Receipt, ReceiptItem

class DataExporter:
    """Export receipt data to various formats"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session or SessionLocal()
    
    def export_to_csv(self, output_file: str, start_date=None, end_date=None):
        """Export receipts to CSV format"""
        receipts = self._get_receipts(start_date, end_date)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'receipt_id', 'filename', 'merchant_name', 'total_amount',
                'purchase_date', 'created_at', 'item_name', 'item_quantity',
                'item_unit_price', 'item_total_price', 'item_category'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for receipt in receipts:
                if receipt.items:
                    for item in receipt.items:
                        writer.writerow({
                            'receipt_id': receipt.id,
                            'filename': receipt.filename,
                            'merchant_name': receipt.merchant_name or '',
                            'total_amount': receipt.total_amount or 0,
                            'purchase_date': receipt.purchase_date.isoformat() if receipt.purchase_date else '',
                            'created_at': receipt.created_at.isoformat(),
                            'item_name': item.item_name,
                            'item_quantity': item.quantity,
                            'item_unit_price': item.unit_price,
                            'item_total_price': item.total_price,
                            'item_category': item.category or ''
                        })
                else:
                    # Receipt without items
                    writer.writerow({
                        'receipt_id': receipt.id,
                        'filename': receipt.filename,
                        'merchant_name': receipt.merchant_name or '',
                        'total_amount': receipt.total_amount or 0,
                        'purchase_date': receipt.purchase_date.isoformat() if receipt.purchase_date else '',
                        'created_at': receipt.created_at.isoformat(),
                        'item_name': '',
                        'item_quantity': '',
                        'item_unit_price': '',
                        'item_total_price': '',
                        'item_category': ''
                    })
        
        print(f"✅ Data exported to CSV: {output_file}")
    
    def export_to_json(self, output_file: str, start_date=None, end_date=None):
        """Export receipts to JSON format"""
        receipts = self._get_receipts(start_date, end_date)
        
        export_data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'total_receipts': len(receipts),
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            },
            'receipts': []
        }
        
        for receipt in receipts:
            receipt_data = {
                'id': receipt.id,
                'filename': receipt.filename,
                'file_path': receipt.file_path,
                'merchant_name': receipt.merchant_name,
                'total_amount': receipt.total_amount,
                'purchase_date': receipt.purchase_date.isoformat() if receipt.purchase_date else None,
                'created_at': receipt.created_at.isoformat(),
                'updated_at': receipt.updated_at.isoformat() if receipt.updated_at else None,
                'raw_text': receipt.raw_text,
                'items': []
            }
            
            for item in receipt.items:
                item_data = {
                    'id': item.id,
                    'item_name': item.item_name,
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price,
                    'category': item.category,
                    'description': item.description
                }
                receipt_data['items'].append(item_data)
            
            export_data['receipts'].append(receipt_data)
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✅ Data exported to JSON: {output_file}")
    
    def export_to_excel(self, output_file: str, start_date=None, end_date=None):
        """Export receipts to Excel format"""
        if not PANDAS_AVAILABLE:
            print("❌ pandas not available. Cannot export to Excel.")
            return
        
        receipts = self._get_receipts(start_date, end_date)
        
        # Prepare data for Excel
        receipts_data = []
        items_data = []
        
        for receipt in receipts:
            receipt_row = {
                'Receipt ID': receipt.id,
                'Filename': receipt.filename,
                'Merchant Name': receipt.merchant_name or '',
                'Total Amount': receipt.total_amount or 0,
                'Purchase Date': receipt.purchase_date.isoformat() if receipt.purchase_date else '',
                'Created At': receipt.created_at.isoformat(),
                'Raw Text': receipt.raw_text or ''
            }
            receipts_data.append(receipt_row)
            
            for item in receipt.items:
                item_row = {
                    'Receipt ID': receipt.id,
                    'Item Name': item.item_name,
                    'Quantity': item.quantity,
                    'Unit Price': item.unit_price,
                    'Total Price': item.total_price,
                    'Category': item.category or '',
                    'Description': item.description or ''
                }
                items_data.append(item_row)
        
        # Create Excel file with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Receipts sheet
            receipts_df = pd.DataFrame(receipts_data)
            receipts_df.to_excel(writer, sheet_name='Receipts', index=False)
            
            # Items sheet
            items_df = pd.DataFrame(items_data)
            items_df.to_excel(writer, sheet_name='Items', index=False)
            
            # Summary sheet
            summary_data = self._generate_summary_data(receipts)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"✅ Data exported to Excel: {output_file}")
    
    def _get_receipts(self, start_date=None, end_date=None):
        """Get receipts from database with optional date filtering"""
        query = self.db_session.query(Receipt)
        
        if start_date:
            query = query.filter(Receipt.created_at >= start_date)
        if end_date:
            query = query.filter(Receipt.created_at <= end_date)
        
        return query.order_by(Receipt.created_at.desc()).all()
    
    def _generate_summary_data(self, receipts: List[Receipt]) -> List[Dict[str, Any]]:
        """Generate summary statistics"""
        total_receipts = len(receipts)
        total_amount = sum(r.total_amount or 0 for r in receipts)
        
        # Category breakdown
        categories = {}
        for receipt in receipts:
            for item in receipt.items:
                category = item.category or 'Uncategorized'
                if category not in categories:
                    categories[category] = {'count': 0, 'total': 0}
                categories[category]['count'] += 1
                categories[category]['total'] += item.total_price
        
        summary_data = [
            {'Metric': 'Total Receipts', 'Value': total_receipts},
            {'Metric': 'Total Amount', 'Value': f"${total_amount:.2f}"},
            {'Metric': 'Average Receipt', 'Value': f"${total_amount/total_receipts:.2f}" if total_receipts > 0 else "$0.00"},
            {'Metric': '', 'Value': ''},  # Empty row
            {'Metric': 'Category Breakdown', 'Value': ''},
        ]
        
        for category, data in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
            summary_data.append({
                'Metric': category,
                'Value': f"${data['total']:.2f} ({data['count']} items)"
            })
        
        return summary_data
    
    def close(self):
        """Close database session"""
        if self.db_session:
            self.db_session.close()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Export receipt data')
    parser.add_argument('format', choices=['csv', 'json', 'excel'], help='Export format')
    parser.add_argument('output', help='Output file path')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    # Export data
    exporter = DataExporter()
    
    try:
        if args.format == 'csv':
            exporter.export_to_csv(args.output, start_date, end_date)
        elif args.format == 'json':
            exporter.export_to_json(args.output, start_date, end_date)
        elif args.format == 'excel':
            exporter.export_to_excel(args.output, start_date, end_date)
    finally:
        exporter.close()

if __name__ == '__main__':
    main()
