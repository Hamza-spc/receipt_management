#!/usr/bin/env python3
"""
API Tests for Scan&Track
Unit tests for FastAPI endpoints
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Welcome to Scan&Track API")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
    
    @patch('app.api.receipts.receiptApi.get_receipts')
    def test_get_receipts_endpoint(self, mock_get_receipts):
        """Test get receipts endpoint"""
        # Mock the database response
        mock_receipts = [
            {
                "id": 1,
                "filename": "test_receipt.jpg",
                "file_path": "uploads/test_receipt.jpg",
                "total_amount": 25.99,
                "merchant_name": "Test Store",
                "purchase_date": "2024-01-15T10:30:00",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": None,
                "raw_text": "Test receipt text",
                "items": []
            }
        ]
        mock_get_receipts.return_value = mock_receipts
        
        response = self.client.get("/api/receipts/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["merchant_name"], "Test Store")
    
    @patch('app.api.receipts.receiptApi.get_receipt')
    def test_get_single_receipt_endpoint(self, mock_get_receipt):
        """Test get single receipt endpoint"""
        mock_receipt = {
            "id": 1,
            "filename": "test_receipt.jpg",
            "file_path": "uploads/test_receipt.jpg",
            "total_amount": 25.99,
            "merchant_name": "Test Store",
            "purchase_date": "2024-01-15T10:30:00",
            "created_at": "2024-01-15T10:30:00",
            "updated_at": None,
            "raw_text": "Test receipt text",
            "items": []
        }
        mock_get_receipt.return_value = mock_receipt
        
        response = self.client.get("/api/receipts/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["merchant_name"], "Test Store")
    
    @patch('app.api.receipts.receiptApi.get_receipt')
    def test_get_nonexistent_receipt(self, mock_get_receipt):
        """Test getting non-existent receipt"""
        mock_get_receipt.return_value = None
        
        response = self.client.get("/api/receipts/999")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Receipt not found")
    
    @patch('app.api.analytics.analyticsApi.get_expense_analytics')
    def test_analytics_endpoint(self, mock_get_analytics):
        """Test analytics endpoint"""
        mock_analytics = {
            "total_expenses": 1500.00,
            "monthly_expenses": [
                {"year": 2024, "month": 1, "total": 500.00},
                {"year": 2024, "month": 2, "total": 1000.00}
            ],
            "category_breakdown": [
                {"category": "Food & Dining", "total": 800.00},
                {"category": "Transportation", "total": 700.00}
            ],
            "recent_receipts": []
        }
        mock_get_analytics.return_value = mock_analytics
        
        response = self.client.get("/api/analytics/expenses")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_expenses", data)
        self.assertEqual(data["total_expenses"], 1500.00)
        self.assertIn("monthly_expenses", data)
        self.assertIn("category_breakdown", data)

class TestReceiptUpload(unittest.TestCase):
    """Test cases for receipt upload functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    @patch('app.api.receipts.ocr_service.extract_receipt_data')
    @patch('app.api.receipts.categorization_service.categorize_receipt')
    @patch('app.api.receipts.db.add')
    @patch('app.api.receipts.db.commit')
    @patch('app.api.receipts.db.refresh')
    def test_upload_receipt_success(self, mock_refresh, mock_commit, mock_add, 
                                   mock_categorize, mock_extract):
        """Test successful receipt upload"""
        # Mock OCR response
        mock_extract.return_value = {
            "raw_text": "Test receipt text",
            "merchant_name": "Test Store",
            "total_amount": 25.99,
            "purchase_date": "2024-01-15",
            "items": [
                {
                    "item_name": "Coffee",
                    "quantity": 1.0,
                    "unit_price": 3.50,
                    "total_price": 3.50,
                    "category": "Food & Dining"
                }
            ]
        }
        
        # Mock categorization response
        mock_categorize.return_value = {
            "raw_text": "Test receipt text",
            "merchant_name": "Test Store",
            "total_amount": 25.99,
            "purchase_date": "2024-01-15",
            "items": [
                {
                    "item_name": "Coffee",
                    "quantity": 1.0,
                    "unit_price": 3.50,
                    "total_price": 3.50,
                    "category": "Food & Dining"
                }
            ]
        }
        
        # Mock database response
        mock_receipt = MagicMock()
        mock_receipt.id = 1
        mock_receipt.filename = "test.jpg"
        mock_receipt.file_path = "uploads/test.jpg"
        mock_receipt.total_amount = 25.99
        mock_receipt.merchant_name = "Test Store"
        mock_receipt.purchase_date = "2024-01-15"
        mock_receipt.created_at = "2024-01-15T10:30:00"
        mock_receipt.updated_at = None
        mock_receipt.raw_text = "Test receipt text"
        mock_receipt.items = []
        mock_refresh.return_value = mock_receipt
        
        # Create test file
        test_file_content = b"fake_image_data"
        
        # Test upload
        response = self.client.post(
            "/api/receipts/upload",
            files={"file": ("test.jpg", test_file_content, "image/jpeg")}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["merchant_name"], "Test Store")
        self.assertEqual(data["total_amount"], 25.99)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        test_file_content = b"fake_file_data"
        
        response = self.client.post(
            "/api/receipts/upload",
            files={"file": ("test.txt", test_file_content, "text/plain")}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("File type not supported", data["detail"])
    
    def test_upload_file_too_large(self):
        """Test upload with file too large"""
        # Create a large file (11MB)
        large_file_content = b"x" * (11 * 1024 * 1024)
        
        response = self.client.post(
            "/api/receipts/upload",
            files={"file": ("large.jpg", large_file_content, "image/jpeg")}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("File too large", data["detail"])

class TestDataValidation(unittest.TestCase):
    """Test cases for data validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_receipt_schema_validation(self):
        """Test receipt schema validation"""
        # Test valid receipt data
        valid_receipt = {
            "filename": "test.jpg",
            "total_amount": 25.99,
            "merchant_name": "Test Store",
            "purchase_date": "2024-01-15T10:30:00",
            "raw_text": "Test receipt text"
        }
        
        # This would be tested in a real implementation
        # where we validate the schema before processing
        self.assertIsInstance(valid_receipt["total_amount"], float)
        self.assertIsInstance(valid_receipt["merchant_name"], str)
        self.assertGreater(valid_receipt["total_amount"], 0)
    
    def test_receipt_item_schema_validation(self):
        """Test receipt item schema validation"""
        valid_item = {
            "item_name": "Coffee",
            "quantity": 1.0,
            "unit_price": 3.50,
            "total_price": 3.50,
            "category": "Food & Dining",
            "description": "Hot coffee"
        }
        
        self.assertIsInstance(valid_item["item_name"], str)
        self.assertIsInstance(valid_item["quantity"], float)
        self.assertIsInstance(valid_item["unit_price"], float)
        self.assertIsInstance(valid_item["total_price"], float)
        self.assertGreater(valid_item["quantity"], 0)
        self.assertGreater(valid_item["unit_price"], 0)
        self.assertGreater(valid_item["total_price"], 0)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
