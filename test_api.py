import json
import pandas as pd

# Load the features dataset
df = pd.read_csv("data/processed/features_v2.csv")

# Load the feature column names
with open("models/feature_columns.json", "r") as f:
    feature_cols = json.load(f)

# Take the first row as a sample
sample = df.iloc[0][feature_cols].to_dict()

# Save to a file
with open("sample_features.json", "w") as f:
    json.dump({"features": sample}, f, indent=2)

print("Done! Saved sample_features.json")
print(f"Number of features: {len(sample)}")