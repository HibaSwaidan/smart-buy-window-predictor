"""
predict_recommendation.py

Backend inference module for Smart Buy Window Predictor V2.1.

This module:
1. Loads the 7-day, 14-day, and 30-day XGBoost price-drop models.
2. Loads the shared feature column order.
3. Loads multi-horizon metadata and availability-risk rules.
4. Predicts meaningful price-drop probability for all horizons.
5. Computes one horizon-agnostic availability-risk score.
6. Combines price signal and availability risk into user-facing recommendations.
"""

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = PROJECT_ROOT / "models"
V2_MODELS_DIR = MODELS_DIR / "v2_1"

HORIZONS = [7, 14, 30]

MODEL_PATHS = {
    7: V2_MODELS_DIR / "xgb_price_drop_7d_model.joblib",
    14: V2_MODELS_DIR / "xgb_price_drop_14d_model.joblib",
    30: V2_MODELS_DIR / "xgb_price_drop_30d_model.joblib",
}

FEATURE_COLUMNS_PATH = V2_MODELS_DIR / "feature_columns.json"
MODEL_METADATA_PATH = V2_MODELS_DIR / "model_metadata_multihorizon.json"
AVAILABILITY_CONFIG_PATH = MODELS_DIR / "availability_risk_config.json"

DEFAULT_PRODUCT_THRESHOLDS = {
    7: {"buy_threshold": 0.350, "wait_threshold": 0.675},
    14: {"buy_threshold": 0.350, "wait_threshold": 0.575},
    30: {"buy_threshold": 0.325, "wait_threshold": 0.550},
}


def load_artifacts():
    """Load multi-horizon models, feature columns, metadata, and availability-risk config."""

    required_files = list(MODEL_PATHS.values()) + [
        FEATURE_COLUMNS_PATH,
        MODEL_METADATA_PATH,
        AVAILABILITY_CONFIG_PATH,
    ]

    missing_files = [str(path) for path in required_files if not path.exists()]

    if missing_files:
        raise FileNotFoundError(
            "Missing required V2.1 model artifact(s): "
            + ", ".join(missing_files)
        )

    models = {
        horizon: joblib.load(path)
        for horizon, path in MODEL_PATHS.items()
    }

    with open(FEATURE_COLUMNS_PATH, "r") as f:
        feature_columns = json.load(f)

    if not isinstance(feature_columns, list):
        raise TypeError("feature_columns.json must contain a JSON list.")

    with open(MODEL_METADATA_PATH, "r") as f:
        metadata = json.load(f)

    with open(AVAILABILITY_CONFIG_PATH, "r") as f:
        availability_config = json.load(f)

    return models, feature_columns, metadata, availability_config


try:
    MODELS, FEATURE_COLUMNS, MODEL_METADATA, AVAILABILITY_CONFIG = load_artifacts()
