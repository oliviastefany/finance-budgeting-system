# 🚀 SETUP SQLITE - Smart Finance ML

**Cara TERMUDAH Setup Database - Tidak Perlu Server!**

---

## ⚡ **KENAPA SQLITE?**

✅ **SUPER MUDAH** - Tidak perlu install server
✅ **TANPA PASSWORD** - Tidak perlu konfigurasi
✅ **SATU FILE** - Semua data dalam 1 file
✅ **CEPAT** - Langsung jalan!
✅ **GRATIS** - Built-in Python

❌ **Tidak Cocok untuk:**
- Production dengan 100+ concurrent users
- Server terpisah dari aplikasi

✅ **COCOK untuk:**
- Development & Testing
- Personal use (1-10 users)
- Prototype & Demo
- Laptop/PC lokal

---

## 🎯 **SETUP OTOMATIS (RECOMMENDED)**

### **Langkah 1: Jalankan Setup Script**

```bash
setup_sqlite.bat
```

**Done!** Setup selesai! ✅

Script ini otomatis:
1. ✅ Buat database SQLite
2. ✅ Migrate data dari CSV
3. ✅ Update konfigurasi .env
4. ✅ Test koneksi

---

## 📋 **SETUP MANUAL (Jika Perlu)**

### **Langkah 1: Migrate Data**

```bash
python migrate_to_sqlite.py
```

Output yang diharapkan:
```
============================================================
SMART FINANCE - CSV TO SQLITE MIGRATION
============================================================
🔌 Initializing SQLite database...
✅ Database file: c:\smart-finance-ml\data\smart_finance.db

==================================================
MIGRATING USERS
==================================================
📊 Found 250 users in CSV
✅ Migrated 250 users successfully!

==================================================
MIGRATING TRANSACTIONS
==================================================
📊 Found 15000 transactions in CSV
✅ Migrated 15000 transactions successfully!

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

### **Langkah 2: Update .env**

Edit file `.env`:
```env
# Ubah dari csv ke sqlite
DATA_STORAGE_MODE=sqlite
```

### **Langkah 3: Jalankan Dashboard**

```bash
# Windows
run_dashboard.bat

# Linux/macOS
./run_dashboard.sh
```

### **Langkah 4: Login**

- **Email**: Ambil dari CSV (contoh: `whitehector@example.net`)
- **Password**: `password123` (default)

---

## 📁 **LOKASI DATABASE**

Database SQLite disimpan di:
```
c:\smart-finance-ml\data\smart_finance.db
```

**Ini hanya 1 file!** Mudah untuk:
- ✅ Backup (copy file saja)
- ✅ Restore (paste file kembali)
- ✅ Transfer ke PC lain

---

## 🔧 **KONFIGURASI**

### **.env File**

```env
# Storage Mode
DATA_STORAGE_MODE=sqlite    # Gunakan SQLite

# Environment
ENVIRONMENT=development
```

**Tidak perlu** konfigurasi host, port, username, password! 🎉

---

## 🧪 **TESTING**

### **Test 1: Cek Database File**

```bash
# Windows
dir data\smart_finance.db

# Linux/macOS
ls -lh data/smart_finance.db
```

Jika file ada, database sudah dibuat! ✅

### **Test 2: Cek Data**

```python
# test_sqlite.py
from src.database.sqlite_manager import get_db_manager

db = get_db_manager()
cursor = db.conn.cursor()

# Count users
cursor.execute("SELECT COUNT(*) FROM users")
print(f"Users: {cursor.fetchone()[0]}")

# Count transactions
cursor.execute("SELECT COUNT(*) FROM transactions")
print(f"Transactions: {cursor.fetchone()[0]}")
```

Run:
```bash
python test_sqlite.py
```

### **Test 3: Login ke Dashboard**

```bash
run_dashboard.bat
```

Login dengan:
- Email: Dari CSV
- Password: `password123`

---

## 📊 **QUERY DATABASE**

### **Cara 1: Via Python**

```python
from src.database.sqlite_manager import get_db_manager

db = get_db_manager()
cursor = db.conn.cursor()

# Get all users
cursor.execute("SELECT * FROM users LIMIT 10")
for row in cursor.fetchall():
    print(row)
```

### **Cara 2: Via SQLite Browser (GUI)**

1. Download **DB Browser for SQLite**: https://sqlitebrowser.org/
2. Buka file: `data\smart_finance.db`
3. Browse & query data dengan GUI

### **Cara 3: Via Command Line**

```bash
# Install sqlite3 (jika belum ada)
# Windows: sudah built-in
# Linux: sudo apt install sqlite3

