# In src/api/endpoints/risk.py
from fastapi import APIRouter, HTTPException
from ..schemas import RiskScoreRequest

router = APIRouter()

@router.post("/detect_risks")
async def detect_risks(request: RiskScoreRequest):
    if not request.authorized:
        raise HTTPException(status_code=403)
    return calculate_risk(request.message_text)