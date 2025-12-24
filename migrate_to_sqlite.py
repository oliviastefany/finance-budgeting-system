"""
Migration Script: CSV to SQLite
Migrate existing CSV data to SQLite database
Super simple, no server needed!
"""
import pandas as pd
import hashlib
from pathlib import Path
from src.database.sqlite_manager import get_db_manager

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'config' / 'data' / 'raw'
USERS_CSV = DATA_DIR / 'users.csv'
TRANSACTIONS_CSV = DATA_DIR / 'transactions.csv'


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def migrate_users(db):
    """Migrate users from CSV to SQLite"""
    print("\n" + "="*60)
    print("MIGRATING USERS")
    print("="*60)

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

    # Clear existing users first
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM users")
    db.conn.commit()
    print("🗑️  Cleared existing users")

    # Insert users
    success_count = 0
    error_count = 0

    for _, row in users_df.iterrows():
        try:

            # Create user
            cursor = db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (user_id, name, email, password_hash, monthly_income, preferred_currency)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    row['user_id'],
                    row['name'],
                    row['email'].lower(),
                    row.get('password_hash', hash_password('password123')),
                    float(row.get('monthly_income', 0)),
                    row.get('preferred_currency', 'USD')
                )
            )
            db.conn.commit()
            success_count += 1

        except Exception as e:
            error_count += 1
            print(f"❌ Error migrating user {row.get('email', 'unknown')}: {e}")

    print(f"\n✅ Migrated {success_count} users successfully!")
    if error_count > 0:
        print(f"⚠️  {error_count} errors")

    # Show sample
    cursor = db.conn.cursor()
    cursor.execute("SELECT user_id, name, email, preferred_currency FROM users LIMIT 5")
    samples = cursor.fetchall()
    print("\n📋 Sample users:")
    for user in samples:
        print(f"   {user[0]} - {user[1]} ({user[2]}) - {user[3]}")

    return True


def migrate_transactions(db):
    """Migrate transactions from CSV to SQLite"""
    print("\n" + "="*60)
    print("MIGRATING TRANSACTIONS")
    print("="*60)

    if not TRANSACTIONS_CSV.exists():
        print(f"❌ Transactions CSV file not found: {TRANSACTIONS_CSV}")
        return False

    # Read CSV
    transactions_df = pd.read_csv(TRANSACTIONS_CSV)
    print(f"📊 Found {len(transactions_df)} transactions in CSV")

    # Convert transaction_date to datetime
    transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])

    # Clear existing transactions first
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM transactions")
    db.conn.commit()
    print("🗑️  Cleared existing transactions")

    # Insert transactions in batches
    success_count = 0
    error_count = 0
    batch_size = 1000

    for i in range(0, len(transactions_df), batch_size):
        batch = transactions_df.iloc[i:i+batch_size]

        for _, row in batch.iterrows():
            try:
                cursor.execute(
                    """
                    INSERT INTO transactions
                    (transaction_id, user_id, amount, currency, category, merchant, description, transaction_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row['transaction_id'],
                        row['user_id'],
                        float(row['amount']),
                        row.get('currency', 'USD'),
                        row['category'],
                        row.get('merchant', ''),
                        row.get('description', ''),
                        row['transaction_date']
                    )
                )
                success_count += 1

            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only show first 5 errors
                    print(f"❌ Error: {e}")

        db.conn.commit()
        print(f"Progress: {min(i+batch_size, len(transactions_df))}/{len(transactions_df)} transactions...")

    print(f"\n✅ Migrated {success_count} transactions successfully!")
    if error_count > 0:
        print(f"⚠️  {error_count} errors (duplicates or invalid data)")

    # Show statistics
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT user_id) as unique_users,
            SUM(amount) as total_amount,
            MIN(transaction_date) as earliest,
            MAX(transaction_date) as latest
        FROM transactions
    """)

    stats = cursor.fetchone()
    print("\n📊 Transaction Statistics:")
    print(f"   Total transactions: {stats[0]}")
    print(f"   Unique users: {stats[1]}")
    if stats[2] is not None:
        print(f"   Total amount: ${stats[2]:,.2f}")
    else:
        print(f"   Total amount: $0.00")
    if stats[3] and stats[4]:
        print(f"   Date range: {stats[3]} to {stats[4]}")
    else:
        print(f"   Date range: No transactions")

    # Show top categories
    cursor.execute("""
        SELECT category, COUNT(*) as count, SUM(amount) as total
        FROM transactions
        GROUP BY category
        ORDER BY total DESC
        LIMIT 5
    """)

    categories = cursor.fetchall()
    print("\n📈 Top 5 Categories:")
    for cat in categories:
        print(f"   {cat[0]}: {cat[1]} transactions (${cat[2]:,.2f})")

    return True


def verify_migration(db):
    """Verify migration was successful"""
    print("\n" + "="*60)
    print("VERIFYING MIGRATION")
    print("="*60)

    try:
        cursor = db.conn.cursor()

        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users in database: {user_count}")

        # Count transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        txn_count = cursor.fetchone()[0]
        print(f"✅ Transactions in database: {txn_count}")

        # Check for orphaned transactions
        cursor.execute("""
            SELECT COUNT(*)
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.user_id
            WHERE u.user_id IS NULL
        """)
        orphaned = cursor.fetchone()[0]

        if orphaned > 0:
            print(f"⚠️  Warning: {orphaned} orphaned transactions (user not found)")
        else:
            print("✅ No orphaned transactions")

        # Test a sample query
        cursor.execute("""
            SELECT u.name, COUNT(t.transaction_id) as txn_count, SUM(t.amount) as total
            FROM users u
            LEFT JOIN transactions t ON u.user_id = t.user_id
            GROUP BY u.user_id, u.name
            ORDER BY total DESC
            LIMIT 5
        """)

        print("\n📊 Top 5 Users by Spending:")
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]} transactions (${row[2] if row[2] else 0:,.2f})")

        return True

    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False


def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("SMART FINANCE - CSV TO SQLITE MIGRATION")
    print("="*60)
    print(f"CSV Data Directory: {DATA_DIR}")
    print(f"Users CSV: {USERS_CSV}")
    print(f"Transactions CSV: {TRANSACTIONS_CSV}")

    try:
        # Initialize database
        print("\n🔌 Initializing SQLite database...")
        db = get_db_manager()
        print(f"✅ Database file: {db.db_path}")

        # Migrate users
        if not migrate_users(db):
            print("\n❌ Migration failed: Error migrating users")
            return

        # Migrate transactions
        if not migrate_transactions(db):
            print("\n❌ Migration failed: Error migrating transactions")
            return

        # Verify migration
        verify_migration(db)

        print("\n" + "="*60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nDatabase location:")
        print(f"   {db.db_path}")
        print("\nNext steps:")
        print("1. Update your .env file:")
        print("   DATA_STORAGE_MODE=sqlite")
        print("2. Run your dashboard:")
        print("   run_dashboard.bat")
        print("3. Login with any user:")
        print("   Email: Any email from CSV")
        print("   Password: password123")
        print("\n✨ SQLite is ready to use! No server needed!")

    except Exception as error:
        print(f"\n❌ Unexpected error: {error}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
