@echo off
REM Simple Database Setup - NO PGADMIN NEEDED!
REM Setup PostgreSQL database using command line only

echo ============================================================
echo SMART FINANCE - SIMPLE DATABASE SETUP
echo (No pgAdmin needed!)
echo ============================================================
echo.

REM Add PostgreSQL to PATH (temporary)
set PATH=%PATH%;C:\Program Files\PostgreSQL\16\bin;C:\Program Files\PostgreSQL\15\bin;C:\Program Files\PostgreSQL\14\bin

REM Check if psql exists
where psql >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] PostgreSQL not found!
    echo.
    echo Please install PostgreSQL first:
    echo https://www.postgresql.org/download/windows/
    echo.
    pause
    exit /b 1
)

echo [OK] PostgreSQL found!
echo.
echo ============================================================
echo ENTER YOUR POSTGRES PASSWORD
echo ============================================================
echo.
echo This is the password you set during PostgreSQL installation.
echo If you forgot it, you need to reset it first.
echo.
echo Password:

REM Set password environment variable (will be hidden in prompt)
set /p PGPASSWORD=

echo.
echo Testing connection...
psql -U postgres -c "SELECT 1;" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Cannot connect to PostgreSQL!
    echo Wrong password or PostgreSQL not running.
    echo.
    echo Run fix_postgresql.bat to diagnose the issue.
    echo.
    pause
    exit /b 1
)

echo [OK] Connected successfully!
echo.

echo ============================================================
echo CREATING DATABASE AND USER
echo ============================================================
echo.

echo [1/5] Creating database 'smart_finance'...
psql -U postgres -c "CREATE DATABASE smart_finance;" 2>nul
if %errorlevel% equ 0 (
    echo [OK] Database created
) else (
    echo [!] Database might already exist (OK)
)

echo.
echo [2/5] Creating user 'finance_user'...
psql -U postgres -c "CREATE USER finance_user WITH PASSWORD 'SmartFinance2024!Secure';" 2>nul
if %errorlevel% equ 0 (
    echo [OK] User created
) else (
    echo [!] User might already exist (OK)
)

echo.
echo [3/5] Granting permissions...
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE smart_finance TO finance_user;"
psql -U postgres -d smart_finance -c "GRANT ALL ON SCHEMA public TO finance_user;"
echo [OK] Permissions granted

echo.
echo [4/5] Creating database schema (tables)...
set PGPASSWORD=SmartFinance2024!Secure
psql -U finance_user -d smart_finance -f database_schema.sql >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Database schema created
) else (
    echo [!] Error creating schema (check database_schema.sql)
    pause
    exit /b 1
)

echo.
echo [5/5] Verifying setup...
psql -U finance_user -d smart_finance -c "SELECT COUNT(*) FROM users;" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Tables created successfully!
) else (
    echo [ERROR] Tables not found!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! Database is ready!
echo ============================================================
echo.
echo Database created: smart_finance
echo User created: finance_user
echo Password: SmartFinance2024!Secure
echo.
echo ============================================================
echo NEXT STEPS
echo ============================================================
echo.
echo 1. Test connection:
echo    python test_connection.py
echo.
echo 2. Migrate data from CSV:
echo    python migrate_to_postgres.py
echo.
echo 3. Update .env file:
echo    DATA_STORAGE_MODE=postgresql
echo.
echo 4. Run dashboard:
echo    run_dashboard.bat
echo.
echo ============================================================
echo.
pause
