import keepa
import pandas as pd
import os
import csv
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
API_KEY = os.getenv("KEEPA_API_KEY")

def process_products(products):
    """Convert keepa product objects to a clean daily DataFrame."""
    all_dfs = []
    for product in products:
        asin = product.get('asin', '')
        try:
            data = product.get('data', {})

            # Priority: Buy Box → Amazon direct → New third-party
            if 'BUY_BOX_SHIPPING' in data and len(data['BUY_BOX_SHIPPING']) > 0:
                prices = data['BUY_BOX_SHIPPING']
                times = data['BUY_BOX_SHIPPING_time']
            elif 'AMAZON' in data and len(data['AMAZON']) > 0:
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

            df = df[df['amazon_price'] > 0]
            df = df[df.index >= '2015-01-01']
            df = df[~df.index.duplicated(keep='last')]
            df = df.resample('D').last()
            df.index.name = 'date'

            if df['amazon_price'].dropna().empty:
                print(f"  SKIPPED {asin}: empty after cleaning")
                continue

            df['asin'] = asin
            df['title'] = product.get('title', '')
            df['brand'] = product.get('brand', '')
            cat_tree = product.get('categoryTree', [])
            df['category'] = cat_tree[-1]['name'] if cat_tree else ''

            rows = len(df)
            pmin = df['amazon_price'].min()
            pmax = df['amazon_price'].max()
            print(f"  Saved {asin}: {rows} rows, ${pmin:.2f}–${pmax:.2f} | {product.get('title','')[:50]}")
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

    # Load ASINs from Product Finder export
    asin_file = "data/asin_lists/raw_exports/product_finder_1000.csv"
    asins = []
    with open(asin_file, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row:
                asins.append(row[0].strip())

    # Add previously pulled good ASINs
    existing_good = [
        "B008KJEYLO", "B013C9OKVU", "B072QXWXS6", "B0795W29GC",
        "B07LFQ9CXC", "B07M6FL57T", "B07SCL613T", "B08QRKY3NJ",
        "B07FZ8S74R", "B07FDJMC9Q", "B07H9B9HYL", "B08KTZ8249"
    ]

    all_asins = list(dict.fromkeys(existing_good + asins))
    print(f"Total ASINs to pull: {len(all_asins)}")

    # Save combined ASIN list
    pd.Series(all_asins).to_csv(
        "data/asin_lists/final_asin_list.csv", index=False, header=["asin"]
    )

    # Pull in batches of 10
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    all_dfs = []
    failed = []
    batch_size = 10

    for i in range(0, len(all_asins), batch_size):
        batch = all_asins[i:i+batch_size]
        print(f"\nBatch {i//batch_size + 1}/{(len(all_asins)+batch_size-1)//batch_size} — ASINs {i+1} to {i+len(batch)}")
        try:
            products = api.query(batch, history=True, stats=730)
            df = process_products(products)
            if not df.empty:
                df.to_csv(f"data/raw/batch_{i//batch_size + 1}.csv")
                all_dfs.append(df)
                print(f"  Saved {len(df)} rows")
        except Exception as e:
            print(f"  Batch failed: {e}")
            failed.extend(batch)

    if all_dfs:
        combined = pd.concat(all_dfs)
        combined.to_csv("data/raw/all_asins_daily.csv")
        print(f"\nDone. Total shape: {combined.shape}")
        print(f"Failed ASINs: {failed}")
    else:
        print("No data collected.")