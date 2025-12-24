"""
Quick Database Check
Cek isi database SQLite
"""
from src.database.sqlite_manager import get_db_manager

print("\n" + "="*60)
print("CHECKING SQLITE DATABASE")
print("="*60)

try:
    db = get_db_manager()
    print(f"\n✅ Database: {db.db_path}")

    cursor = db.conn.cursor()

    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\n👥 Users: {user_count}")

    # Count transactions
    cursor.execute("SELECT COUNT(*) FROM transactions")
    txn_count = cursor.fetchone()[0]
    print(f"💰 Transactions: {txn_count}")

    if user_count == 0:
        print("\n⚠️  DATABASE IS EMPTY!")
        print("\nYou need to run migration first:")
        print("   python migrate_to_sqlite.py")
    else:
        print("\n✅ Database has data!")

        # Show sample users
        cursor.execute("SELECT user_id, name, email FROM users LIMIT 5")
        print("\n📋 Sample users (use these emails to login):")
        for row in cursor.fetchall():
            print(f"   {row[0]} - {row[1]} ({row[2]})")

        print("\n🔑 Default password: password123")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nDatabase might not exist yet.")
    print("Run migration first: python migrate_to_sqlite.py")

print("\n" + "="*60)
