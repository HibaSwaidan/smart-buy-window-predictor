"""
reprocess_raw.py

This script processes the V2 raw Keepa JSON files for the Smart Buy Window Predictor project.

It reads raw product JSON files from:  data/raw/v2_raw/

It extracts and cleans:
    - AMAZON direct price history
    - NEW lowest new-offer price history
    - selected modelling price using AMAZON first, then NEW
    - row-level price_source
    - sales rank history
    - new offer count history
    - Amazon direct availability status
    - Amazon availability delay where available
    - monthly_sold, which represents Amazon's bought-in-past-month signal
    - brand, manufacturer, root category, and leaf category metadata

It applies:
    - daily resampling
    - price validity filtering between $1 and $2,000
    - forward filling with limits
    - ASIN-level quality filters

It saves the final cleaned V2 dataset to: data/processed/clean_data_v2.csv
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path


# ── paths ─────────────────────────────────────────────────────────────────────
INPUT_DIR = Path("data/raw/v2_raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "clean_data_v2.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── quality filter thresholds ─────────────────────────────────────────────────
MIN_HISTORY_DAYS = 365
MIN_VALID_ROWS = 200
MAX_MISSING_PCT = 0.60
MIN_PRICE_STD = 0.5


# ── price validity range ──────────────────────────────────────────────────────
PRICE_MIN = 1.0
PRICE_MAX = 2000.0


# ── forward-fill limits ───────────────────────────────────────────────────────
FFILL_LIMIT_PRICE = 14
FFILL_LIMIT_RANK = 7


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def series_from_field(data, field):
    """
    Extract a named time-series field from the product's data dict.

    Time fields are date strings, for example:
        '2021-03-12 10:08:00'

    Raw timestamps include hours and minutes, so the series is resampled to
    daily frequency using the last observed value per day.
    """
    values = data.get(field)
    times = data.get(f"{field}_time")

    if not values or not times:
        return pd.Series(dtype=float)

    min_len = min(len(values), len(times))

    s = pd.Series(
        values[:min_len],
        index=pd.to_datetime(
            times[:min_len],
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce"
        ),
        dtype=float
    )

    s = s[s.index.notna()]
    s = s.sort_index()
    s = s[~s.index.duplicated(keep="last")]
    s = s.resample("D").last()

    return s


def clean_price(s):
    """
    Clean a raw price series.

    Rules:
    - Replace values <= 0 with NaN.
    - Remove prices below $1 or above $2,000.
    - Do not divide by 100 because raw exploration confirmed prices are already in dollars.
    """
    s = s.copy()
    s[s <= 0] = np.nan
    s[(s < PRICE_MIN) | (s > PRICE_MAX)] = np.nan
    return s


def availability_label(value):
    """
    Map Keepa availabilityAmazon codes to readable labels.

    Keepa mapping:
    -1 = no Amazon offer exists
     0 = Amazon offer is in stock and shippable
     1 = Amazon offer is currently not in stock but preorderable
     2 = Amazon offer availability is unknown
     3 = Amazon offer is currently not in stock but backorderable
     4 = Amazon offer availability is delayed
    """
    mapping = {
        -1: "NO_OFFER",
        0: "NOW",
        1: "PREORDERABLE",
        2: "UNKNOWN",
        3: "BACKORDERABLE",
        4: "DELAYED",
    }

    if pd.isna(value):
        return "UNKNOWN"

    return mapping.get(int(value), "UNKNOWN")


def extract_availability_delay(product):
    """
    Extract availabilityAmazonDelay if available.

    Keepa stores this as two values:
    - minimum shipping delay in hours
    - maximum shipping delay in hours
    """
    delay = product.get("availabilityAmazonDelay")

    if isinstance(delay, list) and len(delay) >= 2:
        return delay[0], delay[1]

    return np.nan, np.nan


# ─────────────────────────────────────────────────────────────────────────────
# Per-ASIN processing
# ─────────────────────────────────────────────────────────────────────────────

def process_json(json_path: Path):
    """
    Load one raw JSON file and return a cleaned daily DataFrame.

    Returns None if no usable price data exists.
    Quality filters are applied later on the combined dataset.
    """
    with open(json_path, encoding="utf-8") as f:
        product = json.load(f)

    asin = product.get("asin", json_path.stem.replace("_raw", ""))
    data = product.get("data") or {}

    # Raw price series
    amazon_raw = clean_price(series_from_field(data, "AMAZON"))
    new_raw = clean_price(series_from_field(data, "NEW"))

    if amazon_raw.empty and new_raw.empty:
        return None

    # Build shared daily index from price series
    all_price = [s for s in [amazon_raw, new_raw] if not s.empty]

    p_min = min(s.index.min() for s in all_price)
    p_max = max(s.index.max() for s in all_price)

    daily_index = pd.date_range(p_min, p_max, freq="D")

    amazon_aligned = amazon_raw.reindex(daily_index)
    new_aligned = new_raw.reindex(daily_index)

    # Row-level selected price
    # Use AMAZON where valid, otherwise NEW, otherwise NaN.
    selected_price = amazon_aligned.where(amazon_aligned.notna(), new_aligned)

    if selected_price.dropna().empty:
        return None

    # Row-level price source label
    # Computed before forward fill, then carried forward with the price.
    price_source = pd.Series(index=daily_index, dtype="object")
    price_source[new_aligned.notna()] = "NEW"
    price_source[amazon_aligned.notna()] = "AMAZON"

    # Other time series
    sales_rank = series_from_field(data, "SALES")
    sales_rank[sales_rank <= 0] = np.nan

    offer_count = series_from_field(data, "COUNT_NEW")
    offer_count[offer_count < 0] = np.nan

    # Extend daily index to cover all series
    all_series = [selected_price, sales_rank, offer_count]
    all_series = [s for s in all_series if not s.empty]

    full_min = min(s.index.min() for s in all_series)
    full_max = max(s.index.max() for s in all_series)

    full_index = pd.date_range(full_min, full_max, freq="D")

    def reindex(s):
        if s.empty:
            return pd.Series(np.nan, index=full_index)
        return s.reindex(full_index)

    selected_price = reindex(selected_price)
    amazon_aligned = reindex(amazon_aligned)
    new_aligned = reindex(new_aligned)
    price_source = reindex(price_source)
    sales_rank = reindex(sales_rank)
    offer_count = reindex(offer_count)

    # Computed after full reindex so it reflects raw AMAZON gaps on each calendar day.
    amazon_price_raw_missing = amazon_aligned.isna().astype(float)

    # Forward fill
    selected_price = selected_price.ffill(limit=FFILL_LIMIT_PRICE)
    amazon_aligned = amazon_aligned.ffill(limit=FFILL_LIMIT_PRICE)
    new_aligned = new_aligned.ffill(limit=FFILL_LIMIT_PRICE)
    price_source = price_source.ffill(limit=FFILL_LIMIT_PRICE)
    sales_rank = sales_rank.ffill(limit=FFILL_LIMIT_RANK)
    offer_count = offer_count.ffill(limit=FFILL_LIMIT_RANK)

    # Assemble DataFrame
    df = pd.DataFrame(
        {
            "amazon_price": selected_price,
            "amazon_price_raw": amazon_aligned,
            "new_price_raw": new_aligned,
            "price_source": price_source,
            "amazon_price_raw_missing": amazon_price_raw_missing,
            "sales_rank": sales_rank,
            "offer_count": offer_count,
        },
        index=full_index
    )

    df = df[df.index >= "2015-01-01"]
    df.index.name = "date"

    # Scalar metadata
    cat_tree = product.get("categoryTree") or []

    avail_val = product.get("availabilityAmazon")
    availability_amazon = int(avail_val) if avail_val is not None else np.nan
    availability_amazon_label = availability_label(availability_amazon)

    delay_min, delay_max = extract_availability_delay(product)

    ms_val = product.get("monthlySold")
    monthly_sold = float(ms_val) if (ms_val is not None and ms_val != -1) else np.nan

    df["asin"] = asin
    df["title"] = product.get("title", "")
    df["brand"] = product.get("brand", "")
    df["manufacturer"] = product.get("manufacturer", "")
    df["root_category"] = cat_tree[0]["name"] if cat_tree else "Unknown"
    df["leaf_category"] = cat_tree[-1]["name"] if cat_tree else "Unknown"

    df["availability_amazon"] = availability_amazon
    df["availability_amazon_label"] = availability_amazon_label
    df["availability_delay_min_hours"] = delay_min
    df["availability_delay_max_hours"] = delay_max

    df["monthly_sold"] = monthly_sold

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    json_files = sorted(INPUT_DIR.glob("*_raw.json"))

    print(f"Found {len(json_files)} raw JSON files\n")

    all_dfs = []
    skipped = 0

    for i, jf in enumerate(json_files):
        try:
            df = process_json(jf)

            if df is not None:
                all_dfs.append(df)
            else:
                skipped += 1

        except Exception as e:
            print(f"  ERROR {jf.name}: {e}")
            skipped += 1

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(json_files)} — collected {len(all_dfs)} so far")

    print(f"\nCollected: {len(all_dfs)} ASINs before quality filters")
    print(f"Skipped (no price / error): {skipped}")

    if not all_dfs:
        print("No data collected.")
        exit()

    # Quality filters applied on combined data
    combined = pd.concat(all_dfs)
    combined.index.name = "date"

    combined_reset = combined.reset_index()

    asin_stats = combined_reset.groupby("asin").agg(
        valid_rows=("amazon_price", lambda x: x.notna().sum()),
        missing_pct=("amazon_price", lambda x: x.isna().mean()),
        price_std=("amazon_price", "std"),
        first_date=("date", "min"),
        last_date=("date", "max"),
    ).reset_index()

    asin_stats["history_days"] = (
        asin_stats["last_date"] - asin_stats["first_date"]
    ).dt.days

    mask = (
        (asin_stats["history_days"] >= MIN_HISTORY_DAYS)
        & (asin_stats["valid_rows"] >= MIN_VALID_ROWS)
        & (asin_stats["missing_pct"] <= MAX_MISSING_PCT)
        & (asin_stats["price_std"] >= MIN_PRICE_STD)
    )

    print("\nQuality filter results:")
    print(f"  Passed:                    {mask.sum()}")
    print(f"  Dropped (any reason):      {(~mask).sum()}")
    print(f"  History < {MIN_HISTORY_DAYS} days:       {(asin_stats['history_days'] < MIN_HISTORY_DAYS).sum()}")
    print(f"  Valid rows < {MIN_VALID_ROWS}:         {(asin_stats['valid_rows'] < MIN_VALID_ROWS).sum()}")
    print(f"  Missing > {int(MAX_MISSING_PCT * 100)}%:            {(asin_stats['missing_pct'] > MAX_MISSING_PCT).sum()}")
    print(f"  Price std < {MIN_PRICE_STD}:           {(asin_stats['price_std'] < MIN_PRICE_STD).sum()}")

    good_asins = asin_stats[mask]["asin"].tolist()

    clean = combined[combined["asin"].isin(good_asins)].copy()
    clean = clean[clean["amazon_price"].notna()]

    print("\nFinal dataset:")
    print(f"  Shape:       {clean.shape}")
    print(f"  ASINs:       {clean['asin'].nunique()}")
    print(f"  Date range:  {clean.index.min()} to {clean.index.max()}")
    print(f"  Price range: ${clean['amazon_price'].min():.2f} – ${clean['amazon_price'].max():.2f}")
    print(f"  Avg price:   ${clean['amazon_price'].mean():.2f}")

    print("\nprice_source distribution:")
    print(clean["price_source"].value_counts(dropna=False))

    print("\navailability_amazon distribution:")
    print(clean["availability_amazon"].value_counts(dropna=False))

    print("\navailability_amazon_label distribution:")
    print(clean["availability_amazon_label"].value_counts(dropna=False))

    print("\nroot_category distribution:")
    print(clean.groupby("root_category")["asin"].nunique().sort_values(ascending=False))

    print("\nMissing % per column:")
    print((clean.isnull().mean() * 100).round(2).to_string())

    clean.to_csv(OUTPUT_FILE)

    print(f"\nSaved: {OUTPUT_FILE}")