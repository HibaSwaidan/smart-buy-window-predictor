import json
import pandas as pd
from pathlib import Path

KEEPA_EPOCH = pd.Timestamp("2011-01-01")

def keepa_minutes_to_datetime(minutes):
    return KEEPA_EPOCH + pd.to_timedelta(minutes, unit='m')

def extract_price_series(csv_data, field_index):
    """Extract price series from raw Keepa csv field."""
    if field_index >= len(csv_data) or not csv_data[field_index]:
        return pd.Series(dtype=float)
    field = csv_data[field_index]
    if len(field) < 2:
        return pd.Series(dtype=float)
    times = field[0::2]
    values = field[1::2]
    # Ensure equal length
    min_len = min(len(times), len(values))
    times = times[:min_len]
    values = values[:min_len]
    index = [keepa_minutes_to_datetime(t) for t in times]
    s = pd.Series(values, index=index, dtype=float)
    s = s[~s.index.duplicated(keep='last')]
    s[s <= 0] = None
    return s / 100  # convert cents to dollars

def reprocess_asin(json_path):
    with open(json_path) as f:
        raw = json.load(f)
    
    products = raw.get('products', [])
    if not products:
        return None
    
    product = products[0]
    asin = product.get('asin', '')
    csv = product.get('csv') or []

    # Priority: Buy Box (index 18) → Amazon (index 0) → New (index 1)
    price_series = extract_price_series(csv, 18)  # Buy Box
    if price_series.dropna().empty:
        price_series = extract_price_series(csv, 0)  # Amazon
    if price_series.dropna().empty:
        price_series = extract_price_series(csv, 1)  # New
    if price_series.dropna().empty:
        print(f"  SKIPPED {asin}: no price data")
        return None

    df = pd.DataFrame({'amazon_price': price_series})
    df.index = pd.to_datetime(df.index)
    df = df[~df.index.duplicated(keep='last')]
    
    # Forward fill gaps up to 14 days max
    df = df.resample('D').last()
    df['amazon_price'] = df['amazon_price'].ffill(limit=14)
    df = df[df.index >= '2015-01-01']
    df.index.name = 'date'

    if df['amazon_price'].dropna().empty:
        print(f"  SKIPPED {asin}: empty after processing")
        return None

    df['asin'] = asin
    df['title'] = product.get('title', '')
    df['brand'] = product.get('brand', '')
    cat_tree = product.get('categoryTree', [])
    df['category'] = cat_tree[-1]['name'] if cat_tree else ''

    valid_rows = df['amazon_price'].notna().sum()
    pmin = df['amazon_price'].min()
    pmax = df['amazon_price'].max()
    print(f"  {asin}: {valid_rows} valid rows, ${pmin:.2f}–${pmax:.2f} | {product.get('title','')[:50]}")
    return df

if __name__ == "__main__":
    raw_dir = Path("data/raw")
    json_files = list(raw_dir.glob("*_raw.json"))
    print(f"Found {len(json_files)} raw JSON files\n")

    all_dfs = []
    for json_path in json_files:
        df = reprocess_asin(json_path)
        if df is not None:
            all_dfs.append(df)

    if all_dfs:
        combined = pd.concat(all_dfs)
        combined.to_csv("data/raw/all_asins_daily_v2.csv")
        print(f"\nDone. Shape: {combined.shape}")
        print(f"Total ASINs: {combined['asin'].nunique()}")
        
        # Check missing data improvement
        missing = combined.groupby('asin')['amazon_price'].apply(
            lambda x: x.isna().mean() * 100
        )
        print(f"\nASINs with <20% missing: {(missing < 20).sum()}")
        print(f"ASINs with <50% missing: {(missing < 50).sum()}")
        print(f"ASINs with >80% missing: {(missing > 80).sum()}")
    else:
        print("No data.")