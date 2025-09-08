import pytesseract
from PIL import Image
import io
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # Configure tesseract path if needed (uncomment and adjust for your system)
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
        pass
    
    def extract_text(self, image_data: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using tesseract
            text = pytesseract.image_to_string(image, config='--psm 6')
            
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    def extract_receipt_data(self, image_data: bytes) -> Dict:
        """Extract structured data from receipt image"""
        try:
            raw_text = self.extract_text(image_data)
            
            # Extract merchant name (usually at the top)
            merchant_name = self._extract_merchant_name(raw_text)
            
            # Extract total amount
            total_amount = self._extract_total_amount(raw_text)
            
            # Extract purchase date
            purchase_date = self._extract_purchase_date(raw_text)
            
            # Extract items (simplified - in real app, this would be more sophisticated)
            items = self._extract_items(raw_text)
            
            return {
                "raw_text": raw_text,
                "merchant_name": merchant_name,
                "total_amount": total_amount,
                "purchase_date": purchase_date,
                "items": items
            }
        except Exception as e:
            logger.error(f"Receipt data extraction failed: {str(e)}")
            raise Exception(f"Failed to extract receipt data: {str(e)}")
    
    def _extract_merchant_name(self, text: str) -> Optional[str]:
        """Extract merchant name from receipt text"""
        lines = text.split('\n')
        # Usually the first non-empty line is the merchant name
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not re.match(r'^\d+$', line):  # Not just numbers
                return line
        return None
    
    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount from receipt text"""
        # Look for patterns like "Total: $123.45" or "TOTAL $123.45"
        patterns = [
            r'total[:\s]*\$?(\d+\.?\d*)',
            r'TOTAL[:\s]*\$?(\d+\.?\d*)',
            r'amount[:\s]*\$?(\d+\.?\d*)',
            r'AMOUNT[:\s]*\$?(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[-1])  # Take the last match (usually the total)
                except ValueError:
                    continue
        
        # Look for currency patterns at the end of lines
        currency_pattern = r'\$(\d+\.?\d*)'
        matches = re.findall(currency_pattern, text)
        if matches:
            try:
                return float(matches[-1])
            except ValueError:
                pass
        
        return None
    
    def _extract_purchase_date(self, text: str) -> Optional[str]:
        """Extract purchase date from receipt text"""
        # Look for date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}\s+\w+\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_items(self, text: str) -> List[Dict]:
        """Extract items from receipt text (simplified implementation)"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for lines that might contain item information
            # This is a simplified approach - in production, you'd use more sophisticated NLP
            if re.search(r'\$?\d+\.?\d*', line) and len(line) > 5:
                # Try to extract price from the line
                price_match = re.search(r'\$?(\d+\.?\d*)', line)
                if price_match:
                    try:
                        price = float(price_match.group(1))
                        # Extract item name (everything before the price)
                        item_name = line[:price_match.start()].strip()
                        if item_name and price > 0:
                            items.append({
                                "item_name": item_name,
                                "quantity": 1.0,
                                "unit_price": price,
                                "total_price": price,
                                "category": None
                            })
                    except ValueError:
                        continue
        
        return items
