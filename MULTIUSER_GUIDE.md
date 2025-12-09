# Multi-User Deployment Guide

## 🎯 Making Your System Public

This guide shows you how to deploy the Smart Finance system so **anyone** can register and track their own budget.

---

## 🚀 Quick Start - Multi-User Version

### Step 1: Launch the Multi-User Dashboard

```bash
streamlit run dashboards/streamlit_dashboard_multiuser.py
```

### Step 2: Users Can Now:
1. **Register** a new account (name, email, password, income)
2. **Login** with their credentials
3. **Add transactions** through the web interface
4. **Track their own budget** (data is private to each user)
5. **Get personalized recommendations**

---

## 🔐 How It Works

### User Registration
- Each user creates account with email & password
- Password is hashed (SHA256) - stored securely
- User gets unique ID (U00001, U00002, etc.)
- Income and currency preferences saved

### User Login
- Email + password authentication
- Session management (stays logged in)
- Each user sees only their own data

### Data Privacy
- All users share same CSV files BUT:
  - Users are filtered by `user_id`
  - Each user sees only their transactions
  - Budget recommendations are personalized

---

## 📊 Features of Multi-User Version

### ✅ What's Included

**For Each User:**
- Personal dashboard with 5 tabs
- Add transactions through web interface (no CSV editing!)
- Budget health score (50/30/20 rule)
- Spending analytics & charts
- Currency conversion
- Export personal data

**Security:**
- Password hashing
- Session management
- Logout functionality
- User data isolation

---

## 🌐 Deployment Options

### Option 1: Local Testing (FREE)

**Good for:** Testing with friends/family on same network

```bash
# Run on your computer
streamlit run dashboards/streamlit_dashboard_multiuser.py --server.address 0.0.0.0

# Share this URL with others on your WiFi:
http://YOUR_COMPUTER_IP:8501
```

**Example:**
- Your computer IP: 192.168.1.100
- Friends access: http://192.168.1.100:8501

**Pros:** Free, fast, private network
**Cons:** Only works on your WiFi, computer must stay on

---

### Option 2: Streamlit Cloud (FREE + PUBLIC)

**Good for:** Making it available to ANYONE on the internet

#### Steps:

1. **Create GitHub Account** (free)
   - Go to https://github.com
   - Sign up with email

2. **Upload Your Code**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/smart-finance.git
   git push -u origin main
   ```

3. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `dashboards/streamlit_dashboard_multiuser.py`
   - Click "Deploy"

4. **Get Your Public URL**
   - Example: `https://your-app-name.streamlit.app`
   - Share this with ANYONE!

**Pros:** Free, accessible anywhere, auto-updates
**Cons:** Public URL (anyone can access), 1GB RAM limit

**Important:**
- Don't commit sensitive data to GitHub
- Consider adding rate limiting for security

---

### Option 3: Cloud VPS ($5-10/month)

**Good for:** Professional deployment, custom domain, unlimited resources

#### Recommended Providers:
- **DigitalOcean** ($6/month)
- **Linode** ($5/month)
- **Vultr** ($5/month)
- **AWS Lightsail** ($5/month)

#### Setup Steps:

1. **Rent a VPS**
   - Choose Ubuntu 22.04
   - Minimum: 1GB RAM, 1 CPU

2. **SSH into Server**
   ```bash
   ssh root@your-server-ip
   ```

3. **Install Dependencies**
   ```bash
   # Update system
   apt update && apt upgrade -y

   # Install Python
   apt install python3-pip python3-venv nginx -y

   # Clone your code
   git clone https://github.com/YOUR_USERNAME/smart-finance.git
   cd smart-finance

   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate

   # Install requirements
   pip install -r requirements.txt
   ```

4. **Run with systemd (auto-restart)**
   ```bash
   # Create service file
   nano /etc/systemd/system/smart-finance.service
   ```

   ```ini
   [Unit]
   Description=Smart Finance Dashboard
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/smart-finance
   Environment="PATH=/root/smart-finance/.venv/bin"
   ExecStart=/root/smart-finance/.venv/bin/streamlit run dashboards/streamlit_dashboard_multiuser.py --server.port 8501 --server.address 0.0.0.0
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   # Start service
   systemctl daemon-reload
   systemctl start smart-finance
   systemctl enable smart-finance
   ```

5. **Setup Nginx (Optional - for custom domain)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

6. **Get SSL Certificate (HTTPS)**
   ```bash
   apt install certbot python3-certbot-nginx -y
   certbot --nginx -d your-domain.com
   ```

**Pros:** Full control, custom domain, unlimited users, professional
**Cons:** Costs $5-10/month, requires technical setup

---

## 🔒 Security Enhancements

### 1. Add Rate Limiting (Prevent Spam Registrations)

Create `dashboards/rate_limiter.py`:

