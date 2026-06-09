# Smart Buy Window Predictor

A deployed machine learning application that helps Amazon shoppers decide whether to buy a product now, wait for a likely price drop, or monitor the product more closely.

The system combines multi-horizon price-drop prediction, availability-risk assessment, and a user-facing recommendation layer to provide practical purchase timing guidance.

---

## Overview

Online shoppers often face the same question:

> Should I buy this product now, or is it worth waiting for a better price?

Existing tools such as Keepa and CamelCamelCamel show historical price charts, but they do not directly answer the buying decision. They show what happened in the past, while the user still has to interpret the chart and decide what to do.

Smart Buy Window Predictor addresses this gap by providing a clear recommendation:

* **Buy Now**
* **Wait**
* **Wait with Caution**
* **Wait and Track**
* **Uncertain**

The system is designed for deal-conscious shoppers making considered, deferrable purchases such as laptops, cameras, appliances, and other products where timing and savings matter.

---

## Key Features

### Multi-Horizon Price-Drop Prediction

The application uses three separate XGBoost classifiers to estimate the probability of a meaningful price drop within:

* 7 days
* 14 days
* 30 days

This allows the user to compare short, medium, and longer waiting windows rather than receiving a single fixed recommendation.

### Meaningful Price-Drop Definition

A price drop is considered meaningful only if it satisfies both conditions:

```text
price drop ≥ 5%
AND
price drop ≥ $5
```

This avoids treating small, non-actionable price movements as useful savings.

### Availability-Risk Layer

The system does not only ask whether the price may drop. It also asks whether it is safe to wait.

The availability-risk module uses marketplace signals such as:

* recent Amazon price missingness
* non-Amazon price source
* recent price-source change
* missing offer-count data
* low offer count
* declining offer count

These signals are combined into a risk score and mapped into:

* LOW
* MEDIUM
* HIGH

### Final Recommendation Logic

The final output combines:

1. price-drop probability
2. horizon-specific recommendation thresholds
3. availability-risk level

This creates a more realistic recommendation than a simple price predictor.

For example:

| Price Signal           | Availability Risk | Final Recommendation |
| ---------------------- | ----------------- | -------------------- |
| Strong wait signal     | Low risk          | Wait                 |
| Strong wait signal     | Medium risk       | Wait with Caution    |
| Strong wait signal     | High risk         | Uncertain            |
| Uncertain price signal | High risk         | Buy Now              |
| Low drop probability   | Any risk level    | Buy Now              |

### Product Tracking

The application includes a tracking request system.

Users can save a product for tracking using either:

* a custom target price
* or the model-defined meaningful-drop threshold

If no target price is entered, the system calculates:

```text
target_price = current_price - max(current_price × 0.05, 5)
```

Tracking requests are stored in Supabase PostgreSQL and can be cancelled by the user.

---

## Live Deployment

Frontend:

```text
https://smartbuy-tan.vercel.app
```

Backend health endpoint:

```text
https://smart-buy-predictor-production.up.railway.app/health
```

Prediction endpoint:

```text
https://smart-buy-predictor-production.up.railway.app/predict
```

---

## System Architecture

```text
User enters Amazon URL or ASIN
        ↓
FastAPI backend extracts ASIN
        ↓
Keepa API retrieves live product history
        ↓
Feature builder creates model-ready features
        ↓
7-day, 14-day, and 30-day XGBoost models predict price-drop probabilities
        ↓
Availability-risk module scores waiting risk
        ↓
Combination layer produces final recommendation
        ↓
React frontend displays recommendation, price outlook, risk signals, and price history
```

---

## Technology Stack

### Frontend

* React
* Vite
* Tailwind CSS
* Recharts

### Backend

* FastAPI
* Python
* XGBoost
* scikit-learn
* pandas
* joblib
* Keepa API
* Supabase PostgreSQL
* psycopg2

### Deployment

* Vercel for frontend
* Railway for backend
* Docker for backend containerization

---

## Repository Structure

