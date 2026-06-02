import json
import numpy as np
import pandas as pd
from pathlib import Path

# =========================
# Configuration
# =========================

INPUT_DIR   = Path("data/raw/v2_raw")
OUTPUT_DIR  = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "clean_data_v2.csv"

MIN_HISTORY_DAYS  = 365
MIN_VALID_ROWS    = 200
MAX_MISSING_PCT   = 0.60
MIN_PRICE_STD     = 0.5
FFILL_LIMIT_PRICE = 14
FFILL_LIMIT_RANK  = 7

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# Processing functions
# =========================

def series_from_field(data, field):
    """Convert a keepa library data field to a dated Series."""
    values = data.get(field)
    times  = data.get(f"{field}_time")
    if not values or not times:
        return pd.Series(dtype=float)
    min_len = min(len(values), len(times))
    s = pd.Series(
        values[:min_len],
        index=pd.to_datetime(times[:min_len]),
        dtype=float
    )
    s = s[~s.index.duplicated(keep='last')]
    return s


def process_json(json_path: Path):
    with open(json_path, encoding="utf-8") as f:
        product = json.load(f)

    asin = product.get("asin", "")
    data = product.get("data") or {}

    # Price priority: AMAZON → NEW_FBA → NEW → BUY_BOX_SHIPPING
    price_series = None
    price_source = None
    for field in ["AMAZON", "NEW_FBA", "NEW", "BUY_BOX_SHIPPING"]:
        s = series_from_field(data, field)
        s[s <= 0] = np.nan
        if s.dropna().shape[0] > 10:
            price_series = s
            price_source = field
            break

    if price_series is None:
        return None

    # Out of stock flag — extract BEFORE removing negatives
    raw_field = series_from_field(data, price_source)
    oos_series = (raw_field == -1).astype(int)

    # Sales rank
    sales_rank = series_from_field(data, "SALES")
    sales_rank[sales_rank <= 0] = np.nan

    # Offer count
    offer_count = series_from_field(data, "COUNT_NEW")
    offer_count[offer_count < 0] = np.nan

    # Rating (convert 0-50 to 0-5)
    rating = series_from_field(data, "RATING")
    rating = rating / 10
    rating[rating <= 0] = np.nan

    # Review count
    review_count = series_from_field(data, "COUNT_REVIEWS")
    review_count[review_count < 0] = np.nan

    # Combine into daily DataFrame
    df = pd.DataFrame({
        "amazon_price":    price_series,
        "is_out_of_stock": oos_series,
        "sales_rank":      sales_rank,
        "offer_count":     offer_count,
        "rating":          rating,
        "review_count":    review_count,
    })

    df.index = pd.to_datetime(df.index)
    df = df[~df.index.duplicated(keep='last')]
    df = df.resample("D").last()

    # Forward fill
    df["amazon_price"]  = df["amazon_price"].ffill(limit=FFILL_LIMIT_PRICE)
    df["sales_rank"]    = df["sales_rank"].ffill(limit=FFILL_LIMIT_RANK)
    df["offer_count"]   = df["offer_count"].ffill(limit=FFILL_LIMIT_RANK)
    df["rating"]        = df["rating"].ffill()
    df["review_count"]  = df["review_count"].ffill()
    # is_out_of_stock: no fill

    df = df[df.index >= "2015-01-01"]
    df.index.name = "date"

    if df["amazon_price"].dropna().empty:
        return None

    # Metadata
    cat_tree = product.get("categoryTree") or []
    df["asin"]         = asin
    df["title"]        = product.get("title", "")
    df["brand"]        = product.get("brand", "")
    df["price_source"] = price_source
    df["category"]     = cat_tree[-1]["name"] if cat_tree else ""

    return df


# =========================
# Main
# =========================

if __name__ == "__main__":
    json_files = sorted(INPUT_DIR.glob("*_raw.json"))
    print(f"Found {len(json_files)} raw JSON files\n")

    all_dfs = []
    skipped = 0

    for i, jf in enumerate(json_files):
        try:
            df = process_json(jf)
            if df is not None:
                valid_rows = df["amazon_price"].notna().sum()
                pmin = df["amazon_price"].min()
                pmax = df["amazon_price"].max()
                asin = df["asin"].iloc[0]
                print(f"  [{i+1}/{len(json_files)}] {asin}: {valid_rows} rows, ${pmin:.2f}–${pmax:.2f}")
                all_dfs.append(df)
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR {jf.name}: {e}")
            skipped += 1

    print(f"\nProcessed: {len(all_dfs)} ASINs")
    print(f"Skipped:   {skipped} ASINs")

    if not all_dfs:
        print("No data collected.")
        exit()

    combined = pd.concat(all_dfs)
    combined.index.name = "date"

    print(f"\nRaw combined shape: {combined.shape}")
    print(f"Raw ASINs: {combined['asin'].nunique()}")

    # Quality filters
    print("\nApplying quality filters...")

    combined_reset = combined.reset_index()

    asin_stats = combined_reset.groupby("asin").agg(
        valid_rows  = ("amazon_price", lambda x: x.notna().sum()),
        missing_pct = ("amazon_price", lambda x: x.isna().mean()),
        price_std   = ("amazon_price", "std"),
        first_date  = ("date", "min"),
        last_date   = ("date", "max"),
    ).reset_index()

    asin_stats["history_days"] = (
        asin_stats["last_date"] - asin_stats["first_date"]
    ).dt.days

    mask = (
        (asin_stats["history_days"] >= MIN_HISTORY_DAYS) &
        (asin_stats["valid_rows"]   >= MIN_VALID_ROWS)   &
        (asin_stats["missing_pct"]  <= MAX_MISSING_PCT)  &
        (asin_stats["price_std"]    >= MIN_PRICE_STD)
    )

    good_asins = asin_stats[mask]["asin"].tolist()

    print(f"ASINs passing filters: {len(good_asins)}")
    print(f"ASINs dropped:         {(~mask).sum()}")
    print(f"  History < {MIN_HISTORY_DAYS} days:  {(asin_stats['history_days'] < MIN_HISTORY_DAYS).sum()}")
    print(f"  Valid rows < {MIN_VALID_ROWS}:       {(asin_stats['valid_rows'] < MIN_VALID_ROWS).sum()}")
    print(f"  Missing > {MAX_MISSING_PCT*100:.0f}%:          {(asin_stats['missing_pct'] > MAX_MISSING_PCT).sum()}")
    print(f"  Price std < {MIN_PRICE_STD}:         {(asin_stats['price_std'] < MIN_PRICE_STD).sum()}")

    clean = combined[combined["asin"].isin(good_asins)].copy()
    clean = clean[clean["amazon_price"].notna()]

    print(f"\nClean shape: {clean.shape}")
    print(f"Clean ASINs: {clean['asin'].nunique()}")
    print(f"Date range:  {clean.index.min()} to {clean.index.max()}")
    print(f"Price range: ${clean['amazon_price'].min():.2f} – ${clean['amazon_price'].max():.2f}")
    print(f"Avg price:   ${clean['amazon_price'].mean():.2f}")

    print(f"\nCategory distribution (top 15):")
    print(clean.groupby("category")["asin"].nunique().sort_values(ascending=False).head(15))

    clean.to_csv(OUTPUT_FILE)
    print(f"\nSaved: {OUTPUT_FILE}")