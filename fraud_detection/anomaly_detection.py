# Pricing anomaly algorithm
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple
import re
import json
import os
from datetime import datetime

class AnomalyDetector:
    """
    Advanced anomaly detection for financial Telegram messages.
    Uses multiple techniques to identify suspicious patterns.
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Suspicious patterns
        self.suspicious_patterns = {
            'urgency': [r'urgent', r'limited time', r'act now', r'expires soon'],
            'financial_promises': [r'guaranteed', r'100%', r'risk free', r'instant profit'],
            'contact_pressure': [r'dm me', r'private message', r'whatsapp', r'call now'],
            'medical_claims': [r'miracle cure', r'instant healing', r'100% effective'],
            'price_manipulation': [r'special price', r'discount', r'50% off', r'limited offer']
        }
    
    def extract_features(self, messages: List[Dict]) -> pd.DataFrame:
        """Extract numerical features from messages for anomaly detection."""
        features = []
        
        for msg in messages:
            text = msg.get('text', '')
            
            # Basic text features
            feature_dict = {
                'text_length': len(text),
                'word_count': len(text.split()),
                'exclamation_count': text.count('!'),
                'question_count': text.count('?'),
                'caps_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
                'digit_ratio': sum(1 for c in text if c.isdigit()) / max(len(text), 1),
                'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
                'mention_count': text.count('@'),
                'hashtag_count': text.count('#'),
                'has_media': int(msg.get('has_media', False))
            }
            
            # Pattern-based features
            for category, patterns in self.suspicious_patterns.items():
                feature_dict[f'{category}_score'] = sum(
                    len(re.findall(pattern, text.lower())) for pattern in patterns
                )
            
            # Time-based features
            if 'date' in msg:
                try:
                    msg_time = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
                    feature_dict['hour'] = msg_time.hour
                    feature_dict['day_of_week'] = msg_time.weekday()
                    feature_dict['is_weekend'] = int(msg_time.weekday() >= 5)
                except:
                    feature_dict['hour'] = 12  # Default
                    feature_dict['day_of_week'] = 1
                    feature_dict['is_weekend'] = 0
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def train(self, messages: List[Dict]) -> None:
        """Train the anomaly detection model on historical messages."""
        if len(messages) < 10:
            raise ValueError("Need at least 10 messages to train the model")
        
        # Extract features
        feature_df = self.extract_features(messages)
        
        # Extract text for TF-IDF
        texts = [msg.get('text', '') for msg in messages]
        
        # Fit TF-IDF vectorizer
        tfidf_features = self.vectorizer.fit_transform(texts)
        
        # Combine numerical and text features
        numerical_features = self.scaler.fit_transform(feature_df)
        
        # For simplicity, we'll use only numerical features for isolation forest
        # In production, you might want to combine TF-IDF and numerical features
        self.isolation_forest.fit(numerical_features)
        
        self.is_trained = True
        print(f"Model trained on {len(messages)} messages")
    
    def detect_anomalies(self, messages: List[Dict]) -> List[Dict]:
        """
        Detect anomalous messages.
        
        Returns:
            List of dictionaries with anomaly scores and classifications
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before detecting anomalies")
        
        # Extract features
        feature_df = self.extract_features(messages)
        numerical_features = self.scaler.transform(feature_df)
        
        # Get anomaly scores
        anomaly_scores = self.isolation_forest.decision_function(numerical_features)
        anomaly_labels = self.isolation_forest.predict(numerical_features)
        
        results = []
        for i, msg in enumerate(messages):
            result = {
                'message_id': msg.get('id', i),
                'text': msg.get('text', '')[:200] + '...' if len(msg.get('text', '')) > 200 else msg.get('text', ''),
                'channel': msg.get('channel', 'unknown'),
                'date': msg.get('date', ''),
                'anomaly_score': float(anomaly_scores[i]),
                'is_anomaly': bool(anomaly_labels[i] == -1),
                'risk_level': self._get_risk_level(anomaly_scores[i]),
                'suspicious_patterns': self._identify_patterns(msg.get('text', ''))
            }
            results.append(result)
        
        # Sort by anomaly score (most anomalous first)
        results.sort(key=lambda x: x['anomaly_score'])
        
        return results
    
    def _get_risk_level(self, score: float) -> str:
        """Convert anomaly score to risk level."""
        if score < -0.2:
            return "HIGH"
        elif score < 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_patterns(self, text: str) -> List[str]:
        """Identify which suspicious patterns are present in the text."""
        found_patterns = []
        text_lower = text.lower()
        
        for category, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    found_patterns.append(category)
                    break  # Only count each category once
        
        return found_patterns
    
    def analyze_channel_behavior(self, channel_messages: Dict[str, List[Dict]]) -> Dict:
        """
        Analyze anomalous behavior patterns across channels.
        
        Args:
            channel_messages: Dict mapping channel names to their messages
            
        Returns:
            Analysis results for each channel
        """
        channel_analysis = {}
        
        for channel, messages in channel_messages.items():
            if len(messages) < 5:  # Skip channels with too few messages
                continue
            
            anomalies = self.detect_anomalies(messages)
            high_risk_count = sum(1 for a in anomalies if a['risk_level'] == 'HIGH')
            
            # Calculate pattern frequencies
            pattern_counts = {}
            for anomaly in anomalies:
                for pattern in anomaly['suspicious_patterns']:
                    pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            
            channel_analysis[channel] = {
                'total_messages': len(messages),
                'anomalous_messages': sum(1 for a in anomalies if a['is_anomaly']),
                'high_risk_messages': high_risk_count,
                'anomaly_rate': sum(1 for a in anomalies if a['is_anomaly']) / len(messages),
                'avg_anomaly_score': np.mean([a['anomaly_score'] for a in anomalies]),
                'top_patterns': sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3],
                'most_anomalous': anomalies[:3] if anomalies else []
            }
        
        return channel_analysis

