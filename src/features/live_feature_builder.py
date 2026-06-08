# src/features/live_feature_builder.py

from pathlib import Path
from typing import Any, Dict, Tuple, List, Optional

import json
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

V2_FEATURE_COLUMNS_PATH = PROJECT_ROOT / "models" / "v2_1" / "feature_columns.json"
MVP_FEATURE_COLUMNS_PATH = PROJECT_ROOT / "models" / "feature_columns.json"

FEATURE_COLUMNS_PATH = (
    V2_FEATURE_COLUMNS_PATH
    if V2_FEATURE_COLUMNS_PATH.exists()
    else MVP_FEATURE_COLUMNS_PATH
)

MIN_HISTORY_DAYS = 365
MIN_VALID_PRICE_DAYS = 200


def load_feature_columns() -> List[str]:
    with open(FEATURE_COLUMNS_PATH, "r") as f:
        return json.load(f)


FEATURE_COLUMNS = load_feature_columns()


def _series_from_keepa_data(data: dict, value_key: str, time_key: str) -> pd.DataFrame:
    values = data.get(value_key, [])
    times = data.get(time_key, [])

    if values is None:
        values = []

    if times is None:
        times = []

    values = list(values)
    times = list(times)

    if len(values) == 0 or len(times) == 0 or len(values) != len(times):
        return pd.DataFrame(columns=["date", value_key])

    temp = pd.DataFrame({
        "datetime": pd.to_datetime(times, errors="coerce"),
        value_key: pd.to_numeric(values, errors="coerce"),
    })

    temp = temp.dropna(subset=["datetime"])
    temp["date"] = temp["datetime"].dt.date
    temp["date"] = pd.to_datetime(temp["date"])

    temp = (
        temp.sort_values("datetime")
        .groupby("date", as_index=False)
        .tail(1)[["date", value_key]]
    )

    return temp


def _get_root_category(product: Dict[str, Any]) -> str:
    category_tree = product.get("categoryTree") or []

    if isinstance(category_tree, list) and len(category_tree) > 0:
        first = category_tree[0]

        if isinstance(first, dict):
            return first.get("name", "Unknown")

    return "Unknown"


def _get_product_image_url(product: Dict[str, Any]) -> Optional[str]:
    """
    Extract a product image URL from the Keepa product response.

    Preferred source:
        product["images"], using the large image filename if available.

    Fallback source:
        product["imagesCSV"], using the first image filename.
    """

    images = product.get("images")

    if isinstance(images, list) and len(images) > 0:
        first_image = images[0]

        if isinstance(first_image, dict):
            image_name = first_image.get("l") or first_image.get("m")

            if isinstance(image_name, str) and image_name.strip():
                return f"https://m.media-amazon.com/images/I/{image_name.strip()}"

    images_csv = product.get("imagesCSV")

    if isinstance(images_csv, str) and images_csv.strip():
        image_name = images_csv.split(",")[0].strip()

        if image_name:
            return f"https://m.media-amazon.com/images/I/{image_name}"

    image = product.get("image")

    if isinstance(image, str) and image.strip():
        image_name = image.strip()

        if image_name.startswith("http"):
            return image_name

        return f"https://m.media-amazon.com/images/I/{image_name}"

    return None


def _get_black_friday(year: int) -> pd.Timestamp:
    november_first = pd.Timestamp(year=year, month=11, day=1)
    thursdays = pd.date_range(november_first, periods=30, freq="D")
    thursdays = [d for d in thursdays if d.weekday() == 3]
    thanksgiving = thursdays[3]

    return thanksgiving + pd.Timedelta(days=1)


def _get_cyber_monday(year: int) -> pd.Timestamp:
    return _get_black_friday(year) + pd.Timedelta(days=3)


def _get_christmas(year: int) -> pd.Timestamp:
    return pd.Timestamp(year=year, month=12, day=25)


def _days_until_event(date: pd.Timestamp, event_func) -> int:
    event = event_func(date.year)

    if date > event:
        event = event_func(date.year + 1)

    return int((event - date).days)


