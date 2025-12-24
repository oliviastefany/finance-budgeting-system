# 🔒 PANDUAN DATABASE & PRIVACY - Smart Finance ML

**Penjelasan Lengkap untuk Pemula tentang Database, Keamanan, dan Privacy**

---

## 📚 **TABLE OF CONTENTS**

1. [Apa itu Database?](#apa-itu-database)
2. [Bagaimana Data Disimpan?](#bagaimana-data-disimpan)
3. [Keamanan Password](#keamanan-password)
4. [Privacy & Proteksi Data User](#privacy-proteksi-data-user)
5. [Cara Mengolah Data User](#cara-mengolah-data-user)
6. [Best Practices](#best-practices)
7. [Upgrade ke Database Real](#upgrade-ke-database-real)

---

## 📦 **1. APA ITU DATABASE?**

### **Definisi Sederhana:**
Database adalah **tempat penyimpanan data** yang terorganisir. Seperti **lemari arsip digital** yang menyimpan:
- Data user (nama, email, password)
- Data transaksi (belanja, tanggal, jumlah)
- Data keuangan (income, budget, dll)

### **Di Proyek Ini:**
Anda menggunakan **2 jenis penyimpanan:**

#### **A. CSV Files (Saat Ini)** ← Yang Anda Pakai
```
config/data/raw/
├── users.csv         ← Data user (250 users)
└── transactions.csv  ← Data transaksi (15,000 transaksi)
```

**Contoh isi `users.csv`:**
```csv
user_id,name,email,phone,monthly_income,preferred_currency
U00001,Rhonda Marks,whitehector@example.net,406.550.8380,15000,IDR
U00002,Christopher Hunter,susan66@example.org,991-233-6455,20000,USD
```

**Contoh isi `transactions.csv`:**
```csv
transaction_id,user_id,amount,currency,category,merchant,transaction_date
T00001,U00001,239.84,USD,Hobbies,Sports Store,2024-01-01 00:18:16
T00002,U00071,169.76,USD,Groceries,Trader Joes,2024-01-01 01:17:08
```

#### **B. SQL Database (Untuk Production Nanti)**
- PostgreSQL
- MySQL
- SQLite
- MongoDB

---

## 💾 **2. BAGAIMANA DATA DISIMPAN?**

### **Flow Penyimpanan Data:**

```
USER INPUT → VALIDATION → PROCESSING → SAVE TO FILE → SECURITY CHECK
     ↓            ↓             ↓             ↓              ↓
  Form       Check data    Hash password   Write CSV    Protect file
```

### **Kode di Proyek Anda:**

#### **A. SAVE USER DATA** ([dashboards/auth.py:34-36](dashboards/auth.py#L34-L36))
```python
def save_users(self, users_df):
    """Save users to CSV"""
    users_df.to_csv(self.users_file, index=False)
```

**Penjelasan:**
1. User registrasi via form
2. Data validasi (email, password, dll)
3. Password di-**hash** (enkripsi)
4. Data disave ke `users.csv`

#### **B. SAVE TRANSACTION DATA** ([dashboards/streamlit_dashboard_multiuser.py:683](dashboards/streamlit_dashboard_multiuser.py#L683))
```python
def add_transaction(user_id, category, merchant, amount, currency, description=""):
    transactions_df = pd.read_csv(RAW_DATA_DIR / 'transactions.csv')

    # Create new transaction
    new_transaction = {
        'transaction_id': new_id,
        'user_id': user_id,  # ← Link ke user
        'amount': amount,
        'currency': currency,
        'category': category,
        # ... data lainnya
    }

    # Append dan save
    transactions_df = pd.concat([transactions_df, pd.DataFrame([new_transaction])], ignore_index=True)
    transactions_df.to_csv(RAW_DATA_DIR / 'transactions.csv', index=False)
```

**Penjelasan:**
1. User add transaksi via form
2. Generate transaction ID (T00001, T00002, dst)
3. Link ke `user_id` (jadi setiap transaksi tahu siapa pemiliknya)
4. Save ke `transactions.csv`

---

## 🔐 **3. KEAMANAN PASSWORD**

### **JANGAN PERNAH Simpan Password Plain Text!**

❌ **SALAH (BERBAHAYA!):**
```csv
user_id,email,password
U00001,john@example.com,password123  ← BAHAYA! Plain text!
```

✅ **BENAR (AMAN!):**
```csv
user_id,email,password_hash
U00001,john@example.com,ef92b778bafe771e89245b89ecbc0815  ← Aman! Hash!
```

### **Cara Kerja Password Hashing:**

#### **Di Code Anda:** ([dashboards/auth.py:24-26](dashboards/auth.py#L24-L26))
```python
def hash_password(self, password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()
```

**Penjelasan:**
1. User input password: `"password123"`
2. Sistem hash dengan SHA256: `"ef92b778bafe771e89245b89ecbc0815"`
3. Yang disave: hash, bukan password asli!
4. **TIDAK BISA di-reverse!** (Tidak bisa balik ke password asli)

### **Cara Verifikasi Login:**

#### **Di Code Anda:** ([dashboards/auth.py:87-103](dashboards/auth.py#L87-L103))
```python
def login(self, email, password):
    users_df = self.load_users()
    user_row = users_df[users_df['email'].str.lower() == email.lower()]

    if len(user_row) == 0:
        return False, None, "Email not found"

    user = user_row.iloc[0]

    # Hash password yang diinput, lalu bandingkan dengan hash yang disimpan
    if user['password_hash'] != self.hash_password(password):
        return False, None, "Incorrect password"

    return True, user['user_id'], "Login successful!"
```

**Flow:**
1. User login dengan email + password
2. Sistem hash password yang diinput
3. Bandingkan hash baru dengan hash yang tersimpan
4. Jika sama → Login berhasil!

---

## 🛡️ **4. PRIVACY & PROTEKSI DATA USER**

### **A. DATA ISOLATION - Setiap User Hanya Lihat Data Sendiri**

#### **Di Code Anda:** ([dashboards/streamlit_dashboard_multiuser.py:903-908](dashboards/streamlit_dashboard_multiuser.py#L903-L908))
```python
# Filter user transactions
user_transactions = transactions_df[
    (transactions_df['user_id'] == user_id) &  # ← FILTER BY USER!
    (transactions_df['transaction_date'] >= start_date) &
    (transactions_df['transaction_date'] <= end_date)
].copy()
```

**Penjelasan:**
- User A (U00001) **HANYA bisa lihat** transaksi dengan `user_id = U00001`
- User B (U00002) **HANYA bisa lihat** transaksi dengan `user_id = U00002`
- **TIDAK BISA** lihat data user lain!

#### **Delete Transaction - Hanya Punya Sendiri:**
```python
def delete_transaction(transaction_id, user_id):
    # Check if transaction belongs to user
    transaction = transactions_df[transactions_df['transaction_id'] == transaction_id]

    if transaction.iloc[0]['user_id'] != user_id:  # ← CEK OWNERSHIP!
        return False, "You can only delete your own transactions"

    # Hapus hanya jika punya sendiri
    transactions_df = transactions_df[transactions_df['transaction_id'] != transaction_id]
```

### **B. FILE SECURITY - Proteksi File dari GitHub**

#### **Di `.gitignore`:** ([.gitignore:1-5](.gitignore#L1-L5))
```gitignore
# Environment Variables (CRITICAL - Contains API keys and passwords)
.env          ← File rahasia TIDAK masuk GitHub
.env.local
.env.*.local
```

**Yang Diproteksi:**
- ✅ `.env` - API keys, passwords
- ✅ `*.db` - Database files
- ✅ `*.sqlite` - SQLite databases
- ✅ `logs/*.log` - Log files (mungkin contain sensitive data)
- ✅ `secrets/` - Folder secrets
- ✅ `*.pem`, `*.key` - Encryption keys

**Yang Boleh Public (Sample Data):**
- ✅ `users.csv` - Sample user (bukan real data)
- ✅ `transactions.csv` - Sample transactions (bukan real data)
- ✅ Source code

### **C. SESSION MANAGEMENT - User Login State**

#### **Di Code Anda:** ([dashboards/auth.py:173-182](dashboards/auth.py#L173-L182))
```python
def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        show_login_page()  # ← Redirect ke login jika belum login
        return False

    return True
```

**Penjelasan:**
1. User login → Session dibuat
2. Session menyimpan: `user_id`, `authenticated = True`
3. Setiap akses page → Check session
4. Jika tidak ada session → Redirect ke login
5. Logout → Session dihapus

---

## 🔧 **5. CARA MENGOLAH DATA USER**

### **A. READ Data User (Aman)**

```python
def get_user_transactions(user_id):
    """Get transactions for specific user only"""
    transactions_df = pd.read_csv('transactions.csv')

    # FILTER by user_id (PENTING!)
    user_data = transactions_df[transactions_df['user_id'] == user_id]

    return user_data
```

### **B. AGGREGATE Data (Analytics) - Aman**

```python
def get_user_spending_summary(user_id):
    """Get spending summary for one user"""
    user_data = get_user_transactions(user_id)

    # Analytics per user
    summary = {
        'total_spending': user_data['amount'].sum(),
        'avg_transaction': user_data['amount'].mean(),
        'top_category': user_data['category'].mode()[0]
    }

    return summary
```

### **C. GLOBAL Analytics (Tanpa Expose Individual Data)**

```python
def get_platform_statistics():
    """Platform-wide stats WITHOUT exposing individual data"""
    transactions_df = pd.read_csv('transactions.csv')
    users_df = pd.read_csv('users.csv')

    # AGGREGATE data - TIDAK tampilkan individual user
    stats = {
        'total_users': len(users_df),
        'total_transactions': len(transactions_df),
        'avg_transaction_amount': transactions_df['amount'].mean(),
        'most_popular_category': transactions_df['category'].mode()[0]
    }

    # JANGAN include: email, name, specific user data
    return stats
```

### **D. Data Export (User Request) - Aman**

```python
def export_user_data(user_id):
    """Export data for ONE user only (GDPR compliance)"""
    # Get user's own data
    user_transactions = get_user_transactions(user_id)

    # Export to CSV
    csv = user_transactions.to_csv(index=False)

    return csv
```

---

## ✅ **6. BEST PRACTICES - Aturan Emas**

### **A. ALWAYS Filter by User ID**
```python
# ✅ BENAR
user_data = df[df['user_id'] == current_user_id]

# ❌ SALAH (Expose semua data!)
all_data = df  # Bahaya!
```

### **B. NEVER Store Plain Text Passwords**
```python
# ✅ BENAR
password_hash = hashlib.sha256(password.encode()).hexdigest()

# ❌ SALAH
stored_password = password  # BAHAYA!
```

### **C. NEVER Expose Sensitive Data in Logs**
```python
# ✅ BENAR
logger.info(f"User {user_id} logged in")

# ❌ SALAH
logger.info(f"User {email} logged in with password {password}")  # BAHAYA!
```

### **D. NEVER Commit Secrets to Git**
```python
# ✅ BENAR - Use .env
API_KEY = os.getenv('API_KEY')

# ❌ SALAH - Hardcoded
API_KEY = "sk-1234567890abcdef"  # BAHAYA!
```

### **E. ALWAYS Validate User Input**
```python
# ✅ BENAR
def add_transaction(user_id, amount):
    if amount <= 0:
        return False, "Invalid amount"
    if not user_id:
        return False, "User not authenticated"
    # ... save data

# ❌ SALAH - No validation
def add_transaction(user_id, amount):
    save_to_db(user_id, amount)  # Bisa inject SQL, XSS, dll
```

### **F. DATA RETENTION - Hapus Data Lama**
```python
def cleanup_old_data():
    """Delete data older than 2 years (GDPR compliance)"""
    cutoff_date = datetime.now() - timedelta(days=730)

    transactions_df = pd.read_csv('transactions.csv')
    transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])

    # Keep only recent data
    recent_data = transactions_df[transactions_df['transaction_date'] > cutoff_date]
    recent_data.to_csv('transactions.csv', index=False)
```

---

## 🚀 **7. UPGRADE KE DATABASE REAL (PostgreSQL/MySQL)**

### **Kenapa Upgrade dari CSV?**

**CSV (Saat Ini):**
- ✅ Simple, mudah untuk belajar
- ✅ Tidak perlu setup database
- ❌ Lambat untuk data besar (>100k rows)
- ❌ Tidak ada concurrent access (banyak user bersamaan)
- ❌ Tidak ada transaction rollback
- ❌ Risiko data corrupt

**SQL Database (Production):**
- ✅ Cepat, bahkan untuk millions of rows
- ✅ Support concurrent users (1000+ users bersamaan)
- ✅ ACID compliance (data integrity)
- ✅ Built-in security features
- ✅ Automatic backup & recovery

### **Cara Migrate ke PostgreSQL:**

#### **Step 1: Install PostgreSQL**
```bash
# Windows: Download dari postgresql.org
# Linux:
sudo apt-get install postgresql postgresql-contrib
```

#### **Step 2: Create Database**
```sql
CREATE DATABASE smart_finance;
CREATE USER finance_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE smart_finance TO finance_user;
```

#### **Step 3: Create Tables**
```sql
-- Users table
CREATE TABLE users (
    user_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,  -- SHA256 hash
    monthly_income DECIMAL(10, 2),
    preferred_currency VARCHAR(3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id VARCHAR(10) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    category VARCHAR(50) NOT NULL,
    merchant VARCHAR(100),
    transaction_date TIMESTAMP NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_transaction_user ON transactions(user_id);
CREATE INDEX idx_transaction_date ON transactions(transaction_date);
```

#### **Step 4: Update Code - Database Manager**
```python
# src/database/db_manager.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'smart_finance'),
            user=os.getenv('DB_USER', 'finance_user'),
            password=os.getenv('DB_PASSWORD')
        )

    def get_user_by_email(self, email):
        """Get user by email"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM users WHERE email = %s",  # ← Parameterized query (aman dari SQL injection!)
                (email,)
            )
            return cur.fetchone()

    def create_user(self, user_data):
        """Create new user"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (user_id, name, email, password_hash, monthly_income, preferred_currency)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_data['user_id'], user_data['name'], user_data['email'],
                 user_data['password_hash'], user_data['monthly_income'], user_data['currency'])
            )
            self.conn.commit()

    def get_user_transactions(self, user_id, start_date, end_date):
        """Get transactions for specific user (FILTERED!)"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT * FROM transactions
                WHERE user_id = %s  -- ← FILTER by user!
                AND transaction_date BETWEEN %s AND %s
                ORDER BY transaction_date DESC
                """,
                (user_id, start_date, end_date)
            )
            return cur.fetchall()
```

#### **Step 5: Update .env**
```bash
# .env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_finance
DB_USER=finance_user
DB_PASSWORD=your_secure_password_here_min_16_chars
```

#### **Step 6: Migrate Data dari CSV ke PostgreSQL**
```python
# scripts/migrate_csv_to_postgres.py
import pandas as pd
from src.database.db_manager import DatabaseManager

def migrate_users():
    """Migrate users from CSV to PostgreSQL"""
    db = DatabaseManager()
    users_df = pd.read_csv('config/data/raw/users.csv')

    for _, user in users_df.iterrows():
        db.create_user({
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email'],
            'password_hash': user.get('password_hash', hashlib.sha256('password123'.encode()).hexdigest()),
            'monthly_income': user['monthly_income'],
            'currency': user['preferred_currency']
        })

    print(f"Migrated {len(users_df)} users")

if __name__ == "__main__":
    migrate_users()
```

---

## 📊 **PERBANDINGAN: CSV vs SQL Database**

| Feature | CSV (Current) | PostgreSQL (Recommended) |
|---------|--------------|-------------------------|
| **Setup** | ✅ Mudah (No setup) | ⚠️ Perlu install & config |
| **Speed (1k rows)** | ✅ Fast | ✅ Very fast |
| **Speed (100k+ rows)** | ❌ Slow | ✅ Very fast |
| **Concurrent Users** | ❌ 1-5 users | ✅ 1000+ users |
| **Data Integrity** | ❌ Risk corrupt | ✅ ACID compliance |
| **Security** | ⚠️ File-based | ✅ Built-in security |
| **Backup** | ⚠️ Manual | ✅ Automatic |
| **Scalability** | ❌ Limited | ✅ Excellent |
| **Best For** | Testing, Learning | Production |

---

## 🎯 **KESIMPULAN**

### **Untuk Belajar & Testing:**
- ✅ CSV sudah cukup (yang Anda pakai sekarang)
- ✅ Simple, mudah dipahami
- ✅ Bisa deploy ke Streamlit Cloud

### **Untuk Production (Real Users):**
- ✅ Upgrade ke PostgreSQL atau MySQL
- ✅ Better security
- ✅ Better performance
- ✅ Support banyak user bersamaan

### **Kapan Harus Upgrade?**
- User > 50 orang
- Transaksi > 50,000 rows
- Butuh real-time analytics
- Butuh backup otomatis

---

## 🔒 **PRIVACY CHECKLIST**

### **Sebelum Deploy ke Production:**

- [ ] Password di-hash (TIDAK plain text)
- [ ] File `.env` di-gitignore
- [ ] Setiap query filter by `user_id`
- [ ] Validasi semua user input
- [ ] Log TIDAK contain password/email
- [ ] HTTPS enabled (SSL certificate)
- [ ] Backup database otomatis
- [ ] Data retention policy (hapus data lama)
- [ ] Privacy policy & Terms of Service
- [ ] GDPR compliance (jika user Eropa)

---

## 📚 **RESOURCES**

### **Belajar Lebih Lanjut:**
- PostgreSQL Tutorial: https://www.postgresqltutorial.com/
- GDPR Compliance: https://gdpr.eu/
- OWASP Security: https://owasp.org/
- Password Hashing: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

**Semoga membantu! 🚀**

Ada pertanyaan? Tanya aja! 😊
