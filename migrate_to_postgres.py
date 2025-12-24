"""
Migration Script: CSV to PostgreSQL
Migrate existing CSV data to PostgreSQL database
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
from dotenv import load_dotenv
from pathlib import Path
import hashlib
from datetime import datetime

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'config' / 'data' / 'raw'
USERS_CSV = DATA_DIR / 'users.csv'
TRANSACTIONS_CSV = DATA_DIR / 'transactions.csv'


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'smart_finance'),
            user=os.getenv('DB_USER', 'finance_user'),
            password=os.getenv('DB_PASSWORD')
        )
        print("✅ Connected to PostgreSQL database")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"❌ Error connecting to database: {error}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if database 'smart_finance' exists")
        print("3. Verify credentials in .env file")
        print("4. Run database setup script first")
        return None


def migrate_users(conn):
    """Migrate users from CSV to PostgreSQL"""
    print("\n" + "="*50)
    print("MIGRATING USERS")
    print("="*50)

    if not USERS_CSV.exists():
        print(f"❌ Users CSV file not found: {USERS_CSV}")
        return False

    # Read CSV
    users_df = pd.read_csv(USERS_CSV)
    print(f"📊 Found {len(users_df)} users in CSV")

    # Check if password_hash column exists
    if 'password_hash' not in users_df.columns:
        print("⚠️  No password_hash column found. Creating default passwords...")
        users_df['password_hash'] = hash_password('password123')

    # Prepare data for insertion
    users_data = []
    for _, row in users_df.iterrows():
        user_data = (
            row['user_id'],
            row['name'],
            row['email'].lower(),
            row.get('password_hash', hash_password('password123')),
            float(row.get('monthly_income', 0)),
            row.get('preferred_currency', 'USD')
        )
        users_data.append(user_data)

    # Insert into database
    try:
        cur = conn.cursor()

        # Clear existing data (optional - comment out if you want to keep existing data)
        cur.execute("DELETE FROM users")
        print("🗑️  Cleared existing users")

        # Insert users
        insert_query = """
            INSERT INTO users (user_id, name, email, password_hash, monthly_income, preferred_currency)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                name = EXCLUDED.name,
                email = EXCLUDED.email,
                password_hash = EXCLUDED.password_hash,
                monthly_income = EXCLUDED.monthly_income,
                preferred_currency = EXCLUDED.preferred_currency
        """

        execute_batch(cur, insert_query, users_data)
        conn.commit()

        print(f"✅ Migrated {len(users_data)} users successfully!")

        # Show sample
        cur.execute("SELECT user_id, name, email, preferred_currency FROM users LIMIT 5")
        samples = cur.fetchall()
        print("\n📋 Sample users:")
        for user in samples:
            print(f"   {user[0]} - {user[1]} ({user[2]}) - {user[3]}")

        cur.close()
        return True

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        print(f"❌ Error migrating users: {error}")
        return False


def migrate_transactions(conn):
    """Migrate transactions from CSV to PostgreSQL"""
    print("\n" + "="*50)
    print("MIGRATING TRANSACTIONS")
    print("="*50)

    if not TRANSACTIONS_CSV.exists():
        print(f"❌ Transactions CSV file not found: {TRANSACTIONS_CSV}")
        return False

    # Read CSV
    transactions_df = pd.read_csv(TRANSACTIONS_CSV)
    print(f"📊 Found {len(transactions_df)} transactions in CSV")

    # Convert transaction_date to datetime
    transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])

    # Prepare data for insertion
    transactions_data = []
    for _, row in transactions_df.iterrows():
        txn_data = (
            row['transaction_id'],
            row['user_id'],
            float(row['amount']),
            row.get('currency', 'USD'),
            row['category'],
            row.get('merchant', ''),
            row.get('description', ''),
            row['transaction_date']
        )
        transactions_data.append(txn_data)

    # Insert into database
    try:
        cur = conn.cursor()

        # Clear existing data (optional)
        cur.execute("DELETE FROM transactions")
        print("🗑️  Cleared existing transactions")

        # Insert transactions in batches
        insert_query = """
            INSERT INTO transactions
            (transaction_id, user_id, amount, currency, category, merchant, description, transaction_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                amount = EXCLUDED.amount,
                currency = EXCLUDED.currency,
                category = EXCLUDED.category,
                merchant = EXCLUDED.merchant,
                description = EXCLUDED.description,
                transaction_date = EXCLUDED.transaction_date
        """

        execute_batch(cur, insert_query, transactions_data, page_size=1000)
        conn.commit()

        print(f"✅ Migrated {len(transactions_data)} transactions successfully!")

        # Show statistics
        cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT user_id) as unique_users,
                SUM(amount) as total_amount,
                MIN(transaction_date) as earliest,
                MAX(transaction_date) as latest
            FROM transactions
        """)

        stats = cur.fetchone()
        print("\n📊 Transaction Statistics:")
        print(f"   Total transactions: {stats[0]}")
        print(f"   Unique users: {stats[1]}")
        print(f"   Total amount: ${stats[2]:,.2f}")
        print(f"   Date range: {stats[3]} to {stats[4]}")

        # Show top categories
        cur.execute("""
            SELECT category, COUNT(*) as count, SUM(amount) as total
            FROM transactions
            GROUP BY category
            ORDER BY total DESC
            LIMIT 5
        """)

        categories = cur.fetchall()
        print("\n📈 Top 5 Categories:")
        for cat in categories:
            print(f"   {cat[0]}: {cat[1]} transactions (${cat[2]:,.2f})")

        cur.close()
        return True

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        print(f"❌ Error migrating transactions: {error}")
        return False


