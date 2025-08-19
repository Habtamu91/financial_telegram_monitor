import unittest
import sys
import os
import json
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from api.main import app

class TestAPIEndpoints(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("version", data)
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
    
    def test_risk_detection_authorized(self):
        """Test risk detection with authorized request."""
        test_message = {
            "message_text": "Guaranteed 100% profit! Risk free investment!",
            "channel": "@test_channel",
            "authorized": True
        }
        
        response = self.client.post("/api/risk/detect", json=test_message)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("risk_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("detected_products", data)
        self.assertIn("risk_factors", data)
        self.assertIn("confidence", data)
        
        # Should detect high risk
        self.assertGreater(data["risk_score"], 0.5)
        self.assertEqual(data["risk_level"], "HIGH")
    
    def test_risk_detection_unauthorized(self):
        """Test risk detection with unauthorized request."""
        test_message = {
            "message_text": "Test message",
            "authorized": False
        }
        
        response = self.client.post("/api/risk/detect", json=test_message)
        self.assertEqual(response.status_code, 403)
    
    def test_risk_detection_low_risk(self):
        """Test risk detection with low-risk message."""
        test_message = {
            "message_text": "Hello, how are you today?",
            "authorized": True
        }
        
        response = self.client.post("/api/risk/detect", json=test_message)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertLess(data["risk_score"], 0.4)
        self.assertEqual(data["risk_level"], "LOW")
    
    def test_risky_messages_endpoint(self):
        """Test the risky messages endpoint."""
        response = self.client.get("/api/risk/risky_messages")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        
        # If there are results, check structure
        if data:
            message = data[0]
            self.assertIn("id", message)
            self.assertIn("text", message)
            self.assertIn("channel", message)
            self.assertIn("risk_score", message)
            self.assertIn("detected_products", message)
            self.assertIn("risk_factors", message)
    
    def test_risky_messages_with_parameters(self):
        """Test risky messages endpoint with parameters."""
        response = self.client.get("/api/risk/risky_messages?limit=5&min_risk_score=0.8")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 5)
    
    def test_trending_products_endpoint(self):
        """Test the trending products endpoint."""
        response = self.client.get("/api/risk/trending_products")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("trending_products", data)
        self.assertIsInstance(data["trending_products"], list)
        
        # If there are results, check structure
        if data["trending_products"]:
            product = data["trending_products"][0]
            self.assertIn("product", product)
            self.assertIn("mentions", product)
    
    def test_trending_products_with_days_parameter(self):
        """Test trending products endpoint with days parameter."""
        response = self.client.get("/api/risk/trending_products?days=30")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("trending_products", data)
    
    def test_channel_statistics_endpoint(self):
        """Test the channel statistics endpoint."""
        response = self.client.get("/api/risk/channel_stats")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("channel_statistics", data)
        self.assertIsInstance(data["channel_statistics"], dict)
        
        # If there are results, check structure
        if data["channel_statistics"]:
            channel_name = list(data["channel_statistics"].keys())[0]
            stats = data["channel_statistics"][channel_name]
            
            self.assertIn("total_messages", stats)
            self.assertIn("high_risk_messages", stats)
            self.assertIn("avg_risk_score", stats)
    
    def test_invalid_endpoint(self):
        """Test accessing an invalid endpoint."""
        response = self.client.get("/api/risk/nonexistent")
        self.assertEqual(response.status_code, 404)
    
    def test_risk_detection_with_medical_products(self):
        """Test risk detection with medical product mentions."""
        test_message = {
            "message_text": "We have paracetamol and ibuprofen tablets available at special prices!",
            "authorized": True
        }
        
        response = self.client.post("/api/risk/detect", json=test_message)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("paracetamol", data["detected_products"])
        self.assertIn("ibuprofen", data["detected_products"])
        
        # Should have some risk due to "special prices"
        self.assertGreater(data["risk_score"], 0.0)

if __name__ == '__main__':
    unittest.main()
