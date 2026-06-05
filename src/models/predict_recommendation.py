"""
predict_recommendation.py

Backend inference module for Smart Buy Window Predictor.

This module:
1. Loads the trained XGBoost price-drop model.
2. Loads the required feature column order.
3. Loads model metadata and availability-risk rules.
4. Predicts meaningful 14-day price-drop probability.
5. Computes availability-risk score.
6. Combines both into BUY NOW / WAIT / UNCERTAIN.
"""

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = PROJECT_ROOT / "models"

if not MODELS_DIR.exists():
    raise RuntimeError(f"models/ directory not found at expected path: {MODELS_DIR}")

MODEL_PATH = MODELS_DIR / "xgb_price_drop_14d_model.joblib"
FEATURE_COLUMNS_PATH = MODELS_DIR / "feature_columns.json"
MODEL_METADATA_PATH = MODELS_DIR / "model_metadata.json"
AVAILABILITY_CONFIG_PATH = MODELS_DIR / "availability_risk_config.json"

def load_artifacts():
    """Load model, feature columns, metadata, and availability-risk config."""

    required_files = [
        MODEL_PATH,
        FEATURE_COLUMNS_PATH,
        MODEL_METADATA_PATH,
        AVAILABILITY_CONFIG_PATH,
    ]

    missing_files = [str(path) for path in required_files if not path.exists()]

    if missing_files:
        raise FileNotFoundError(
            "Missing required model artifact(s): "
            + ", ".join(missing_files)
        )

    model = joblib.load(MODEL_PATH)

    with open(FEATURE_COLUMNS_PATH, "r") as f:
        feature_columns = json.load(f)

    if not isinstance(feature_columns, list):
        raise TypeError("feature_columns.json must contain a JSON list.")

    with open(MODEL_METADATA_PATH, "r") as f:
        metadata = json.load(f)

    with open(AVAILABILITY_CONFIG_PATH, "r") as f:
        availability_config = json.load(f)

    return model, feature_columns, metadata, availability_config


try:
    MODEL, FEATURE_COLUMNS, MODEL_METADATA, AVAILABILITY_CONFIG = load_artifacts()
except Exception as e:
    raise RuntimeError(
        "Failed to load prediction artifacts. "
        "Check that the models/ directory contains: "
        "xgb_price_drop_14d_model.joblib, feature_columns.json, "
        "model_metadata.json, and availability_risk_config.json. "
        f"Original error: {e}"
    )


def align_features(product_features: dict) -> pd.DataFrame:
    """
    Align incoming product features to the exact training feature order.

    Missing features are filled with NaN. Extra fields are ignored.
    """

    aligned = {}

    for col in FEATURE_COLUMNS:
        aligned[col] = product_features.get(col, np.nan)

    return pd.DataFrame([aligned], columns=FEATURE_COLUMNS)


def get_price_zone(probability: float) -> str:
    """
    Convert price-drop probability into a price recommendation zone.
    """

    buy_threshold = MODEL_METADATA.get("confident_buy_threshold", 0.25)
    wait_threshold = MODEL_METADATA.get("confident_wait_threshold", 0.65)

    if probability <= buy_threshold:
        return "confident_buy"

    if probability >= wait_threshold:
        return "confident_wait"

    return "uncertain"


def calculate_availability_risk(product_features: dict) -> dict:
    """
    Calculate rule-based availability-risk score.

    This is not a stock-out ML model. It is a transparent risk proxy based on
    Amazon source stability, source switching, offer count, and offer-count trend.
    """

    amazon_missing_14d = product_features.get("amazon_price_raw_missing_rolling_14", np.nan)
    price_source_amazon = product_features.get("price_source_amazon", np.nan)
    price_source_changed_7d = product_features.get("price_source_changed_7d", np.nan)
    offer_count_missing_flag = product_features.get("offer_count_missing_flag", np.nan)
    offer_count = product_features.get("offer_count", np.nan)
    offer_count_trend_14 = product_features.get("offer_count_trend_14", np.nan)

    risk_flags = {
        "risk_amazon_missing_recent": int(pd.notna(amazon_missing_14d) and amazon_missing_14d >= 0.85),
        "risk_not_amazon_source": int(pd.notna(price_source_amazon) and price_source_amazon == 0),
        "risk_price_source_changed": int(pd.notna(price_source_changed_7d) and price_source_changed_7d == 1),
        "risk_offer_count_missing": int(pd.notna(offer_count_missing_flag) and offer_count_missing_flag == 1),
        "risk_low_offer_count": int(pd.notna(offer_count) and offer_count <= 2),
        "risk_offer_count_declining": int(pd.notna(offer_count_trend_14) and offer_count_trend_14 <= -2),
    }

    score = (
        1 * risk_flags["risk_amazon_missing_recent"]
        + 2 * risk_flags["risk_not_amazon_source"]
        + 1 * risk_flags["risk_price_source_changed"]
        + 1 * risk_flags["risk_offer_count_missing"]
        + 2 * risk_flags["risk_low_offer_count"]
        + 2 * risk_flags["risk_offer_count_declining"]
    )

    if score <= 2:
        level = "LOW"
    elif score <= 4:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "availability_risk_score": int(score),
        "availability_risk_level": level,
        "risk_flags": risk_flags,
    }