def _build_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df["month"] = df["date"].dt.month
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.dayofweek

    df["days_until_black_friday"] = df["date"].apply(
        lambda d: _days_until_event(d, _get_black_friday)
    )
    df["days_until_cyber_monday"] = df["date"].apply(
        lambda d: _days_until_event(d, _get_cyber_monday)
    )
    df["days_until_christmas"] = df["date"].apply(
        lambda d: _days_until_event(d, _get_christmas)
    )

    df["is_black_friday_period"] = (df["days_until_black_friday"] <= 7).astype(int)
    df["is_cyber_monday_period"] = (df["days_until_cyber_monday"] <= 7).astype(int)
    df["is_christmas_period"] = (df["days_until_christmas"] <= 14).astype(int)

    return df


def _build_price_history_for_frontend(
    df: pd.DataFrame,
    days: int = 90,
) -> List[Dict[str, Any]]:
    recent = df.tail(days)[["date", "amazon_price"]].copy()
    recent = recent.dropna(subset=["amazon_price"])

    return [
        {
            "date": row["date"].strftime("%Y-%m-%d"),
            "price": round(float(row["amazon_price"]), 2),
        }
        for _, row in recent.iterrows()
    ]


def build_live_features_from_keepa(
    product: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Build one model-ready feature dictionary from a live Keepa product response.
    """

    asin = product.get("asin")
    title = product.get("title", "")
    brand = product.get("brand", "")
    root_category = _get_root_category(product)
    image_url = _get_product_image_url(product)

    data = product.get("data") or {}

    amazon_df = _series_from_keepa_data(data, "AMAZON", "AMAZON_time")
    new_df = _series_from_keepa_data(data, "NEW", "NEW_time")
    sales_df = _series_from_keepa_data(data, "SALES", "SALES_time")
    count_new_df = _series_from_keepa_data(data, "COUNT_NEW", "COUNT_NEW_time")

    available_dates = []

    for temp_df in [amazon_df, new_df, sales_df, count_new_df]:
        if not temp_df.empty:
            available_dates.extend(temp_df["date"].tolist())

    if not available_dates:
        raise ValueError("Not enough Keepa history was found for this product.")

    start_date = min(available_dates)
    end_date = max(available_dates)

    history_days = (end_date - start_date).days

    if history_days < MIN_HISTORY_DAYS:
        raise ValueError(
            f"Not enough price history for reliable prediction. "
            f"Found {history_days} days, but at least {MIN_HISTORY_DAYS} days are required."
        )

    daily = pd.DataFrame({"date": pd.date_range(start_date, end_date, freq="D")})

    for temp_df in [amazon_df, new_df, sales_df, count_new_df]:
        if not temp_df.empty:
            daily = daily.merge(temp_df, on="date", how="left")

    if "AMAZON" not in daily.columns:
        daily["AMAZON"] = np.nan

    if "NEW" not in daily.columns:
        daily["NEW"] = np.nan

    if "SALES" not in daily.columns:
        daily["SALES"] = np.nan

    if "COUNT_NEW" not in daily.columns:
        daily["COUNT_NEW"] = np.nan

    daily["amazon_price_raw_missing"] = daily["AMAZON"].isna().astype(int)

    daily["amazon_price_raw_ffill"] = daily["AMAZON"].ffill(limit=14)
    daily["new_price_raw_ffill"] = daily["NEW"].ffill(limit=14)
    daily["sales_rank"] = daily["SALES"].ffill(limit=7)
    daily["offer_count"] = daily["COUNT_NEW"].ffill(limit=14)

    daily["amazon_price"] = np.where(
        daily["amazon_price_raw_ffill"].notna(),
        daily["amazon_price_raw_ffill"],
        daily["new_price_raw_ffill"],
    )

    daily["price_source"] = pd.Series(pd.NA, index=daily.index, dtype="object")
    daily.loc[daily["new_price_raw_ffill"].notna(), "price_source"] = "NEW"
    daily.loc[daily["amazon_price_raw_ffill"].notna(), "price_source"] = "AMAZON"

    daily["price_source_amazon"] = (daily["price_source"] == "AMAZON").astype(int)

    valid_price_days = daily["amazon_price"].notna().sum()

    if valid_price_days < MIN_VALID_PRICE_DAYS:
        raise ValueError(
            f"Not enough valid price observations for reliable prediction. "
            f"Found {valid_price_days}, but at least {MIN_VALID_PRICE_DAYS} are required."
        )

    for lag in [1, 7, 14, 30]:
        daily[f"price_lag_{lag}"] = daily["amazon_price"].shift(lag)

    for window in [7, 14, 30]:
        daily[f"price_rolling_mean_{window}"] = (
            daily["amazon_price"].shift(1).rolling(window).mean()
        )
        daily[f"price_rolling_std_{window}"] = (
            daily["amazon_price"].shift(1).rolling(window).std()
        )

    for lag in [7, 14, 30]:
        daily[f"price_pct_change_{lag}"] = (
            (daily["amazon_price"] - daily[f"price_lag_{lag}"])
            / daily[f"price_lag_{lag}"]
        )

    daily["price_vs_rolling_mean_30"] = (
        (daily["amazon_price"] - daily["price_rolling_mean_30"])
        / daily["price_rolling_mean_30"]
    )

    daily["sales_rank_lag_7"] = daily["sales_rank"].shift(7)
    daily["sales_rank_rolling_mean_14"] = daily["sales_rank"].shift(1).rolling(14).mean()
    daily["sales_rank_velocity_14"] = (
        (daily["sales_rank"] - daily["sales_rank"].shift(14))
        / daily["sales_rank"].shift(14)
    )
    daily["sales_rank_missing_flag"] = daily["sales_rank"].isna().astype(int)

    daily["offer_count_lag_7"] = daily["offer_count"].shift(7)
    daily["offer_count_rolling_mean_14"] = (
        daily["offer_count"].shift(1).rolling(14).mean()
    )
    daily["offer_count_trend_14"] = daily["offer_count"] - daily["offer_count"].shift(14)
    daily["offer_count_missing_flag"] = daily["offer_count"].isna().astype(int)

    daily["amazon_price_raw_missing_rolling_14"] = (
        daily["amazon_price_raw_missing"].shift(1).rolling(14).mean()
    )

    daily["price_source_changed"] = (
        daily["price_source"] != daily["price_source"].shift(1)
    ).astype(int)

    daily["price_source_changed_7d"] = (
        daily["price_source_changed"].shift(1).rolling(7).max()
    )

    daily["new_price_shipping_included"] = (
        (daily["price_source"] == "NEW")
        & (daily["date"] >= pd.Timestamp("2026-02-16"))
    ).astype(int)

    daily = _build_calendar_features(daily)

    category_columns = [
        "root_category_Appliances",
        "root_category_Electronics",
        "root_category_Home & Kitchen",
        "root_category_Sports & Outdoors",
        "root_category_Tools & Home Improvement",
        "root_category_Toys & Games",
    ]

    for col in category_columns:
        category_name = col.replace("root_category_", "")
        daily[col] = int(root_category == category_name)

    usable = daily.dropna(subset=["amazon_price"]).copy()

    if usable.empty:
        raise ValueError("No usable final price row was available after feature construction.")

    latest_row = usable.iloc[-1].to_dict()

    feature_dict = {}

    for col in FEATURE_COLUMNS:
        value = latest_row.get(col, np.nan)

        if pd.isna(value):
            feature_dict[col] = np.nan
        elif isinstance(value, np.integer):
            feature_dict[col] = int(value)
        elif isinstance(value, np.floating):
            feature_dict[col] = float(value)
        else:
            feature_dict[col] = value

    feature_dict["asin"] = asin
    feature_dict["title"] = title
    feature_dict["brand"] = brand
    feature_dict["root_category"] = root_category
    feature_dict["image_url"] = image_url
    feature_dict["latest_date"] = latest_row["date"].strftime("%Y-%m-%d")

    price_history = _build_price_history_for_frontend(usable, days=90)

    metadata = {
        "asin": asin,
        "title": title,
        "brand": brand,
        "root_category": root_category,
        "image_url": image_url,
        "history_start": start_date.strftime("%Y-%m-%d"),
        "history_end": end_date.strftime("%Y-%m-%d"),
        "history_days": int(history_days),
        "valid_price_days": int(valid_price_days),
        "latest_price": round(float(latest_row["amazon_price"]), 2),
        "latest_date": latest_row["date"].strftime("%Y-%m-%d"),
    }

    return feature_dict, price_history, metadata