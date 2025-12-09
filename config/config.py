"""
Configuration file for Smart Financial Budgeting System
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'smart_finance'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# Data Generation Configuration
from datetime import datetime as dt
DATA_GEN_CONFIG = {
    'n_users': 250,  # 100-300 users as requested
    'n_transactions': 15000,  # 5,000-20,000 transactions as requested
    'start_date': '2024-01-01',  # Start from 2024
    'end_date': dt.now().strftime('%Y-%m-%d'),  # Up to today
    'fraud_rate': 0.05,  # 5% anomalies
    'currencies': ['USD', 'IDR', 'CNY']
}

# Transaction Categories
TRANSACTION_CATEGORIES = {
    'essentials': ['Groceries', 'Utilities', 'Rent', 'Healthcare', 'Insurance', 'Transportation'],
    'discretionary': ['Dining', 'Entertainment', 'Shopping', 'Travel', 'Hobbies'],
    'savings': ['Savings', 'Investment', 'Emergency Fund']
}

# Fraud Detection Configuration
FRAUD_CONFIG = {
    'contamination': 0.05,
    'models': ['IsolationForest', 'AutoEncoder'],
    'feature_columns': ['amount', 'hour', 'day_of_week', 'category_encoded']
}

# Forecasting Configuration
FORECAST_CONFIG = {
    'forecast_periods': 90,  # 3 months
    'seasonality_mode': 'multiplicative',
    'yearly_seasonality': True,
    'weekly_seasonality': True,
    'daily_seasonality': False
}

# Currency Configuration
CURRENCY_CONFIG = {
    'api_key': os.getenv('EXCHANGE_RATE_API_KEY', ''),
    'base_currency': 'USD',
    'target_currencies': ['IDR', 'CNY', 'USD'],
    'api_url': 'https://api.exchangerate.host/latest',
    'cache_duration': 3600  # 1 hour in seconds
}

# Budget Configuration (50/30/20 Rule)
BUDGET_CONFIG = {
    'essentials': 0.50,
    'discretionary': 0.30,
    'savings': 0.20
}

# Airflow Configuration
AIRFLOW_CONFIG = {
    'fx_update_schedule': '0 0 * * *',  # Daily at midnight
    'model_retrain_schedule': '0 0 * * 0',  # Weekly on Sunday
    'alert_check_schedule': '0 */6 * * *'  # Every 6 hours
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'host': '0.0.0.0',
    'port': 8501,
    'theme': 'light',
    'title': 'Smart Finance Dashboard'
}

# Model Paths
MODEL_PATHS = {
    'fraud_detector': MODELS_DIR / 'fraud_detector.pkl',
    'forecaster': MODELS_DIR / 'forecaster.pkl',
    'scaler': MODELS_DIR / 'scaler.pkl'
}