def load_and_analyze():
    """Load data and perform anomaly analysis."""
    detector = AnomalyDetector()
    
    # Load data from JSON files
    data_dir = os.path.join(os.path.dirname(__file__), '../data/raw')
    all_messages = []
    channel_messages = {}
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                        all_messages.extend(messages)
                        
                        # Group by channel
                        for msg in messages:
                            channel = msg.get('channel', 'unknown')
                            if channel not in channel_messages:
                                channel_messages[channel] = []
                            channel_messages[channel].append(msg)
                            
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    if len(all_messages) < 10:
        print("Not enough data to train anomaly detection model")
        return
    
    # Train the model
    print(f"Training anomaly detection model on {len(all_messages)} messages...")
    detector.train(all_messages)
    
    # Analyze anomalies
    print("Detecting anomalies...")
    anomalies = detector.detect_anomalies(all_messages)
    
    # Print top anomalies
    print("\n=== TOP 10 ANOMALOUS MESSAGES ===")
    for i, anomaly in enumerate(anomalies[:10]):
        print(f"\n{i+1}. Channel: {anomaly['channel']}")
        print(f"   Risk Level: {anomaly['risk_level']}")
        print(f"   Anomaly Score: {anomaly['anomaly_score']:.3f}")
        print(f"   Text: {anomaly['text']}")
        if anomaly['suspicious_patterns']:
            print(f"   Patterns: {', '.join(anomaly['suspicious_patterns'])}")
    
    # Channel analysis
    print("\n=== CHANNEL ANALYSIS ===")
    channel_analysis = detector.analyze_channel_behavior(channel_messages)
    
    for channel, stats in channel_analysis.items():
        print(f"\nChannel: {channel}")
        print(f"  Total Messages: {stats['total_messages']}")
        print(f"  Anomaly Rate: {stats['anomaly_rate']:.2%}")
        print(f"  High Risk Messages: {stats['high_risk_messages']}")
        print(f"  Avg Anomaly Score: {stats['avg_anomaly_score']:.3f}")
        if stats['top_patterns']:
            print(f"  Top Patterns: {', '.join([p[0] for p in stats['top_patterns']])}")

if __name__ == "__main__":
    load_and_analyze()
