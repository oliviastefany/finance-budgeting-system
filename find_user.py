"""
Find User in Database
Cari user berdasarkan email atau nama
"""
import sys
from src.database.sqlite_manager import get_db_manager

# Get search term from command line
search = sys.argv[1] if len(sys.argv) > 1 else "olivia"

print("\n" + "="*60)
print(f"SEARCHING FOR: {search}")
print("="*60)

try:
    db = get_db_manager()
    cursor = db.conn.cursor()

    # Search by email or name
    cursor.execute("""
        SELECT user_id, name, email, preferred_currency
        FROM users
        WHERE email LIKE ? OR name LIKE ?
        ORDER BY user_id
    """, (f'%{search}%', f'%{search}%'))

    results = cursor.fetchall()

    if results:
        print(f"\n✅ Found {len(results)} user(s):\n")
        for row in results:
            print(f"User ID:   {row[0]}")
            print(f"Name:      {row[1]}")
            print(f"Email:     {row[2]}")
            print(f"Currency:  {row[3]}")
            print(f"Password:  password123 (default)")
            print("-" * 60)
    else:
        print(f"\n❌ No users found matching '{search}'")
        print("\nTry searching for other names/emails.")

        # Show sample users
        cursor.execute("SELECT user_id, name, email FROM users LIMIT 10")
        samples = cursor.fetchall()

        print("\n📋 Here are some available users:")
        for row in samples:
            print(f"   {row[2]} - {row[1]}")

except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