except Exception as e:
    raise RuntimeError(
        "Failed to load V2.1 prediction artifacts. "
        "Check that models/v2_1 contains the three joblib models, feature_columns.json, "
        "model_metadata_multihorizon.json, and that models/availability_risk_config.json exists. "
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


def get_product_thresholds(horizon: int) -> dict:
    """
    Load validation-optimised product thresholds for the selected horizon.
    Falls back to fixed V2.1 thresholds if metadata is missing the values.
    """

    metadata_thresholds = (
        MODEL_METADATA
        .get("threshold_selection", {})
        .get("selected_product_thresholds", {})
    )

    threshold_info = metadata_thresholds.get(str(horizon)) or metadata_thresholds.get(horizon)

    if isinstance(threshold_info, dict):
        buy_threshold = threshold_info.get("buy_threshold")
        wait_threshold = threshold_info.get("wait_threshold")

        if buy_threshold is not None and wait_threshold is not None:
            return {
                "buy_threshold": float(buy_threshold),
                "wait_threshold": float(wait_threshold),
            }

    return DEFAULT_PRODUCT_THRESHOLDS[horizon]


def get_price_zone(probability: float, horizon: int) -> str:
    """
    Convert price-drop probability into a product recommendation zone.
    """

    thresholds = get_product_thresholds(horizon)
    buy_threshold = thresholds["buy_threshold"]
    wait_threshold = thresholds["wait_threshold"]

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


def combine_price_and_availability(price_zone: str, availability_risk_level: str, horizon: int) -> str:
    """
    Combine price-drop zone with availability risk.

    Price signal answers: is a meaningful drop likely?
    Availability signal answers: is it safe to wait?
    """

    if price_zone == "confident_buy":
        return "BUY_NOW"

    if price_zone == "uncertain":
        if availability_risk_level == "HIGH":
            return "BUY_NOW"
        return "UNCERTAIN"

    if price_zone == "confident_wait":
        if availability_risk_level == "HIGH":
            return "UNCERTAIN"

        if availability_risk_level == "MEDIUM":
            return "WAIT_WITH_CAUTION"

        if horizon == 30:
            return "WAIT_AND_TRACK"

        return "WAIT"

    return "UNCERTAIN"


def build_horizon_explanation(
    probability: float,
    horizon: int,
    price_zone: str,
    availability_result: dict,
    final_recommendation: str,
) -> list:
    """
    Build concise explanation messages for a single horizon.
    """

    risk_level = availability_result["availability_risk_level"]

    explanations = [
        (
            f"The model estimates a {probability:.1%} probability of a meaningful "
            f"price drop within {horizon} days."
        )
    ]

    if price_zone == "confident_wait":
        explanations.append("The price signal is strong enough to support waiting.")
    elif price_zone == "confident_buy":
        explanations.append("The price signal does not show a strong waiting opportunity.")
    else:
        explanations.append(
            "The price signal is moderate, so the model avoids a strong price-only recommendation."
        )

    if risk_level == "LOW":
        explanations.append("Availability risk is low based on current marketplace signals.")
    elif risk_level == "MEDIUM":
        explanations.append("Availability risk is medium, so waiting should be treated with caution.")
    else:
        explanations.append(
            "Availability risk is high, so waiting may expose the user to product or price-source instability."
        )

    if final_recommendation == "WAIT":
        explanations.append(
            "Recommendation: WAIT because the price opportunity is strong and availability risk is not high."
        )
    elif final_recommendation == "WAIT_WITH_CAUTION":
        explanations.append(
            "Recommendation: WAIT WITH CAUTION because the price opportunity is strong, "
            "but marketplace signals are less stable."
        )
    elif final_recommendation == "WAIT_AND_TRACK":
        explanations.append(
            "Recommendation: WAIT AND TRACK because a longer-window price drop is likely, "
            "but the user should monitor the product and buy when the drop occurs."
        )
    elif final_recommendation == "BUY_NOW":
        explanations.append(
            "Recommendation: BUY NOW because waiting is not supported strongly enough, "
            "or availability risk makes waiting less attractive."
        )
    else:
        explanations.append(
            "Recommendation: UNCERTAIN because the price opportunity and risk signals "
            "do not support a confident action."
        )

    return explanations


def choose_final_recommendation(horizon_predictions: dict) -> dict:
    """
    Select the headline recommendation from all horizon-level outputs.

    WAIT-family recommendations are prioritised using confidence above the
    horizon-specific wait threshold. If no wait opportunity exists, the system
    returns UNCERTAIN if any horizon is uncertain, otherwise BUY_NOW.
    """

    wait_recommendations = []

    for horizon_key, prediction in horizon_predictions.items():
        recommendation = prediction["recommendation"]

        if recommendation in {"WAIT", "WAIT_WITH_CAUTION", "WAIT_AND_TRACK"}:
            horizon = prediction["horizon"]
            thresholds = get_product_thresholds(horizon)
            wait_margin = prediction["price_drop_probability"] - thresholds["wait_threshold"]

            wait_recommendations.append({
                "horizon_key": horizon_key,
                "horizon": horizon,
                "recommendation": recommendation,
                "wait_margin": wait_margin,
                "probability": prediction["price_drop_probability"],
            })

    if wait_recommendations:
        selected = sorted(
            wait_recommendations,
            key=lambda item: (item["wait_margin"], item["probability"]),
            reverse=True,
        )[0]

        return {
            "best_horizon": selected["horizon"],
            "recommendation": selected["recommendation"],
            "selected_horizon_key": selected["horizon_key"],
        }

    uncertain_predictions = [
        prediction
        for prediction in horizon_predictions.values()
        if prediction["recommendation"] == "UNCERTAIN"
    ]

    if uncertain_predictions:
        selected = sorted(
            uncertain_predictions,
            key=lambda item: item["price_drop_probability"],
            reverse=True,
        )[0]

        return {
            "best_horizon": selected["horizon"],
            "recommendation": "UNCERTAIN",
            "selected_horizon_key": f"{selected['horizon']}d",
        }

    return {
        "best_horizon": 14,
        "recommendation": "BUY_NOW",
        "selected_horizon_key": "14d",
    }


def build_final_explanation(
    selected_prediction: dict,
    availability_result: dict,
) -> list:
    """
    Build explanation for the headline recommendation.
    """

    horizon = selected_prediction["horizon"]
    probability = selected_prediction["price_drop_probability"]
    recommendation = selected_prediction["recommendation"]
    price_zone = selected_prediction["price_zone"]
    risk_level = availability_result["availability_risk_level"]

    explanations = [
        f"Price outlook: the selected {horizon}-day model estimates a {probability:.1%} probability of a meaningful price drop."
    ]

    if risk_level == "LOW":
        explanations.append("Availability signal: marketplace conditions look stable.")
    elif risk_level == "MEDIUM":
        explanations.append("Availability signal: some marketplace instability is present, so waiting should be monitored.")
    else:
        explanations.append("Availability signal: availability risk is high, so waiting may be risky.")

    if recommendation == "WAIT":
        explanations.append("Combined recommendation: WAIT because the price signal is strong and availability risk is low.")
        explanations.append("Suggested action: check back soon or track the product for a lower price.")
    elif recommendation == "WAIT_WITH_CAUTION":
        explanations.append("Combined recommendation: WAIT WITH CAUTION because the price signal is strong, but availability risk is not fully stable.")
        explanations.append("Suggested action: monitor the product actively and buy promptly if the price drops.")
    elif recommendation == "WAIT_AND_TRACK":
        explanations.append("Combined recommendation: WAIT AND TRACK because the longer-window price opportunity is strong.")
        explanations.append("Suggested action: track the product during the waiting window and buy when the drop occurs, rather than waiting passively until day 30.")
    elif recommendation == "BUY_NOW":
        if price_zone == "confident_buy":
            explanations.append("Combined recommendation: BUY NOW because the model does not see a strong waiting opportunity.")
        else:
            explanations.append("Combined recommendation: BUY NOW because availability risk outweighs the uncertain price opportunity.")
        explanations.append("Suggested action: buying now is reasonable if this is a considered purchase.")
    else:
        explanations.append("Combined recommendation: UNCERTAIN because the model does not have enough confidence for a strong buy or wait decision.")
        explanations.append("Suggested action: monitor the price and return for a fresh recommendation when more data becomes available.")

    return explanations


def predict_recommendation(product_features: dict) -> dict:
    """
    Predict price-drop probabilities for 7, 14, and 30 days and return a
    combined recommendation using availability risk.
    """

    X = align_features(product_features)
    availability_result = calculate_availability_risk(product_features)

    horizon_predictions = {}

    for horizon in HORIZONS:
        model = MODELS[horizon]
        probability = float(model.predict_proba(X)[0, 1])
        price_zone = get_price_zone(probability, horizon)

        recommendation = combine_price_and_availability(
            price_zone=price_zone,
            availability_risk_level=availability_result["availability_risk_level"],
            horizon=horizon,
        )

        thresholds = get_product_thresholds(horizon)

        horizon_predictions[f"{horizon}d"] = {
            "horizon": horizon,
            "price_drop_probability": round(probability, 4),
            "price_zone": price_zone,
            "buy_threshold": thresholds["buy_threshold"],
            "wait_threshold": thresholds["wait_threshold"],
            "recommendation": recommendation,
            "explanation": build_horizon_explanation(
                probability=probability,
                horizon=horizon,
                price_zone=price_zone,
                availability_result=availability_result,
                final_recommendation=recommendation,
            ),
        }

    final_selection = choose_final_recommendation(horizon_predictions)
    selected_prediction = horizon_predictions[final_selection["selected_horizon_key"]]

    final_explanation = build_final_explanation(
        selected_prediction=selected_prediction,
        availability_result=availability_result,
    )

    return {
        "recommendation": final_selection["recommendation"],
        "best_horizon": final_selection["best_horizon"],
        "price_drop_probability": selected_prediction["price_drop_probability"],
        "price_zone": selected_prediction["price_zone"],
        "availability_risk_level": availability_result["availability_risk_level"],
        "availability_risk_score": availability_result["availability_risk_score"],
        "risk_flags": availability_result["risk_flags"],
        "horizon_predictions": horizon_predictions,
        "explanation": final_explanation,
    }