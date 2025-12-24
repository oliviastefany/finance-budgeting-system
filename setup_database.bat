@echo off
REM Smart Finance - PostgreSQL Setup Script (Windows)
REM This script helps you setup PostgreSQL database step by step

echo ============================================================
echo SMART FINANCE - POSTGRESQL SETUP
echo ============================================================
echo.

REM Check if psql is installed
where psql >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PostgreSQL not found!
    echo.
    echo Please install PostgreSQL first:
    echo 1. Download from: https://www.postgresql.org/download/windows/
    echo 2. Run the installer
    echo 3. Add PostgreSQL bin folder to PATH
    echo.
    pause
    exit /b 1
)

echo [OK] PostgreSQL found!
echo.

REM Step 1: Create Database
echo ============================================================
echo STEP 1: Creating Database
echo ============================================================
echo.
echo This will create the 'smart_finance' database
echo You will need to enter the PostgreSQL 'postgres' user password
echo.
pause

psql -U postgres -c "CREATE DATABASE smart_finance;"
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Database might already exist or there was an error
    echo Continuing...
)

echo.
echo [OK] Database setup complete
echo.

REM Step 2: Create User
echo ============================================================
echo STEP 2: Creating User
echo ============================================================
echo.
pause

psql -U postgres -c "CREATE USER finance_user WITH PASSWORD 'SmartFinance2024!Secure';"
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] User might already exist or there was an error
    echo Continuing...
)

echo.
echo Granting permissions...
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE smart_finance TO finance_user;"
psql -U postgres -d smart_finance -c "GRANT ALL ON SCHEMA public TO finance_user;"

echo.
echo [OK] User setup complete
echo.

REM Step 3: Create Schema
echo ============================================================
echo STEP 3: Creating Database Schema (Tables)
echo ============================================================
echo.
pause

psql -U finance_user -d smart_finance -f database_schema.sql
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to create schema
    echo Please check database_schema.sql file
    pause
    exit /b 1
)

echo.
echo [OK] Database schema created
echo.

REM Step 4: Test Connection
echo ============================================================
echo STEP 4: Testing Connection
echo ============================================================
echo.
pause

python test_connection.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Connection test failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo NEXT STEPS
echo ============================================================
echo.
echo 1. Run migration to import CSV data:
echo    python migrate_to_postgres.py
echo.
echo 2. Update .env file:
echo    DATA_STORAGE_MODE=postgresql
echo.
echo 3. Run your dashboard:
echo    run_dashboard.bat
echo.
echo ============================================================
echo SETUP COMPLETE!
echo ============================================================
pause
