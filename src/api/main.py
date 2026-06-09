import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from src.services.asin_parser import extract_asin
from src.services.keepa_client import fetch_keepa_product
from src.features.live_feature_builder import build_live_features_from_keepa
from src.models.predict_recommendation import predict_recommendation
from src.services.tracking_store import (
    save_tracking_request,
    get_tracking_requests,
    cancel_tracking_request,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Smart Buy Window Predictor API",
    description=(
        "Predicts 7-day, 14-day, and 30-day price-drop opportunities using live "
        "Keepa history, multi-horizon XGBoost models, and an availability-risk layer."
    ),
    version="2.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


class HorizonPrediction(BaseModel):
    horizon: int
    price_drop_probability: float
    price_zone: str
    buy_threshold: float
    wait_threshold: float
    recommendation: str
    explanation: List[str]


class PredictionResponse(BaseModel):
    asin: str
    title: Optional[str] = None
    brand: Optional[str] = None
    root_category: Optional[str] = None
    image_url: Optional[str] = None
    latest_price: Optional[float] = None
    latest_date: Optional[str] = None
    history_days: Optional[int] = None
    valid_price_days: Optional[int] = None

    recommendation: str
    best_horizon: int
    price_drop_probability: float
    price_zone: str

    availability_risk_level: str
    availability_risk_score: int
    risk_flags: Dict[str, int]

    horizon_predictions: Dict[str, HorizonPrediction]
    explanation: List[str]
    price_history: List[PriceHistoryPoint]


class TrackingRequest(BaseModel):
    asin: str = Field(..., description="Product ASIN to track.")
    email: EmailStr = Field(..., description="Email address to notify.")
    product_title: Optional[str] = None
    image_url: Optional[str] = None
    current_price: Optional[float] = None
    target_price: Optional[float] = None
    tracking_horizon: int = Field(
        14,
        description="Tracking window in days. Use 7, 14, or 30.",
    )
    notify_on_meaningful_drop: bool = True


class TrackingResponse(BaseModel):
    id: str
    asin: str
    email: EmailStr
    product_title: Optional[str] = None
    image_url: Optional[str] = None
    current_price: Optional[float] = None
    target_price: Optional[float] = None
    tracking_horizon: int
    notify_on_meaningful_drop: bool
    created_at: str
    last_checked_at: Optional[str] = None
    last_seen_price: Optional[float] = None
    status: str
    message: str


def _default_meaningful_drop_target(current_price: Optional[float]) -> Optional[float]:
    if current_price is None or current_price <= 0:
        return None

    drop_amount = max(current_price * 0.05, 5)
    return round(current_price - drop_amount, 2)


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Accepts an Amazon URL or ASIN, pulls live Keepa history, builds V2.1 features,
    and returns multi-horizon BUY NOW / WAIT / WAIT AND TRACK / UNCERTAIN guidance.
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
            "image_url": metadata.get("image_url"),
            "latest_price": metadata.get("latest_price"),
            "latest_date": metadata.get("latest_date"),
            "history_days": metadata.get("history_days"),
            "valid_price_days": metadata.get("valid_price_days"),
            **result,
            "price_history": price_history,
        }

        logger.info(
            f"Prediction successful for ASIN {asin}: "
            f"{result['recommendation']} over {result['best_horizon']} days"
        )

        return response

    except ValueError as e:
        logger.warning(f"Bad request or insufficient data: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/track", response_model=TrackingResponse)
async def track_product(request: TrackingRequest):
    """
    Saves a product tracking request into Supabase/Postgres.
    """

    try:
        logger.info(
            f"Received tracking request for ASIN {request.asin} "
            f"and email {request.email}"
        )

        normalized_asin = extract_asin(request.asin)

        if request.tracking_horizon not in [7, 14, 30]:
            raise ValueError("Tracking horizon must be 7, 14, or 30 days.")

        if request.current_price is not None and request.current_price <= 0:
            raise ValueError("Current price must be greater than 0.")

        target_price = request.target_price

        if target_price is None and request.notify_on_meaningful_drop:
            target_price = _default_meaningful_drop_target(request.current_price)

        if target_price is not None and target_price <= 0:
            raise ValueError("Target price must be greater than 0.")

        saved_request = save_tracking_request(
            asin=normalized_asin,
            email=str(request.email),
            product_title=request.product_title,
            image_url=request.image_url,
            current_price=request.current_price,
            target_price=target_price,
            tracking_horizon=request.tracking_horizon,
            notify_on_meaningful_drop=request.notify_on_meaningful_drop,
        )

        return {
            **saved_request,
            "message": (
                "Tracking request saved. You will be notified when the product "
                "matches your tracking condition."
            ),
        }

    except ValueError as e:
        logger.warning(f"Invalid tracking request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to save tracking request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Tracking request could not be saved: {str(e)}",
        )


@app.get("/tracking")
async def list_tracking_requests(
    email: EmailStr = Query(..., description="Email address used for tracking.")
):
    """
    Returns tracking requests for one email only.
    """

    try:
        return {
            "items": get_tracking_requests(str(email)),
        }

    except Exception as e:
        logger.error(f"Failed to list tracking requests: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Tracking requests could not be loaded: {str(e)}",
        )


@app.delete("/tracking/{tracking_id}")
async def untrack_product(
    tracking_id: str,
    email: EmailStr = Query(..., description="Email address used for tracking."),
):
    """
    Cancels a tracking request only if the tracking ID belongs to the given email.
    """

    try:
        updated_request = cancel_tracking_request(tracking_id, str(email))

        return {
            **updated_request,
            "message": "Tracking has been cancelled for this product.",
        }

    except ValueError as e:
        logger.warning(f"Invalid untrack request: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"Failed to cancel tracking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Tracking could not be cancelled: {str(e)}",
        )


@app.get("/health")
async def health():
    return {"status": "ok"}