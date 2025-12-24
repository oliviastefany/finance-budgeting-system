# 🗄️ DATABASE OPTIONS - Smart Finance ML

**Pilih database yang cocok untuk Anda!**

---

## 📊 **PERBANDINGAN STORAGE OPTIONS**

| Feature | CSV | SQLite | PostgreSQL |
|---------|-----|--------|------------|
| **Setup Difficulty** | ✅ Easiest | ✅ Easy | ⚠️ Medium |
| **Speed (1k rows)** | ⚠️ ~50ms | ✅ ~5ms | ✅ ~10ms |
| **Speed (100k+ rows)** | ❌ Slow | ✅ Fast | ✅ Very Fast |
| **Concurrent Users** | ⚠️ 1-5 | ⚠️ 1-10 | ✅ 100+ |
| **Server Required** | ❌ No | ❌ No | ✅ Yes |
| **Configuration** | None | None | Password, port, etc |
| **Backup** | Copy file | Copy file | pg_dump |
| **Best For** | Testing | Development | Production |

---

## 🎯 **REKOMENDASI**

### **🥇 PILIHAN #1: SQLite** (RECOMMENDED untuk pemula!)

**Cocok untuk:**
- ✅ Belajar & development
- ✅ Personal use (1-10 users)
- ✅ Laptop/PC lokal
- ✅ Tidak mau ribet setup

**Setup:**
```bash
setup_sqlite.bat
```

**Keuntungan:**
- ✅ Setup 2 menit
- ✅ Tidak perlu password
- ✅ Tidak perlu server
- ✅ Backup = copy file saja

**Dokumentasi:** [SETUP_SQLITE.md](SETUP_SQLITE.md)

---

### **🥈 PILIHAN #2: CSV Files** (Yang sekarang)

**Cocok untuk:**
- ✅ Quick testing
- ✅ Sample data
- ✅ Tidak perlu database sama sekali

**Setup:**
```env
# .env
DATA_STORAGE_MODE=csv
```

**Keuntungan:**
- ✅ Sudah jalan (default)
- ✅ Tidak perlu setup
- ✅ Data mudah dilihat (Excel/text editor)

**Kekurangan:**
- ❌ Lambat untuk data besar
- ❌ Tidak cocok untuk concurrent users

---

### **🥉 PILIHAN #3: PostgreSQL** (Production)

**Cocok untuk:**
- ✅ Production deployment
- ✅ Banyak users (50+)
- ✅ Server remote
- ✅ Advanced features

**Setup:**
```bash
# Windows
setup_database_simple.bat

# Atau otomatis (jika PostgreSQL sudah installed)
setup_database.bat
```

**Keuntungan:**
- ✅ Very fast
- ✅ Support 100+ concurrent users
- ✅ Advanced features
- ✅ Industry standard

**Kekurangan:**
- ❌ Perlu install PostgreSQL server
- ❌ Perlu konfigurasi
- ❌ Lebih kompleks

**Dokumentasi:** [SETUP_POSTGRESQL.md](SETUP_POSTGRESQL.md)

---

## 🚀 **QUICK START BY USE CASE**

### **Scenario 1: "Saya mau coba-coba dulu"**

**Gunakan:** CSV (default)
```bash
# Langsung run aja!
run_dashboard.bat
```

### **Scenario 2: "Saya mau development serius, tapi gak mau ribet"**

**Gunakan:** SQLite
```bash
setup_sqlite.bat
run_dashboard.bat
```

### **Scenario 3: "Saya mau deploy ke production / server"**

**Gunakan:** PostgreSQL
```bash
# Install PostgreSQL dulu
# Lalu:
setup_database_simple.bat
run_dashboard.bat
```

---

## 📁 **FILE STRUKTUR**

```
smart-finance-ml/
├── data/
│   └── smart_finance.db          # SQLite database file
├── config/data/raw/
│   ├── users.csv                 # CSV data
│   └── transactions.csv          # CSV data
├── src/database/
│   ├── sqlite_manager.py         # SQLite manager
│   └── postgres_manager.py       # PostgreSQL manager
├── dashboards/
│   ├── auth.py                   # Auth (CSV only)
│   ├── auth_postgres.py          # Auth (CSV + PostgreSQL)
│   └── auth_sqlite.py            # Auth (CSV + SQLite + PostgreSQL)
├── setup_sqlite.bat              # SQLite setup
├── setup_database.bat            # PostgreSQL setup (full)
├── setup_database_simple.bat     # PostgreSQL setup (simple)
├── migrate_to_sqlite.py          # Migrate CSV → SQLite
├── migrate_to_postgres.py        # Migrate CSV → PostgreSQL
└── .env                          # Configuration
```

---

## ⚙️ **KONFIGURASI (.env)**

