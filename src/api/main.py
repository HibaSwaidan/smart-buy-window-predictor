import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List

# Import the inference function
from src.models.predict_recommendation import predict_recommendation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Buy Window Predictor API",
    description="Predicts whether to BUY NOW, WAIT, or be UNCERTAIN based on price-drop probability and availability risk.",
    version="1.0.0"
)

# Request model – expects a dictionary of features
class PredictionRequest(BaseModel):
    features: Dict[str, Any] = Field(..., description="Feature dictionary matching the trained model's feature set.")

# Response model – matches the output of predict_recommendation()
class PredictionResponse(BaseModel):
    recommendation: str
    price_drop_probability: float
    price_zone: str
    availability_risk_level: str
    availability_risk_score: int
    risk_flags: Dict[str, int]
    explanation: List[str]

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Accepts product features and returns a buy/wait recommendation.
    """
    try:
        logger.info(f"Received prediction request with feature keys: {list(request.features.keys())}")
        result = predict_recommendation(request.features)
        logger.info(f"Prediction successful: {result['recommendation']}")
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok"}