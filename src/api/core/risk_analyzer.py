import re
import os
from typing import List, Dict, Tuple
from datetime import datetime

class RiskAnalyzer:
    def __init__(self):
        self.risk_threshold = float(os.getenv('RISK_THRESHOLD', 0.7))
        
        # Define risk patterns and their weights
        self.risk_patterns = {
            # Financial fraud indicators
            'guaranteed_returns': {
                'patterns': [r'guaranteed.*return', r'100%.*profit', r'risk.*free'],
                'weight': 0.8
            },
            'urgency_pressure': {
                'patterns': [r'limited.*time', r'act.*now', r'hurry', r'expires.*soon'],
                'weight': 0.6
            },
            'unrealistic_claims': {
                'patterns': [r'miracle.*cure', r'instant.*results', r'amazing.*results'],
                'weight': 0.7
            },
            'contact_requests': {
                'patterns': [r'dm.*me', r'private.*message', r'whatsapp', r'telegram.*@'],
                'weight': 0.5
            },
            'price_manipulation': {
                'patterns': [r'special.*price', r'discount.*today', r'50%.*off'],
                'weight': 0.4
            }
        }
        
        # Medical/pharmaceutical product keywords
        self.medical_products = [
            'paracetamol', 'ibuprofen', 'aspirin', 'antibiotic', 'vaccine',
            'insulin', 'cream', 'pills', 'tablets', 'capsules', 'syrup',
            'injection', 'medicine', 'drug', 'pharmaceutical'
        ]

    def calculate_risk_score(self, text: str) -> Tuple[float, List[str], List[str]]:
        """
        Calculate risk score for a given text message.
        
        Returns:
            Tuple of (risk_score, detected_products, risk_factors)
        """
        text_lower = text.lower()
        risk_factors = []
        total_risk = 0.0
        
        # Check for risk patterns
        for category, config in self.risk_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, text_lower):
                    risk_factors.append(category.replace('_', ' ').title())
                    total_risk += config['weight']
                    break  # Only count each category once
        
        # Detect medical products
        detected_products = []
        for product in self.medical_products:
            if product in text_lower:
                detected_products.append(product)
        
        # Normalize risk score to 0-1 range
        risk_score = min(total_risk, 1.0)
        
        return risk_score, detected_products, risk_factors

    def get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to categorical level."""
        if risk_score >= 0.7:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def analyze_message(self, text: str, channel: str = None) -> Dict:
        """
        Comprehensive message analysis.
        
        Returns:
            Dictionary with risk analysis results
        """
        risk_score, detected_products, risk_factors = self.calculate_risk_score(text)
        
        return {
            'risk_score': risk_score,
            'risk_level': self.get_risk_level(risk_score),
            'detected_products': detected_products,
            'risk_factors': risk_factors,
            'confidence': min(0.9, risk_score + 0.1),  # Simple confidence calculation
            'channel': channel,
            'analyzed_at': datetime.now().isoformat()
        }
