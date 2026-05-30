import keepa
import pandas as pd
import os
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
API_KEY = os.getenv("KEEPA_API_KEY")

# Target category names we want (matched against Keepa's root categories)
TARGET_CATEGORIES = [
    "Electronics",
    "Home & Kitchen",
    "Toys & Games",
    "Tools & Home Improvement",
    "Sports & Outdoors",
    "Baby",
]

def get_target_category_ids(api):
    """Get category IDs by looking up all root categories — costs no tokens."""
    print("Looking up root categories (free, no tokens used)...")
    all_categories = api.category_lookup(0)  # 0 = return all root categories
    
    matched = {}
    for cat_id, cat_data in all_categories.items():
        name = cat_data.get('name', '')
        for target in TARGET_CATEGORIES:
            if target.lower() in name.lower():
                matched[target] = cat_id
                print(f"  Matched '{target}' -> '{name}' (id={cat_id})")
                break

    print(f"  Found {len(matched)}/{len(TARGET_CATEGORIES)} target categories")
    return matched

def get_bestseller_asins(api, category_ids, limit_per_category=30):
    """Pull bestseller ASINs for each category."""
    all_asins = []
    for name, cat_id in category_ids.items():
        print(f"Fetching bestsellers for {name} (id={cat_id})...")
        try:
            asins = api.best_sellers_query(str(cat_id), domain='US')
            asins = list(asins[:limit_per_category])
            print(f"  Got {len(asins)} ASINs")
            all_asins.extend(asins)
        except Exception as e:
            print(f"  Failed: {e}")
        time.sleep(5)

    all_asins = list(dict.fromkeys(all_asins))  # deduplicate
    print(f"\nTotal unique ASINs collected: {len(all_asins)}")
    return all_asins

def process_products(products):
    """Convert keepa product objects to a clean daily DataFrame."""
    all_dfs = []
    for product in products:
        asin = product.get('asin', '')
        try:
            data = product.get('data', {})

            # Use AMAZON price first, fall back to NEW (third-party)
            if 'AMAZON' in data and len(data['AMAZON']) > 0:
                prices = data['AMAZON']
                times = data['AMAZON_time']
            elif 'NEW' in data and len(data['NEW']) > 0:
                prices = data['NEW']
                times = data['NEW_time']
            else:
                print(f"  SKIPPED {asin}: no price data")
                continue

            df = pd.DataFrame({
                'amazon_price': prices,
            }, index=pd.to_datetime(times))

            # Clean up
            df = df[df['amazon_price'] > 0]  # remove -0.01 (out of stock marker)
            df['amazon_price'] = df['amazon_price']  # already in dollars from keepa lib
            df = df[df.index >= '2015-01-01']
            df = df[~df.index.duplicated(keep='last')]
            df = df.resample('D').last()
            df.index.name = 'date'

            if df['amazon_price'].dropna().empty:
                print(f"  SKIPPED {asin}: empty after cleaning")
                continue

            # Add metadata
            df['asin'] = asin
            df['title'] = product.get('title', '')
            df['brand'] = product.get('brand', '')
            cat_tree = product.get('categoryTree', [])
            df['category'] = cat_tree[-1]['name'] if cat_tree else ''

            rows = len(df)
            pmin = df['amazon_price'].min()
            pmax = df['amazon_price'].max()
            print(f"  Saved {asin}: {rows} rows, ${pmin:.2f}–${pmax:.2f} | {df['title'][:50]}")
            all_dfs.append(df)

        except Exception as e:
            print(f"  SKIPPED {asin}: {e}")

    return pd.concat(all_dfs) if all_dfs else pd.DataFrame()


if __name__ == "__main__":
    api = keepa.Keepa(API_KEY)
    api.update_status()
    print(f"Connected. Tokens available: {api.tokens_left}\n")

    if api.tokens_left < 10:
        print("Not enough tokens. Come back later.")
        exit()

    # Step 1: get category IDs (free)
    category_ids = get_target_category_ids(api)

    if not category_ids:
        print("No categories matched. Exiting.")
        exit()

    # Save category mapping for reference
    Path("data/asin_lists").mkdir(parents=True, exist_ok=True)
    pd.DataFrame([
        {'category': k, 'cat_id': v} for k, v in category_ids.items()
    ]).to_csv("data/asin_lists/category_ids.csv", index=False)

    # Step 2: get bestseller ASINs (costs tokens)
    all_asins = get_bestseller_asins(api, category_ids, limit_per_category=30)
    pd.Series(all_asins).to_csv(
        "data/asin_lists/pilot_asins_v2.csv", index=False, header=["asin"]
    )
    print(f"Saved {len(all_asins)} ASINs to data/asin_lists/pilot_asins_v2.csv")

    # Step 3: pull product data for first 10 ASINs to test
    print(f"\nPulling data for first 10 ASINs...")
    products = api.query(all_asins[:10], history=True, stats=730)

    # Step 4: process and save
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    df = process_products(products)

    if not df.empty:
        df.to_csv("data/raw/all_asins_daily.csv")
        print(f"\nDone. Shape: {df.shape}")
        print(df.head(10))
    else:
        print("No usable data collected.")