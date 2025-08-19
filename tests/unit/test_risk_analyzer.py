import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from api.core.risk_analyzer import RiskAnalyzer

class TestRiskAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.analyzer = RiskAnalyzer()
    
    def test_low_risk_message(self):
        """Test that normal messages get low risk scores."""
        text = "Hello, how are you today? I hope you're doing well."
        risk_score, products, factors = self.analyzer.calculate_risk_score(text)
        
        self.assertLess(risk_score, 0.4)
        self.assertEqual(len(products), 0)
        self.assertEqual(len(factors), 0)
    
    def test_high_risk_financial_message(self):
        """Test that financial scam messages get high risk scores."""
        text = "Guaranteed 100% profit! Risk free investment! Act now, limited time offer!"
        risk_score, products, factors = self.analyzer.calculate_risk_score(text)
        
        self.assertGreater(risk_score, 0.7)
        self.assertIn("Guaranteed Returns", factors)
        self.assertIn("Urgency Pressure", factors)
    
    def test_medical_product_detection(self):
        """Test detection of medical products."""
        text = "We have paracetamol and ibuprofen tablets available."
        risk_score, products, factors = self.analyzer.calculate_risk_score(text)
        
        self.assertIn("paracetamol", products)
        self.assertIn("ibuprofen", products)
    
    def test_risk_level_classification(self):
        """Test risk level classification."""
        self.assertEqual(self.analyzer.get_risk_level(0.8), "HIGH")
        self.assertEqual(self.analyzer.get_risk_level(0.5), "MEDIUM")
        self.assertEqual(self.analyzer.get_risk_level(0.2), "LOW")
    
    def test_comprehensive_analysis(self):
        """Test the complete message analysis."""
        text = "Miracle cure pills! 100% effective! DM me for special price!"
        analysis = self.analyzer.analyze_message(text, "@test_channel")
        
        self.assertIn('risk_score', analysis)
        self.assertIn('risk_level', analysis)
        self.assertIn('detected_products', analysis)
        self.assertIn('risk_factors', analysis)
        self.assertIn('confidence', analysis)
        self.assertEqual(analysis['channel'], "@test_channel")
        
        # Should detect high risk
        self.assertEqual(analysis['risk_level'], "HIGH")
        self.assertIn("pills", analysis['detected_products'])
    
    def test_empty_message(self):
        """Test handling of empty messages."""
        risk_score, products, factors = self.analyzer.calculate_risk_score("")
        
        self.assertEqual(risk_score, 0.0)
        self.assertEqual(len(products), 0)
        self.assertEqual(len(factors), 0)
    
    def test_contact_pressure_detection(self):
        """Test detection of contact pressure patterns."""
        text = "Great opportunity! WhatsApp me for details. Private message only!"
        risk_score, products, factors = self.analyzer.calculate_risk_score(text)
        
        self.assertGreater(risk_score, 0.4)
        self.assertIn("Contact Requests", factors)

if __name__ == '__main__':
    unittest.main()
