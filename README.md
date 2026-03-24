# Smart Finance ML - Personal Finance Management System

An intelligent personal finance tracking and budgeting system with ML-powered fraud detection, spending forecasting, and personalized budget recommendations using the 50/30/20 rule.


✅ Live demo : https://finance-budgeting-system.streamlit.app/

---

## 🎯 What This System Does

### For You (Personal Use)
- **Track Your Spending**: Record and categorize all your transactions
- **Multi-Currency Support**: Handle USD, IDR, and CNY with real-time conversion
- **Budget Recommendations**: Get personalized advice based on the 50/30/20 rule
- **Health Score**: See how well you're managing your finances (0-100 scale)
- **Visual Analytics**: Interactive charts showing spending patterns
- **Fraud Detection**: ML algorithms flag suspicious transactions (optional)
- **Spending Forecasts**: Predict future spending trends (optional)

### Current System
Right now, the system contains **250 demo users** with **15,000 transactions**. You can:
1. View any demo user's financial data
2. See how the system works
3. Understand the features before adding your own data

---

## 🚀 Quick Start - Using the System NOW

### Step 1: Launch the Dashboard
```bash
streamlit run dashboards/streamlit_dashboard.py
```

The dashboard opens at: http://localhost:8501 (or http://localhost:8506 if 8501 is busy)

### Step 2: Select a User
In the sidebar:
1. **Select User**: Choose any user from the dropdown (e.g., "Brandi Silva")
2. **Display Currency**: Choose USD, IDR, or CNY
3. **Date Range**: Select "All Time" to see all data

### Step 3: Explore Features

#### 📊 Overview Tab
- See total spending, transaction count
- View spending by category (bar chart & pie chart)
- Track daily spending trends
- Review recent transactions

