"""
Smart Finance Dashboard - Multi-User Version
Users can register, login, and track their own finances
"""
import streamlit as st
import pandas as pd
import numpy as np



import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_PATHS
from src.currency.currency_converter import CurrencyConverter
from src.budgeting.budget_recommender import BudgetRecommender
from src.fraud_detection.fraud_detector import FraudDetector
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

# Import authentication
from auth import check_authentication, logout, get_current_user_id, get_current_user_email, AuthManager

# Page configuration
st.set_page_config(
    page_title="Smart Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Ultra Modern Premium Design
st.markdown("""
<style>
    /* Import premium fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main background - Rich gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 30%, #312e81 60%, #581c87 100%);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Main header - Premium gradient text */
    .main-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 50%, #d946ef 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 20px;
        letter-spacing: -0.02em;
        line-height: 1.2;
        text-shadow: 0 0 30px rgba(124, 58, 237, 0.5);
    }

    /* Metric cards - Premium glassmorphism */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                    0 0 0 1px rgba(124, 58, 237, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(124, 58, 237, 0.4);
        transition: all 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(124, 58, 237, 0.4), 0 0 20px rgba(34, 211, 238, 0.3);
        border-color: rgba(34, 211, 238, 0.6);
    }

    div[data-testid="metric-container"] label {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-family: 'Space Grotesk', sans-serif;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #7c3aed 0%, #d946ef 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        filter: drop-shadow(0 0 10px rgba(124, 58, 237, 0.5));
    }

    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Tabs - Ultra modern */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 10px;
        border: 2px solid rgba(71, 85, 105, 0.5);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 14px;
        padding: 14px 28px;
        background-color: transparent;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
        color: #94a3b8;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.02em;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(71, 85, 105, 0.4);
        color: #e2e8f0;
        transform: translateY(-2px);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%) !important;
        color: #0f172a !important;
        font-weight: 700;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
    }

    /* Alert boxes - Premium glassmorphism */
    .warning-box {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        backdrop-filter: blur(10px);
        color: #ec4899;
        padding: 20px 24px;
        border-radius: 16px;
        border: 2px solid rgba(124, 58, 237, 0.4);
        margin: 16px 0;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.2);
    }

    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
        backdrop-filter: blur(10px);
        color: #6ee7b7;
        padding: 20px 24px;
        border-radius: 16px;
        border: 2px solid rgba(16, 185, 129, 0.4);
        margin: 16px 0;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
    }

    .alert-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
        backdrop-filter: blur(10px);
        color: #fca5a5;
        padding: 20px 24px;
        border-radius: 16px;
        border: 2px solid rgba(239, 68, 68, 0.4);
        margin: 16px 0;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2);
    }

    /* Buttons - Premium design */
    .stButton > button {
        border-radius: 14px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        padding: 16px 36px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
        color: #0f172a;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
        letter-spacing: 0.02em;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 32px rgba(124, 58, 237, 0.6);
        background: linear-gradient(135deg, #ec4899 0%, #7c3aed 100%);
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
    }

    /* Sidebar - Premium dark */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #1e1b4b 100%);
        border-right: 2px solid rgba(71, 85, 105, 0.5);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
    }

    section[data-testid="stSidebar"] > div {
        background: transparent;
    }

    section[data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
        font-size: 0.95rem;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #7c3aed !important;
        font-weight: 700;
        font-size: 1.1rem !important;
    }

    /* Input fields - Premium glassmorphism */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 2px solid rgba(71, 85, 105, 0.5);
        padding: 14px 18px;
        transition: all 0.3s ease;
        color: #e2e8f0;
        font-size: 1rem;
        font-weight: 500;
    }

    /* Selectbox - SEPARATE STYLING */
    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.6) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 2px solid rgba(71, 85, 105, 0.5);
    }

    /* Make sure selectbox text is BRIGHT WHITE */
    .stSelectbox {
        color: #ffffff !important;
    }

    .stSelectbox label {
        color: #cbd5e1 !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus-within,
    .stTextArea > div > div > textarea:focus {
        border-color: #7c3aed;
        box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2),
                    0 4px 16px rgba(124, 58, 237, 0.3);
        background: rgba(51, 65, 85, 0.8);
        transform: translateY(-2px);
    }

    /* Dropdown options - FORCE VISIBILITY! */
    /* Selected value in dropdown box - THE FIX! */
    .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    .stSelectbox div[data-baseweb="select"] div {
        color: #ffffff !important;
    }

    .stSelectbox div[data-baseweb="select"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Target the value container specifically */
    .stSelectbox [data-baseweb="select"] [class*="ValueContainer"] {
        color: #ffffff !important;
    }

    .stSelectbox [data-baseweb="select"] [class*="ValueContainer"] > div {
        color: #ffffff !important;
    }

    .stSelectbox [data-baseweb="select"] [class*="singleValue"] {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    /* Make sure the input inside selectbox is visible */
    .stSelectbox input {
        color: #ffffff !important;
    }

    /* ULTIMATE FIX - Force all text in selectbox to be visible */
    .stSelectbox *,
    .stSelectbox *::before,
    .stSelectbox *::after {
        color: #ffffff !important;
    }

    .stSelectbox div,
    .stSelectbox span,
    .stSelectbox p,
    .stSelectbox > div,
    .stSelectbox > div > div,
    .stSelectbox > div > div > div {
        color: #ffffff !important;
    }

    /* Nuclear option - force everything in baseweb select */
    [data-baseweb="select"],
    [data-baseweb="select"] *,
    [data-baseweb="select"] div,
    [data-baseweb="select"] span {
        color: #ffffff !important;
    }

    [data-baseweb="select"] div[id*="react-select"],
    [data-baseweb="select"] div[id*="react-select"] * {
        color: #ffffff !important;
    }

    /* Force the single value (selected item display) - CRITICAL! */
    [class*="singleValue"],
    div[class*="singleValue"],
    span[class*="singleValue"] {
        color: #ffffff !important;
        text-shadow: 0 0 8px rgba(0, 0, 0, 1), 0 0 15px rgba(124, 58, 237, 0.8) !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Control container */
    [class*="control"],
    div[class*="control"] {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
    }

    /* Value container - where the selected text sits */
    [class*="ValueContainer"],
    [class*="valueContainer"],
    div[class*="ValueContainer"],
    div[class*="valueContainer"] {
        color: #ffffff !important;
    }

    [class*="ValueContainer"] *,
    [class*="valueContainer"] * {
        color: #ffffff !important;
    }

    /* Placeholder */
    [class*="placeholder"],
    div[class*="placeholder"] {
        color: rgba(255, 255, 255, 0.6) !important;
    }

    /* Input in selectbox */
    [class*="Input"],
    [class*="input"] {
        color: #ffffff !important;
    }

    /* Dropdown menu list */
    [data-baseweb="popover"] {
        background-color: rgba(15, 23, 42, 0.98) !important;
        border: 2px solid rgba(124, 58, 237, 0.6) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7), 0 0 20px rgba(124, 58, 237, 0.4) !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Dropdown options items */
    [role="option"] {
        background-color: rgba(30, 41, 59, 0.95) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        padding: 14px 20px !important;
        min-height: 50px !important;
    }

    [role="option"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    [role="option"]:hover {
        background-color: rgba(124, 58, 237, 0.4) !important;
        color: #ec4899 !important;
    }

    [role="option"]:hover span {
        color: #ec4899 !important;
        font-weight: 700 !important;
    }

    [role="option"][aria-selected="true"] {
        background-color: rgba(124, 58, 237, 0.5) !important;
        color: #ec4899 !important;
        font-weight: 700 !important;
    }

    [role="option"][aria-selected="true"] span {
        color: #ec4899 !important;
        font-weight: 700 !important;
    }

    /* Dropdown list container */
    [role="listbox"] {
        background-color: rgba(15, 23, 42, 0.98) !important;
        padding: 8px !important;
    }

    [role="listbox"] ul {
        background-color: transparent !important;
    }

    [role="listbox"] li {
        color: #ffffff !important;
    }

    /* Forms - Premium card */
    .stForm {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(51, 65, 85, 0.6) 100%);
        backdrop-filter: blur(20px);
        padding: 36px;
        border-radius: 24px;
        border: 2px solid rgba(71, 85, 105, 0.5);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    /* Dataframes - Light Purple/Pastel Theme */
    .dataframe {
        border-radius: 14px;
        overflow: hidden;
        border: 2px solid rgba(192, 132, 252, 0.3) !important;
        background: rgba(233, 213, 255, 0.08) !important;
        backdrop-filter: blur(10px);
        font-size: 0.9rem;
    }

    /* Table container background override */
    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrame"] > div,
    div[data-testid="stDataFrame"] > div > div {
        background: rgba(233, 213, 255, 0.08) !important;
    }

    /* Table itself */
    div[data-testid="stDataFrame"] table {
        background: rgba(233, 213, 255, 0.1) !important;
    }

    /* Table header styling - Pastel Purple */
    div[data-testid="stDataFrame"] table thead tr th {
        background: linear-gradient(135deg, rgba(192, 132, 252, 0.25) 0%, rgba(167, 139, 250, 0.25) 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-bottom: 2px solid rgba(192, 132, 252, 0.4) !important;
    }

    /* Table body styling - Light rows */
    div[data-testid="stDataFrame"] table tbody tr {
        background: rgba(249, 245, 255, 0.05) !important;
        transition: all 0.2s ease !important;
    }

    /* Alternate row colors for better readability */
    div[data-testid="stDataFrame"] table tbody tr:nth-child(even) {
        background: rgba(233, 213, 255, 0.08) !important;
    }

    div[data-testid="stDataFrame"] table tbody tr:hover {
        background: rgba(192, 132, 252, 0.2) !important;
    }

    div[data-testid="stDataFrame"] table tbody tr td {
        color: #f1f5f9 !important;
        border-bottom: 1px solid rgba(192, 132, 252, 0.15) !important;
        padding: 12px 16px !important;
    }

    /* Text colors and sizing */
    .stApp p {
        color: #cbd5e1;
        font-size: 1rem;
        line-height: 1.6;
    }

    .stApp span {
        color: #e2e8f0;
    }

    .stApp div {
        color: #e2e8f0;
    }

    /* Headings - Premium typography */
    .stApp h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: #7c3aed;
        letter-spacing: -0.02em;
    }

    .stApp h2 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #7c3aed;
        letter-spacing: -0.01em;
    }

    .stApp h3 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #7c3aed;
        margin-top: 2rem;
        margin-bottom: 1rem;
        letter-spacing: -0.01em;
    }

    /* Charts - Premium glassmorphism */
    .stPlotlyChart {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(51, 65, 85, 0.6) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                    0 0 0 1px rgba(124, 58, 237, 0.1);
        border: 2px solid rgba(71, 85, 105, 0.5);
    }

    /* Info boxes */
    .stAlert {
        border-radius: 16px;
        border: 2px solid rgba(71, 85, 105, 0.5);
        padding: 20px;
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.6) 0%, rgba(71, 85, 105, 0.6) 100%);
        backdrop-filter: blur(10px);
        color: #cbd5e1;
        font-size: 1rem;
    }

    /* Transaction rows */
    hr {
        margin: 16px 0;
        border-color: rgba(71, 85, 105, 0.3);
        opacity: 0.6;
    }

    /* Smooth scrolling and selection */
    html {
        scroll-behavior: smooth;
    }

    ::selection {
        background: rgba(124, 58, 237, 0.3);
        color: #ec4899;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication first
if not check_authentication():
    st.stop()

# Initialize session state
if 'currency_converter' not in st.session_state:
    st.session_state.currency_converter = CurrencyConverter()
    st.session_state.currency_converter.fetch_rates()

if 'budget_recommender' not in st.session_state:
    st.session_state.budget_recommender = BudgetRecommender()

@st.cache_data
def load_data():
    """Load all required data"""
    users_df = pd.read_csv(RAW_DATA_DIR / 'users.csv')
    transactions_df = pd.read_csv(RAW_DATA_DIR / 'transactions.csv')
    transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])

    # Always use raw transactions for multi-user dashboard
    # This ensures new transactions added via the interface appear immediately
    return users_df, transactions_df

def add_transaction(user_id, category, merchant, amount, currency, description=""):
    """Add a new transaction for the current user"""
    transactions_df = pd.read_csv(RAW_DATA_DIR / 'transactions.csv')

    # Generate new transaction ID
    last_id = transactions_df['transaction_id'].iloc[-1]
    number = int(last_id[1:]) + 1
    new_id = f'T{number:05d}'

    # Get current timestamp
    now = datetime.now()

    # Convert to USD for amount_usd column
    converter = st.session_state.currency_converter
    amount_usd = converter.convert(amount, currency, 'USD')

    # Create new transaction with all required columns
    new_transaction = {
        'transaction_id': new_id,
        'user_id': user_id,
        'amount': amount,
        'amount_usd': amount_usd,
        'currency': currency,
        'category': category,
        'merchant': merchant,
        'merchant_location': 'Unknown',  # Default value
        'payment_method': 'card',  # Default value
        'transaction_date': now.strftime('%Y-%m-%d %H:%M:%S'),
        'is_fraud': 0,  # Not fraud
        'fraud_type': 'none',  # No fraud
        'description': description,
        'day_of_week': now.strftime('%A'),
        'hour': now.hour,
        'month': now.month
    }

    # Append
    transactions_df = pd.concat([transactions_df, pd.DataFrame([new_transaction])], ignore_index=True)

    # Save
    transactions_df.to_csv(RAW_DATA_DIR / 'transactions.csv', index=False)

    # Clear cache to reload data
    st.cache_data.clear()

    return True

def delete_transaction(transaction_id, user_id):
    """Delete a transaction (only if it belongs to the user)"""
    transactions_df = pd.read_csv(RAW_DATA_DIR / 'transactions.csv')

    # Check if transaction belongs to user
    transaction = transactions_df[transactions_df['transaction_id'] == transaction_id]
    if len(transaction) == 0:
        return False, "Transaction not found"

    if transaction.iloc[0]['user_id'] != user_id:
        return False, "You can only delete your own transactions"

    # Delete the transaction
    transactions_df = transactions_df[transactions_df['transaction_id'] != transaction_id]

    # Save
    transactions_df.to_csv(RAW_DATA_DIR / 'transactions.csv', index=False)

    # Clear cache
    st.cache_data.clear()

    return True, "Transaction deleted successfully"

@st.cache_data(ttl=3600)
def forecast_user_spending(user_id, transactions_df, days_ahead=30):
    """Forecast user's spending for the next N days using Prophet"""
    try:
        # Filter user transactions
        user_data = transactions_df[transactions_df['user_id'] == user_id].copy()

        if len(user_data) < 7:  # Need at least 7 days of data
            return None, "Need at least 7 transactions for forecasting"

        # Prepare data for Prophet (needs 'ds' and 'y' columns)
        daily_spending = user_data.groupby(user_data['transaction_date'].dt.date)['amount_usd'].sum().reset_index()
        daily_spending.columns = ['ds', 'y']
        daily_spending['ds'] = pd.to_datetime(daily_spending['ds'])

        # Create and fit Prophet model
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=False,
            changepoint_prior_scale=0.05
        )
        model.fit(daily_spending)

        # Make future dataframe
        future = model.make_future_dataframe(periods=days_ahead)
        forecast = model.predict(future)

        # Get only future predictions
        future_forecast = forecast[forecast['ds'] > daily_spending['ds'].max()].copy()

        return future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], None

    except Exception as e:
        return None, str(e)

