@echo off
REM Smart Finance - SQLite Setup Script
REM Super simple setup - NO server needed!

echo ============================================================
echo SMART FINANCE - SQLITE SETUP
echo ============================================================
echo.
echo SQLite is the EASIEST way to setup database!
echo.
echo  [CHECKMARK] No PostgreSQL server needed
echo  [CHECKMARK] No password to remember
echo  [CHECKMARK] Just one file
echo  [CHECKMARK] Works immediately!
echo.
echo ============================================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python first: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Install/verify dependencies
echo [1/4] Installing dependencies...
pip install python-dotenv >nul 2>&1
echo [OK] Dependencies ready
echo.

REM Create database and migrate data
echo [2/4] Creating SQLite database and migrating data...
echo.
python migrate_to_sqlite.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Migration failed!
    echo Please check error messages above.
    pause
    exit /b 1
)

echo.
echo [OK] Database created and data migrated!
echo.

REM Update .env file
echo [3/4] Updating .env configuration...

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env >nul 2>&1
)

REM Update DATA_STORAGE_MODE to sqlite
powershell -Command "(gc .env) -replace 'DATA_STORAGE_MODE=.*', 'DATA_STORAGE_MODE=sqlite' | Out-File -encoding ASCII .env"

echo [OK] Configuration updated (DATA_STORAGE_MODE=sqlite)
echo.

REM Test connection
echo [4/4] Testing database connection...
python -c "from src.database.sqlite_manager import get_db_manager; db = get_db_manager(); cursor = db.conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users'); print(f'\n[OK] Found {cursor.fetchone()[0]} users in database')" 2>nul

if %errorlevel% neq 0 (
    echo [WARNING] Could not verify database
) else (
    echo [OK] Database is working!
)

echo.
echo ============================================================
echo SUCCESS! SQLite is ready to use!
echo ============================================================
echo.
echo Database file location:
echo   data\smart_finance.db
echo.
echo Configuration:
echo   DATA_STORAGE_MODE=sqlite (in .env)
echo.
echo ============================================================
echo NEXT STEPS
echo ============================================================
echo.
echo 1. Run your dashboard:
echo    run_dashboard.bat
echo.
echo 2. Login with any user:
echo    Email: Any email from your CSV
echo    Password: password123
echo.
echo 3. Start using the app!
echo.
echo ============================================================
echo.
echo TIP: SQLite database file is at: data\smart_finance.db
echo You can backup this single file to save all your data!
echo.
pause
