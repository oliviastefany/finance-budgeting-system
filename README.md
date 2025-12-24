# Smart Finance Budgeting System 💜📊

A modern **multi-user personal finance dashboard** with **budget insights**, **multi-currency support**, and **ML-based spending forecasting**.  
Built with **Streamlit + SQLite + Prophet + Plotly** for an interactive and deployment-ready analytics experience.

🚀 **Live Demo:** https://smartfinancedashboard.streamlit.app/

---

## ✨ What This Project Does

Smart Finance helps users track spending, understand financial habits, and plan better through:
- **Transaction tracking** with categories, merchants, and descriptions  
- **Budget insights + health score** (0–100)  
- **ML-based spending forecasting** (Prophet) with 30-day predictions + confidence intervals  
- **Multi-user authentication** with bcrypt password hashing and user-level data isolation  
- **Multi-currency support** (USD / IDR / CNY) using real-time exchange rates + offline fallback  

---

## 📌 Key Highlights
✅ End-to-end data product (not only notebooks)  
✅ Multi-user system with secure authentication  
✅ Forecasting pipeline using Prophet  
✅ Interactive analytics dashboard with Plotly charts  
✅ Real-time API integration + caching/fallback logic  
✅ Clean modular architecture

## 🔥 Features

### 🎨 Modern UI/UX
- Premium glassmorphism styling with purple/magenta theme
- Fully responsive dashboard with dark mode
- Smooth transitions and clean layout
- Interactive Plotly charts

### 👥 Multi-User System
- Secure login/register with **bcrypt password hashing**
- Individual user profiles + preferred currency settings
- **User data isolation** (each user only sees their own transactions)
- Session-based authentication flow

### 🤖 ML-Assisted Features
#### 1) Spending Forecasting (Prophet)
- Forecast horizon: **30 days**
- Confidence bounds (upper/lower)
- Interactive Plotly forecast chart

#### 2) Budget Insights + Recommendations
- Category-wise spending analysis
- Top merchants insights
- Spending-to-income ratio indicators
- **Budget health score** (0–100) for behavioral finance tracking

### 💱 Currency Management
- Multi-currency support: **USD / IDR / CNY**
- Real-time exchange rates using API integration
- Exchange rate caching
- Offline fallback rates for reliability
- Currency converter + visual exchange rate matrix

### 📊 Financial Analytics & Reporting
- Transaction tracking with categories and merchants
- Monthly income tracking
- Custom date range filtering
- Search, sort, and bulk delete
- Reports with export-ready tables

---

## 🧠 ML / Analytics Details

### Spending Forecasting (Prophet)
The forecasting module uses time-series modeling to estimate future spending trends:
- Uses historical daily spending values
- Produces **30-day forecast** with confidence intervals
- Visualized interactively in the dashboard

### Budget Health Score
A score from **0–100** calculated using spending-to-income patterns and category thresholds to help users quickly understand budget condition.

---

## 🏗️ System Architecture (High Level)

- **Frontend/UI:** Streamlit + Plotly + Custom CSS
- **Backend/Logic:** Modular Python services (budgeting, forecasting, currency, database)
- **Database:** **SQLite** (lightweight and ideal for local/deployment demo)
- **External Services:** Exchange rate API + fallback for offline operation

---

## 🛠️ Tech Stack

**Frontend**
- Streamlit (web dashboard)
- Plotly (interactive visualization)
- Custom CSS (glassmorphism UI)

**Backend**
- Python
- pandas, NumPy
- Prophet (forecasting)

**Storage**
- SQLite (transactions + users)
- CSV / JSON (config + sample data)

**Security**
- bcrypt password hashing
- session management
- user-level data isolation

---

## 📁 Project Structure

```
smart-finance-ml/
├── dashboards/
│ ├── streamlit_dashboard_multiuser.py # Main dashboard app
│ └── auth.py # Authentication module
├── src/
│ ├── budgeting/
│ │ └── budget_recommender.py # Budget insights + scoring
│ ├── currency/
│ │ └── currency_converter.py # Currency conversion logic
│ ├── database/
│ │ └── db_manager.py # SQLite operations
│ ├── data_generation/
│ │ └── generate_data.py # Sample data generator
│ └── forecasting/
│ └── forecaster.py # Prophet-based forecasting
├── config/
│ └── config.py # Configuration settings
├── data/
│ ├── raw/
│ ├── processed/
│ └── users/
├── models/ # Saved ML models (optional)
├── docs/ # Documentation
├── requirements.txt # Python dependencies
└── README.md # This file
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

🧩 Troubleshooting
App is slow
- Reduce dataset size
- Cache exchange rate calls
- Use st.cache_data for processed dataframes

✅ Future Improvements

- Add forecasting evaluation dashboard (MAE/MAPE/RMSE)
- Add automated testing + CI/CD pipeline
- Add model monitoring / drift detection for long-term stability
- Add database migration path SQLite → PostgreSQL
- Add export to CSV/Excel + automated monthly report PDF

👩‍💻 Author
Olivia Stefany Can
LinkedIn: https://linkedin.com/in/oliviastefanycan
GitHub: https://github.com/oliviastefany

## 📄 License
This project is for educational and personal use.


**Made with ❤️ using Python, Streamlit, and AI**

Last Updated: December 2025
