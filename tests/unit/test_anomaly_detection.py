import unittest
import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from fraud_detection.anomaly_detection import AnomalyDetector

class TestAnomalyDetector(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = AnomalyDetector()
        
        # Create sample training data
        self.training_messages = [
            {
                'id': i,
                'text': f"Normal message {i} about medical products",
                'channel': '@test_channel',
                'date': '2024-01-01T12:00:00Z',
                'has_media': False
            }
            for i in range(20)
        ]
        
        # Add some suspicious messages
        self.training_messages.extend([
            {
                'id': 100,
                'text': "URGENT!!! 100% GUARANTEED PROFIT!!! LIMITED TIME OFFER!!! DM ME NOW!!!",
                'channel': '@suspicious_channel',
                'date': '2024-01-01T12:00:00Z',
                'has_media': True
            },
            {
                'id': 101,
                'text': "Miracle cure! Instant healing! Call now for special discount!",
                'channel': '@medical_scam',
                'date': '2024-01-01T12:00:00Z',
                'has_media': False
            }
        ])
    
    def test_feature_extraction(self):
        """Test feature extraction from messages."""
        features_df = self.detector.extract_features(self.training_messages[:5])
        
        # Check that all expected columns are present
        expected_columns = [
            'text_length', 'word_count', 'exclamation_count', 'question_count',
            'caps_ratio', 'digit_ratio', 'url_count', 'mention_count', 'hashtag_count',
            'has_media', 'urgency_score', 'financial_promises_score',
            'contact_pressure_score', 'medical_claims_score', 'price_manipulation_score',
            'hour', 'day_of_week', 'is_weekend'
        ]
        
        for col in expected_columns:
            self.assertIn(col, features_df.columns)
        
        # Check data types
        self.assertEqual(len(features_df), 5)
        self.assertTrue(all(isinstance(x, (int, float, np.integer, np.floating)) for x in features_df.iloc[0]))
    
    def test_model_training(self):
        """Test model training."""
        self.detector.train(self.training_messages)
        self.assertTrue(self.detector.is_trained)
    
    def test_anomaly_detection_requires_training(self):
        """Test that anomaly detection requires a trained model."""
        with self.assertRaises(ValueError):
            self.detector.detect_anomalies([self.training_messages[0]])
    
    def test_anomaly_detection(self):
        """Test anomaly detection on trained model."""
        # Train the model
        self.detector.train(self.training_messages)
        
        # Test messages including a clearly anomalous one
        test_messages = [
            {
                'id': 200,
                'text': "Normal message about paracetamol availability",
                'channel': '@normal_channel',
                'date': '2024-01-02T12:00:00Z',
                'has_media': False
            },
            {
                'id': 201,
                'text': "URGENT!!! GUARANTEED 100% PROFIT!!! RISK FREE!!! ACT NOW!!! LIMITED TIME!!!",
                'channel': '@scam_channel',
                'date': '2024-01-02T12:00:00Z',
                'has_media': True
            }
        ]
        
        results = self.detector.detect_anomalies(test_messages)
        
        # Check results structure
        self.assertEqual(len(results), 2)
        
        for result in results:
            self.assertIn('message_id', result)
            self.assertIn('text', result)
            self.assertIn('channel', result)
            self.assertIn('anomaly_score', result)
            self.assertIn('is_anomaly', result)
            self.assertIn('risk_level', result)
            self.assertIn('suspicious_patterns', result)
        
        # The suspicious message should have a lower anomaly score (more anomalous)
        suspicious_result = next(r for r in results if r['message_id'] == 201)
        normal_result = next(r for r in results if r['message_id'] == 200)
        
        self.assertLess(suspicious_result['anomaly_score'], normal_result['anomaly_score'])
    
    def test_risk_level_classification(self):
        """Test risk level classification."""
        self.assertEqual(self.detector._get_risk_level(-0.5), "HIGH")
        self.assertEqual(self.detector._get_risk_level(-0.1), "MEDIUM")
        self.assertEqual(self.detector._get_risk_level(0.1), "LOW")
    
    def test_pattern_identification(self):
        """Test identification of suspicious patterns."""
        text = "Guaranteed profit! Limited time offer! DM me for details!"
        patterns = self.detector._identify_patterns(text)
        
        self.assertIn("financial_promises", patterns)
        self.assertIn("urgency", patterns)
        self.assertIn("contact_pressure", patterns)
    
    def test_insufficient_training_data(self):
        """Test handling of insufficient training data."""
        with self.assertRaises(ValueError):
            self.detector.train([self.training_messages[0]])  # Only one message
    
    def test_channel_behavior_analysis(self):
        """Test channel behavior analysis."""
        # Train the model first
        self.detector.train(self.training_messages)
        
        # Create channel-grouped messages
        channel_messages = {
            '@normal_channel': self.training_messages[:10],
            '@suspicious_channel': self.training_messages[10:15] + [self.training_messages[-1]]  # Include suspicious message
        }
        
        analysis = self.detector.analyze_channel_behavior(channel_messages)
        
        # Check structure
        self.assertIn('@normal_channel', analysis)
        self.assertIn('@suspicious_channel', analysis)
        
        for channel, stats in analysis.items():
            self.assertIn('total_messages', stats)
            self.assertIn('anomalous_messages', stats)
            self.assertIn('high_risk_messages', stats)
            self.assertIn('anomaly_rate', stats)
            self.assertIn('avg_anomaly_score', stats)
            self.assertIn('top_patterns', stats)
            self.assertIn('most_anomalous', stats)

if __name__ == '__main__':
    unittest.main()
