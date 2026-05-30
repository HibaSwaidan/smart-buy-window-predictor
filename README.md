# Smart Buy Window Predictor

An application-oriented machine learning system that helps users decide whether to buy an Amazon product now or wait.

The system predicts:
1. Whether a meaningful price drop is likely within 7, 14, or 30 days.
2. Whether the product is at risk of becoming unavailable during that waiting period.

The final output is a buy-window recommendation: buy now, wait 7 days, wait 14 days, wait 30 days, or uncertain.

## Project Type

Option A: Application-Oriented ML System

## Core Components

- Keepa data collection
- Feature engineering
- Non-AI baseline
- Logistic regression baseline
- XGBoost classifier
- Walk-forward validation
- Shopper backtesting
- SHAP explanations
- Dockerized API
- Minimal user interface

## ASIN Selection — Decision Log

### Pilot v1 (Manual List) — May 30, 2026
Initially selected 10 ASINs manually across 4 categories based on product popularity
(Echo Dot, Fire TV Stick, Instant Pot, etc.).

**Problem discovered:** Most ASINs had no usable price history in Keepa's `csv[0]`
(Amazon direct price) because these products are predominantly sold by third-party
sellers. Only 4 out of 10 ASINs returned viable data.

**Root cause:** Manually chosen ASINs have no guarantee of Keepa tracking history.

### Pilot v2 (Keepa Bestseller API) — May 30, 2026
Switched to pulling ASINs directly from Keepa's bestseller endpoint per category.
These ASINs are guaranteed to have active tracking history since Keepa only lists
products it monitors continuously.

**Categories targeted:** Electronics, Home & Kitchen, Toys & Games, Office Products.