def verify_migration(conn):
    """Verify migration was successful"""
    print("\n" + "="*50)
    print("VERIFYING MIGRATION")
    print("="*50)

    try:
        cur = conn.cursor()

        # Count users
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        print(f"✅ Users in database: {user_count}")

        # Count transactions
        cur.execute("SELECT COUNT(*) FROM transactions")
        txn_count = cur.fetchone()[0]
        print(f"✅ Transactions in database: {txn_count}")

        # Check for orphaned transactions
        cur.execute("""
            SELECT COUNT(*)
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.user_id
            WHERE u.user_id IS NULL
        """)
        orphaned = cur.fetchone()[0]

        if orphaned > 0:
            print(f"⚠️  Warning: {orphaned} orphaned transactions (user not found)")
        else:
            print("✅ No orphaned transactions")

        # Test a sample query
        cur.execute("""
            SELECT u.name, COUNT(t.transaction_id) as txn_count, SUM(t.amount) as total
            FROM users u
            LEFT JOIN transactions t ON u.user_id = t.user_id
            GROUP BY u.user_id, u.name
            ORDER BY total DESC
            LIMIT 5
        """)

        print("\n📊 Top 5 Users by Spending:")
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[1]} transactions (${row[2]:,.2f})")

        cur.close()
        return True

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"❌ Error verifying migration: {error}")
        return False


def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("SMART FINANCE - CSV TO POSTGRESQL MIGRATION")
    print("="*60)
    print(f"CSV Data Directory: {DATA_DIR}")
    print(f"Users CSV: {USERS_CSV}")
    print(f"Transactions CSV: {TRANSACTIONS_CSV}")

    # Connect to database
    conn = connect_to_database()
    if not conn:
        print("\n❌ Migration failed: Cannot connect to database")
        return

    try:
        # Migrate users
        if not migrate_users(conn):
            print("\n❌ Migration failed: Error migrating users")
            return

        # Migrate transactions
        if not migrate_transactions(conn):
            print("\n❌ Migration failed: Error migrating transactions")
            return

        # Verify migration
        verify_migration(conn)

        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("1. Update your application to use PostgreSQL")
        print("2. Update DATA_STORAGE_MODE in .env to 'postgresql'")
        print("3. Test login with existing users (password: password123)")
        print("4. Backup your PostgreSQL database regularly")

    except Exception as error:
        print(f"\n❌ Unexpected error: {error}")

    finally:
        if conn:
            conn.close()
            print("\n🔌 Database connection closed")


if __name__ == "__main__":
    main()