```env
# ========================================
# DATA STORAGE MODE
# ========================================
# Options: csv, sqlite, postgresql
DATA_STORAGE_MODE=csv              # Ubah sesuai pilihan

# ========================================
# POSTGRESQL CONFIGURATION (jika pakai postgresql)
# ========================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_finance
DB_USER=finance_user
DB_PASSWORD=SmartFinance2024!Secure
```

---

## 🔄 **SWITCH ANTAR MODE**

### **CSV → SQLite**

```bash
# 1. Migrate data
python migrate_to_sqlite.py

# 2. Update .env
# DATA_STORAGE_MODE=sqlite

# 3. Restart dashboard
run_dashboard.bat
```

### **CSV → PostgreSQL**

```bash
# 1. Install & setup PostgreSQL
setup_database_simple.bat

# 2. Migrate data
python migrate_to_postgres.py

# 3. Update .env
# DATA_STORAGE_MODE=postgresql

# 4. Restart dashboard
run_dashboard.bat
```

### **SQLite → PostgreSQL**

```bash
# 1. Setup PostgreSQL
setup_database_simple.bat

# 2. Export dari SQLite, import ke PostgreSQL
# (manual atau buat script)

# 3. Update .env
# DATA_STORAGE_MODE=postgresql
```

### **Kembali ke CSV**

```env
# Edit .env
DATA_STORAGE_MODE=csv
```

Data CSV tidak dihapus, jadi bisa balik kapan saja!

---

## 📚 **DOKUMENTASI LENGKAP**

| Storage | Quick Start | Full Guide |
|---------|-------------|------------|
| **SQLite** | [QUICK_START_SQLITE.md](QUICK_START_SQLITE.md) | [SETUP_SQLITE.md](SETUP_SQLITE.md) |
| **PostgreSQL** | [QUICK_START_POSTGRESQL.md](QUICK_START_POSTGRESQL.md) | [SETUP_POSTGRESQL.md](SETUP_POSTGRESQL.md) |
| **Privacy** | - | [PANDUAN_DATABASE_PRIVACY.md](PANDUAN_DATABASE_PRIVACY.md) |

---

## 🐛 **TROUBLESHOOTING**

### **Problem: Aplikasi error setelah ganti mode**

```bash
# 1. Cek .env
notepad .env

# 2. Pastikan mode sudah benar
# DATA_STORAGE_MODE=sqlite  # atau csv atau postgresql

# 3. Restart dashboard
run_dashboard.bat
```

### **Problem: Database kosong**

```bash
# Jalankan migration
python migrate_to_sqlite.py      # untuk SQLite
python migrate_to_postgres.py    # untuk PostgreSQL
```

### **Problem: "Module not found"**

```bash
# Install dependencies
pip install -r requirements.txt
```

---

## 💡 **TIPS & BEST PRACTICES**

### **Development:**
✅ Gunakan SQLite atau CSV
✅ Backup database file secara berkala
✅ Test dengan data kecil dulu

### **Production:**
✅ Gunakan PostgreSQL
✅ Setup automatic backup
✅ Monitor performance
✅ Enable SSL/TLS

### **Backup:**

**SQLite:**
```bash
copy data\smart_finance.db backups\backup_%date%.db
```

**PostgreSQL:**
```bash
pg_dump -U finance_user smart_finance > backup.sql
```

**CSV:**
```bash
xcopy config\data\raw backups\ /E /I
```

---

## 🎓 **FAQ**

**Q: Mana yang paling mudah?**
A: SQLite! Setup cuma 2 menit, tidak perlu server.

**Q: Mana yang paling cepat?**
A: PostgreSQL untuk data besar, tapi SQLite sudah cukup cepat.

**Q: Apakah data akan hilang saat switch mode?**
A: Tidak! CSV tetap ada. Tapi perlu migrate ulang jika switch.

**Q: Bisa pakai ketiganya sekaligus?**
A: Bisa, tapi hanya 1 aktif di waktu bersamaan (sesuai .env).

**Q: Rekomendasi untuk pemula?**
A: **SQLite**! Mudah, cepat, tidak ribet.

**Q: Kapan harus upgrade ke PostgreSQL?**
A: Jika users > 50, atau deploy ke server production.

---

## 🎯 **KESIMPULAN**

### **Pilih SQLite jika:**
- ✅ Mau cepat & mudah
- ✅ Development/testing
- ✅ Personal use
- ✅ Tidak mau install server

### **Pilih PostgreSQL jika:**
- ✅ Production deployment
- ✅ Banyak users
- ✅ Butuh advanced features
- ✅ Sudah biasa setup database

### **Tetap pakai CSV jika:**
- ✅ Cuma mau quick test
- ✅ Data kecil (<1000 rows)
- ✅ Tidak perlu database

---

**Saran saya: Mulai dengan SQLite! 🚀**

Setup paling mudah, performa bagus, cocok untuk belajar!

```bash
setup_sqlite.bat
run_dashboard.bat
```

Done! 🎉
