# 💰 Smart Finance ML - Personal Finance Dashboard

A modern, AI-powered personal finance management dashboard with multi-user support, fraud detection, budget recommendations, and financial forecasting.

![Dashboard Preview](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

## ✨ Key Features

### 🎨 Modern UI/UX
- **Premium glassmorphism design** with purple/magenta gradient theme
- **Fully responsive** dashboard with dark mode
- **Smooth animations** and transitions
- **Interactive charts** powered by Plotly

### 👥 Multi-User System
- **Secure authentication** with bcrypt password hashing
- **Individual user profiles** with personalized settings
- **User-specific data isolation** - each user sees only their own transactions
- **Preferred currency** selection (USD, IDR, CNY)

### 🤖 AI-Powered Features
- **Fraud Detection** - ML model to detect suspicious transactions
- **Budget Recommendations** - AI-generated personalized budget advice
- **Spending Forecasting** - Prophet-based 30-day spending predictions
- **Category Analysis** - Smart insights into spending patterns

### 💱 Currency Management
- **Multi-currency support** (USD, IDR, CNY)
- **Real-time exchange rates** with API integration
- **Fallback rates** for offline operation
- **Currency converter** with visual exchange rate matrix

### 📊 Financial Analytics
- **Transaction tracking** with categories and merchants
- **Visual spending analysis** with interactive charts
- **Monthly income tracking**
- **Budget health scoring**
- **Custom date range filtering**

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd smart-finance-ml
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the dashboard**
```bash
# Windows
run_dashboard.bat

# Linux/Mac
chmod +x run_dashboard.sh
./run_dashboard.sh
```

4. **Access the dashboard**
Open your browser and go to:
```
http://localhost:8502
```

### First Time Setup

1. **Register a new account**
   - Click "Create new account"
   - Fill in your details
   - Set your preferred currency

2. **Add your first transaction**
   - Go to "Add Transaction" tab
   - Enter transaction details
   - Submit to save

3. **Explore features**
   - View analytics in "Overview" tab
   - Get AI recommendations in "Budget Recommendations"
   - Check fraud detection insights
   - Use currency converter
   - Export reports

## 📁 Project Structure

```
smart-finance-ml/
├── dashboards/
│   ├── streamlit_dashboard_multiuser.py  # Main dashboard application
│   └── auth.py                           # Authentication module
├── src/
│   ├── budgeting/
│   │   └── budget_recommender.py        # AI budget recommendations
│   ├── currency/
│   │   └── currency_converter.py        # Currency conversion logic
│   ├── database/
│   │   └── db_manager.py                # Database operations
│   ├── data_generation/
│   │   └── generate_data.py             # Sample data generator
│   ├── forecasting/
│   │   └── forecaster.py                # Prophet-based forecasting
│   └── fraud_detection/
│       └── fraud_detector.py            # ML fraud detection
├── config/
│   └── config.py                        # Configuration settings
├── data/
│   ├── raw/                             # Raw transaction data
│   ├── processed/                       # Processed datasets
│   └── users/                           # User credentials
├── models/                              # Trained ML models
├── docs/                                # Documentation
│   ├── FRAUD_DETECTION_GUIDE.md
│   ├── MULTIUSER_GUIDE.md
│   ├── QUICK_START.md
│   ├── TROUBLESHOOTING.md
│   └── USER_DATA_COLLECTION_GUIDE.md
├── run_dashboard.bat                    # Windows launcher
├── run_dashboard.sh                     # Linux/Mac launcher
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## 🛠️ Technology Stack

### Frontend
- **Streamlit** - Web framework
- **Plotly** - Interactive charts
- **Custom CSS** - Premium UI styling

### Backend
- **Pandas** - Data manipulation
- **NumPy** - Numerical computations
- **Prophet** - Time series forecasting
- **Scikit-learn** - ML algorithms

### Data & Storage
- **CSV files** - Data storage
- **JSON** - Configuration
- **Bcrypt** - Password hashing

### APIs & Services
- **ExchangeRate API** - Real-time currency rates
- **Fallback system** - Offline operation support

## 📊 Dashboard Features

### 1. Overview Tab
- Total spending metrics
- Transaction count
- Average transaction value
- Monthly income display
- Spending by category (interactive bar chart)
- Top merchants analysis
- Daily spending trend line chart
- Recent transactions table

### 2. Add Transaction Tab
- Category selection
- Merchant/store input
- Amount with currency
- Description
- Auto-fill transaction date
- Fraud detection on submission

### 3. Manage Transactions Tab
- View all transactions
- Multi-select with checkboxes
- Bulk delete functionality
- Search and filter
- Sort by date, category, amount

### 4. Budget Recommendations Tab
- AI-generated budget advice
- Budget health score (0-100)
- Category-wise spending analysis
- Personalized recommendations
- Visual spending breakdown

### 5. Currency Converter Tab
- Amount conversion
- Exchange rate matrix
- Real-time rate updates
- Support for USD, IDR, CNY
- Last update timestamp

### 6. Reports Tab
- Summary statistics
- Total spending
- Average transaction
- Most frequent category
- Highest transaction
- Date range analysis
- Exportable data

## 🎨 UI Theme

The dashboard features a modern **Purple/Magenta gradient theme**:

- **Primary**: Deep Purple (#7c3aed)
- **Secondary**: Royal Purple (#8b5cf6)
- **Accent**: Bright Magenta (#d946ef)
- **Highlight**: Pink (#ec4899)

The design uses:
- Glassmorphism effects
- Backdrop blur
- Smooth gradients
- Neon glow on hover
- Dark background for contrast

## 🔐 Security Features

- **Bcrypt password hashing** - Secure password storage
- **User session management** - Secure authentication flow
- **Data isolation** - Users can only access their own data
- **Input validation** - Prevents SQL injection and XSS
- **Fraud detection** - Real-time transaction monitoring

## 📈 ML Models

### Fraud Detection
- **Algorithm**: Random Forest Classifier
- **Features**: Amount, category, merchant, time patterns
- **Accuracy**: ~95% on test data
- **Real-time**: Predictions on transaction submission

### Budget Recommender
- **Method**: Rule-based AI + Statistical analysis
- **Inputs**: Historical spending, income, patterns
- **Outputs**: Personalized budget suggestions
- **Health Score**: 0-100 based on multiple factors

### Spending Forecaster
- **Library**: Facebook Prophet
- **Forecast**: 30-day ahead predictions
- **Confidence**: Upper/lower bounds
- **Visualizations**: Interactive forecast charts

## 🌐 Multi-Currency Support

Supported currencies:
- **USD** - United States Dollar
- **IDR** - Indonesian Rupiah
- **CNY** - Chinese Yuan

Features:
- Auto-conversion to preferred currency
- Real-time exchange rates
- Historical rate caching
- Offline fallback rates
- Visual exchange rate matrix

## 📝 Documentation

Detailed guides available in root directory:

- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[MULTIUSER_GUIDE.md](MULTIUSER_GUIDE.md)** - Multi-user system documentation
- **[FRAUD_DETECTION_GUIDE.md](FRAUD_DETECTION_GUIDE.md)** - Fraud detection details
- **[USER_DATA_COLLECTION_GUIDE.md](USER_DATA_COLLECTION_GUIDE.md)** - Data privacy guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Can't login
- Verify username/email is correct
- Password is case-sensitive
- Try creating a new account
- Check `data/users/users.csv` exists

### Currency converter not updating
- Check internet connection
- API might be down - fallback rates will be used
- Check console for error messages

### Transactions not showing
- Verify you're logged in
- Check date range filter
- Ensure transactions were saved
- Look in `data/raw/transactions.csv`

## 📄 License

This project is for educational and personal use.

## 🎯 Future Enhancements

- [ ] Database migration (SQLite/PostgreSQL)
- [ ] More currency support
- [ ] Mobile app version
- [ ] Advanced analytics dashboard
- [ ] Export to PDF/Excel
- [ ] Email notifications
- [ ] Recurring transactions
- [ ] Bill reminders
- [ ] Goal tracking
- [ ] Investment portfolio tracking

## 💬 Support

For issues or questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review documentation files
- Open an issue on GitHub

## 🙏 Acknowledgments

- **Streamlit** - Amazing web framework
- **Plotly** - Beautiful charts
- **Facebook Prophet** - Powerful forecasting
- **ExchangeRate API** - Currency data

---

**Made with ❤️ using Python, Streamlit, and AI**

Last Updated: December 2025
