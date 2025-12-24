"""
PostgreSQL Database Manager for Smart Finance
Handles all database operations with connection pooling and security
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import os
from dotenv import load_dotenv
import hashlib
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgreSQLManager:
    """
    PostgreSQL Database Manager with connection pooling
    Provides secure CRUD operations for users and transactions
    """

    def __init__(self):
        """Initialize database connection pool"""
        try:
            # Create connection pool (min 1, max 10 connections)
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'smart_finance'),
                user=os.getenv('DB_USER', 'finance_user'),
                password=os.getenv('DB_PASSWORD')
            )

            if self.connection_pool:
                logger.info("✅ Database connection pool created successfully")

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"❌ Error creating connection pool: {error}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self.connection_pool.getconn()
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error getting connection from pool: {error}")
            raise

    def return_connection(self, conn):
        """Return a connection to the pool"""
        try:
            self.connection_pool.putconn(conn)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error returning connection to pool: {error}")

    def close_all_connections(self):
        """Close all database connections"""
        try:
            self.connection_pool.closeall()
            logger.info("All database connections closed")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error closing connections: {error}")

    # ========================================
    # USER OPERATIONS
    # ========================================

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_user_by_email(self, email):
        """
        Get user by email

        Args:
            email (str): User email

        Returns:
            dict: User data or None if not found
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM users WHERE LOWER(email) = LOWER(%s)",
                    (email,)
                )
                user = cur.fetchone()
                return dict(user) if user else None
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error getting user by email: {error}")
            return None
        finally:
            self.return_connection(conn)

    def get_user_by_id(self, user_id):
        """
        Get user by user_id

        Args:
            user_id (str): User ID

        Returns:
            dict: User data or None if not found
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM users WHERE user_id = %s",
                    (user_id,)
                )
                user = cur.fetchone()
                return dict(user) if user else None
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error getting user by ID: {error}")
            return None
        finally:
            self.return_connection(conn)

    def create_user(self, name, email, password, monthly_income, preferred_currency='USD'):
        """
        Create a new user

        Args:
            name (str): User's full name
            email (str): User's email
            password (str): User's password (will be hashed)
            monthly_income (float): User's monthly income
            preferred_currency (str): Preferred currency (USD, IDR, CNY)

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

        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Generate next user_id
                cur.execute("SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1")
                last_user = cur.fetchone()

                if last_user:
                    last_id = last_user[0]
                    number = int(last_id[1:]) + 1
                    new_user_id = f'U{number:05d}'
                else:
                    new_user_id = 'U00001'

                # Hash password
                password_hash = self.hash_password(password)

                # Insert new user
                cur.execute(
                    """
                    INSERT INTO users (user_id, name, email, password_hash, monthly_income, preferred_currency)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING user_id
                    """,
                    (new_user_id, name, email.lower(), password_hash, monthly_income, preferred_currency)
                )

                user_id = cur.fetchone()[0]
                conn.commit()

                logger.info(f"✅ User created: {user_id} - {email}")
                return True, user_id, "Registration successful!"

        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            logger.error(f"❌ Error creating user: {error}")
            return False, None, f"Database error: {str(error)}"
        finally:
            self.return_connection(conn)

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
        """
        Get all users (for admin purposes)
        WARNING: Only use for admin functions!

        Returns:
            list: List of all users
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT user_id, name, email, monthly_income, preferred_currency, created_at FROM users ORDER BY created_at DESC")
                users = cur.fetchall()
                return [dict(user) for user in users]
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error getting all users: {error}")
            return []
        finally:
            self.return_connection(conn)

    # ========================================
    # TRANSACTION OPERATIONS
    # ========================================

    def get_user_transactions(self, user_id, start_date=None, end_date=None):
        """
        Get transactions for a specific user (FILTERED BY USER!)

        Args:
            user_id (str): User ID
            start_date (datetime): Start date filter
            end_date (datetime): End date filter

        Returns:
            list: List of transactions
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if start_date and end_date:
                    cur.execute(
                        """
                        SELECT * FROM transactions
                        WHERE user_id = %s
                        AND transaction_date BETWEEN %s AND %s
                        ORDER BY transaction_date DESC
                        """,
                        (user_id, start_date, end_date)
                    )
                else:
                    cur.execute(
                        """
                        SELECT * FROM transactions
                        WHERE user_id = %s
                        ORDER BY transaction_date DESC
                        """,
                        (user_id,)
                    )

                transactions = cur.fetchall()
                return [dict(txn) for txn in transactions]
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error getting user transactions: {error}")
            return []
        finally:
            self.return_connection(conn)

    def add_transaction(self, user_id, amount, currency, category, merchant, description=''):
        """
        Add a new transaction for a user

        Args:
            user_id (str): User ID
            amount (float): Transaction amount
            currency (str): Currency code
            category (str): Transaction category
            merchant (str): Merchant name
            description (str): Transaction description

        Returns:
            tuple: (success: bool, transaction_id: str or None, message: str)
        """
        # Validate inputs
        if not user_id:
            return False, None, "User not authenticated"

        if amount <= 0:
            return False, None, "Invalid amount"

        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Generate next transaction_id
                cur.execute("SELECT transaction_id FROM transactions ORDER BY transaction_id DESC LIMIT 1")
                last_txn = cur.fetchone()

                if last_txn:
                    last_id = last_txn[0]
                    number = int(last_id[1:]) + 1
                    new_txn_id = f'T{number:05d}'
                else:
                    new_txn_id = 'T00001'

                # Insert transaction
                cur.execute(
                    """
                    INSERT INTO transactions
                    (transaction_id, user_id, amount, currency, category, merchant, description, transaction_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING transaction_id
                    """,
                    (new_txn_id, user_id, amount, currency, category, merchant, description, datetime.now())
                )

                txn_id = cur.fetchone()[0]
                conn.commit()

                logger.info(f"✅ Transaction created: {txn_id} for user {user_id}")
                return True, txn_id, "Transaction added successfully!"

        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            logger.error(f"❌ Error adding transaction: {error}")
            return False, None, f"Database error: {str(error)}"
        finally:
            self.return_connection(conn)

    def delete_transaction(self, transaction_id, user_id):
        """
        Delete a transaction (ONLY if it belongs to the user!)

        Args:
            transaction_id (str): Transaction ID
            user_id (str): User ID (for ownership verification)

        Returns:
            tuple: (success: bool, message: str)
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # First, verify transaction belongs to user
                cur.execute(
                    "SELECT user_id FROM transactions WHERE transaction_id = %s",
                    (transaction_id,)
                )

                txn = cur.fetchone()

                if not txn:
                    return False, "Transaction not found"

                if txn['user_id'] != user_id:
                    return False, "You can only delete your own transactions"

                # Delete transaction
                cur.execute(
                    "DELETE FROM transactions WHERE transaction_id = %s",
                    (transaction_id,)
                )

                conn.commit()

                logger.info(f"✅ Transaction deleted: {transaction_id} by user {user_id}")
                return True, "Transaction deleted successfully!"

        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            logger.error(f"❌ Error deleting transaction: {error}")
            return False, f"Database error: {str(error)}"
        finally:
            self.return_connection(conn)

    def get_transaction_by_id(self, transaction_id):
        """
        Get a specific transaction by ID

        Args:
            transaction_id (str): Transaction ID

        Returns:
            dict: Transaction data or None
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM transactions WHERE transaction_id = %s",
                    (transaction_id,)
                )
                txn = cur.fetchone()
                return dict(txn) if txn else None
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error getting transaction: {error}")
            return None
        finally:
            self.return_connection(conn)

    # ========================================
    # ANALYTICS & REPORTING
    # ========================================

    def get_user_spending_summary(self, user_id, start_date=None, end_date=None):
        """
        Get spending summary for a user

        Args:
            user_id (str): User ID
            start_date (datetime): Start date
            end_date (datetime): End date

        Returns:
            dict: Spending summary
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT
                        COUNT(*) as total_transactions,
                        SUM(amount) as total_spending,
                        AVG(amount) as avg_transaction,
                        MAX(amount) as max_transaction,
                        MIN(amount) as min_transaction
                    FROM transactions
                    WHERE user_id = %s
                """

                params = [user_id]

                if start_date and end_date:
                    query += " AND transaction_date BETWEEN %s AND %s"
                    params.extend([start_date, end_date])

                cur.execute(query, params)
                summary = cur.fetchone()

                return dict(summary) if summary else {}
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error getting spending summary: {error}")
            return {}
        finally:
            self.return_connection(conn)

    def get_category_breakdown(self, user_id, start_date=None, end_date=None):
        """
        Get spending breakdown by category for a user

        Args:
            user_id (str): User ID
            start_date (datetime): Start date
            end_date (datetime): End date

        Returns:
            list: Category breakdown
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
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

                if start_date and end_date:
                    query += " AND transaction_date BETWEEN %s AND %s"
                    params.extend([start_date, end_date])

                query += " GROUP BY category ORDER BY total_amount DESC"

                cur.execute(query, params)
                breakdown = cur.fetchall()

                return [dict(row) for row in breakdown]
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error getting category breakdown: {error}")
            return []
        finally:
            self.return_connection(conn)


# Singleton instance
_db_manager = None

def get_db_manager():
    """Get or create PostgreSQLManager singleton instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = PostgreSQLManager()
    return _db_manager
