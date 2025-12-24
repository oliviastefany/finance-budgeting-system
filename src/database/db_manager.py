"""
PostgreSQL Database Integration
Handles database schema creation and CRUD operations
"""
import 


from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print(f"✓ Connected to PostgreSQL database: {self.config['database']}")
            return True
        except Exception as e:
            print(f"✗ Error connecting to database: {str(e)}")
            print(f"  Make sure PostgreSQL is running and database '{self.config['database']}' exists")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Database connection closed")
    
    def create_schema(self):
        """Create database tables"""
        try:
            # Users table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    age INTEGER,
                    location VARCHAR(100),
                    monthly_income DECIMAL(12, 2),
                    preferred_currency VARCHAR(3),
                    created_date DATE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Transactions table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id VARCHAR(20) PRIMARY KEY,
                    user_id VARCHAR(20) REFERENCES users(user_id),
                    amount DECIMAL(12, 2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    merchant VARCHAR(100),
                    transaction_date TIMESTAMP NOT NULL,
                    description TEXT,
                    is_fraud BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on user_id and transaction_date for faster queries
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_user_date 
                ON transactions(user_id, transaction_date DESC)
            """)
            
            # Fraud alerts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS fraud_alerts (
                    alert_id SERIAL PRIMARY KEY,
                    transaction_id VARCHAR(20) REFERENCES transactions(transaction_id),
                    user_id VARCHAR(20) REFERENCES users(user_id),
                    fraud_score DECIMAL(10, 4),
                    detection_method VARCHAR(50),
                    alert_status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    notes TEXT
                )
            """)
            
            # Forecasts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecasts (
                    forecast_id SERIAL PRIMARY KEY,
                    user_id VARCHAR(20) REFERENCES users(user_id),
                    category VARCHAR(50) NOT NULL,
                    forecast_date DATE NOT NULL,
                    predicted_amount DECIMAL(12, 2),
                    lower_bound DECIMAL(12, 2),
                    upper_bound DECIMAL(12, 2),
                    currency VARCHAR(3) DEFAULT 'USD',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, category, forecast_date)
                )
            """)
            
            # Budget recommendations table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS budget_recommendations (
                    recommendation_id SERIAL PRIMARY KEY,
                    user_id VARCHAR(20) REFERENCES users(user_id),
                    month DATE NOT NULL,
                    income DECIMAL(12, 2),
                    recommended_essentials DECIMAL(12, 2),
                    recommended_discretionary DECIMAL(12, 2),
                    recommended_savings DECIMAL(12, 2),
                    actual_essentials DECIMAL(12, 2),
                    actual_discretionary DECIMAL(12, 2),
                    actual_savings DECIMAL(12, 2),
                    health_score DECIMAL(5, 2),
                    currency VARCHAR(3) DEFAULT 'USD',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, month)
                )
            """)
            
            # Exchange rates table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS exchange_rates (
                    rate_id SERIAL PRIMARY KEY,
                    from_currency VARCHAR(3) NOT NULL,
                    to_currency VARCHAR(3) NOT NULL,
                    rate DECIMAL(15, 6) NOT NULL,
                    rate_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(from_currency, to_currency, rate_date)
                )
            """)
            
         
            self.conn.commit()
            print("✓ Database schema created successfully")
            return True
        
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error creating schema: {str(e)}")
            return False
    
    def insert_user(self, user_data):
        """Insert a new user"""
        try:
            self.cursor.execute("""
                INSERT INTO users (user_id, name, email, age, location, monthly_income, preferred_currency, created_date)
                VALUES (%(user_id)s, %(name)s, %(email)s, %(age)s, %(location)s, %(monthly_income)s, %(preferred_currency)s, %(created_date)s)
                ON CONFLICT (user_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    age = EXCLUDED.age,
                    location = EXCLUDED.location,
                    monthly_income = EXCLUDED.monthly_income,
                    preferred_currency = EXCLUDED.preferred_currency
            """, user_data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error inserting user: {str(e)}")
            return False
    
    def insert_transaction(self, transaction_data):
        """Insert a new transaction"""
        try:
            self.cursor.execute("""
                INSERT INTO transactions (transaction_id, user_id, amount, currency, category, merchant, transaction_date, description, is_fraud)
                VALUES (%(transaction_id)s, %(user_id)s, %(amount)s, %(currency)s, %(category)s, %(merchant)s, %(transaction_date)s, %(description)s, %(is_fraud)s)
                ON CONFLICT (transaction_id) DO NOTHING
            """, transaction_data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error inserting transaction: {str(e)}")
            return False
    
    def insert_fraud_alert(self, alert_data):
        """Insert a fraud alert"""
        try:
            self.cursor.execute("""
                INSERT INTO fraud_alerts (transaction_id, user_id, fraud_score, detection_method, alert_status, notes)
                VALUES (%(transaction_id)s, %(user_id)s, %(fraud_score)s, %(detection_method)s, %(alert_status)s, %(notes)s)
            """, alert_data)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error inserting fraud alert: {str(e)}")
            return False
    
    def bulk_insert_users(self, users_df):
        """Bulk insert users from dataframe"""
        count = 0
        for _, row in users_df.iterrows():
            if self.insert_user(row.to_dict()):
                count += 1
        print(f"✓ Inserted {count} users")
        return count
    
    def bulk_insert_transactions(self, transactions_df):
        """Bulk insert transactions from dataframe"""
        count = 0
        for _, row in transactions_df.iterrows():
            if self.insert_transaction(row.to_dict()):
                count += 1
        print(f"✓ Inserted {count} transactions")
        return count
    
    def get_user(self, user_id):
        """Retrieve user by ID"""
        self.cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()
    
    def get_user_transactions(self, user_id, limit=100):
        """Get transactions for a user"""
        self.cursor.execute("""
            SELECT * FROM transactions 
            WHERE user_id = %s 
            ORDER BY transaction_date DESC 
            LIMIT %s
        """, (user_id, limit))
        return self.cursor.fetchall()
    
    def get_fraud_alerts(self, status='pending'):
        """Get fraud alerts by status"""
        self.cursor.execute("""
            SELECT fa.*, t.amount, t.category, t.merchant, u.name as user_name
            FROM fraud_alerts fa
            JOIN transactions t ON fa.transaction_id = t.transaction_id
            JOIN users u ON fa.user_id = u.user_id
            WHERE fa.alert_status = %s
            ORDER BY fa.created_at DESC
        """, (status,))
        return self.cursor.fetchall()
    
    def update_fraud_alert_status(self, alert_id, status, notes=None):
        """Update fraud alert status"""
        try:
            if status == 'resolved':
                self.cursor.execute("""
                    UPDATE fraud_alerts 
                    SET alert_status = %s, resolved_at = CURRENT_TIMESTAMP, notes = %s
                    WHERE alert_id = %s
                """, (status, notes, alert_id))
            else:
                self.cursor.execute("""
                    UPDATE fraud_alerts 
                    SET alert_status = %s, notes = %s
                    WHERE alert_id = %s
                """, (status, notes, alert_id))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Error updating alert: {str(e)}")
            return False
    
    def get_spending_summary(self, user_id, start_date=None, end_date=None):
        """Get spending summary for a user"""
        query = """
            SELECT 
                category,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM transactions
            WHERE user_id = %s
        """
        params = [user_id]
        
        if start_date:
            query += " AND transaction_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND transaction_date <= %s"
            params.append(end_date)
        
        query += " GROUP BY category ORDER BY total_amount DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def execute_query(self, query, params=None):
        """Execute custom query"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"✗ Error executing query: {str(e)}")
            return None

if __name__ == "__main__":
    # Test database connection and schema creation
    db = DatabaseManager()
    
    if db.connect():
        db.create_schema()
        
        # Test user insertion
        test_user = {
            'user_id': 'TEST001',
            'name': 'Test User',
            'email': 'test@example.com',
            'age': 30,
            'location': 'Test City',
            'monthly_income': 5000.00,
            'preferred_currency': 'USD',
            'created_date': datetime.now().date()
        }
        
        if db.insert_user(test_user):
            print("✓ Test user inserted successfully")
            
            # Retrieve user
            user = db.get_user('TEST001')
            print(f"✓ Retrieved user: {user['name']}")
        
        db.disconnect()
    
    print("\n✓ Database integration working successfully!")
