from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import risk
from .core.risk_analyzer import RiskAnalyzer

app = FastAPI(
    title="Financial Telegram Monitor API",
    description="API for analyzing financial risks in Telegram messages",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize risk analyzer
risk_analyzer = RiskAnalyzer()

# Include routers
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])

@app.get("/")
async def root():
    return {"message": "Financial Telegram Monitor API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



