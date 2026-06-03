import pandas as pd
import numpy as np
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────
RAW_FILE        = "data/raw/all_asins_daily.csv"
OUTPUT_FILE     = "data/processed/clean_data.csv"
INTERIM_FILE    = "data/interim/ffill_data.csv"

MIN_HISTORY_DAYS   = 365    # at least 1 year of data
MIN_VALID_ROWS     = 200    # at least 200 non-null prices after filling
MAX_MISSING_PCT    = 0.60   # drop ASINs still >60% missing after ffill
MIN_PRICE          = 5.0    # remove obvious data errors
MAX_PRICE          = 2000.0 # remove obvious data errors
MIN_PRICE_STD      = 0.5    # remove completely flat-price products
FFILL_LIMIT        = 14     # forward fill max 14 days gap

Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("data/interim").mkdir(parents=True, exist_ok=True)

# ── Step 1: Load ─────────────────────────────────────────────────
print("Step 1: Loading data...")
df = pd.read_csv(RAW_FILE, parse_dates=['date'])
print(f"  Raw shape: {df.shape}")
print(f"  ASINs: {df['asin'].nunique()}")

# ── Step 2: Remove obvious price errors ──────────────────────────
print("\nStep 2: Removing price errors...")
before = len(df)
df.loc[df['amazon_price'] < MIN_PRICE, 'amazon_price'] = np.nan
df.loc[df['amazon_price'] > MAX_PRICE, 'amazon_price'] = np.nan
print(f"  Rows with price errors nulled: {before - df['amazon_price'].notna().sum()}")

# ── Step 3: Forward fill within each ASIN ────────────────────────
print("\nStep 3: Forward filling missing prices (max 14 days)...")
df = df.sort_values(['asin', 'date'])
df['amazon_price'] = df.groupby('asin')['amazon_price'].transform(
    lambda x: x.ffill(limit=FFILL_LIMIT)
)
df.to_csv(INTERIM_FILE, index=False)
print(f"  Saved interim file: {INTERIM_FILE}")

# ── Step 4: Filter ASINs by quality ──────────────────────────────
print("\nStep 4: Filtering ASINs by quality...")

asin_stats = df.groupby('asin').agg(
    total_rows     = ('amazon_price', 'count'),
    valid_rows     = ('amazon_price', lambda x: x.notna().sum()),
    missing_pct    = ('amazon_price', lambda x: x.isna().mean()),
    price_std      = ('amazon_price', 'std'),
    price_min      = ('amazon_price', 'min'),
    price_max      = ('amazon_price', 'max'),
    first_date     = ('date', 'min'),
    last_date      = ('date', 'max'),
).reset_index()

asin_stats['history_days'] = (asin_stats['last_date'] - asin_stats['first_date']).dt.days

# Apply filters
mask = (
    (asin_stats['history_days']  >= MIN_HISTORY_DAYS) &
    (asin_stats['valid_rows']    >= MIN_VALID_ROWS)   &
    (asin_stats['missing_pct']   <= MAX_MISSING_PCT)  &
    (asin_stats['price_std']     >= MIN_PRICE_STD)
)

good_asins = asin_stats[mask]['asin'].tolist()
dropped    = asin_stats[~mask]

print(f"  ASINs passing all filters: {len(good_asins)}")
print(f"  ASINs dropped: {len(dropped)}")
print(f"\n  Drop reasons:")
print(f"    History < {MIN_HISTORY_DAYS} days:  {(asin_stats['history_days'] < MIN_HISTORY_DAYS).sum()}")
print(f"    Valid rows < {MIN_VALID_ROWS}:       {(asin_stats['valid_rows'] < MIN_VALID_ROWS).sum()}")
print(f"    Missing > {MAX_MISSING_PCT*100:.0f}%:          {(asin_stats['missing_pct'] > MAX_MISSING_PCT).sum()}")
print(f"    Price std < {MIN_PRICE_STD}:         {(asin_stats['price_std'] < MIN_PRICE_STD).sum()}")

# ── Step 5: Keep only good ASINs ─────────────────────────────────
print("\nStep 5: Filtering dataframe to good ASINs...")
df_clean = df[df['asin'].isin(good_asins)].copy()

# Drop rows before first valid price per ASIN
df_clean = df_clean[df_clean['amazon_price'].notna()]

print(f"  Clean shape: {df_clean.shape}")
print(f"  Clean ASINs: {df_clean['asin'].nunique()}")

# ── Step 6: Save ─────────────────────────────────────────────────
print("\nStep 6: Saving clean data...")
df_clean.to_csv(OUTPUT_FILE, index=False)
print(f"  Saved: {OUTPUT_FILE}")

# ── Step 7: Summary ──────────────────────────────────────────────
print("\n── Summary ──────────────────────────────────────────────")
print(f"  Raw ASINs:         {df['asin'].nunique()}")
print(f"  Clean ASINs:       {df_clean['asin'].nunique()}")
print(f"  Total rows:        {len(df_clean):,}")
print(f"  Date range:        {df_clean['date'].min()} to {df_clean['date'].max()}")
print(f"  Price range:       ${df_clean['amazon_price'].min():.2f} – ${df_clean['amazon_price'].max():.2f}")
print(f"  Avg price:         ${df_clean['amazon_price'].mean():.2f}")

print("\nCategory distribution after cleaning:")
print(df_clean.groupby('category')['asin'].nunique().sort_values(ascending=False).head(15))