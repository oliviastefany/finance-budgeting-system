@echo off
REM Fix PostgreSQL Connection Issues
REM Diagnose and fix common PostgreSQL problems

echo ============================================================
echo POSTGRESQL CONNECTION FIXER
echo ============================================================
echo.

echo [1/4] Checking if PostgreSQL service is running...
echo.

REM Check PostgreSQL service status
sc query postgresql-x64-16 > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PostgreSQL service 'postgresql-x64-16' not found
    echo Trying alternative service names...

    sc query postgresql-x64-15 > nul 2>&1
    if %errorlevel% equ 0 (
        set SERVICE_NAME=postgresql-x64-15
        goto :found_service
    )

    sc query postgresql-x64-14 > nul 2>&1
    if %errorlevel% equ 0 (
        set SERVICE_NAME=postgresql-x64-14
        goto :found_service
    )

    echo.
    echo [X] PostgreSQL service not found!
    echo.
    echo This means PostgreSQL is not installed properly.
    echo.
    echo SOLUTION: Install PostgreSQL
    echo 1. Download: https://www.postgresql.org/download/windows/
    echo 2. Run installer
    echo 3. Follow wizard (default settings OK)
    echo 4. Remember the password you set!
    echo.
    pause
    exit /b 1
) else (
    set SERVICE_NAME=postgresql-x64-16
)

:found_service
echo [OK] Found PostgreSQL service: %SERVICE_NAME%
echo.

echo [2/4] Checking service status...
sc query %SERVICE_NAME% | find "RUNNING" > nul
if %errorlevel% neq 0 (
    echo [!] PostgreSQL service is NOT running!
    echo.
    echo Starting PostgreSQL service...
    net start %SERVICE_NAME%

    if %errorlevel% equ 0 (
        echo [OK] PostgreSQL service started successfully!
    ) else (
        echo [X] Failed to start PostgreSQL service
        echo.
        echo Try manually:
        echo 1. Press Win + R
        echo 2. Type: services.msc
        echo 3. Find "postgresql-x64-16"
        echo 4. Right-click -^> Start
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] PostgreSQL service is running
)
echo.

echo [3/4] Testing PostgreSQL connection...
echo.
psql --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] psql command not found in PATH
    echo.
    echo Adding PostgreSQL to PATH...
    set PATH=%PATH%;C:\Program Files\PostgreSQL\16\bin;C:\Program Files\PostgreSQL\15\bin;C:\Program Files\PostgreSQL\14\bin

    psql --version > nul 2>&1
    if %errorlevel% neq 0 (
        echo [X] Still cannot find psql
        echo.
        echo Please add PostgreSQL bin folder to PATH manually:
        echo C:\Program Files\PostgreSQL\16\bin
        echo.
        pause
        exit /b 1
    )
)

echo [OK] psql command found
psql --version
echo.

echo [4/4] Testing connection to database...
echo.
echo Enter postgres user password when prompted
echo (This is the password you set during PostgreSQL installation)
echo.

psql -U postgres -c "SELECT version();"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] PostgreSQL is working!
    echo ============================================================
    echo.
    echo pgAdmin is OPTIONAL. You can setup database without it!
    echo.
    echo NEXT STEP: Run setup script without pgAdmin
    echo    setup_database.bat
    echo.
    echo Or continue with manual setup (see below)
    echo.
) else (
    echo.
    echo ============================================================
    echo [FAILED] Cannot connect to PostgreSQL
    echo ============================================================
    echo.
    echo Common solutions:
    echo.
    echo 1. Wrong password - Try resetting:
    echo    - Stop PostgreSQL service
    echo    - Edit pg_hba.conf (trust method)
    echo    - Restart service
    echo.
    echo 2. PostgreSQL not listening on port 5432
    echo    - Check postgresql.conf
    echo    - Verify port: 5432
    echo.
    echo 3. Firewall blocking
    echo    - Allow port 5432 in Windows Firewall
    echo.
)

pause