```python
import streamlit as st
from datetime import datetime, timedelta

def check_rate_limit(email, limit=5, window=3600):
    """Allow max 5 attempts per hour"""
    if 'rate_limits' not in st.session_state:
        st.session_state['rate_limits'] = {}

    now = datetime.now()
    key = f"login_{email}"

    if key in st.session_state['rate_limits']:
        attempts, last_time = st.session_state['rate_limits'][key]

        # Reset if window expired
        if (now - last_time).seconds > window:
            st.session_state['rate_limits'][key] = (1, now)
            return True

        # Check limit
        if attempts >= limit:
            return False

        # Increment
        st.session_state['rate_limits'][key] = (attempts + 1, now)
        return True
    else:
        st.session_state['rate_limits'][key] = (1, now)
        return True
```

### 2. Email Verification (Optional)

Use SendGrid or SMTP to send verification emails:

```python
import smtplib
from email.mime.text import MIMEText

def send_verification_email(email, code):
    msg = MIMEText(f"Your verification code: {code}")
    msg['Subject'] = 'Verify Your Email'
    msg['From'] = 'noreply@yourapp.com'
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email@gmail.com', 'your-password')
        server.send_message(msg)
```

### 3. Two-Factor Authentication (Advanced)

Use PyOTP for 2FA:

```bash
pip install pyotp qrcode
```

### 4. Database Migration (Recommended for Production)

**Why:** CSV files don't scale well for many users

**Solution:** Use PostgreSQL

```bash
# Install PostgreSQL
apt install postgresql postgresql-contrib -y

# Create database
sudo -u postgres psql
CREATE DATABASE smart_finance;
CREATE USER finance_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE smart_finance TO finance_user;
```

Then use SQLAlchemy to replace CSV operations:

```python
from sqlalchemy import create_engine
engine = create_engine('postgresql://finance_user:secure_password@localhost/smart_finance')
```

---

## 📊 Monitoring & Analytics

### Track User Growth

Add to your dashboard:

```python
# Show total users
total_users = len(auth.load_users())
st.sidebar.metric("Total Users", total_users)

# Show active users (last 7 days)
recent_transactions = transactions_df[
    transactions_df['transaction_date'] >= datetime.now() - timedelta(days=7)
]
active_users = recent_transactions['user_id'].nunique()
st.sidebar.metric("Active Users (7d)", active_users)
```

### Backup Strategy

**Automated Daily Backups:**

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/root/backups"

# Backup data
cp config/data/raw/users.csv $BACKUP_DIR/users_$DATE.csv
cp config/data/raw/transactions.csv $BACKUP_DIR/transactions_$DATE.csv

# Keep only last 30 days
find $BACKUP_DIR -name "*.csv" -mtime +30 -delete
```

Add to cron:
```bash
crontab -e
# Add: 0 2 * * * /root/smart-finance/backup.sh
```

---

## 🎯 Customization Options

### 1. Branding

Edit `streamlit_dashboard_multiuser.py`:

```python
st.set_page_config(
    page_title="YourCompany Finance",
    page_icon="💰",
    layout="wide"
)

st.markdown('<h1 style="color: #YOUR_COLOR;">Your Company Name</h1>', unsafe_allow_html=True)
```

### 2. Add Features

**Email Notifications:**
- Send weekly spending summaries
- Alert on large transactions
- Budget exceeded warnings

**Social Features:**
- Leaderboard (who saves most)
- Compare with average user
- Challenges & goals

**Premium Features:**
- Free tier: Basic tracking
- Premium tier: ML predictions, advanced analytics
- Use Stripe for payments

---

## 💰 Monetization Ideas

If you want to make money from this:

1. **Freemium Model**
   - Free: 50 transactions/month
   - Pro ($5/month): Unlimited, ML forecasting, priority support

2. **Affiliate Links**
   - Recommend financial products
   - Earn commission on sign-ups

3. **White Label**
   - License to banks/companies
   - Custom branding

4. **Ads**
   - Google AdSense (least preferred)

---

## 📱 Mobile App (Future)

To reach more users, create a mobile app:

1. **React Native** - iOS + Android from one codebase
2. **Flutter** - Google's framework
3. **Progressive Web App (PWA)** - Web app that works offline

---

## 🚀 Quick Deploy Command

```bash
# For Streamlit Cloud deployment:
git add .
git commit -m "Ready for deployment"
git push origin main

# Then go to streamlit.io/cloud and click Deploy!
```

---

## ✅ Pre-Launch Checklist

Before making public:

- [ ] Test registration with multiple users
- [ ] Test data isolation (users can't see each other's data)
- [ ] Add rate limiting
- [ ] Set up backups
- [ ] Test on mobile browsers
- [ ] Add privacy policy
- [ ] Add terms of service
- [ ] Test with high traffic (load testing)
- [ ] Set up error monitoring (Sentry)
- [ ] Add analytics (Google Analytics)

---

## 📞 Support

**For Deployment Help:**
- Streamlit Community: https://discuss.streamlit.io
- DigitalOcean Docs: https://docs.digitalocean.com
- GitHub Discussions: Your repository

---

**Ready to go public? Pick a deployment option and launch!** 🚀

**Recommended Path:**
1. Start with Streamlit Cloud (free, easy)
2. Test with real users
3. Migrate to VPS when you have 100+ users
4. Add database when you have 1000+ users