```text
smart-buy-window-predictor/
│
├── data/
│   └── sample/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
├── models/
│   └── v2_1/
│       ├── xgb_price_drop_7d_model.joblib
│       ├── xgb_price_drop_14d_model.joblib
│       ├── xgb_price_drop_30d_model.joblib
│       ├── feature_columns.json
│       ├── model_metadata_multihorizon.json
│       └── evaluation outputs
│
├── notebooks/
│   ├── 07_v2_availability_risk_module.ipynb
│   └── 08_multi_horizon_price_drop_modelling.ipynb
│
├── src/
│   ├── api/
│   │   └── main.py
│   ├── features/
│   │   └── live_feature_builder.py
│   ├── models/
│   │   └── predict_recommendation.py
│   ├── services/
│   │   ├── asin_parser.py
│   │   ├── keepa_client.py
│   │   └── tracking_store.py
│   └── evaluation/
│
├── Dockerfile
├── requirements-api.txt
└── README.md
```

---

## Machine Learning Methodology

### Task Formulation

The modelling task is binary classification per horizon.

For each product-day, the model predicts whether a meaningful price drop will occur within:

* 7 days
* 14 days
* 30 days

Each horizon has a separate label and a separate trained model.

### Data

The dataset was built from Keepa historical Amazon product data.

Final cleaned dataset:

* 922 ASINs
* 1.95 million daily rows
* 2015 to 2026 historical coverage
* 6 root product categories

### Feature Engineering

Features were built from historical price and marketplace signals only.

Main feature groups include:

* current price
* lagged prices
* rolling price means
* rolling price standard deviations
* price percentage changes
* price relative to 30-day rolling average
* sales-rank signals
* offer-count signals
* price-source signals
* missingness indicators
* calendar features
* category indicators

### Leakage Prevention

The project uses a chronological design to avoid future leakage.

Key safeguards:

* rolling features are shifted before calculation
* future price columns are excluded from training
* snapshot fields collected after the historical period are excluded
* train, validation, and test sets are split chronologically
* thresholds are selected on validation data only
* the 2026 test set is used only for final evaluation

Data split:

| Split      | Period       |
| ---------- | ------------ |
| Training   | 2015 to 2024 |
| Validation | 2025         |
| Test       | 2026         |

---

## Model Selection

Several approaches were evaluated:

* majority baseline
* rule baseline
* logistic regression
* XGBoost

The rule baseline predicts a drop when the current price is above its recent rolling average.

XGBoost was selected because it performed best on tabular historical pricing data and captured non-linear interactions between price position, volatility, seasonality, category, and marketplace signals.

Representative ROC-AUC comparison:

| Model               | ROC-AUC × 100 |
| ------------------- | ------------: |
| Majority baseline   |          50.0 |
| Rule baseline       |          74.1 |
| Logistic regression |          77.0 |
| XGBoost             |          81.8 |

---

## Recommendation Thresholds

The XGBoost models output probabilities. These probabilities are converted into recommendation zones using validation-selected thresholds.

The purpose of the thresholds is not only to maximize a technical score, but to create practical decision zones:

* low probability: Buy Now
* middle probability: Uncertain
* high probability: Wait

Final deployed thresholds:

| Horizon | Buy Zone | Wait Zone |
| ------- | -------: | --------: |
| 7 days  |  ≤ 35.0% |   ≥ 67.5% |
| 14 days |  ≤ 35.0% |   ≥ 57.5% |
| 30 days |  ≤ 32.5% |   ≥ 55.0% |

Probabilities between the buy and wait thresholds are treated as uncertain.

---

## Evaluation

The final evaluation uses the 2026 held-out test set.

The project evaluates performance at three levels:

### 1. Model Metrics

Metrics include:

* ROC-AUC
* PR-AUC
* precision
* recall
* F1 score

### 2. Recommendation Zones

The system checks whether each zone behaves as expected:

* Buy Now zone should have a low actual drop rate.
* Wait zone should have a high actual drop rate.
* Uncertain zone should capture middle-confidence cases.

### 3. Shopper Backtest

The shopper backtest evaluates what would happen if a user followed the recommendations.

Key results:

* Confident Wait recommendations achieved approximately 73% to 77% actual drop rate across horizons.
* Buy Now recommendations had much lower future drop rates.
* Longer 30-day waits showed higher passive-waiting risk, which motivated the Wait and Track recommendation.