def main():
    # Get current user
    user_id = get_current_user_id()
    user_email = get_current_user_email()

    # Get user info early
    auth = AuthManager()
    user_info = auth.get_user_info(user_id)

    if not user_info:
        st.error("User not found")
        return

    # Header with logout
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown('<h1 class="main-header">💰 Smart Finance</h1>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <p style='
            text-align: center;
            padding-top: 20px;
            font-family: "Space Grotesk", sans-serif;
            font-size: 1.25rem;
            font-weight: 600;
            color: #e0e7ff;
            letter-spacing: 0.01em;
        '>
            Welcome, <span style='color: #7c3aed; font-weight: 700;'>{user_info['name']}</span>
        </p>
        """, unsafe_allow_html=True)
    with col3:
        if st.button("Logout", type="primary"):
            logout()

    # Load data
    try:
        users_df, transactions_df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Sidebar
    st.sidebar.title("⚙️ Settings")

    # Display user info card - Premium design
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        border: 2px solid rgba(124, 58, 237, 0.3);
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    ">
        <div style="text-align: center; margin-bottom: 16px;">
            <div style="
                width: 64px;
                height: 64px;
                background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                font-weight: bold;
                color: #0f172a;
                margin-bottom: 12px;
            ">
                {user_info['name'][0].upper()}
            </div>
        </div>
        <div style="text-align: center;">
            <div style="
                font-size: 1.25rem;
                font-weight: 700;
                color: #7c3aed;
                margin-bottom: 8px;
                font-family: 'Space Grotesk', sans-serif;
            ">
                {user_info['name']}
            </div>
            <div style="
                font-size: 0.85rem;
                color: #94a3b8;
                margin-bottom: 16px;
            ">
                {user_info['email']}
            </div>
            <div style="
                background: rgba(30, 41, 59, 0.5);
                border-radius: 10px;
                padding: 12px;
                border: 1px solid rgba(71, 85, 105, 0.5);
            ">
                <div style="
                    font-size: 0.7rem;
                    color: #94a3b8;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    margin-bottom: 4px;
                ">
                    Monthly Income
                </div>
                <div style="
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #6ee7b7;
                    font-family: 'Space Grotesk', sans-serif;
                ">
                    {user_info['preferred_currency']} {user_info['monthly_income']:,.0f}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Currency selection
    currency = st.sidebar.selectbox(
        "Display Currency",
        ['USD', 'IDR', 'CNY'],
        index=['USD', 'IDR', 'CNY'].index(user_info['preferred_currency'])
    )

    # Date range filter
    st.sidebar.subheader("📅 Date Range")
    date_filter = st.sidebar.radio(
        "Select Period",
        ['Last 7 Days', 'Last 30 Days', 'Last 3 Months', 'Last 6 Months', 'All Time', 'Custom']
    )

    if date_filter == 'Last 7 Days':
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
    elif date_filter == 'Last 30 Days':
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif date_filter == 'Last 3 Months':
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
    elif date_filter == 'Last 6 Months':
        start_date = datetime.now() - timedelta(days=180)
        end_date = datetime.now()
    elif date_filter == 'Custom':
        col1, col2 = st.sidebar.columns(2)
        start_date = col1.date_input("From", datetime.now() - timedelta(days=90))
        end_date = col2.date_input("To", datetime.now())
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    else:  # All Time
        start_date = transactions_df['transaction_date'].min()
        end_date = transactions_df['transaction_date'].max()

    # Filter user transactions
    user_transactions = transactions_df[
        (transactions_df['user_id'] == user_id) &
        (transactions_df['transaction_date'] >= start_date) &
        (transactions_df['transaction_date'] <= end_date)
    ].copy()


    # Convert amounts to selected currency
    converter = st.session_state.currency_converter
    if len(user_transactions) > 0:
        try:
            user_transactions = converter.convert_dataframe(
                user_transactions,
                amount_column='amount',
                currency_column='currency',
                target_currency=currency
            )
        except Exception as e:
            st.sidebar.error(f"Currency conversion error: {str(e)}")
            # Fallback: just add the column with original amounts
            user_transactions[f'amount_{currency}'] = user_transactions['amount']

        # Ensure the currency column exists (in case conversion didn't create it)
        # This handles cases where convert_dataframe fails or returns without creating the column
        if f'amount_{currency}' not in user_transactions.columns:
            user_transactions[f'amount_{currency}'] = user_transactions['amount']

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "➕ Add Transaction",
        "🗑️ Manage Transactions",
        "💡 Budget Recommendations",
        "💱 Currency Converter",
        "📄 Reports"
    ])

    # TAB 1: Overview
    with tab1:
        st.subheader(f"📊 Financial Overview - {user_info['name']}")

        if len(user_transactions) == 0:
            st.info("No transactions found for this period. Add your first transaction in the 'Add Transaction' tab!")
        else:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)

            total_spent = user_transactions[f'amount_{currency}'].sum()
            num_transactions = len(user_transactions)
            avg_transaction = user_transactions[f'amount_{currency}'].mean()

            with col1:
                st.metric("Total Spending", f"{currency} {total_spent:,.2f}")
            with col2:
                st.metric("Transactions", f"{num_transactions:,}")
            with col3:
                st.metric("Avg. Transaction", f"{currency} {avg_transaction:,.2f}")
            with col4:
                monthly_income_converted = converter.convert(
                    user_info['monthly_income'], user_info['preferred_currency'], currency
                )
                st.metric("Monthly Income", f"{currency} {monthly_income_converted:,.2f}")

            # Spending by category
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("💸 Spending by Category")
                category_spending = user_transactions.groupby('category')[f'amount_{currency}'].sum().sort_values(ascending=False)

                # Muted & sophisticated color palette
                category_colors = {
                    'Groceries': '#9ca3af',      # Slate gray - neutral, essential
                    'Utilities': '#7dd3fc',      # Light sky blue - reliable
                    'Rent': '#a78bfa',           # Soft purple - stability
                    'Healthcare': '#5eead4',     # Teal - medical, wellness
                    'Insurance': '#93c5fd',      # Soft blue - protection
                    'Transportation': '#fbbf24', # Warm yellow - movement
                    'Dining': '#fb923c',         # Warm orange - dining
                    'Entertainment': '#f472b6',  # Rose pink - fun, leisure
                    'Shopping': '#fda4af',       # Light coral - retail
                    'Travel': '#60a5fa',         # Medium blue - adventure
                    'Hobbies': '#c084fc',        # Lavender - creativity
                    'Savings': '#94a3b8',        # Slate blue - conservative growth
                    'Investment': '#818cf8',     # Indigo - wealth, prosperity
                    'Emergency Fund': '#f87171'  # Soft red - urgent
                }

                # Map colors to categories
                bar_colors = [category_colors.get(cat, '#6b7280') for cat in category_spending.index]

                fig = go.Figure(data=[
                    go.Bar(x=category_spending.index, y=category_spending.values,
                           marker=dict(color=bar_colors))
                ])
                fig.update_layout(
                    title=f'Spending by Category ({currency})',
                    xaxis_title='Category',
                    yaxis_title=f'Amount ({currency})',
                    height=500,
                    dragmode=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            with col2:
                st.subheader("📊 Category Distribution")
                # Use same category colors for consistency
                pie_colors = [category_colors.get(cat, '#6b7280') for cat in category_spending.index]

                fig = px.pie(
                    values=category_spending.values,
                    names=category_spending.index,
                    title='Spending Distribution',
                    color_discrete_sequence=pie_colors
                )
                fig.update_layout(
                    height=500,
                    dragmode=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=80, b=20)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # Spending over time
            st.subheader("📅 Spending Trend")
            daily_spending = user_transactions.groupby(
                user_transactions['transaction_date'].dt.date
            )[f'amount_{currency}'].sum().reset_index()
            daily_spending.columns = ['Date', 'Amount']

            # Soft coral line for spending trend
            fig = px.line(
                daily_spending,
                x='Date',
                y='Amount',
                title=f'Daily Spending Trend ({currency})'
            )
            fig.update_traces(line=dict(color='#fb7185', width=3), fill='tozeroy', fillcolor='rgba(251, 113, 133, 0.15)')
            fig.update_layout(
                height=500,
                dragmode=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=50, r=50, t=80, b=50)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            # Recent transactions
            st.subheader("📝 Recent Transactions")
            recent_transactions = user_transactions.nlargest(10, 'transaction_date')[
                ['transaction_date', 'category', 'merchant', f'amount_{currency}', 'description']
            ].copy()
            recent_transactions['transaction_date'] = recent_transactions['transaction_date'].dt.strftime('%Y-%m-%d %H:%M')

            # Style the dataframe with purple theme
            st.dataframe(
                recent_transactions,
                use_container_width=True,
                column_config={
                    "transaction_date": st.column_config.TextColumn("Date", width="medium"),
                    "category": st.column_config.TextColumn("Category", width="medium"),
                    "merchant": st.column_config.TextColumn("Merchant", width="medium"),
                    f"amount_{currency}": st.column_config.NumberColumn(f"Amount ({currency})", format="%.2f"),
                    "description": st.column_config.TextColumn("Description", width="large")
                }
            )

    # TAB 2: Add Transaction
    with tab2:
        st.subheader("➕ Add New Transaction")

        with st.form("add_transaction_form"):
            col1, col2 = st.columns(2)

            with col1:
                category = st.selectbox("Category", [
                    'Groceries', 'Utilities', 'Rent', 'Healthcare', 'Insurance', 'Transportation',
                    'Dining', 'Entertainment', 'Shopping', 'Travel', 'Hobbies',
                    'Savings', 'Investment', 'Emergency Fund'
                ])
                merchant = st.text_input("Merchant/Store")

            with col2:
                amount = st.number_input("Amount", min_value=0.0, step=0.01)
                trans_currency = st.selectbox("Currency", ['USD', 'IDR', 'CNY'], index=['USD', 'IDR', 'CNY'].index(user_info['preferred_currency']))

            description = st.text_area("Description (optional)")

            submitted = st.form_submit_button("Add Transaction")

            if submitted:
                if not merchant or amount <= 0:
                    st.error("Please fill in merchant and amount")
                else:
                    success = add_transaction(user_id, category, merchant, amount, trans_currency, description)
                    if success:
                        st.success("✅ Transaction added successfully!")
                        st.balloons()
                        # Rerun to refresh data
                        st.rerun()

    # TAB 3: Manage Transactions (Bulk Delete)
    with tab3:
        st.subheader("🗑️ Manage Your Transactions")
        st.markdown("**Delete wrong or duplicate transactions - Select multiple to delete at once!**")

        if len(user_transactions) == 0:
            st.info("No transactions to manage. Add your first transaction!")
        else:
            # Bulk delete feature
            st.write(f"**Total Transactions:** {len(user_transactions)}")

            # Create transaction display dataframe
            display_df = user_transactions.sort_values('transaction_date', ascending=False).copy()
            display_df['Select'] = False
            display_df['Date'] = display_df['transaction_date'].dt.strftime('%Y-%m-%d %H:%M')
            display_df['Amount'] = display_df[f'amount_{currency}'].apply(lambda x: f"{currency} {x:,.2f}")

            # Show only relevant columns
            display_columns = ['Date', 'category', 'merchant', 'Amount', 'description']

            # Create selection interface
            st.markdown("### 📋 Select Transactions to Delete")

            # Multi-select using checkboxes
            selected_ids = []

            for idx, row in display_df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 1.5, 1.5, 2, 2])

                with col1:
                    # Checkbox for selection
                    is_selected = st.checkbox("Select", key=f"select_{row['transaction_id']}", label_visibility="collapsed")
                    if is_selected:
                        selected_ids.append(row['transaction_id'])

                with col2:
                    st.markdown(f"**📅 {row['Date']}**")
                with col3:
                    st.markdown(f"📁 {row['category']}")
                with col4:
                    st.markdown(f"🏪 {row['merchant']}")
                with col5:
                    st.markdown(f"**💰 {row['Amount']}**")
                with col6:
                    if row['description'] and row['description'] != '':
                        st.caption(f"📝 {row['description']}")

                st.markdown("---")

            # Bulk delete button
            if len(selected_ids) > 0:
                st.markdown(f"### ⚠️ **{len(selected_ids)} transaction(s) selected**")

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button(f"🗑️ DELETE {len(selected_ids)} SELECTED TRANSACTION(S)",
                                type="primary",
                                use_container_width=True):
                        # Delete all selected transactions
                        success_count = 0
                        for trans_id in selected_ids:
                            success, _ = delete_transaction(trans_id, user_id)
                            if success:
                                success_count += 1

                        if success_count == len(selected_ids):
                            st.success(f"✅ Successfully deleted {success_count} transaction(s)!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.warning(f"Deleted {success_count} out of {len(selected_ids)} transactions")
                            st.rerun()
            else:
                st.info("💡 **Tip:** Check the box next to transactions you want to delete, then click the delete button.")

    # TAB 4: Budget Recommendations
    with tab4:
        st.subheader("💡 Budget Recommendations (50/30/20 Rule)")

        if len(user_transactions) == 0:
            st.info("Add some transactions first to see budget recommendations!")
        else:
            # Get analysis and recommendations
            recommender = st.session_state.budget_recommender
            analysis = recommender.analyze_user_spending(transactions_df, user_id, months=3, target_currency=currency)

            if analysis:
                recommendations = recommender.generate_recommendations(
                    {'amount': user_info['monthly_income'], 'currency': user_info['preferred_currency']},
                    analysis,
                    target_currency=currency
                )

                # Budget health score
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    score = recommendations['budget_health_score']['overall']
                    color = 'green' if score >= 70 else 'orange' if score >= 50 else 'red'
                    st.markdown(f"<div style='text-align: center;'><h1 style='color: {color};'>{score:.0f}</h1><p>Health Score</p></div>", unsafe_allow_html=True)
                with col2:
                    st.metric("Essentials Score", f"{recommendations['budget_health_score']['essentials']:.0f}")
                with col3:
                    st.metric("Discretionary Score", f"{recommendations['budget_health_score']['discretionary']:.0f}")
                with col4:
                    st.metric("Savings Score", f"{recommendations['budget_health_score']['savings']:.0f}")

                # Budget comparison
                st.subheader("📊 Ideal vs Actual Spending")

                categories = ['Essentials', 'Discretionary', 'Savings']
                ideal_values = [
                    recommendations['ideal_budget']['essentials'],
                    recommendations['ideal_budget']['discretionary'],
                    recommendations['ideal_budget']['savings']
                ]
                actual_values = [
                    recommendations['current_spending']['essentials'],
                    recommendations['current_spending']['discretionary'],
                    recommendations['current_spending']['savings']
                ]

                # Soft mint for ideal, soft coral for actual (subtle contrast)
                fig = go.Figure(data=[
                    go.Bar(name='Ideal (50/30/20)', x=categories, y=ideal_values, marker_color='#6ee7b7'),
                    go.Bar(name='Actual', x=categories, y=actual_values, marker_color='#fda4af')
                ])
                fig.update_layout(
                    barmode='group',
                    yaxis_title=f'Amount ({currency})',
                    height=500,
                    dragmode=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=50, r=50, t=80, b=50)
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # Recommendations
                st.subheader("💡 Personalized Recommendations")
                for rec in recommendations['recommendations']:
                    if rec['type'] == 'critical':
                        st.markdown(f"<div class='alert-box'>🚨 <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)
                    elif rec['type'] == 'warning':
                        st.markdown(f"<div class='warning-box'>⚠️ <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='success-box'>✅ <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)

                # SPENDING FORECAST
                st.markdown("---")
                st.subheader("📈 Spending Forecast - Next 30 Days")
                st.markdown("**AI-powered prediction of your future expenses**")

                with st.spinner("Generating forecast..."):
                    forecast_data, error = forecast_user_spending(user_id, transactions_df, days_ahead=30)

                if error:
                    st.warning(f"⚠️ Cannot generate forecast: {error}")
                    st.info("💡 Tip: Add more transactions (at least 7 days of data) to see spending predictions!")
                elif forecast_data is not None:
                    # Convert to user's currency
                    forecast_data['predicted'] = forecast_data['yhat'].apply(
                        lambda x: converter.convert(x, 'USD', currency)
                    )
                    forecast_data['predicted_low'] = forecast_data['yhat_lower'].apply(
                        lambda x: converter.convert(max(0, x), 'USD', currency)
                    )
                    forecast_data['predicted_high'] = forecast_data['yhat_upper'].apply(
                        lambda x: converter.convert(x, 'USD', currency)
                    )

                    # Show total predicted spending
                    total_predicted = forecast_data['predicted'].sum()
                    avg_daily = total_predicted / 30

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Predicted Total (30 days)", f"{currency} {total_predicted:,.2f}")
                    with col2:
                        st.metric("📅 Average Daily Spending", f"{currency} {avg_daily:,.2f}")
                    with col3:
                        monthly_income = converter.convert(user_info['monthly_income'], user_info['preferred_currency'], currency)
                        remaining = monthly_income - total_predicted
                        st.metric("💰 Expected Remaining", f"{currency} {remaining:,.2f}",
                                 delta=f"{(remaining/monthly_income)*100:.1f}% of income")

                    # Plot forecast
                    fig = go.Figure()

                    # Add prediction line
                    fig.add_trace(go.Scatter(
                        x=forecast_data['ds'],
                        y=forecast_data['predicted'],
                        mode='lines',
                        name='Predicted Spending',
                        line=dict(color='#7c3aed', width=3)
                    ))

                    # Add confidence interval
                    fig.add_trace(go.Scatter(
                        x=forecast_data['ds'],
                        y=forecast_data['predicted_high'],
                        mode='lines',
                        name='Upper Bound',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=forecast_data['ds'],
                        y=forecast_data['predicted_low'],
                        fill='tonexty',
                        mode='lines',
                        name='Confidence Range',
                        line=dict(width=0),
                        fillcolor='rgba(124, 58, 237, 0.2)'
                    ))

                    fig.update_layout(
                        title=f'Daily Spending Forecast - Next 30 Days ({currency})',
                        xaxis_title='Date',
                        yaxis_title=f'Predicted Spending ({currency})',
                        hovermode='x unified',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=500,
                        dragmode=False,
                        margin=dict(l=50, r=50, t=80, b=50)
                    )

                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                    st.success("✨ This prediction is based on your historical spending patterns using AI (Prophet model)")
                    st.caption("💡 The more data you have, the more accurate the predictions become!")

    # TAB 5: Currency Converter
    with tab5:
        st.subheader("💱 Real-Time Currency Converter")

        # Update rates button
        if st.button("🔄 Update Exchange Rates"):
            converter.fetch_rates(force_update=True)
            st.success("✅ Exchange rates updated!")

        # Display last update time
        if converter.last_update:
            st.info(f"Last updated: {converter.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

        # Converter interface
        col1, col2, col3 = st.columns(3)

        with col1:
            amount_to_convert = st.number_input("Amount", value=100.0, min_value=0.0)
        with col2:
            from_currency = st.selectbox("From", ['USD', 'IDR', 'CNY'])
        with col3:
            to_currency = st.selectbox("To", ['USD', 'IDR', 'CNY'])

        if st.button("Convert"):
            converted_amount = converter.convert(amount_to_convert, from_currency, to_currency)
            st.success(f"{amount_to_convert:,.2f} {from_currency} = {converted_amount:,.2f} {to_currency}")

        # Exchange rate matrix
        st.subheader("📊 Exchange Rate Matrix")
        rate_matrix = converter.get_rate_matrix()
        st.dataframe(rate_matrix, use_container_width=True)

    # TAB 6: Reports
    with tab6:
        st.subheader("📄 Export Reports")

        if len(user_transactions) > 0:
            col1, col2 = st.columns(2)

            with col1:
                # Export transaction data
                if st.button("📥 Export Transactions (CSV)"):
                    csv = user_transactions.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"transactions_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            with col2:
                # Export summary report
                if st.button("📊 Generate Summary Report"):
                    st.success("Report generation feature coming soon!")

            # Display summary statistics
            st.subheader("📈 Summary Statistics")

            summary_stats = {
                'Metric': [
                    'Total Transactions',
                    'Total Spending',
                    'Average Transaction',
                    'Most Frequent Category',
                    'Highest Single Transaction',
                    'Date Range'
                ],
                'Value': [
                    f"{len(user_transactions):,}",
                    f"{currency} {user_transactions[f'amount_{currency}'].sum():,.2f}",
                    f"{currency} {user_transactions[f'amount_{currency}'].mean():,.2f}",
                    user_transactions['category'].mode()[0] if len(user_transactions) > 0 else 'N/A',
                    f"{currency} {user_transactions[f'amount_{currency}'].max():,.2f}",
                    f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                ]
            }

            st.table(pd.DataFrame(summary_stats))
        else:
            st.info("No transactions to export. Add some transactions first!")

if __name__ == "__main__":
    main()
