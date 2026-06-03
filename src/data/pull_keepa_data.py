import os
import csv
import json
import time
from pathlib import Path
from datetime import datetime

import keepa
import numpy as np
import pandas as pd
from dotenv import load_dotenv


# =========================
# Configuration
# =========================

INPUT_FILE = Path("data/asin_lists/raw_exports/product_finder_1000_v2.csv")
OUTPUT_DIR = Path("data/raw/v2_raw")
FINAL_ASIN_LIST = Path("data/asin_lists/final_asin_list_v2.csv")

BATCH_SIZE = 10
DOMAIN = "US"

HISTORY = True
BUYBOX = False

MAX_ASINS = int(os.getenv("MAX_ASINS", "0"))
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")


# =========================
# Helper functions
# =========================

def json_default(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (pd.Timestamp, datetime)):
        return str(obj)
    return str(obj)


def read_asins_from_csv_file(path: Path):
    asins = []
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return []
    start_index = 1 if rows[0] and "asin" in rows[0][0].lower() else 0
    for row in rows[start_index:]:
        if not row:
            continue
        asin = row[0].strip()
        if len(asin) == 10:
            asins.append(asin)
    return asins


def get_already_pulled_asins(output_dir: Path):
    already = set()
    for json_file in output_dir.glob("*_raw.json"):
        asin = json_file.name.replace("_raw.json", "")
        if len(asin) == 10:
            already.add(asin)
    return already


def safe_get(product, key, default=None):
    try:
        return product.get(key, default)
    except Exception:
        return default


def extract_metadata_summary(product):
    asin = safe_get(product, "asin", "")
    category_tree = safe_get(product, "categoryTree", []) or []
    root_category = ""
    leaf_category = ""
    try:
        if category_tree:
            root_category = category_tree[0].get("name", "")
            leaf_category = category_tree[-1].get("name", "")
    except Exception:
        pass
    data = safe_get(product, "data", {}) or {}
    return {
        "asin": asin,
        "title": safe_get(product, "title", ""),
        "brand": safe_get(product, "brand", ""),
        "root_category": root_category,
        "leaf_category": leaf_category,
        "has_AMAZON": "AMAZON" in data,
        "has_NEW_FBA": "NEW_FBA" in data,
        "has_NEW": "NEW" in data,
        "has_BUY_BOX_SHIPPING": "BUY_BOX_SHIPPING" in data,
        "has_SALES": "SALES" in data,
        "has_COUNT_NEW": "COUNT_NEW" in data,
        "has_RATING": "RATING" in data,
        "has_COUNT_REVIEWS": "COUNT_REVIEWS" in data,
    }


# =========================
# Main
# =========================

if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("KEEPA_API_KEY")
    if not api_key:
        raise ValueError("Missing KEEPA_API_KEY. Add it to your .env file.")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_ASIN_LIST.parent.mkdir(parents=True, exist_ok=True)

    # Read ASINs from v2 file only
    asins = read_asins_from_csv_file(INPUT_FILE)
    asins = list(dict.fromkeys(asins))  # deduplicate
    print(f"Unique ASINs in v2 export: {len(asins)}")

    if MAX_ASINS > 0:
        asins = asins[:MAX_ASINS]

    already_pulled = get_already_pulled_asins(OUTPUT_DIR)
    new_asins = [a for a in asins if a not in already_pulled]

    pd.Series(asins, name="asin").to_csv(FINAL_ASIN_LIST, index=False)

    print("=" * 70)
    print("Smart Buy Window Predictor: Raw Keepa Pull")
    print("=" * 70)
    print(f"Input file           : {INPUT_FILE}")
    print(f"Output directory     : {OUTPUT_DIR}")
    print(f"Total unique ASINs   : {len(asins)}")
    print(f"Already pulled       : {len(already_pulled)}")
    print(f"New ASINs to pull    : {len(new_asins)}")
    print(f"Run ID               : {RUN_ID}")
    print(f"History              : {HISTORY}")
    print(f"Buy Box              : {BUYBOX}")
    print(f"Domain               : {DOMAIN} (amazon.com)")
    print("=" * 70)

    if not new_asins:
        print("No new ASINs to pull.")
        exit()

    api = keepa.Keepa(api_key)
    api.update_status()
    print(f"Connected to Keepa. Tokens available: {api.tokens_left}\n")

    if api.tokens_left < 5:
        print("Not enough tokens. Come back later.")
        exit()

    manifest_rows = []
    metadata_rows = []
    failed_asins = []

    total_batches = (len(new_asins) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(new_asins), BATCH_SIZE):
        batch = new_asins[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        print()
        print("-" * 70)
        print(f"Batch {batch_num}/{total_batches} — ASINs {i+1} to {i+len(batch)}")
        print(batch)
        print("-" * 70)

        tokens_before = None
        tokens_after = None
        returned_asins = []

        try:
            api.update_status()
            tokens_before = api.tokens_left
            print(f"Tokens before: {tokens_before}")

            products = api.query(
                batch,
                domain=DOMAIN,
                history=HISTORY,
                buybox=BUYBOX
            )

            api.update_status()
            tokens_after = api.tokens_left
            print(f"Tokens after:  {tokens_after}")

            for product in products:
                asin = product.get("asin", "")
                if not asin:
                    continue

                returned_asins.append(asin)
                json_path = OUTPUT_DIR / f"{asin}_raw.json"

                if json_path.exists():
                    print(f"  Already exists, skipping: {asin}")
                else:
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(product, f, default=json_default)
                    print(f"  Saved: {asin}")

                metadata_rows.append(extract_metadata_summary(product))

            missing_returned = [a for a in batch if a not in returned_asins]
            if missing_returned:
                failed_asins.extend(missing_returned)
                print(f"  Missing: {missing_returned}")

            manifest_rows.append({
                "run_id": RUN_ID,
                "batch_num": batch_num,
                "requested_asins": ",".join(batch),
                "returned_asins": ",".join(returned_asins),
                "missing_asins": ",".join(missing_returned),
                "tokens_before": tokens_before,
                "tokens_after": tokens_after,
                "status": "success",
                "error": ""
            })

        except Exception as e:
            print(f"  Batch failed: {e}")
            failed_asins.extend(batch)
            manifest_rows.append({
                "run_id": RUN_ID,
                "batch_num": batch_num,
                "requested_asins": ",".join(batch),
                "returned_asins": "",
                "missing_asins": ",".join(batch),
                "tokens_before": tokens_before,
                "tokens_after": tokens_after,
                "status": "failed",
                "error": str(e)
            })

        # Save tracking files after every batch
        pd.DataFrame(manifest_rows).to_csv(
            OUTPUT_DIR / f"pull_manifest_{RUN_ID}.csv", index=False
        )
        pd.DataFrame(metadata_rows).drop_duplicates(subset=["asin"], keep="last").to_csv(
            OUTPUT_DIR / f"metadata_summary_{RUN_ID}.csv", index=False
        )
        pd.Series(sorted(set(failed_asins)), name="asin").to_csv(
            OUTPUT_DIR / f"failed_asins_{RUN_ID}.csv", index=False
        )

        time.sleep(2)

    print()
    print("=" * 70)
    print("Pull complete")
    print("=" * 70)
    print(f"Requested  : {len(new_asins)}")
    print(f"Saved JSON : {len(list(OUTPUT_DIR.glob('*_raw.json')))}")
    print(f"Failed     : {len(set(failed_asins))}")
    print(f"Manifest   : {OUTPUT_DIR}")
    print("Done.")