def combine_recommendation(price_zone: str, availability_risk_level: str) -> str:
    """
    Combine price-drop model output and availability risk.

    Availability risk acts as a caution layer. If availability risk is HIGH,
    we avoid strong WAIT recommendations.
    """

    if availability_risk_level == "HIGH":
        if price_zone == "confident_wait":
            return "UNCERTAIN"
        return "BUY_NOW"

    if price_zone == "confident_wait":
        return "WAIT"

    if price_zone == "confident_buy":
        return "BUY_NOW"

    return "UNCERTAIN"


def build_explanation(
    probability: float,
    price_zone: str,
    availability_result: dict,
    final_recommendation: str,
) -> list:
    """
    Build short human-readable explanation messages.
    """

    explanations = []

    explanations.append(
        f"The model estimates a {probability:.1%} probability of a meaningful 14-day price drop."
    )

    if price_zone == "confident_wait":
        explanations.append("The price-drop model sees a strong waiting opportunity.")
    elif price_zone == "confident_buy":
        explanations.append("The price-drop model sees a low chance of a meaningful short-term drop.")
    else:
        explanations.append("The price-drop model is uncertain, so a strong price-based recommendation is avoided.")

    risk_level = availability_result["availability_risk_level"]

    if risk_level == "HIGH":
        explanations.append("Availability risk is high, so waiting may be risky.")
    elif risk_level == "MEDIUM":
        explanations.append("Availability risk is medium, so waiting should be treated with some caution.")
    else:
        explanations.append("Availability risk is low based on current marketplace signals.")

        if final_recommendation == "WAIT":
            explanations.append(
                "Final recommendation: WAIT because the model sees a strong chance of a meaningful price drop and availability risk is not high."
            )
        elif final_recommendation == "BUY_NOW":
            if price_zone == "confident_buy":
                explanations.append(
                    "Final recommendation: BUY NOW because the model estimates a low chance of a meaningful short-term price drop."
                )
            elif availability_result["availability_risk_level"] == "HIGH":
                explanations.append(
                    "Final recommendation: BUY NOW because availability risk is high, so waiting may be risky."
                )
            else:
                explanations.append(
                    "Final recommendation: BUY NOW because the current signals do not support waiting."
                )
        else:
            explanations.append(
                "Final recommendation: UNCERTAIN because the model is not confident enough to recommend buying now or waiting. Consider checking again in a few days or monitoring the price manually."
            )
    return explanations


def predict_recommendation(product_features: dict) -> dict:
    """
    Main backend prediction function.

    Input:
        product_features: dictionary containing the engineered features for one product-date row.

    Output:
        dictionary containing final recommendation, probability, risk score, and explanations.
    """

    X = align_features(product_features)

    probability = float(MODEL.predict_proba(X)[0, 1])
    price_zone = get_price_zone(probability)

    availability_result = calculate_availability_risk(product_features)

    final_recommendation = combine_recommendation(
        price_zone=price_zone,
        availability_risk_level=availability_result["availability_risk_level"],
    )

    explanations = build_explanation(
        probability=probability,
        price_zone=price_zone,
        availability_result=availability_result,
        final_recommendation=final_recommendation,
    )

    return {
        "recommendation": final_recommendation,
        "price_drop_probability": round(probability, 4),
        "price_zone": price_zone,
        "availability_risk_level": availability_result["availability_risk_level"],
        "availability_risk_score": availability_result["availability_risk_score"],
        "risk_flags": availability_result["risk_flags"],
        "explanation": explanations,
    }