#### 💡 Budget Recommendations Tab
- Enter monthly income (or use the demo user's income)
- See ideal vs actual spending (50/30/20 rule)
- Get budget health score (0-100)
- Receive personalized recommendations

#### 💱 Currency Converter Tab
- Convert between USD, IDR, CNY
- View exchange rate matrix
- Update rates in real-time

#### 📄 Reports Tab
- Export transactions to CSV
- View summary statistics

---

## 📝 How to Use This for YOUR OWN Finances

### Option 1: Manual Entry (Simple - Start Here!)
Edit the CSV files directly:

1. **Add yourself as a user:**
   ```bash
   # Open: config/data/raw/users.csv
   # Add a new row:
   U00251,Your Name,your@email.com,5000,USD
   ```

2. **Add your transactions:**
   ```bash
   # Open: config/data/raw/transactions.csv
   # Add rows for each transaction:
   T15001,U00251,2025-11-27 10:30:00,Groceries,Walmart,150.50,USD,Weekly shopping
   T15002,U00251,2025-11-27 14:00:00,Dining,Restaurant,45.00,USD,Lunch
   ```

3. **Refresh the dashboard** - Your data appears immediately!

**Format for transactions.csv:**
```
transaction_id,user_id,transaction_date,category,merchant,amount,currency,description
```

**Available Categories:**
- **Essentials**: Groceries, Utilities, Rent, Healthcare, Insurance, Transportation
- **Discretionary**: Dining, Entertainment, Shopping, Travel, Hobbies
- **Savings**: Savings, Investment, Emergency Fund

### Option 2: Database Integration (Recommended for Production)

The system includes PostgreSQL support. To use it:

1. **Setup PostgreSQL:**
   ```bash
   # Install PostgreSQL
   # Create database
   createdb smart_finance
   ```

2. **Configure environment:**
   ```bash
   # Create .env file
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=smart_finance
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

3. **Initialize database:**
   ```bash
   python src/database/db_manager.py
   ```

### Option 3: Build a Data Entry Interface (Future Enhancement)

You could add a simple form to input transactions through the dashboard:
- Add a new tab "Add Transaction"
- Fill in: date, category, merchant, amount, currency
- Submit → saves to CSV or database

---

## 🎯 Next Steps - Your Roadmap

### Week 1: Get Familiar (This Week!)

#### Day 1-2: Explore Demo Data
```bash
# Launch and explore
streamlit run dashboards/streamlit_dashboard.py

# Try all features:
# - Select different users
# - Change currencies
# - Adjust date ranges
# - Check budget recommendations
```

#### Day 3-4: Add Your Data
```bash
# 1. Open config/data/raw/users.csv
# 2. Add yourself as user U00251
# 3. Open config/data/raw/transactions.csv
# 4. Add your last month's transactions
# 5. Refresh dashboard to see YOUR data
```

#### Day 5-7: Track New Transactions
- Add each transaction as it happens
- Review daily spending in dashboard
- Check your budget health score

### Week 2-3: Advanced Features

#### Train ML Models (Optional but Recommended)
```bash
# Train fraud detection (10-15 minutes)
python src/fraud_detection/fraud_detector.py

# Train spending forecaster (5-10 minutes)
python src/forecasting/forecaster.py
```

**Benefits:**
- Fraud Detection Tab will work
- Forecasting Tab will show predictions
- Automatic anomaly alerts

#### Set Up Automation (Optional)
```bash
# Install Apache Airflow
pip install apache-airflow

# Initialize Airflow
airflow db init
airflow users create --username admin --password admin --role Admin

# Start Airflow
airflow webserver -p 8080  # In one terminal
airflow scheduler            # In another terminal
```

**Automated tasks:**
- Update exchange rates daily
- Retrain ML models weekly
- Generate monthly reports

### Month 1+: Production Ready

#### Add Authentication
- Password protect your dashboard
- See security section below

#### Deploy to Cloud
- Make it accessible from anywhere
- See deployment guide below

#### Optimize Workflow
- Set up mobile access
- Add transaction shortcuts
- Create monthly review routines

---

## 💡 Using the 50/30/20 Budget Rule

### What is 50/30/20?
- **50% Essentials**: Rent, groceries, utilities, insurance, healthcare
- **30% Discretionary**: Dining out, entertainment, hobbies, shopping
- **20% Savings**: Emergency fund, investments, debt repayment

### How the System Helps You

1. **Automatic Categorization**
   - System categorizes your transactions
   - Calculates how much you spend in each category

2. **Health Score (0-100)**
   - 100 = Perfect budget adherence
   - 70-99 = Good, minor adjustments needed
   - 50-69 = Needs attention
   - 0-49 = Significant overspending

3. **Personalized Recommendations**
   - **Critical**: Overspending by >20% (red alert)
   - **Warning**: Slight overspending (yellow warning)
   - **Good**: Well-balanced or under budget (green)

### Example: How to Adjust YOUR Spending

**Your Input:**
- Monthly Income: $5,000

**System Shows (Ideal):**
- Essentials Budget: $2,500 (50%)
- Discretionary Budget: $1,500 (30%)
- Savings Budget: $1,000 (20%)

**Your Actual (from dashboard):**
- Essentials: $2,800 ❌ ($300 over)
- Discretionary: $1,200 ✅ ($300 under)
- Savings: $800 ⚠️ ($200 under)

**How to Fix:**
1. Review essentials spending in dashboard
2. Find areas to cut (groceries, utilities)
3. Move $300 from essentials to savings
4. Track progress weekly
5. Aim for health score >70

**Track Progress:**
- Week 1: Health Score 65
- Week 2: Health Score 72 ✅
- Week 3: Health Score 78 ✅
- Week 4: Health Score 85 🎉

---

## 📱 Daily Usage Workflow

### Morning Routine (5 minutes)
1. Open dashboard: `streamlit run dashboards/streamlit_dashboard.py`
2. Check yesterday's spending
3. Review budget health score
4. Read any unusual transactions

### After Making Purchases
**Option A: Quick Entry**
```bash
# Open: config/data/raw/transactions.csv
# Add line:
T15003,U00251,2025-11-27 18:30:00,Groceries,Target,85.50,USD,Dinner items
```

**Option B: Batch Entry (End of Day)**
```bash
# Collect all receipts
# Add all transactions at once
# Categories: Groceries, Dining, Entertainment, etc.
```

### Weekly Review (15 minutes - Every Sunday)
1. Open dashboard
2. Select "Last 7 Days" date range
3. Review spending by category
4. Check if over/under budget
5. Adjust next week's spending plan
6. Export weekly report (Reports tab)

### Monthly Planning (30 minutes - End of Month)
1. Select "Last 30 Days"
2. Analyze health score trend
3. Review all categories
4. Set next month's budget goals
5. Check forecast predictions (if trained)
6. Export monthly report
7. Archive old data if needed

---

## 🌐 Deployment Guide

### Option 1: Keep it Local (Current Setup)
**Best for**: Personal use only, highest privacy

```bash
# Just run it on your computer
streamlit run dashboards/streamlit_dashboard.py
```

Pros: Free, private, full control
Cons: Only works on your computer

### Option 2: Local Network Sharing
**Best for**: Share with family on same WiFi

```bash
# Run with network access
streamlit run dashboards/streamlit_dashboard.py --server.address 0.0.0.0

# Family members access at:
# http://YOUR_COMPUTER_IP:8501
# Example: http://192.168.1.100:8501
```

Pros: Free, works on any device at home
Cons: Only works on your WiFi network

### Option 3: Streamlit Cloud (Free Online)
**Best for**: Access from anywhere, free

1. Create GitHub account
2. Push your code to GitHub (without sensitive data!)
3. Go to https://streamlit.io/cloud
4. Connect your GitHub repository
5. Deploy with one click
6. Get URL: https://your-app.streamlit.app

Pros: Free, accessible anywhere, auto-updates
Cons: Public URL (add password protection!)

### Option 4: Cloud Server (Professional)
**Best for**: Full control, custom domain

**Using AWS/DigitalOcean/etc ($5-10/month):**

```bash
# 1. Rent a VPS
# 2. SSH into server
ssh user@your-server-ip

# 3. Install dependencies
sudo apt update
sudo apt install python3-pip
git clone your-repo
cd smart-finance-ml
pip install -r requirements.txt

# 4. Run with screen/tmux
screen -S finance
streamlit run dashboards/streamlit_dashboard.py --server.port 80

# 5. Access at: http://your-server-ip
```

### Adding Password Protection (IMPORTANT!)

Add this to the top of `dashboards/streamlit_dashboard.py`:

```python
import streamlit as st

def check_password():
    """Returns True if password is correct"""
    def password_entered():
        if st.session_state["password"] == "YOUR_SECURE_PASSWORD_HERE":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# ... rest of your dashboard code
```

---

## 📊 System Architecture

```
smart-finance-ml/
├── config/                    # Configuration & Data
│   ├── config.py             # System settings
│   └── data/
│       ├── raw/              # users.csv, transactions.csv ← YOUR DATA HERE
│       └── processed/        # ML-processed data
│
├── src/                      # Core Modules
│   ├── currency/             # Currency conversion
│   ├── budgeting/           # 50/30/20 budget analyzer
│   ├── fraud_detection/     # ML fraud detection
│   ├── forecasting/         # Spending prediction
│   ├── data_generation/     # Demo data generator
│   └── database/            # PostgreSQL integration
│
├── dashboards/              # Streamlit UI
│   └── streamlit_dashboard.py  ← Main dashboard
│
├── airflow/                 # Automation (optional)
│   └── dags/               # Scheduled tasks
│
└── models/                  # Trained ML models
```

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- 500MB disk space
- PostgreSQL (optional)

### Full Installation

```bash
# 1. Navigate to project
cd smart-finance-ml

# 2. Create virtual environment (recommended)
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python test_dashboard_fixes.py

# 5. Launch dashboard
streamlit run dashboards/streamlit_dashboard.py
```

**Expected output from test:**
```
======================================================================
TESTING DASHBOARD FIXES
======================================================================
[1] Testing CurrencyConverter... PASS
[2] Testing BudgetRecommender... PASS
[3] Testing Dashboard Integration... PASS
======================================================================
ALL TESTS PASSED!
======================================================================
```

---

## 🛠️ Troubleshooting

### "No data showing in dashboard"
**Fix**: Select "All Time" in date range filter (sidebar)

### "Charts not displaying"
**Fix**: Clear browser cache (Ctrl+Shift+R) or try different browser

### "Streamlit won't start"
```bash
# Check if port is busy
netstat -ano | findstr :8501

# Use different port
streamlit run dashboards/streamlit_dashboard.py --server.port 8502
```

### "Import errors"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "Currency API not working"
**Normal**: System uses fallback rates (USD=1.0, CNY=7.2, IDR=15,800)

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📈 Success Metrics - Track Your Progress

### Financial Health Indicators
- **Budget Health Score**: Aim for 70+ consistently
- **Savings Rate**: Target 20%+ of income
- **Spending Awareness**: Know where every dollar goes
- **Emergency Fund**: Build 3-6 months expenses

### System Usage Goals
- **Week 1**: Add all transactions daily
- **Week 2-4**: Review dashboard 3x/week
- **Month 2+**: Weekly reviews become automatic
- **Month 3+**: Hit budget targets consistently

---

## 🎁 What You Have Now (Working Features)

✅ **Core Features**:
- Interactive dashboard with 6 tabs
- 250 demo users + 15,000 transactions
- Real-time currency conversion (USD, IDR, CNY)
- Budget recommendations (50/30/20 rule)
- Budget health scoring (0-100)
- Visual analytics & charts
- CSV export functionality
- Multi-currency support

✅ **Ready to Use**:
- Add your own transactions (edit CSV)
- Track spending categories
- Get budget recommendations
- Monitor financial health
- Export reports

⚠️ **Optional Enhancements** (Train models first):
- Fraud detection & alerts
- Spending forecasts & predictions
- Automated workflows

---

## 🚀 START NOW - 3 Simple Steps

### Today (10 minutes)
```bash
# 1. Launch dashboard
streamlit run dashboards/streamlit_dashboard.py

# 2. Explore features with demo data
# - Select user from sidebar
# - Choose "All Time" date range
# - Try all 6 tabs

# 3. Understand the interface
```

### This Week (30 minutes)
```bash
# 1. Add yourself to users.csv
# User ID: U00251
# Name: Your Name
# Email: your@email.com
# Income: 5000
# Currency: USD

# 2. Add your November transactions
# Transaction ID: T15001, T15002, T15003...
# Use format: ID,UserID,Date,Category,Merchant,Amount,Currency,Description

# 3. Refresh dashboard - see YOUR data!
```

### This Month (1-2 hours)
```bash
# 1. Add all your transactions from last 3 months
# 2. Review budget recommendations
# 3. Set financial goals based on health score
# 4. Train ML models (optional)
# 5. Set up weekly review routine
```

---

## 📞 Support & Resources

### Project Documentation
- **[QUICK_START.md](QUICK_START.md)** - 5-minute quick start
- **[VALIDATION_REPORT.md](VALIDATION_REPORT.md)** - Technical details
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues

### External Resources
- **50/30/20 Rule**: https://www.investopedia.com/ask/answers/022916/what-502030-budget-rule.asp
- **Streamlit Docs**: https://docs.streamlit.io
- **Personal Finance**: r/personalfinance on Reddit

### Files to Know
- **Your data**: `config/data/raw/users.csv` & `transactions.csv`
- **Settings**: `config/config.py`
- **Dashboard**: `dashboards/streamlit_dashboard.py`
- **Tests**: `test_dashboard_fixes.py`

---

## 🎯 Your Journey to Financial Health

### Phase 1: Awareness (Week 1-2)
- **Goal**: Understand where money goes
- **Action**: Track all transactions
- **Metric**: 100% transaction coverage

### Phase 2: Analysis (Week 3-4)
- **Goal**: Identify spending patterns
- **Action**: Review weekly dashboards
- **Metric**: Know your top 5 expense categories

### Phase 3: Optimization (Month 2-3)
- **Goal**: Align with 50/30/20 rule
- **Action**: Cut unnecessary spending
- **Metric**: Health score 70+

### Phase 4: Mastery (Month 4+)
- **Goal**: Consistent budget adherence
- **Action**: Automated tracking, monthly reviews
- **Metric**: Health score 80+, 20%+ savings rate

---

## 🏆 Built With

- **Frontend**: Streamlit
- **Data**: Pandas, NumPy
- **Visualization**: Plotly
- **ML**: PyOD, Prophet, scikit-learn
- **Database**: PostgreSQL (optional)
- **Automation**: Apache Airflow (optional)

---

**Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: 2025-11-27
**Built with ❤️ for smart personal finance management**

---

## Quick Command Reference

```bash
# Launch dashboard
streamlit run dashboards/streamlit_dashboard.py

# Regenerate demo data
python src/data_generation/generate_data.py

# Train fraud detection
python src/fraud_detection/fraud_detector.py

# Train forecasting
python src/forecasting/forecaster.py

# Run tests
python test_dashboard_fixes.py

# Clear Streamlit cache
streamlit cache clear
```

**Ready to take control of your finances? Launch the dashboard and start exploring!** 🚀
