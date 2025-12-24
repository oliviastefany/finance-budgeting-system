# 🚀 PANDUAN DEPLOYMENT - Smart Finance ML

**Panduan Lengkap untuk Pemula**

---

## ✅ **SUDAH SIAP PUSH KE GITHUB!**

Proyek ini sudah dikonfigurasi dan siap di-push ke GitHub serta dideploy!

---

## 📦 **Yang Sudah Disiapkan:**

### ✅ **1. File .env (API Configuration)**
- ✅ File `.env` sudah dibuat
- ✅ API Currency Exchange **GRATIS** tanpa perlu registrasi
- ✅ Menggunakan `https://api.exchangerate.host/latest` (FREE API)
- ✅ **TIDAK PERLU API KEY!**

### ✅ **2. File .gitignore**
- ✅ File `.env` **TIDAK** akan ter-push ke GitHub (aman!)
- ✅ File data CSV **AKAN** ter-push (agar data sample tersedia)
- ✅ Secret dan credential terlindungi

### ✅ **3. Data Transaksi**
- ✅ File `data/raw/transactions.csv` **AKAN IKUT** ke GitHub
- ✅ File `data/raw/users.csv` **AKAN IKUT** ke GitHub
- ✅ Data transaksi Anda **TIDAK AKAN HILANG** lagi!

---

## 🎯 **CARA PUSH KE GITHUB:**

### **Step 1: Cek Status Git**
```bash
git status
```

### **Step 2: Add Semua File**
```bash
git add .
```

### **Step 3: Commit Perubahan**
```bash
git commit -m "Update: Fix data persistence and add deployment config"
```

### **Step 4: Push ke GitHub**
```bash
git push origin main
```

---

## 🌐 **CARA DEPLOY (Untuk Testing User):**

### **OPSI 1: Streamlit Cloud (GRATIS & MUDAH!)**

1. **Buka Streamlit Cloud**
   - Pergi ke https://streamlit.io/cloud
   - Login dengan GitHub account Anda

2. **Deploy App**
   - Klik "New app"
   - Pilih repository: `smart-finance-ml`
   - Main file path: `dashboards/streamlit_dashboard_multiuser.py`
   - Klik "Deploy"

3. **Set Environment Variables (PENTING!)**
   - Di Streamlit Cloud dashboard, klik "Advanced settings"
   - Buka tab "Secrets"
   - Copy isi file `.env` Anda dan paste di sana
   - **CATATAN:** Untuk proyek ini, API key kosong pun sudah cukup karena menggunakan FREE API

4. **Selesai!**
   - App akan deploy dalam 5-10 menit
   - Anda akan dapat public URL seperti: `https://your-app.streamlit.app`
   - Bagikan URL ini ke user untuk testing!

---

### **OPSI 2: Heroku (GRATIS dengan Verifikasi)**

1. **Install Heroku CLI**
   ```bash
   # Windows
   # Download dari https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create smart-finance-ml-app
   ```

4. **Set Environment Variables**
   ```bash
   # Set buildpack untuk Python
   heroku buildpacks:set heroku/python

   # TIDAK PERLU set API key karena API gratis
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Buka App**
   ```bash
   heroku open
   ```

---

### **OPSI 3: Railway (GRATIS & MODERN)**

1. **Buka Railway**
   - Pergi ke https://railway.app
   - Login dengan GitHub

2. **New Project**
   - Klik "New Project"
   - Pilih "Deploy from GitHub repo"
   - Pilih `smart-finance-ml`

3. **Configure**
   - Railway akan auto-detect Python app
   - Add environment variables dari `.env` (optional karena API gratis)

4. **Deploy**
   - Railway akan otomatis deploy
   - Anda akan dapat public URL

---

## 🧪 **CARA TEST APLIKASI LOKAL:**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Generate Sample Data (Jika Belum Ada)**
```bash
python src/data_generation/generate_data.py
```

### **3. Run Dashboard**
```bash
# Windows
run_dashboard.bat

# Linux/Mac
./run_dashboard.sh
```

### **4. Buka Browser**
```
http://localhost:8501
```

---

## 👥 **CARA USER TEST APLIKASI:**

### **Akun Test yang Tersedia:**
Setelah deploy, user bisa:

1. **Register Akun Baru:**
   - Buka URL app
   - Klik "Register"
   - Isi form registrasi
   - Login dengan akun baru

2. **Atau Login dengan Sample User:**
   - Email: `user001@example.com`
   - Password: `password123`

   *(Cek file `data/raw/users.csv` untuk akun sample lainnya)*

### **Fitur yang Bisa Ditest:**
- ✅ Login/Register
- ✅ Add Transaction (transaksi akan tersimpan!)
- ✅ View Dashboard
- ✅ Budget Recommendations
- ✅ Currency Conversion (REAL-TIME dari API!)
- ✅ Spending Forecast
- ✅ Delete Transactions
- ✅ Export Reports

---

## 🔒 **KEAMANAN:**

### ✅ **Yang AMAN di GitHub:**
- ✅ Source code
- ✅ Sample data (bukan data real user)
- ✅ Configuration files
- ✅ README dan dokumentasi

### ❌ **Yang TIDAK akan ke GitHub:**
- ❌ File `.env` (secret!)
- ❌ Database files (`.db`, `.sqlite`)
- ❌ Model files (`.pkl`, `.h5`)
- ❌ Logs dengan data sensitif

---

## 🆘 **TROUBLESHOOTING:**

### **Problem: "No transactions found"**
**Solusi:**
```bash
# Generate sample data
python src/data_generation/generate_data.py
```

### **Problem: "Currency API Error"**
**Solusi:**
- API `exchangerate.host` adalah FREE dan tidak perlu key
- Jika error, aplikasi akan gunakan fallback rates:
  - USD: 1.0
  - CNY: 7.2
  - IDR: 15800.0

### **Problem: "Module not found"**
**Solusi:**
```bash
# Install ulang dependencies
pip install -r requirements.txt
```

### **Problem: "Data hilang setelah push"**
**Solusi:**
- Sudah FIXED! File `.gitignore` sudah diupdate
- File CSV sekarang akan ikut ke GitHub

---

## 📧 **KONTAK & SUPPORT:**

Jika ada masalah:
1. Cek file `TROUBLESHOOTING.md`
2. Cek file `QUICK_START.md`
3. Lihat logs di folder `logs/`

---

## 🎉 **SELAMAT!**

Aplikasi Anda sudah siap untuk:
- ✅ Push ke GitHub
- ✅ Deploy ke cloud
- ✅ Testing oleh user
- ✅ Production use!

**Good luck! 🚀**
