#!/usr/bin/env python3
"""
Batch Receipt Processor for Scan&Track
Processes multiple receipt images in a directory
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import OCRService
from app.services.categorization_service import CategorizationService

class BatchProcessor:
    """Process multiple receipt images in batch"""
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.categorization_service = CategorizationService()
        self.results = []
    
    def process_directory(self, input_dir, output_file=None):
        """Process all images in a directory"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Directory '{input_dir}' not found")
        
        # Supported image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        # Find all image files
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"❌ No image files found in '{input_dir}'")
            return
        
        print(f"🔍 Found {len(image_files)} image files to process")
        
        # Process each image
        for i, image_file in enumerate(image_files, 1):
            print(f"\n📄 Processing {i}/{len(image_files)}: {image_file.name}")
            
            try:
                # Read image
                with open(image_file, 'rb') as f:
                    image_data = f.read()
                
                # Extract data
                receipt_data = self.ocr_service.extract_receipt_data(image_data)
                categorized_data = self.categorization_service.categorize_receipt(receipt_data)
                
                # Add metadata
                result = {
                    'filename': image_file.name,
                    'filepath': str(image_file),
                    'processed_at': datetime.now().isoformat(),
                    'merchant_name': categorized_data.get('merchant_name'),
                    'total_amount': categorized_data.get('total_amount'),
                    'purchase_date': categorized_data.get('purchase_date'),
                    'raw_text': categorized_data.get('raw_text'),
                    'items': categorized_data.get('items', []),
                    'status': 'success'
                }
                
                self.results.append(result)
                print(f"✅ Successfully processed: {image_file.name}")
                
            except Exception as e:
                error_result = {
                    'filename': image_file.name,
                    'filepath': str(image_file),
                    'processed_at': datetime.now().isoformat(),
                    'error': str(e),
                    'status': 'error'
                }
                self.results.append(error_result)
                print(f"❌ Error processing {image_file.name}: {str(e)}")
        
        # Save results
        if output_file:
            self.save_results(output_file)
        
        # Print summary
        self.print_summary()
    
    def save_results(self, output_file):
        """Save results to JSON file"""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")
    
    def print_summary(self):
        """Print processing summary"""
        successful = len([r for r in self.results if r['status'] == 'success'])
        failed = len([r for r in self.results if r['status'] == 'error'])
        total_amount = sum(r.get('total_amount', 0) for r in self.results if r['status'] == 'success')
        
        print(f"\n📊 BATCH PROCESSING SUMMARY")
        print("=" * 40)
        print(f"Total files processed: {len(self.results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total amount extracted: ${total_amount:.2f}")
        
        if successful > 0:
            # Category breakdown
            categories = {}
            for result in self.results:
                if result['status'] == 'success':
                    for item in result.get('items', []):
                        category = item.get('category', 'Uncategorized')
                        categories[category] = categories.get(category, 0) + 1
            
            print(f"\n📈 Category Breakdown:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count} items")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Batch Receipt Processor')
    parser.add_argument('input_dir', help='Directory containing receipt images')
    parser.add_argument('--output', '-o', help='Output JSON file for results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        processor = BatchProcessor()
        processor.process_directory(args.input_dir, args.output)
        return 0
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