---

## API Documentation

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### Predict Recommendation

```http
POST /predict
```

Request:

```json
{
  "url_or_asin": "B00008IHL8"
}
```

Response includes:

```json
{
  "asin": "B00008IHL8",
  "title": "Product title",
  "brand": "Brand",
  "root_category": "Category",
  "image_url": "https://...",
  "latest_price": 28.49,
  "recommendation": "BUY_NOW",
  "best_horizon": 14,
  "price_drop_probability": 0.1566,
  "price_zone": "confident_buy",
  "availability_risk_level": "LOW",
  "availability_risk_score": 2,
  "horizon_predictions": {
    "7d": {},
    "14d": {},
    "30d": {}
  },
  "explanation": [],
  "price_history": []
}
```

### Save Tracking Request

```http
POST /track
```

Request:

```json
{
  "asin": "B00008IHL8",
  "email": "user@example.com",
  "product_title": "Product title",
  "image_url": "https://...",
  "current_price": 28.49,
  "target_price": null,
  "tracking_horizon": 30,
  "notify_on_meaningful_drop": true
}
```

If `target_price` is null, the backend calculates the model-aligned meaningful-drop target.

Example response:

```json
{
  "id": "tracking-id",
  "asin": "B00008IHL8",
  "email": "user@example.com",
  "target_price": 23.49,
  "tracking_horizon": 30,
  "status": "active",
  "message": "Tracking request saved."
}
```

### Get Tracked Products

```http
GET /tracking?email=user@example.com
```

Returns tracking records belonging to that email.

### Cancel Tracking

```http
DELETE /tracking/{tracking_id}?email=user@example.com
```

This marks the tracking request as cancelled rather than deleting it.

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/HibaSwaidan/smart-buy-window-predictor.git
cd smart-buy-window-predictor
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements-api.txt
```

### 4. Create environment variables

Create a `.env` file in the project root:

```env
KEEPA_API_KEY=your_keepa_api_key
DATABASE_URL=your_supabase_postgres_connection_string
```

Do not commit `.env`.

### 5. Run the backend

```bash
uvicorn src.api.main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

Test:

```bash
curl http://127.0.0.1:8000/health
```

---

## Frontend Setup

From the project root:

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Run the frontend:

```bash
npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

## Docker Usage

Build the backend Docker image:

```bash
docker build -t smart-buy-window-api .
```

Run the container:

```bash
docker run --rm -p 8000:8000 --env-file .env smart-buy-window-api
```

Test:

```bash
curl http://127.0.0.1:8000/health
```

---

## Environment Variables

| Variable            | Required              | Purpose                                          |
| ------------------- | --------------------- | ------------------------------------------------ |
| `KEEPA_API_KEY`     | Yes                   | Fetches live Amazon product history from Keepa   |
| `DATABASE_URL`      | Required for tracking | Connects the backend to Supabase PostgreSQL      |
| `VITE_API_BASE_URL` | Yes for frontend      | Defines the backend API URL used by the frontend |

---

## Current Limitations

The system is a deployed prototype, not a perfect price oracle.

Main limitations:

1. **Availability is a proxy**
   The dataset does not contain reliable historical daily stock-out labels. The availability-risk module is rule-based and estimates waiting risk from marketplace signals.

2. **Flash sales are difficult to predict**
   Very short, unannounced discounts are structurally hard to predict from daily historical data.

3. **Dataset coverage is limited**
   The training data covers 922 ASINs across six product categories. Broader production deployment would require more categories and a larger product set.
   
---

## Future Work

Planned extensions include:

* larger product dataset
* additional Amazon categories
* category-specific calibration
* richer frontend explanations
* user accounts for saved tracking history
* deployment monitoring and logging dashboard


---

## Project Status

Current status:

* Multi-horizon prediction backend deployed
* Frontend deployed
* Dockerized backend working
* Product image retrieval working
* Availability-risk layer integrated
* Tracking request system implemented
* Supabase tracking storage integrated
* Scheduled alerts not yet implemented

This repository contains the full machine learning pipeline, deployed backend API, React frontend, model artifacts, and evaluation outputs for the Smart Buy Window Predictor.
