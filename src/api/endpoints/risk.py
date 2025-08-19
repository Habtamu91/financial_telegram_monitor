from fastapi import APIRouter, HTTPException, Depends
from typing import List
import json
import os
from datetime import datetime, timedelta

from ..schemas.risk_schemas import RiskScoreRequest, RiskScoreResponse, MessageAnalysis
from ..core.risk_analyzer import RiskAnalyzer

router = APIRouter()
risk_analyzer = RiskAnalyzer()

@router.post("/detect", response_model=RiskScoreResponse)
async def detect_risks(request: RiskScoreRequest):
    """Analyze a single message for risk factors."""
    if not request.authorized:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    analysis = risk_analyzer.analyze_message(request.message_text, request.channel)
    
    return RiskScoreResponse(
        risk_score=analysis['risk_score'],
        risk_level=analysis['risk_level'],
        detected_products=analysis['detected_products'],
        risk_factors=analysis['risk_factors'],
        confidence=analysis['confidence']
    )

@router.get("/risky_messages", response_model=List[MessageAnalysis])
async def get_risky_messages(limit: int = 10, min_risk_score: float = 0.5):
    """Get top risky messages from stored data."""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), '../../../data/raw')
        risky_messages = []
        
        # Scan through JSON files in data directory
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(data_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                            
                        for msg in messages:
                            analysis = risk_analyzer.analyze_message(msg['text'], msg['channel'])
                            if analysis['risk_score'] >= min_risk_score:
                                risky_messages.append(MessageAnalysis(
                                    id=msg['id'],
                                    text=msg['text'][:200] + '...' if len(msg['text']) > 200 else msg['text'],
                                    channel=msg['channel'],
                                    date=datetime.fromisoformat(msg['date'].replace('Z', '+00:00')),
                                    risk_score=analysis['risk_score'],
                                    detected_products=analysis['detected_products'],
                                    risk_factors=analysis['risk_factors']
                                ))
                    except Exception as e:
                        continue  # Skip corrupted files
        
        # Sort by risk score and return top results
        risky_messages.sort(key=lambda x: x.risk_score, reverse=True)
        return risky_messages[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving risky messages: {str(e)}")

@router.get("/trending_products")
async def get_trending_products(days: int = 7):
    """Get most mentioned medical products in recent messages."""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), '../../../data/raw')
        product_counts = {}
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(data_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                            
                        for msg in messages:
                            msg_date = datetime.fromisoformat(msg['date'].replace('Z', '+00:00'))
                            if msg_date >= cutoff_date:
                                for product in msg.get('mentions', []):
                                    product_counts[product] = product_counts.get(product, 0) + 1
                    except Exception:
                        continue
        
        # Sort by count and return top 10
        trending = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return {"trending_products": [{"product": k, "mentions": v} for k, v in trending]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trending products: {str(e)}")

@router.get("/channel_stats")
async def get_channel_statistics():
    """Get statistics about monitored channels."""
    try:
        data_dir = os.path.join(os.path.dirname(__file__), '../../../data/raw')
        channel_stats = {}
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(data_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                            
                        for msg in messages:
                            channel = msg['channel']
                            if channel not in channel_stats:
                                channel_stats[channel] = {
                                    'total_messages': 0,
                                    'high_risk_messages': 0,
                                    'avg_risk_score': 0.0
                                }
                            
                            channel_stats[channel]['total_messages'] += 1
                            analysis = risk_analyzer.analyze_message(msg['text'])
                            
                            if analysis['risk_score'] >= 0.7:
                                channel_stats[channel]['high_risk_messages'] += 1
                            
                            # Update running average
                            current_avg = channel_stats[channel]['avg_risk_score']
                            total_msgs = channel_stats[channel]['total_messages']
                            channel_stats[channel]['avg_risk_score'] = (
                                (current_avg * (total_msgs - 1) + analysis['risk_score']) / total_msgs
                            )
                    except Exception:
                        continue
        
        return {"channel_statistics": channel_stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving channel statistics: {str(e)}")
