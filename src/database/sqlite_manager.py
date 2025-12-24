"""
SQLite Database Manager for Smart Finance
Simple, no server needed, perfect for development!
"""
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database file location
DB_DIR = Path(__file__).resolve().parent.parent.parent / 'data'
DB_DIR.mkdir(exist_ok=True)
DB_FILE = DB_DIR / 'smart_finance.db'


class SQLiteManager:
    """
    SQLite Database Manager
    Simple, lightweight, no server required!
    """

    def __init__(self, db_path=None):
        """Initialize SQLite database"""
        self.db_path = db_path or DB_FILE
        self.conn = None
        self.connect()
        self.create_tables()
        logger.info(f"✅ SQLite database initialized: {self.db_path}")

    def connect(self):
        """Connect to SQLite database"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            logger.info("✅ Connected to SQLite database")
        except Exception as e:
            logger.error(f"❌ Error connecting to SQLite: {e}")
            raise

    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            cursor = self.conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    monthly_income REAL DEFAULT 0.0,
                    preferred_currency TEXT DEFAULT 'USD',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    category TEXT NOT NULL,
                    merchant TEXT,
                    description TEXT,
                    transaction_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)")

            self.conn.commit()
            logger.info("✅ Database tables created/verified")

        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
            raise

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    # ========================================
    # USER OPERATIONS
    # ========================================

    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Get user by user_id"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    def create_user(self, name, email, password, monthly_income, preferred_currency='USD'):
        """
        Create a new user

        Args:
            name (str): User's full name
            email (str): User's email
            password (str): User's password (will be hashed)
            monthly_income (float): User's monthly income
            preferred_currency (str): Preferred currency

        Returns:
            tuple: (success: bool, user_id: str or None, message: str)
        """
        # Validate inputs
        if not name or not email or not password:
            return False, None, "All fields are required"

        if len(password) < 6:
            return False, None, "Password must be at least 6 characters"

        # Check if email already exists
        if self.get_user_by_email(email):
            return False, None, "Email already registered"

        try:
            cursor = self.conn.cursor()

            # Generate next user_id
            cursor.execute("SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1")
            last_user = cursor.fetchone()

            if last_user:
                last_id = last_user[0]
                number = int(last_id[1:]) + 1
                new_user_id = f'U{number:05d}'
            else:
                new_user_id = 'U00001'

            # Hash password
            password_hash = self.hash_password(password)

            # Insert new user
            cursor.execute(
                """
                INSERT INTO users (user_id, name, email, password_hash, monthly_income, preferred_currency)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (new_user_id, name, email.lower(), password_hash, monthly_income, preferred_currency)
            )

            self.conn.commit()
            logger.info(f"✅ User created: {new_user_id} - {email}")
            return True, new_user_id, "Registration successful!"

        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error creating user: {e}")
            return False, None, f"Database error: {str(e)}"

    def verify_login(self, email, password):
        """
        Verify user login credentials

        Args:
            email (str): User email
            password (str): User password

        Returns:
            tuple: (success: bool, user_id: str or None, message: str)
        """
        user = self.get_user_by_email(email)

        if not user:
            return False, None, "Email not found"

        # Verify password
        password_hash = self.hash_password(password)
        if user['password_hash'] != password_hash:
            return False, None, "Incorrect password"

        return True, user['user_id'], "Login successful!"

    def get_all_users(self):
        """Get all users (for admin purposes)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT user_id, name, email, monthly_income, preferred_currency, created_at FROM users ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    # ========================================
    # TRANSACTION OPERATIONS
    # ========================================

    def get_user_transactions(self, user_id, start_date=None, end_date=None):
        """Get transactions for a specific user"""
        try:
            cursor = self.conn.cursor()

            if start_date and end_date:
                cursor.execute(
                    """
                    SELECT * FROM transactions
                    WHERE user_id = ?
                    AND transaction_date BETWEEN ? AND ?
                    ORDER BY transaction_date DESC
                    """,
                    (user_id, start_date, end_date)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM transactions
                    WHERE user_id = ?
                    ORDER BY transaction_date DESC
                    """,
                    (user_id,)
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting user transactions: {e}")
            return []

    def add_transaction(self, user_id, amount, currency, category, merchant, description=''):
        """Add a new transaction for a user"""
        # Validate inputs
        if not user_id:
            return False, None, "User not authenticated"

        if amount <= 0:
            return False, None, "Invalid amount"

        try:
            cursor = self.conn.cursor()

            # Generate next transaction_id
            cursor.execute("SELECT transaction_id FROM transactions ORDER BY transaction_id DESC LIMIT 1")
            last_txn = cursor.fetchone()

            if last_txn:
                last_id = last_txn[0]
                number = int(last_id[1:]) + 1
                new_txn_id = f'T{number:05d}'
            else:
                new_txn_id = 'T00001'

            # Insert transaction
            cursor.execute(
                """
                INSERT INTO transactions
                (transaction_id, user_id, amount, currency, category, merchant, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (new_txn_id, user_id, amount, currency, category, merchant, description, datetime.now())
            )

            self.conn.commit()
            logger.info(f"✅ Transaction created: {new_txn_id} for user {user_id}")
            return True, new_txn_id, "Transaction added successfully!"

        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error adding transaction: {e}")
            return False, None, f"Database error: {str(e)}"

    def delete_transaction(self, transaction_id, user_id):
        """Delete a transaction (only if it belongs to the user!)"""
        try:
            cursor = self.conn.cursor()

            # First, verify transaction belongs to user
            cursor.execute("SELECT user_id FROM transactions WHERE transaction_id = ?", (transaction_id,))
            txn = cursor.fetchone()

            if not txn:
                return False, "Transaction not found"

            if txn[0] != user_id:
                return False, "You can only delete your own transactions"

            # Delete transaction
            cursor.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
            self.conn.commit()

            logger.info(f"✅ Transaction deleted: {transaction_id} by user {user_id}")
            return True, "Transaction deleted successfully!"

        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error deleting transaction: {e}")
            return False, f"Database error: {str(e)}"

    def get_transaction_by_id(self, transaction_id):
        """Get a specific transaction by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting transaction: {e}")
            return None

    # ========================================
    # ANALYTICS & REPORTING
    # ========================================

    def get_user_spending_summary(self, user_id, start_date=None, end_date=None):
        """Get spending summary for a user"""
        try:
            cursor = self.conn.cursor()

            if start_date and end_date:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_transactions,
                        SUM(amount) as total_spending,
                        AVG(amount) as avg_transaction,
                        MAX(amount) as max_transaction,
                        MIN(amount) as min_transaction
                    FROM transactions
                    WHERE user_id = ?
                    AND transaction_date BETWEEN ? AND ?
                    """,
                    (user_id, start_date, end_date)
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_transactions,
                        SUM(amount) as total_spending,
                        AVG(amount) as avg_transaction,
                        MAX(amount) as max_transaction,
                        MIN(amount) as min_transaction
                    FROM transactions
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )

            row = cursor.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            logger.error(f"Error getting spending summary: {e}")
            return {}

    def get_category_breakdown(self, user_id, start_date=None, end_date=None):
        """Get spending breakdown by category for a user"""
        try:
            cursor = self.conn.cursor()

            if start_date and end_date:
                cursor.execute(
                    """
                    SELECT
                        category,
                        COUNT(*) as transaction_count,
                        SUM(amount) as total_amount,
                        AVG(amount) as avg_amount
                    FROM transactions
                    WHERE user_id = ?
                    AND transaction_date BETWEEN ? AND ?
                    GROUP BY category
                    ORDER BY total_amount DESC
                    """,
                    (user_id, start_date, end_date)
                )
            else:
                cursor.execute(
                    """
                    SELECT
                        category,
                        COUNT(*) as transaction_count,
                        SUM(amount) as total_amount,
                        AVG(amount) as avg_amount
                    FROM transactions
                    WHERE user_id = ?
                    GROUP BY category
                    ORDER BY total_amount DESC
                    """,
                    (user_id,)
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting category breakdown: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Singleton instance
_db_manager = None

def get_db_manager():
    """Get or create SQLiteManager singleton instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = SQLiteManager()
    return _db_manager
