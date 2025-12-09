"""
Synthetic Financial Data Generator
Generates realistic user profiles and transaction data with built-in anomalies
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.config import DATA_GEN_CONFIG, TRANSACTION_CATEGORIES, RAW_DATA_DIR

fake = Faker()
np.random.seed(42)
random.seed(42)

class FinancialDataGenerator:
    def __init__(self, n_users=200, n_transactions=10000, fraud_rate=0.05):
        self.n_users = n_users
        self.n_transactions = n_transactions
        self.fraud_rate = fraud_rate
        self.currencies = DATA_GEN_CONFIG['currencies']

        # Currency exchange rates (approximate, relative to USD)
        self.exchange_rates = {
            'USD': 1.0,
            'CNY': 7.2,     # Chinese Yuan
            'IDR': 15800.0  # Indonesian Rupiah
        }

        # Category spending patterns (mean in USD, std)
        self.category_patterns = {
            'Groceries': (150, 50),
            'Utilities': (120, 30),
            'Rent': (1200, 200),
            'Healthcare': (200, 100),
            'Insurance': (300, 50),
            'Transportation': (100, 40),
            'Dining': (80, 30),
            'Entertainment': (100, 50),
            'Shopping': (200, 100),
            'Travel': (500, 300),
            'Hobbies': (150, 80),
            'Savings': (400, 200),
            'Investment': (500, 250),
            'Emergency Fund': (300, 150)
        }

        # Time-based spending patterns (by hour)
        self.hour_weights = {
            range(0, 6): 0.02,   # Late night - rare
            range(6, 9): 0.08,   # Early morning
            range(9, 12): 0.20,  # Morning - high activity
            range(12, 14): 0.25, # Lunch - peak
            range(14, 18): 0.20, # Afternoon
            range(18, 21): 0.22, # Evening - high activity
            range(21, 24): 0.03  # Night - low
        }
        
        # Merchants by category
        self.merchants = {
            'Groceries': ['Walmart', 'Whole Foods', 'Trader Joes', 'Safeway', 'Kroger'],
            'Utilities': ['Electric Co', 'Water Dept', 'Gas Company', 'Internet Provider'],
            'Rent': ['Property Management', 'Landlord Payment', 'Housing Complex'],
            'Healthcare': ['City Hospital', 'Health Clinic', 'Pharmacy', 'Doctor Office'],
            'Insurance': ['Insurance Corp', 'Health Insurance', 'Auto Insurance'],
            'Transportation': ['Gas Station', 'Uber', 'Public Transit', 'Parking'],
            'Dining': ['Restaurant A', 'Cafe B', 'Fast Food C', 'Diner D'],
            'Entertainment': ['Cinema', 'Concert Hall', 'Streaming Service', 'Gaming'],
            'Shopping': ['Amazon', 'Target', 'Best Buy', 'Mall Store'],
            'Travel': ['Airline', 'Hotel', 'Travel Agency', 'AirBnB'],
            'Hobbies': ['Sports Store', 'Craft Shop', 'Music Store', 'Book Store'],
            'Savings': ['Savings Account', 'High Yield Savings'],
            'Investment': ['Stock Broker', 'Mutual Fund', 'Crypto Exchange'],
            'Emergency Fund': ['Emergency Savings']
        }
    
    def generate_users(self):
        """Generate synthetic user profiles with realistic demographics"""
        users = []

        # Locations with currency preferences
        location_currency_map = {
            'New York': 'USD', 'Los Angeles': 'USD', 'Chicago': 'USD',
            'Houston': 'USD', 'Phoenix': 'USD', 'Philadelphia': 'USD',
            'Beijing': 'CNY', 'Shanghai': 'CNY', 'Guangzhou': 'CNY',
            'Jakarta': 'IDR', 'Surabaya': 'IDR', 'Bandung': 'IDR'
        }

        for i in range(self.n_users):
            location = random.choice(list(location_currency_map.keys()))
            preferred_currency = location_currency_map[location]

            # Age-based income distribution
            age = np.random.randint(22, 70)
            if age < 30:
                income = np.random.choice([3000, 4000, 5000, 6000])
            elif age < 45:
                income = np.random.choice([5000, 6000, 8000, 10000])
            else:
                income = np.random.choice([6000, 8000, 10000, 15000, 20000])

            user = {
                'user_id': f'U{i+1:05d}',
                'name': fake.name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'age': age,
                'location': location,
                'country': 'USA' if location in ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia']
                          else 'China' if location in ['Beijing', 'Shanghai', 'Guangzhou']
                          else 'Indonesia',
                'monthly_income': income,
                'created_date': fake.date_between(start_date='-3y', end_date='-1y'),
                'preferred_currency': preferred_currency,
                'credit_score': np.random.randint(550, 850)
            }
            users.append(user)

        return pd.DataFrame(users)
    
    def get_realistic_hour(self):
        """Generate realistic transaction hours based on probability weights"""
        hours = []
        weights = []
        for hour_range, weight in self.hour_weights.items():
            for hour in hour_range:
                hours.append(hour)
                weights.append(weight)
        return np.random.choice(hours, p=np.array(weights)/sum(weights))

    def convert_currency(self, amount_usd, target_currency):
        """Convert amount from USD to target currency"""
        return round(amount_usd * self.exchange_rates[target_currency], 2)

    def generate_transactions(self, users_df):
        """Generate synthetic transaction data with realistic patterns and anomalies"""
        transactions = []
        start_date = datetime.strptime(DATA_GEN_CONFIG['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(DATA_GEN_CONFIG['end_date'], '%Y-%m-%d')

        all_categories = []
        for cat_list in TRANSACTION_CATEGORIES.values():
            all_categories.extend(cat_list)

        for i in range(self.n_transactions):
            user = users_df.sample(1).iloc[0]

            # Random date within range
            days_diff = (end_date - start_date).days
            random_days = np.random.randint(0, days_diff)
            transaction_date = start_date + timedelta(days=random_days)

            # Realistic time distribution
            random_hour = self.get_realistic_hour()
            
            random_minute = np.random.randint(0, 60)
            random_second = np.random.randint(0, 60)
            transaction_datetime = transaction_date.replace(
                hour=random_hour, minute=random_minute, second=random_second
            )

            # Select category and amount (in USD first)
            category = random.choice(all_categories)
            mean_amount, std_amount = self.category_patterns[category]
            amount_usd = abs(np.random.normal(mean_amount, std_amount))

            # Use user's preferred currency 70% of the time
            if np.random.random() < 0.7:
                currency = user['preferred_currency']
            else:
                currency = random.choice(self.currencies)

            # Convert to target currency
            amount = self.convert_currency(amount_usd, currency)

            # Inject fraud patterns
            is_fraud = np.random.random() < self.fraud_rate
            fraud_type = None

            if is_fraud:
                fraud_type = random.choice([
                    'high_amount', 'unusual_time', 'rapid_succession',
                    'foreign_location', 'round_amount'
                ])

                if fraud_type == 'high_amount':
                    amount *= np.random.uniform(5, 20)
                elif fraud_type == 'unusual_time':
                    transaction_datetime = transaction_datetime.replace(
                        hour=np.random.randint(2, 5)
                    )
                elif fraud_type == 'round_amount':
                    amount = round(amount / 100) * 100
                elif fraud_type == 'foreign_location':
                    currency = random.choice([c for c in self.currencies
                                            if c != user['preferred_currency']])

            merchant = random.choice(self.merchants[category])

            # Merchant location based on currency
            if currency == 'USD':
                merchant_location = random.choice(['New York, USA', 'Los Angeles, USA', 'Chicago, USA'])
            elif currency == 'CNY':
                merchant_location = random.choice(['Beijing, China', 'Shanghai, China', 'Guangzhou, China'])
            else:
                merchant_location = random.choice(['Jakarta, Indonesia', 'Surabaya, Indonesia', 'Bandung, Indonesia'])

            payment_method = random.choice(['Credit Card', 'Debit Card', 'Digital Wallet', 'Bank Transfer'])

            transaction = {
                'transaction_id': f'T{i+1:08d}',
                'user_id': user['user_id'],
                'amount': round(amount, 2),
                'amount_usd': round(amount_usd, 2),
                'currency': currency,
                'category': category,
                'merchant': merchant,
                'merchant_location': merchant_location,
                'payment_method': payment_method,
                'transaction_date': transaction_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'is_fraud': int(is_fraud),
                'fraud_type': fraud_type if is_fraud else None,
                'description': f'{category} purchase at {merchant}',
                'day_of_week': transaction_datetime.strftime('%A'),
                'hour': transaction_datetime.hour,
                'month': transaction_datetime.month
            }
            transactions.append(transaction)

        df = pd.DataFrame(transactions)
        df = df.sort_values('transaction_date').reset_index(drop=True)
        return df
    
    def save_data(self, users_df, transactions_df):
        """Save generated data to CSV files"""
        users_path = RAW_DATA_DIR / 'users.csv'
        transactions_path = RAW_DATA_DIR / 'transactions.csv'

        users_df.to_csv(users_path, index=False)
        transactions_df.to_csv(transactions_path, index=False)

        print(f"\n{'='*60}")
        print(f"  DATA GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"\n[OK] Users data saved to: {users_path}")
        print(f"[OK] Transactions data saved to: {transactions_path}")
        print(f"\n{'='*60}")
        print(f"  DATA SUMMARY")
        print(f"{'='*60}")
        print(f"  Total Users: {len(users_df)}")
        print(f"  Total Transactions: {len(transactions_df)}")
        print(f"  Fraud Cases: {transactions_df['is_fraud'].sum()} ({transactions_df['is_fraud'].mean()*100:.2f}%)")
        print(f"  Date Range: {transactions_df['transaction_date'].min()} to {transactions_df['transaction_date'].max()}")
        print(f"\n  Currency Distribution:")
        for curr, count in transactions_df['currency'].value_counts().items():
            print(f"    {curr}: {count} ({count/len(transactions_df)*100:.1f}%)")
        print(f"\n  Fraud Types:")
        fraud_types = transactions_df[transactions_df['is_fraud'] == 1]['fraud_type'].value_counts()
        for ftype, count in fraud_types.items():
            print(f"    {ftype}: {count}")
        print(f"{'='*60}\n")
    
    def generate_all(self):
        """Generate complete dataset"""
        print("Generating synthetic financial data...")
        print(f"Parameters: {self.n_users} users, {self.n_transactions} transactions")
        
        users_df = self.generate_users()
        transactions_df = self.generate_transactions(users_df)
        self.save_data(users_df, transactions_df)
        
        return users_df, transactions_df

if __name__ == "__main__":
    generator = FinancialDataGenerator(
        n_users=DATA_GEN_CONFIG['n_users'],
        n_transactions=DATA_GEN_CONFIG['n_transactions'],
        fraud_rate=DATA_GEN_CONFIG['fraud_rate']
    )
    users_df, transactions_df = generator.generate_all()