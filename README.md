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