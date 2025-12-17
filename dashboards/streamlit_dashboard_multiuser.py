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
from src.forecasting.forecaster import SpendingForecaster

# Import authentication
from auth import check_authentication, logout, get_current_user_id, get_current_user_email, AuthManager

# Page configuration
st.set_page_config(
    page_title="Smart Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .alert-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
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

    # Load fraud scores if available
    fraud_file = PROCESSED_DATA_DIR / 'transactions_with_fraud_scores.csv'
    if fraud_file.exists():
        fraud_df = pd.read_csv(fraud_file)
        fraud_df['transaction_date'] = pd.to_datetime(fraud_df['transaction_date'])
        return users_df, fraud_df

    return users_df, transactions_df

def add_transaction(user_id, category, merchant, amount, currency, description=""):
    """Add a new transaction for the current user"""
    transactions_df = pd.read_csv(RAW_DATA_DIR / 'transactions.csv')

    # Generate new transaction ID
    last_id = transactions_df['transaction_id'].iloc[-1]
    number = int(last_id[1:]) + 1
    new_id = f'T{number:05d}'

    # Create new transaction
    new_transaction = {
        'transaction_id': new_id,
        'user_id': user_id,
        'transaction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'category': category,
        'merchant': merchant,
        'amount': amount,
        'currency': currency,
        'description': description
    }

    # Append
    transactions_df = pd.concat([transactions_df, pd.DataFrame([new_transaction])], ignore_index=True)

    # Save
    transactions_df.to_csv(RAW_DATA_DIR / 'transactions.csv', index=False)

    # Clear cache to reload data
    load_data.clear()

    return True

def main():
    # Get current user
    user_id = get_current_user_id()
    user_email = get_current_user_email()

    # Header with logout
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown('<h1 class="main-header">💰 Smart Finance</h1>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p style='text-align: center; padding-top: 20px;'>Welcome, {user_email}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Logout", type="primary"):
            logout()

    # Load data
    try:
        users_df, transactions_df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Get user info
    auth = AuthManager()
    user_info = auth.get_user_info(user_id)

    if not user_info:
        st.error("User not found")
        return

    # Sidebar
    st.sidebar.title("⚙️ Settings")

    # Display user info
    st.sidebar.info(f"""
    **User:** {user_info['name']}
    **Email:** {user_info['email']}
    **Income:** {user_info['preferred_currency']} {user_info['monthly_income']:,.2f}
    """)

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
        user_transactions = converter.convert_dataframe(
            user_transactions,
            amount_column='amount',
            currency_column='currency',
            target_currency=currency
        )

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "➕ Add Transaction",
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

                fig = go.Figure(data=[
                    go.Bar(x=category_spending.index, y=category_spending.values, marker_color='#1f77b4')
                ])
                fig.update_layout(
                    title=f'Spending by Category ({currency})',
                    xaxis_title='Category',
                    yaxis_title=f'Amount ({currency})'
                )
                st.plotly_chart(fig, width='stretch')

            with col2:
                st.subheader("📊 Category Distribution")
                fig = px.pie(
                    values=category_spending.values,
                    names=category_spending.index,
                    title='Spending Distribution'
                )
                st.plotly_chart(fig, width='stretch')

            # Spending over time
            st.subheader("📅 Spending Trend")
            daily_spending = user_transactions.groupby(
                user_transactions['transaction_date'].dt.date
            )[f'amount_{currency}'].sum().reset_index()
            daily_spending.columns = ['Date', 'Amount']

            fig = px.line(
                daily_spending,
                x='Date',
                y='Amount',
                title=f'Daily Spending Trend ({currency})'
            )
            fig.update_traces(line_color='#1f77b4')
            st.plotly_chart(fig, width='stretch')

            # Recent transactions
            st.subheader("📝 Recent Transactions")
            recent_transactions = user_transactions.nlargest(10, 'transaction_date')[
                ['transaction_date', 'category', 'merchant', f'amount_{currency}', 'description']
            ].copy()
            recent_transactions['transaction_date'] = recent_transactions['transaction_date'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(recent_transactions, width='stretch')

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
                        # Suggest to refresh
                        st.info("Go to Overview tab to see your updated data!")

    # TAB 3: Budget Recommendations
    with tab3:
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

                fig = go.Figure(data=[
                    go.Bar(name='Ideal (50/30/20)', x=categories, y=ideal_values, marker_color='#1f77b4'),
                    go.Bar(name='Actual', x=categories, y=actual_values, marker_color='#ff7f0e')
                ])
                fig.update_layout(barmode='group', yaxis_title=f'Amount ({currency})')
                st.plotly_chart(fig, width='stretch')

                # Recommendations
                st.subheader("💡 Personalized Recommendations")
                for rec in recommendations['recommendations']:
                    if rec['type'] == 'critical':
                        st.markdown(f"<div class='alert-box'>🚨 <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)
                    elif rec['type'] == 'warning':
                        st.markdown(f"<div class='warning-box'>⚠️ <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='success-box'>✅ <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)

    # TAB 4: Currency Converter
    with tab4:
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
        st.dataframe(rate_matrix, width='stretch')

    # TAB 5: Reports
    with tab5:
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
