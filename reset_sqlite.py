"""
Reset SQLite Database
Hapus database lama dan buat ulang dari awal
"""
import os
from pathlib import Path

# Database file location
DB_DIR = Path(__file__).resolve().parent / 'data'
DB_FILE = DB_DIR / 'smart_finance.db'

print("\n" + "="*60)
print("RESET SQLITE DATABASE")
print("="*60)
print(f"\nDatabase file: {DB_FILE}")

if DB_FILE.exists():
    print(f"\n⚠️  Database file exists. Size: {DB_FILE.stat().st_size / 1024:.2f} KB")
    print("\nDeleting old database...")

    try:
        os.remove(DB_FILE)
        print("✅ Old database deleted!")
    except Exception as e:
        print(f"❌ Error deleting database: {e}")
        print("\nTry manually:")
        print(f"   del {DB_FILE}")
        exit(1)
else:
    print("\n✅ No existing database found")

print("\n" + "="*60)
print("✅ DATABASE RESET COMPLETE!")
print("="*60)
print("\nNext step: Run migration")
print("   python migrate_to_sqlite.py")
