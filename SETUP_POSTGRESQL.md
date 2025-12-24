# 🗄️ SETUP POSTGRESQL - Smart Finance ML

**Panduan Lengkap Instalasi dan Konfigurasi PostgreSQL di Laptop**

---

## 📑 **DAFTAR ISI**

1. [Download & Install PostgreSQL](#1-download--install-postgresql)
2. [Konfigurasi Database](#2-konfigurasi-database)
3. [Setup Environment Variables](#3-setup-environment-variables)
4. [Jalankan Schema Database](#4-jalankan-schema-database)
5. [Migrasi Data CSV ke PostgreSQL](#5-migrasi-data-csv-ke-postgresql)
6. [Update Aplikasi untuk Gunakan PostgreSQL](#6-update-aplikasi-untuk-gunakan-postgresql)
7. [Testing Koneksi](#7-testing-koneksi)
8. [Troubleshooting](#8-troubleshooting)

---

## 🚀 **1. DOWNLOAD & INSTALL POSTGRESQL**

### **Windows:**

#### **Opsi A: Download dari Website Resmi**

1. **Download PostgreSQL Installer**
   - Kunjungi: https://www.postgresql.org/download/windows/
   - Pilih **PostgreSQL 16** (versi terbaru stable)
   - Download installer (postgresql-16.x-windows-x64.exe)

2. **Jalankan Installer**
   - Double-click file installer
   - Ikuti wizard instalasi:
     - Installation Directory: `C:\Program Files\PostgreSQL\16` (default)
     - Select Components: ✅ Centang semua (PostgreSQL Server, pgAdmin, Command Line Tools)
     - Data Directory: `C:\Program Files\PostgreSQL\16\data` (default)
     - **Password**: Buat password untuk user `postgres` (INGAT PASSWORD INI!)
     - Port: `5432` (default)
     - Locale: `English, United States` atau sesuai lokasi Anda
   - Klik **Next** sampai selesai
   - ⚠️ **PENTING**: Catat password yang Anda buat!

3. **Verifikasi Instalasi**
   - Buka **Command Prompt** atau **PowerShell**
   - Jalankan:
   ```cmd
   psql --version
   ```
   - Jika muncul `psql (PostgreSQL) 16.x`, instalasi berhasil! ✅

#### **Opsi B: Install via Chocolatey (Windows Package Manager)**

Jika Anda sudah install Chocolatey:
```cmd
choco install postgresql
```

### **Linux (Ubuntu/Debian):**

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

### **macOS:**

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@16

# Start PostgreSQL service
brew services start postgresql@16

# Verify installation
psql --version
```

---

## ⚙️ **2. KONFIGURASI DATABASE**

### **Windows:**

1. **Buka pgAdmin 4**
   - Cari "pgAdmin 4" di Start Menu
   - Masukkan master password (password yang Anda buat saat instalasi)

2. **Buat Database Baru**
   - Di panel kiri, expand **Servers** > **PostgreSQL 16**
   - Klik kanan pada **Databases** > **Create** > **Database**
   - Isi form:
     - **Database**: `smart_finance`
     - **Owner**: `postgres` (default)
     - Klik **Save**

3. **Buat User Baru (Recommended)**
   - Klik kanan pada **Login/Group Roles** > **Create** > **Login/Group Role**
   - Tab **General**:
     - Name: `finance_user`
   - Tab **Definition**:
     - Password: `SmartFinance2024!Secure` (atau password pilihan Anda)
   - Tab **Privileges**:
     - ✅ Can login?: **Yes**
   - Klik **Save**

4. **Grant Permissions ke User**
   - Klik kanan database `smart_finance` > **Query Tool**
   - Jalankan query:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE smart_finance TO finance_user;
   ```

### **Linux/macOS (Command Line):**

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE smart_finance;

# Create user
CREATE USER finance_user WITH PASSWORD 'SmartFinance2024!Secure';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE smart_finance TO finance_user;

# Exit
\q
```

---

## 🔐 **3. SETUP ENVIRONMENT VARIABLES**

File `.env` sudah dibuat di root project. Edit file tersebut:

```bash
# Open .env file
notepad .env    # Windows
nano .env       # Linux/macOS
```

Isi dengan konfigurasi database Anda:

```env
# ========================================
# DATABASE CONFIGURATION
# ========================================

# PostgreSQL Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_finance
DB_USER=finance_user
DB_PASSWORD=SmartFinance2024!Secure    # Ganti dengan password Anda!

# Database URL
DATABASE_URL=postgresql://finance_user:SmartFinance2024!Secure@localhost:5432/smart_finance

# ========================================
# APPLICATION SETTINGS
# ========================================

# Data Storage Mode: csv atau postgresql
DATA_STORAGE_MODE=postgresql    # Ubah ke postgresql setelah migrasi berhasil!

# Environment
ENVIRONMENT=development
```

⚠️ **PENTING:**
- Ganti `DB_PASSWORD` dengan password yang Anda buat
- File `.env` sudah di-gitignore, jadi aman (tidak akan ter-commit ke GitHub)

---

## 🛠️ **4. JALANKAN SCHEMA DATABASE**

### **Cara 1: Via pgAdmin (GUI)**

1. Buka **pgAdmin 4**
2. Expand **Servers** > **PostgreSQL 16** > **Databases** > **smart_finance**
3. Klik kanan `smart_finance` > **Query Tool**
4. Buka file `database_schema.sql`:
   - Klik **File** > **Open** > Pilih `database_schema.sql`
5. Klik tombol **Execute** (⚡ icon) atau tekan **F5**
6. Jika berhasil, akan muncul pesan: `Database schema created successfully!` ✅

### **Cara 2: Via Command Line**

```bash
# Windows (Command Prompt)
cd c:\smart-finance-ml
psql -U finance_user -d smart_finance -f database_schema.sql

# Linux/macOS
cd ~/smart-finance-ml
psql -U finance_user -d smart_finance -f database_schema.sql
```

Masukkan password Anda saat diminta.

### **Verifikasi Schema**

Jalankan query ini untuk cek tabel sudah dibuat:

```sql
-- List all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Should show: users, transactions
```

---

## 📦 **5. MIGRASI DATA CSV KE POSTGRESQL**

Sekarang pindahkan data dari CSV ke PostgreSQL:

### **Jalankan Migration Script**

```bash
# Pastikan Anda di root project
cd c:\smart-finance-ml

# Install dependencies (jika belum)
pip install -r requirements.txt

# Jalankan migration
python migrate_to_postgres.py
```

### **Output yang Diharapkan:**

```
============================================================
SMART FINANCE - CSV TO POSTGRESQL MIGRATION
============================================================
✅ Connected to PostgreSQL database

==================================================
MIGRATING USERS
==================================================
📊 Found 250 users in CSV
🗑️  Cleared existing users
✅ Migrated 250 users successfully!

📋 Sample users:
   U00001 - Rhonda Marks (whitehector@example.net) - USD
   U00002 - Christopher Hunter (susan66@example.org) - USD
   ...

==================================================
MIGRATING TRANSACTIONS
==================================================
📊 Found 15000 transactions in CSV
🗑️  Cleared existing transactions
✅ Migrated 15000 transactions successfully!

📊 Transaction Statistics:
   Total transactions: 15000
   Unique users: 250
   Total amount: $2,345,678.90
   Date range: 2024-01-01 to 2024-12-31

📈 Top 5 Categories:
   Housing: 2500 transactions ($456,789.00)
   Groceries: 3200 transactions ($234,567.00)
   ...

==================================================
VERIFYING MIGRATION
==================================================
✅ Users in database: 250
✅ Transactions in database: 15000
✅ No orphaned transactions

============================================================
✅ MIGRATION COMPLETED SUCCESSFULLY!
============================================================
```

---

## 🔄 **6. UPDATE APLIKASI UNTUK GUNAKAN POSTGRESQL**

### **Ubah Storage Mode**

Edit file `.env`:

```env
# Ubah dari csv ke postgresql
DATA_STORAGE_MODE=postgresql
```

### **Update Kode (Jika Perlu)**

Jika Anda menggunakan `auth.py` yang lama, ganti dengan `auth_postgres.py`:

```python
# Ubah import di file dashboard Anda
# DARI:
from dashboards.auth import AuthManager, check_authentication, logout

# KE:
from dashboards.auth_postgres import AuthManager, check_authentication, logout
```

Atau rename file:

```bash
# Backup file lama
mv dashboards/auth.py dashboards/auth_csv_backup.py

# Gunakan yang baru
mv dashboards/auth_postgres.py dashboards/auth.py
```

---

## ✅ **7. TESTING KONEKSI**

### **Test 1: Cek Koneksi Database**

Buat file test sederhana `test_connection.py`:

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print("✅ Database connection successful!")

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    print(f"✅ Found {user_count} users in database")

    cur.execute("SELECT COUNT(*) FROM transactions")
    txn_count = cur.fetchone()[0]
    print(f"✅ Found {txn_count} transactions in database")

    conn.close()

except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Jalankan:
```bash
python test_connection.py
```

### **Test 2: Test Login**

Jalankan dashboard Anda:

```bash
# Windows
run_dashboard.bat

# Linux/macOS
./run_dashboard.sh
```

Login dengan:
- **Email**: Salah satu email dari CSV (contoh: `whitehector@example.net`)
- **Password**: `password123` (default dari migration)

Jika berhasil login, PostgreSQL sudah terhubung! ✅

---

## 🛠️ **8. TROUBLESHOOTING**

### **Problem 1: `psql: command not found`**

**Solusi (Windows):**
1. Tambahkan PostgreSQL ke PATH:
   - Buka **Environment Variables**
   - Edit **Path**
   - Tambahkan: `C:\Program Files\PostgreSQL\16\bin`
2. Restart Command Prompt

### **Problem 2: `password authentication failed`**

**Solusi:**
1. Pastikan password di `.env` sama dengan password di PostgreSQL
2. Reset password user:
   ```sql
   ALTER USER finance_user WITH PASSWORD 'NewPasswordHere';
   ```

### **Problem 3: `database "smart_finance" does not exist`**

**Solusi:**
```bash
# Buat database manual
psql -U postgres -c "CREATE DATABASE smart_finance;"
```

### **Problem 4: `FATAL: role "finance_user" does not exist`**

**Solusi:**
```sql
-- Login sebagai postgres
psql -U postgres

-- Buat user
CREATE USER finance_user WITH PASSWORD 'SmartFinance2024!Secure';
GRANT ALL PRIVILEGES ON DATABASE smart_finance TO finance_user;
```

### **Problem 5: Connection Timeout**

**Solusi:**
1. Pastikan PostgreSQL service running:
   ```bash
   # Windows
   services.msc   # Cari "PostgreSQL", pastikan status "Running"

   # Linux
   sudo systemctl status postgresql
   sudo systemctl start postgresql
   ```

2. Check firewall settings (allow port 5432)

### **Problem 6: Migration Error - Orphaned Transactions**

**Solusi:**
Beberapa transaksi punya `user_id` yang tidak ada di tabel users.

```sql
-- Hapus transaksi orphan
DELETE FROM transactions
WHERE user_id NOT IN (SELECT user_id FROM users);
```

---

## 📊 **QUERY BERGUNA**

### **Cek Jumlah Data**

```sql
-- Count users
SELECT COUNT(*) FROM users;

-- Count transactions
SELECT COUNT(*) FROM transactions;

-- Count per user
SELECT u.name, COUNT(t.transaction_id) as txn_count
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name
ORDER BY txn_count DESC
LIMIT 10;
```

### **Lihat Top Spenders**

```sql
SELECT
    u.name,
    u.email,
    COUNT(t.transaction_id) as total_transactions,
    SUM(t.amount) as total_spending
FROM users u
JOIN transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name, u.email
ORDER BY total_spending DESC
LIMIT 10;
```

### **Category Breakdown**

```sql
SELECT
    category,
    COUNT(*) as count,
    SUM(amount) as total,
    AVG(amount) as average
FROM transactions
GROUP BY category
ORDER BY total DESC;
```

### **Reset Password User**

```sql
-- Reset password ke "password123"
UPDATE users
SET password_hash = 'ef92b778bafe771e89245b89ecbc08153c0cca5c2e2f3c38e0e52a1e8be3b8db'
WHERE email = 'user@example.com';
```

---

## 🎯 **NEXT STEPS**

Setelah PostgreSQL berhasil terkoneksi:

1. ✅ **Backup Database Regularly**
   ```bash
   pg_dump -U finance_user smart_finance > backup.sql
   ```

2. ✅ **Setup Automatic Backup** (Recommended)
   - Windows: Task Scheduler
   - Linux: Cron job

3. ✅ **Monitor Performance**
   - Gunakan pgAdmin untuk monitor queries
   - Check slow queries

4. ✅ **Security Hardening**
   - Ganti password default
   - Limit connections dari localhost only (edit `pg_hba.conf`)
   - Enable SSL (untuk production)

5. ✅ **Deploy ke Production** (Optional)
   - Lihat: [PANDUAN_DEPLOYMENT.md](PANDUAN_DEPLOYMENT.md)

---

## 📚 **RESOURCES**

- PostgreSQL Official Docs: https://www.postgresql.org/docs/
- pgAdmin 4 Docs: https://www.pgadmin.org/docs/
- Python psycopg2 Docs: https://www.psycopg.org/docs/
- SQLAlchemy Tutorial: https://docs.sqlalchemy.org/

---

## ❓ **FAQ**

**Q: Apakah saya bisa pakai SQLite instead of PostgreSQL?**
A: Bisa! Tapi PostgreSQL lebih recommended untuk production karena support concurrent users dan lebih cepat untuk data besar.

**Q: Data CSV masih diperlukan setelah migrasi?**
A: Setelah migrasi berhasil, data CSV hanya sebagai backup. Sistem akan pakai PostgreSQL.

**Q: Bagaimana cara switch kembali ke CSV?**
A: Ubah `DATA_STORAGE_MODE=csv` di file `.env`

**Q: Apakah harus install PostgreSQL di server production?**
A: Tidak harus. Anda bisa pakai managed database seperti:
   - AWS RDS (PostgreSQL)
   - Google Cloud SQL
   - Azure Database for PostgreSQL
   - Heroku Postgres
   - Supabase (Free tier available!)

---

**Semoga berhasil! 🚀**

Jika ada error atau pertanyaan, cek bagian **Troubleshooting** atau tanya aja! 😊
