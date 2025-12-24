# ⚡ QUICK START - SQLite (TERMUDAH!)

**Setup Database PALING MUDAH - 2 Menit Selesai!**

---

## 🎯 **KENAPA PILIH SQLITE?**

✅ **TIDAK PERLU**:
- ❌ Install PostgreSQL server
- ❌ Konfigurasi password
- ❌ Setup pgAdmin
- ❌ Service management

✅ **CUKUP**:
- ✅ Run 1 script
- ✅ Done! 🎉

---

## 🚀 **SETUP (2 LANGKAH)**

### **Langkah 1: Jalankan Setup**

```bash
setup_sqlite.bat
```

### **Langkah 2: Run Dashboard**

```bash
run_dashboard.bat
```

**DONE!** ✅

---

## 🔑 **LOGIN**

Buka browser: http://localhost:8501

**Login dengan:**
- Email: Ambil dari CSV Anda (contoh: `whitehector@example.net`)
- Password: `password123`

---

## 📁 **DATABASE FILE**

Lokasi: `data\smart_finance.db`

**Backup mudah:**
```bash
copy data\smart_finance.db data\backup.db
```

---

## 🔄 **SWITCH KE MODE LAIN**

### **Kembali ke CSV:**

Edit `.env`:
```env
DATA_STORAGE_MODE=csv
```

### **Upgrade ke PostgreSQL:**

1. Install PostgreSQL
2. Run: `setup_database.bat`
3. Edit `.env`:
   ```env
   DATA_STORAGE_MODE=postgresql
   ```

---

## 🐛 **TROUBLESHOOTING**

### **Error saat migrate?**

```bash
# Hapus database lama
del data\smart_finance.db

# Coba lagi
python migrate_to_sqlite.py
```

### **Dashboard tidak jalan?**

```bash
# Cek mode di .env
notepad .env

# Pastikan:
# DATA_STORAGE_MODE=sqlite
```

---

## 📚 **DOKUMENTASI LENGKAP**

Baca: [SETUP_SQLITE.md](SETUP_SQLITE.md)

---

**Selamat! SQLite adalah pilihan TERCEPAT untuk mulai! 🚀**

Tidak perlu ribet dengan server PostgreSQL!
