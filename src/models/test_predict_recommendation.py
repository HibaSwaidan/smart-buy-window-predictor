from pathlib import Path
import pandas as pd

from src.models.predict_recommendation import predict_recommendation


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features_v2.csv"

df = pd.read_csv(FEATURES_PATH)

sample_row = df.iloc[-1].to_dict()

result = predict_recommendation(sample_row)

print(result)