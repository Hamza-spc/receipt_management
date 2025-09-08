#!/usr/bin/env python3
"""
OCR Service Tests for Scan&Track
Unit tests for OCR functionality
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ocr_service import OCRService
from app.services.categorization_service import CategorizationService

class TestOCRService(unittest.TestCase):
    """Test cases for OCR service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ocr_service = OCRService()
        self.categorization_service = CategorizationService()
    
    def test_extract_merchant_name(self):
        """Test merchant name extraction"""
        test_text = """
        STARBUCKS COFFEE
        123 Main Street
        City, State 12345
        
        Receipt #12345
        Date: 2024-01-15
        """
        
        merchant_name = self.ocr_service._extract_merchant_name(test_text)
        self.assertEqual(merchant_name, "STARBUCKS COFFEE")
    
    def test_extract_total_amount(self):
        """Test total amount extraction"""
        test_cases = [
            ("Total: $12.45", 12.45),
            ("TOTAL $25.99", 25.99),
            ("Amount: $8.50", 8.50),
            ("Final Total: $100.00", 100.00),
            ("$15.75", 15.75),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.ocr_service._extract_total_amount(text)
                self.assertEqual(result, expected)
    
    def test_extract_purchase_date(self):
        """Test purchase date extraction"""
        test_cases = [
            ("Date: 01/15/2024", "01/15/2024"),
            ("2024-01-15", "2024-01-15"),
            ("15-Jan-2024", "15-Jan-2024"),
            ("Purchase Date: 01/15/2024", "01/15/2024"),
        ]
        
        for text, expected in test_cases:
            with self.subTest(text=text):
                result = self.ocr_service._extract_purchase_date(text)
                self.assertEqual(result, expected)
    
    def test_extract_items(self):
        """Test item extraction"""
        test_text = """
        Coffee $3.50
        Sandwich $8.99
        Cookie $2.25
        Tax $1.20
        Total $16.94
        """
        
        items = self.ocr_service._extract_items(test_text)
        self.assertGreater(len(items), 0)
        
        # Check that items have required fields
        for item in items:
            self.assertIn('item_name', item)
            self.assertIn('unit_price', item)
            self.assertIn('total_price', item)
            self.assertGreater(item['unit_price'], 0)

class TestCategorizationService(unittest.TestCase):
    """Test cases for categorization service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.categorization_service = CategorizationService()
    
    def test_categorize_food_items(self):
        """Test food item categorization"""
        food_items = [
            "Coffee",
            "Sandwich",
            "Pizza Slice",
            "Salad",
            "Burger",
            "Chicken Wings"
        ]
        
        for item in food_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Food & Dining")
    
    def test_categorize_transportation_items(self):
        """Test transportation item categorization"""
        transport_items = [
            "Gas",
            "Uber Ride",
            "Parking Fee",
            "Toll",
            "Bus Ticket"
        ]
        
        for item in transport_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Transportation")
    
    def test_categorize_shopping_items(self):
        """Test shopping item categorization"""
        shopping_items = [
            "T-Shirt",
            "Jeans",
            "Shoes",
            "Electronics",
            "Book"
        ]
        
        for item in shopping_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Shopping")
    
    def test_categorize_healthcare_items(self):
        """Test healthcare item categorization"""
        health_items = [
            "Prescription",
            "Vitamins",
            "Bandage",
            "Medicine"
        ]
        
        for item in health_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Healthcare")
    
    def test_categorize_entertainment_items(self):
        """Test entertainment item categorization"""
        entertainment_items = [
            "Movie Ticket",
            "Netflix",
            "Gym Membership",
            "Concert Ticket"
        ]
        
        for item in entertainment_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Entertainment")
    
    def test_categorize_utility_items(self):
        """Test utility item categorization"""
        utility_items = [
            "Electric Bill",
            "Internet",
            "Phone Bill",
            "Water Bill"
        ]
        
        for item in utility_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Utilities")
    
    def test_categorize_office_items(self):
        """Test office item categorization"""
        office_items = [
            "Office Supplies",
            "Printer Paper",
            "Pen",
            "Meeting Room"
        ]
        
        for item in office_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Office & Business")
    
    def test_categorize_travel_items(self):
        """Test travel item categorization"""
        travel_items = [
            "Hotel",
            "Flight",
            "Airbnb",
            "Luggage"
        ]
        
        for item in travel_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Travel")
    
    def test_categorize_unknown_items(self):
        """Test categorization of unknown items"""
        unknown_items = [
            "Random Item",
            "Unknown Product",
            "Miscellaneous"
        ]
        
        for item in unknown_items:
            with self.subTest(item=item):
                category = self.categorization_service.categorize_item(item)
                self.assertEqual(category, "Other")

class TestIntegration(unittest.TestCase):
    """Integration tests for OCR and categorization"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ocr_service = OCRService()
        self.categorization_service = CategorizationService()
    
    def test_full_receipt_processing(self):
        """Test complete receipt processing pipeline"""
        # Mock receipt text
        receipt_text = """
        STARBUCKS COFFEE
        123 Main Street
        City, State 12345
        
        Receipt #12345
        Date: 01/15/2024
        
        Coffee $3.50
        Sandwich $8.99
        Cookie $2.25
        Tax $1.20
        Total $16.94
        
        Thank you for your visit!
        """
        
        # Mock OCR service to return our test text
        with patch.object(self.ocr_service, 'extract_text', return_value=receipt_text):
            receipt_data = self.ocr_service.extract_receipt_data(b"fake_image_data")
            
            # Verify basic extraction
            self.assertIsNotNone(receipt_data.get('merchant_name'))
            self.assertIsNotNone(receipt_data.get('total_amount'))
            self.assertIsNotNone(receipt_data.get('raw_text'))
            
            # Test categorization
            categorized_data = self.categorization_service.categorize_receipt(receipt_data)
            
            # Verify categorization worked
            self.assertIn('items', categorized_data)
            for item in categorized_data['items']:
                self.assertIn('category', item)
                self.assertIsNotNone(item['category'])

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
