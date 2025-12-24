# ⚡ QUICK START - PostgreSQL Setup

**Cara Tercepat Setup PostgreSQL untuk Smart Finance**

---

## 🎯 **RINGKASAN CEPAT**

Total waktu setup: **~15-30 menit**

1. Install PostgreSQL (5-10 menit)
2. Setup Database (2 menit)
3. Migrasi Data (1 menit)
4. Test & Run (1 menit)

---

## 📋 **LANGKAH CEPAT**

### **1️⃣ Install PostgreSQL** (Jika belum)

**Windows:**
- Download: https://www.postgresql.org/download/windows/
- Install → Set password → Port 5432 → Selesai
- **Catat password Anda!**

**Linux:**
```bash
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

---

### **2️⃣ Setup Database** (Otomatis)

**Windows:**
```cmd
cd c:\smart-finance-ml
setup_database.bat
```

**Linux/macOS:**
```bash
cd ~/smart-finance-ml
chmod +x setup_database.sh
./setup_database.sh
```

Script ini akan otomatis:
- ✅ Buat database `smart_finance`
- ✅ Buat user `finance_user`
- ✅ Buat tabel (users, transactions)
- ✅ Test koneksi

---

### **3️⃣ Edit File .env**

Buka file `.env` dan pastikan konfigurasi benar:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_finance
DB_USER=finance_user
DB_PASSWORD=SmartFinance2024!Secure    # Sesuaikan jika perlu

# PENTING: Ubah ini setelah migrasi berhasil
DATA_STORAGE_MODE=csv    # Nanti ganti ke 'postgresql'
```

---

### **4️⃣ Test Koneksi**

```bash
python test_connection.py
```

Jika muncul ✅ **ALL TESTS PASSED**, lanjut ke step berikutnya!

---

### **5️⃣ Migrasi Data dari CSV**

```bash
python migrate_to_postgres.py
```

Output yang diharapkan:
```
✅ Migrated 250 users successfully!
✅ Migrated 15000 transactions successfully!
✅ MIGRATION COMPLETED SUCCESSFULLY!
```

---

### **6️⃣ Aktifkan PostgreSQL Mode**

Edit `.env`, ubah:
```env
DATA_STORAGE_MODE=postgresql    # Ubah dari csv ke postgresql
```

---

### **7️⃣ Jalankan Dashboard**

**Windows:**
```cmd
run_dashboard.bat
```

**Linux/macOS:**
```bash
./run_dashboard.sh
```

---

### **8️⃣ Login & Test**

Buka browser: http://localhost:8501

**Login dengan:**
- Email: Ambil dari CSV atau dari output migration (contoh: `whitehector@example.net`)
- Password: `password123` (default dari migration)

---

## ✅ **VERIFIKASI**

Cek apakah PostgreSQL sudah bekerja:

1. **Login berhasil** ✅
2. **Data transaksi muncul** ✅
3. **Bisa add/delete transaction** ✅
4. **Dashboard loading cepat** ✅

---

## 🐛 **TROUBLESHOOTING CEPAT**

### ❌ **"psql: command not found"**
- **Windows**: Tambahkan `C:\Program Files\PostgreSQL\16\bin` ke PATH
- **Linux**: `sudo apt install postgresql-client`

### ❌ **"password authentication failed"**
```bash
# Reset password
psql -U postgres
ALTER USER finance_user WITH PASSWORD 'SmartFinance2024!Secure';
```

### ❌ **"database smart_finance does not exist"**
```bash
psql -U postgres -c "CREATE DATABASE smart_finance;"
```

### ❌ **"Connection refused"**
```bash
# Windows: Cek Services → PostgreSQL harus Running
# Linux: sudo systemctl start postgresql
```

### ❌ **Migration error**
```bash
# Cek file CSV ada
dir config\data\raw\*.csv    # Windows
ls config/data/raw/*.csv     # Linux

# Re-run migration
python migrate_to_postgres.py
```

---

## 📚 **FILE PENTING**

| File | Deskripsi |
|------|-----------|
| `SETUP_POSTGRESQL.md` | **Panduan lengkap & detail** |
| `database_schema.sql` | SQL schema untuk tabel |
| `migrate_to_postgres.py` | Script migrasi CSV → PostgreSQL |
| `test_connection.py` | Test koneksi database |
| `setup_database.bat/.sh` | Setup otomatis |
| `.env` | Konfigurasi database |

---

## 🎓 **QUERY BERGUNA**

### Cek jumlah data:
```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM transactions;
```

### Lihat top spenders:
```sql
SELECT u.name, SUM(t.amount) as total
FROM users u
JOIN transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name
ORDER BY total DESC
LIMIT 10;
```

### Reset password user:
```sql
-- Password: password123
UPDATE users
SET password_hash = 'ef92b778bafe771e89245b89ecbc08153c0cca5c2e2f3c38e0e52a1e8be3b8db'
WHERE email = 'user@example.com';
```

---

## 🔄 **ROLLBACK KE CSV**

Jika ada masalah dan mau kembali ke CSV:

1. Edit `.env`:
   ```env
   DATA_STORAGE_MODE=csv
   ```

2. Restart dashboard

Data CSV tetap utuh, tidak dihapus!

---

## 📞 **BUTUH BANTUAN?**

1. Baca: [SETUP_POSTGRESQL.md](SETUP_POSTGRESQL.md) (panduan lengkap)
2. Cek bagian **Troubleshooting** di panduan lengkap
3. Run test: `python test_connection.py`

---

**Selamat! Sistem Anda sekarang menggunakan PostgreSQL! 🎉**

PostgreSQL jauh lebih cepat dan stabil untuk data besar dan banyak user!
