"""
Time-Series Forecasting Module
Uses Prophet for forecasting future spending patterns
"""
import pandas as pd
import numpy as np
from prophet import Prophet
import joblib
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_PATHS, FORECAST_CONFIG


class SpendingForecaster:
    def __init__(self):
        self.models = {}
        self.forecast_periods = FORECAST_CONFIG['forecast_periods']

    def load_data(self):
        print("\n[1/5] Loading transaction data...")
        transactions_path = RAW_DATA_DIR / 'transactions.csv'
        df = pd.read_csv(transactions_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        print(f"  Loaded {len(df)} transactions")
        return df

    def prepare_data_for_prophet(self, df):
        print("\n[2/5] Preparing data for Prophet...")
        daily_spending = df.groupby([pd.Grouper(key='transaction_date', freq='D'), 'category'])['amount_usd'].sum().reset_index()
        daily_spending.columns = ['ds', 'category', 'y']
        categories = daily_spending['category'].unique()
        print(f"  Found {len(categories)} spending categories")
        
        category_data = {}
        for category in categories:
            cat_data = daily_spending[daily_spending['category'] == category][['ds', 'y']].copy()
            cat_data = cat_data.sort_values('ds')
            date_range = pd.date_range(start=cat_data['ds'].min(), end=cat_data['ds'].max(), freq='D')
            cat_data = cat_data.set_index('ds').reindex(date_range, fill_value=0).reset_index()
            cat_data.columns = ['ds', 'y']
            category_data[category] = cat_data
        
        print(f"  Prepared data for {len(category_data)} categories")
        return category_data

    def train_models(self, category_data):
        print("\n[3/5] Training Prophet models per category...")
        for i, (category, data) in enumerate(category_data.items(), 1):
            try:
                print(f"  [{i}/{len(category_data)}] Training: {category}")
                model = Prophet(yearly_seasonality=True, weekly_seasonality=True,
                              daily_seasonality=False, seasonality_mode='multiplicative')
                model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
                model.fit(data)
                self.models[category] = model
            except Exception as e:
                print(f"    Warning: {category}: {str(e)}")
        print(f"\n  Trained {len(self.models)} models")

    def generate_forecasts(self):
        print(f"\n[4/5] Generating {self.forecast_periods}-day forecasts...")
        all_forecasts = {}
        for i, (category, model) in enumerate(self.models.items(), 1):
            try:
                print(f"  [{i}/{len(self.models)}] Forecasting: {category}")
                future = model.make_future_dataframe(periods=self.forecast_periods, freq='D')
                forecast = model.predict(future)
                forecast_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
                forecast_data['category'] = category
                forecast_data['yhat'] = forecast_data['yhat'].clip(lower=0)
                forecast_data['yhat_lower'] = forecast_data['yhat_lower'].clip(lower=0)
                forecast_data['yhat_upper'] = forecast_data['yhat_upper'].clip(lower=0)
                all_forecasts[category] = forecast_data
            except Exception as e:
                print(f"    Warning: {category}: {str(e)}")
        print(f"\n  Generated forecasts for {len(all_forecasts)} categories")
        return all_forecasts

    def save_models_and_forecasts(self, all_forecasts):
        print("\n[5/5] Saving models and forecasts...")
        model_data = {'models': self.models, 'forecast_periods': self.forecast_periods}
        joblib.dump(model_data, MODEL_PATHS['forecaster'])
        print(f"  Models saved to: {MODEL_PATHS['forecaster']}")
        
        if all_forecasts:
            combined = pd.concat(all_forecasts.values(), ignore_index=True)
            forecast_path = PROCESSED_DATA_DIR / 'spending_forecasts.csv'
            combined.to_csv(forecast_path, index=False)
            print(f"  Forecasts saved to: {forecast_path}")
            
            future_forecasts = combined[combined['ds'] > pd.Timestamp.now()]
            category_totals = future_forecasts.groupby('category')['yhat'].sum().sort_values(ascending=False)
            print("\n  Forecast Summary (Next 90 days):")
            for category, total in category_totals.head(10).items():
                print(f"    {category}: ${total:,.2f}")
            print(f"\n    Total: ${category_totals.sum():,.2f}")
        return combined if all_forecasts else None

    def train_and_save(self):
        print("\n" + "="*60)
        print("  TIME-SERIES FORECASTING MODEL TRAINING")
        print("="*60)
        df = self.load_data()
        category_data = self.prepare_data_for_prophet(df)
        self.train_models(category_data)
        all_forecasts = self.generate_forecasts()
        combined = self.save_models_and_forecasts(all_forecasts)
        print("\n" + "="*60)
        print("  FORECASTING TRAINING COMPLETE")
        print("="*60 + "\n")
        return combined


if __name__ == "__main__":
    forecaster = SpendingForecaster()
    forecasts = forecaster.train_and_save()