# Open database
sqlite3 data/smart_finance.db

# Query
SELECT COUNT(*) FROM users;
SELECT * FROM users LIMIT 5;
SELECT * FROM transactions WHERE user_id = 'U00001' LIMIT 10;

# Exit
.quit
```

---

## 🔄 **BACKUP & RESTORE**

### **Backup (Super Mudah!)**

```bash
# Cara 1: Copy file
copy data\smart_finance.db data\backup_smart_finance.db

# Cara 2: Dengan timestamp
copy data\smart_finance.db data\smart_finance_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db
```

### **Restore**

```bash
# Restore dari backup
copy data\backup_smart_finance.db data\smart_finance.db
```

### **Auto Backup Script**

```batch
REM backup_sqlite.bat
@echo off
set backup_dir=backups\sqlite
mkdir %backup_dir% 2>nul
copy data\smart_finance.db %backup_dir%\smart_finance_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db
echo Backup created: %backup_dir%\smart_finance_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db
```

---

## 🐛 **TROUBLESHOOTING**

### **Problem: "Database is locked"**

**Penyebab:** Ada proses lain yang pakai database

**Solusi:**
```bash
# Close dashboard dulu
# Restart dashboard
run_dashboard.bat
```

### **Problem: "Table not found"**

**Penyebab:** Database belum dibuat atau corrupt

**Solusi:**
```bash
# Delete database
del data\smart_finance.db

# Re-run migration
python migrate_to_sqlite.py
```

### **Problem: "No such file or directory"**

**Penyebab:** Folder `data/` belum ada

**Solusi:**
```bash
# Create folder
mkdir data

# Run migration
python migrate_to_sqlite.py
```

---

## 📈 **PERFORMANCE**

### **SQLite vs CSV**

| Operation | CSV | SQLite |
|-----------|-----|--------|
| Read 1k rows | ~50ms | ~5ms ⚡ |
| Write 1 row | ~100ms | ~1ms ⚡ |
| Complex query | ❌ Slow | ✅ Fast |
| Concurrent reads | ⚠️ Limited | ✅ Good |
| File size | Large | Small ⚡ |

### **SQLite vs PostgreSQL**

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Setup** | ✅ No setup | ❌ Need server |
| **Maintenance** | ✅ Zero | ⚠️ Need maintenance |
| **Concurrent users** | ⚠️ 1-10 | ✅ 1000+ |
| **Best for** | Development | Production |

---

## 🔄 **SWITCH STORAGE MODE**

### **SQLite → CSV**

Edit `.env`:
```env
DATA_STORAGE_MODE=csv
```

Data CSV tetap ada, tidak dihapus!

### **SQLite → PostgreSQL**

1. Install PostgreSQL
2. Run: `python migrate_sqlite_to_postgres.py` (jika ada)
3. Edit `.env`:
   ```env
   DATA_STORAGE_MODE=postgresql
   ```

---

## 📚 **QUERY BERGUNA**

### **Count Data**

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM transactions;
```

### **Top Spenders**

```sql
SELECT
    u.name,
    SUM(t.amount) as total_spending
FROM users u
JOIN transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name
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

### **Reset Password**

```sql
-- Password: password123
UPDATE users
SET password_hash = 'ef92b778bafe771e89245b89ecbc08153c0cca5c2e2f3c38e0e52a1e8be3b8db'
WHERE email = 'user@example.com';
```

---

## ✨ **KEUNTUNGAN SQLITE**

✅ **Zero Configuration** - Tidak perlu setup apapun
✅ **Portable** - Satu file, bawa kemana-mana
✅ **Fast** - Lebih cepat dari CSV
✅ **Reliable** - ACID compliant
✅ **Built-in** - Sudah ada di Python
✅ **Small** - File size kecil
✅ **Simple Backup** - Copy-paste file saja

---

## 🎯 **KAPAN UPGRADE KE POSTGRESQL?**

Upgrade ke PostgreSQL jika:
- ✅ Users > 50 concurrent
- ✅ Need remote database
- ✅ Deploy to production server
- ✅ Need advanced features (replication, etc)

Untuk development & personal use, **SQLite sudah cukup!**

---

## 📞 **BUTUH BANTUAN?**

File bermasalah? Coba:

```bash
# 1. Hapus database lama
del data\smart_finance.db

# 2. Re-run migration
python migrate_to_sqlite.py

# 3. Test
run_dashboard.bat
```

---

**Selamat! SQLite siap digunakan! 🎉**

Sekarang Anda punya database yang cepat, mudah, dan tidak ribet!
