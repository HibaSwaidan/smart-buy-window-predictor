import pandas as pd
import json

# Read the CSV file
df = pd.read_csv("data/sample/sample_features_for_api_testing.csv")

# Load the feature columns list
with open("models/feature_columns.json", "r") as f:
    feature_cols = json.load(f)

# Take the first row
sample = df.iloc[0].to_dict()

# Extract only the features the model expects
features = {col: sample[col] for col in feature_cols if col in sample}

# Save to JSON file for API testing
with open("sample_features_api.json", "w") as f:
    json.dump({"features": features}, f, indent=2)

print(f"Done! Created sample_features_api.json with {len(features)} features")