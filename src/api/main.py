import logging
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.services.asin_parser import extract_asin
from src.services.keepa_client import fetch_keepa_product
from src.features.live_feature_builder import build_live_features_from_keepa
from src.models.predict_recommendation import predict_recommendation


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Smart Buy Window Predictor API",
    description=(
        "Predicts whether to BUY NOW, WAIT, or be UNCERTAIN using live Keepa "
        "history, a trained price-drop model, and an availability-risk module."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Fine for MVP. Restrict this later in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    url_or_asin: str = Field(
        ...,
        description="Amazon product URL or 10-character ASIN.",
        examples=["https://www.amazon.com/dp/B00008IHL8"],
    )


class PriceHistoryPoint(BaseModel):
    date: str
    price: float


class PredictionResponse(BaseModel):
    asin: str
    title: Optional[str] = None
    brand: Optional[str] = None
    root_category: Optional[str] = None
    latest_price: Optional[float] = None
    latest_date: Optional[str] = None
    history_days: Optional[int] = None
    valid_price_days: Optional[int] = None

    recommendation: str
    price_drop_probability: float
    price_zone: str
    availability_risk_level: str
    availability_risk_score: int
    risk_flags: Dict[str, int]
    explanation: List[str]
    price_history: List[PriceHistoryPoint]


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Accepts an Amazon URL or ASIN, pulls live Keepa history, builds V2 model
    features, and returns a BUY NOW / WAIT / UNCERTAIN recommendation.
    """

    try:
        logger.info(f"Received prediction request: {request.url_or_asin}")

        asin = extract_asin(request.url_or_asin)
        logger.info(f"Extracted ASIN: {asin}")

        product = fetch_keepa_product(asin)
        logger.info(f"Fetched Keepa product data for ASIN: {asin}")

        features, price_history, metadata = build_live_features_from_keepa(product)
        logger.info(
            f"Built live features for ASIN: {asin}. "
            f"History days: {metadata.get('history_days')}, "
            f"Valid price days: {metadata.get('valid_price_days')}"
        )

        result = predict_recommendation(features)

        response = {
            "asin": metadata.get("asin"),
            "title": metadata.get("title"),
            "brand": metadata.get("brand"),
            "root_category": metadata.get("root_category"),
            "latest_price": metadata.get("latest_price"),
            "latest_date": metadata.get("latest_date"),
            "history_days": metadata.get("history_days"),
            "valid_price_days": metadata.get("valid_price_days"),
            **result,
            "price_history": price_history,
        }

        logger.info(f"Prediction successful for ASIN {asin}: {result['recommendation']}")

        return response

    except ValueError as e:
        logger.warning(f"Bad request or insufficient data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "ok"}