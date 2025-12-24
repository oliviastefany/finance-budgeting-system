#!/bin/bash
# Smart Finance - PostgreSQL Setup Script (Linux/macOS)
# This script helps you setup PostgreSQL database step by step

echo "============================================================"
echo "SMART FINANCE - POSTGRESQL SETUP"
echo "============================================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}[ERROR] PostgreSQL not found!${NC}"
    echo
    echo "Please install PostgreSQL first:"
    echo "Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
    echo "macOS: brew install postgresql@16"
    echo
    exit 1
fi

echo -e "${GREEN}[OK] PostgreSQL found!${NC}"
echo

# Step 1: Create Database
echo "============================================================"
echo "STEP 1: Creating Database"
echo "============================================================"
echo
echo "This will create the 'smart_finance' database"
echo "Press Enter to continue..."
read

sudo -u postgres psql -c "CREATE DATABASE smart_finance;"
if [ $? -ne 0 ]; then
    echo
    echo -e "${YELLOW}[WARNING] Database might already exist or there was an error${NC}"
    echo "Continuing..."
fi

echo
echo -e "${GREEN}[OK] Database setup complete${NC}"
echo

# Step 2: Create User
echo "============================================================"
echo "STEP 2: Creating User"
echo "============================================================"
echo
echo "Press Enter to continue..."
read

sudo -u postgres psql -c "CREATE USER finance_user WITH PASSWORD 'SmartFinance2024!Secure';"
if [ $? -ne 0 ]; then
    echo
    echo -e "${YELLOW}[WARNING] User might already exist or there was an error${NC}"
    echo "Continuing..."
fi

echo
echo "Granting permissions..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE smart_finance TO finance_user;"
sudo -u postgres psql -d smart_finance -c "GRANT ALL ON SCHEMA public TO finance_user;"

echo
echo -e "${GREEN}[OK] User setup complete${NC}"
echo

# Step 3: Create Schema
echo "============================================================"
echo "STEP 3: Creating Database Schema (Tables)"
echo "============================================================"
echo
echo "Press Enter to continue..."
read

PGPASSWORD='SmartFinance2024!Secure' psql -U finance_user -d smart_finance -f database_schema.sql
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}[ERROR] Failed to create schema${NC}"
    echo "Please check database_schema.sql file"
    exit 1
fi

echo
echo -e "${GREEN}[OK] Database schema created${NC}"
echo

# Step 4: Test Connection
echo "============================================================"
echo "STEP 4: Testing Connection"
echo "============================================================"
echo
echo "Press Enter to continue..."
read

python3 test_connection.py
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}[ERROR] Connection test failed${NC}"
    exit 1
fi

echo
echo "============================================================"
echo "NEXT STEPS"
echo "============================================================"
echo
echo "1. Run migration to import CSV data:"
echo "   python3 migrate_to_postgres.py"
echo
echo "2. Update .env file:"
echo "   DATA_STORAGE_MODE=postgresql"
echo
echo "3. Run your dashboard:"
echo "   ./run_dashboard.sh"
echo
echo "============================================================"
echo "SETUP COMPLETE!"
echo "============================================================"
