"""
Real-Time Currency Exchange Module
Fetches live exchange rates and performs conversions
"""
import requests
import json
from datetime import datetime, timedelta
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.config import CURRENCY_CONFIG


class CurrencyConverter:
    def __init__(self):
        self.base_currency = CURRENCY_CONFIG['base_currency']
        self.target_currencies = CURRENCY_CONFIG['target_currencies']
        self.api_url = CURRENCY_CONFIG['api_url']
        self.cache = {}
        self.cache_timestamp = None
        self.last_update = None
        self.cache_duration = CURRENCY_CONFIG['cache_duration']

        # Fallback rates if API fails
        self.fallback_rates = {
            'USD': 1.0,
            'CNY': 7.2,
            'IDR': 15800.0
        }

    def _is_cache_valid(self):
        if self.cache_timestamp is None:
            return False
        age = (datetime.now() - self.cache_timestamp).total_seconds()
        return age < self.cache_duration

    def fetch_rates(self, force_update=False):
        """Fetch latest exchange rates from API"""
        if not force_update and self._is_cache_valid():
            print("[Cache] Using cached exchange rates")
            return self.cache

        try:
            print(f"[API] Fetching rates from {self.api_url}")
            response = requests.get(self.api_url, params={'base': self.base_currency}, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if 'rates' in data:
                    self.cache = data['rates']
                    self.cache_timestamp = datetime.now()
                    self.last_update = datetime.now()
                    print(f"[OK] Retrieved rates for {len(self.cache)} currencies")
                    return self.cache

            print("[Warning] API request failed, using fallback rates")
            self._use_fallback_rates()
            return self.fallback_rates

        except Exception as e:
            print(f"[Error] {str(e)}, using fallback rates")
            self._use_fallback_rates()
            return self.fallback_rates

    def _use_fallback_rates(self):
        """Set fallback rates as cache"""
        if not self.cache:
            self.cache = self.fallback_rates.copy()
            self.cache_timestamp = datetime.now()
            self.last_update = datetime.now()

    def convert(self, amount, from_currency, to_currency):
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount

        rates = self.fetch_rates()
        
        # Convert to base currency (USD) first
        if from_currency != self.base_currency:
            amount_in_base = amount / rates.get(from_currency, self.fallback_rates[from_currency])
        else:
            amount_in_base = amount

        # Convert from base to target currency
        if to_currency != self.base_currency:
            result = amount_in_base * rates.get(to_currency, self.fallback_rates[to_currency])
        else:
            result = amount_in_base

        return round(result, 2)

    def get_rate(self, currency):
        """Get exchange rate for a currency relative to base"""
        rates = self.fetch_rates()
        return rates.get(currency, self.fallback_rates.get(currency, 1.0))

    def format_amount(self, amount, currency):
        """Format amount with currency symbol"""
        symbols = {'USD': '$', 'CNY': '¥', 'IDR': 'Rp'}
        symbol = symbols.get(currency, currency + ' ')

        if currency == 'IDR':
            return f"{symbol}{amount:,.0f}"
        else:
            return f"{symbol}{amount:,.2f}"

    def convert_dataframe(self, df, amount_column='amount', currency_column='currency', target_currency='USD'):
        """Convert amounts in a dataframe to target currency"""
        import pandas as pd

        df = df.copy()
        converted_amounts = []

        for _, row in df.iterrows():
            amount = row[amount_column]
            from_currency = row[currency_column] if currency_column in df.columns else 'USD'
            converted = self.convert(amount, from_currency, target_currency)
            converted_amounts.append(converted)

        df[f'{amount_column}_{target_currency}'] = converted_amounts
        return df

    def get_rate_matrix(self):
        """Get exchange rate matrix as a DataFrame"""
        import pandas as pd

        rates = self.fetch_rates()
        currencies = ['USD', 'IDR', 'CNY']

        matrix = []
        for from_curr in currencies:
            row = {}
            for to_curr in currencies:
                if from_curr == to_curr:
                    row[to_curr] = 1.0
                else:
                    row[to_curr] = self.convert(1, from_curr, to_curr)
            matrix.append(row)

        df = pd.DataFrame(matrix, index=currencies)
        return df


if __name__ == "__main__":
    converter = CurrencyConverter()
    
    print("\n" + "="*60)
    print("  CURRENCY CONVERTER TEST")
    print("="*60)
    
    # Test conversions
    tests = [
        (100, 'USD', 'CNY'),
        (100, 'USD', 'IDR'),
        (720, 'CNY', 'USD'),
        (158000, 'IDR', 'USD'),
        (100, 'CNY', 'IDR')
    ]
    
    for amount, from_cur, to_cur in tests:
        result = converter.convert(amount, from_cur, to_cur)
        formatted = converter.format_amount(result, to_cur)
        print(f"\n{converter.format_amount(amount, from_cur)} = {formatted}")
    
    print("\n" + "="*60 + "\n")
