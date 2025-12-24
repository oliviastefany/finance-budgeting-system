"""
Test PostgreSQL Database Connection
Quick script to verify database setup and connection
"""
import psycopg2
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for Windows color support
init()

# Load environment variables
load_dotenv()


def test_connection():
    """Test database connection"""
    print("\n" + "="*60)
    print("TESTING POSTGRESQL CONNECTION")
    print("="*60)

    # Check environment variables
    print("\n📋 Checking environment variables...")
    db_config = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD')
    }

    missing = [key for key, value in db_config.items() if not value]
    if missing:
        print(f"{Fore.RED}❌ Missing environment variables: {', '.join(missing)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️  Please check your .env file{Style.RESET_ALL}")
        return False

    print(f"{Fore.GREEN}✅ All environment variables found{Style.RESET_ALL}")
    print(f"   Host: {db_config['DB_HOST']}")
    print(f"   Port: {db_config['DB_PORT']}")
    print(f"   Database: {db_config['DB_NAME']}")
    print(f"   User: {db_config['DB_USER']}")

    # Test connection
    print(f"\n🔌 Attempting to connect to database...")
    try:
        conn = psycopg2.connect(
            host=db_config['DB_HOST'],
            port=db_config['DB_PORT'],
            database=db_config['DB_NAME'],
            user=db_config['DB_USER'],
            password=db_config['DB_PASSWORD']
        )

        print(f"{Fore.GREEN}✅ Database connection successful!{Style.RESET_ALL}")

        # Test queries
        cur = conn.cursor()

        # Check if tables exist
        print(f"\n📊 Checking database tables...")
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cur.fetchall()

        if not tables:
            print(f"{Fore.YELLOW}⚠️  No tables found. Run database_schema.sql first!{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Found {len(tables)} tables:{Style.RESET_ALL}")
            for table in tables:
                print(f"   - {table[0]}")

        # Check data
        if tables:
            print(f"\n📈 Checking data...")

            # Count users
            cur.execute("SELECT COUNT(*) FROM users")
            user_count = cur.fetchone()[0]
            print(f"   Users: {user_count}")

            # Count transactions
            cur.execute("SELECT COUNT(*) FROM transactions")
            txn_count = cur.fetchone()[0]
            print(f"   Transactions: {txn_count}")

            if user_count == 0:
                print(f"{Fore.YELLOW}⚠️  No data found. Run migrate_to_postgres.py to import data!{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✅ Database has data!{Style.RESET_ALL}")

                # Show sample users
                print(f"\n👥 Sample users:")
                cur.execute("""
                    SELECT user_id, name, email, preferred_currency
                    FROM users
                    LIMIT 5
                """)
                users = cur.fetchall()
                for user in users:
                    print(f"   {user[0]} - {user[1]} ({user[2]}) - {user[3]}")

        cur.close()
        conn.close()

        print(f"\n{Fore.GREEN}{'='*60}")
        print("✅ ALL TESTS PASSED!")
        print(f"{'='*60}{Style.RESET_ALL}")
        print("\nYou can now:")
        print("1. Update DATA_STORAGE_MODE=postgresql in .env")
        print("2. Run your dashboard: run_dashboard.bat")
        print("3. Login with any user (password: password123)")

        return True

    except psycopg2.OperationalError as e:
        print(f"{Fore.RED}❌ Connection failed!{Style.RESET_ALL}")
        print(f"\nError: {str(e)}")
        print(f"\n{Fore.YELLOW}Troubleshooting steps:{Style.RESET_ALL}")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if database 'smart_finance' exists")
        print("3. Verify credentials in .env file")
        print("4. Check if user 'finance_user' has correct permissions")
        return False

    except Exception as e:
        print(f"{Fore.RED}❌ Unexpected error: {str(e)}{Style.RESET_ALL}")
        return False


def main():
    """Main function"""
    try:
        test_connection()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
