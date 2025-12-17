"""
Smart Finance Dashboard - Interactive Streamlit Application
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

def main():
    # Header
    st.markdown('<h1 class="main-header">💰 Smart Finance Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    try:
        users_df, transactions_df = load_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please run the data generation script first: `python src/data_generation/generate_data.py`")
        return
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    # User selection
    user_names = users_df['name'].tolist()
    selected_user_name = st.sidebar.selectbox("Select User", user_names)
    user = users_df[users_df['name'] == selected_user_name].iloc[0]
    user_id = user['user_id']
    
    # Currency selection
    currency = st.sidebar.selectbox(
        "Display Currency",
        ['USD', 'IDR', 'CNY'],
        index=0
    )
    
    # Date range filter
    st.sidebar.subheader("📅 Date Range")
    date_filter = st.sidebar.radio(
        "Select Period",
        ['Last 30 Days', 'Last 3 Months', 'Last 6 Months', 'All Time', 'Custom']
    )
    
    if date_filter == 'Last 30 Days':
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
    user_transactions = converter.convert_dataframe(
        user_transactions,
        amount_column='amount',
        currency_column='currency',
        target_currency=currency
    )
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "🚨 Fraud Detection",
        "📈 Forecasting",
        "💡 Budget Recommendations",
        "💱 Currency Converter",
        "📄 Reports"
    ])
    
    # TAB 1: Overview
    with tab1:
        st.subheader(f"📊 Financial Overview - {selected_user_name}")
        
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
                user['monthly_income'], 'USD', currency
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
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Category Distribution")
            fig = px.pie(
                values=category_spending.values,
                names=category_spending.index,
                title='Spending Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
        
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
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent transactions
        st.subheader("📝 Recent Transactions")
        recent_transactions = user_transactions.nlargest(10, 'transaction_date')[
            ['transaction_date', 'category', 'merchant', f'amount_{currency}', 'description']
        ].copy()
        recent_transactions['transaction_date'] = recent_transactions['transaction_date'].dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(recent_transactions, use_container_width=True)
    
    # TAB 2: Fraud Detection
    with tab2:
        st.subheader("🚨 Fraud Detection & Anomalies")
        
        # Check if fraud scores are available
        if 'ensemble_fraud' in user_transactions.columns:
            fraud_transactions = user_transactions[user_transactions['ensemble_fraud'] == 1]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Alerts", len(fraud_transactions))
            with col2:
                fraud_amount = fraud_transactions[f'amount_{currency}'].sum()
                st.metric("Flagged Amount", f"{currency} {fraud_amount:,.2f}")
            with col3:
                fraud_rate = (len(fraud_transactions) / len(user_transactions) * 100) if len(user_transactions) > 0 else 0
                st.metric("Alert Rate", f"{fraud_rate:.2f}%")
            
            if len(fraud_transactions) > 0:
                st.warning(f"⚠️ {len(fraud_transactions)} suspicious transactions detected!")
                
                # Show fraud alerts
                st.subheader("🚨 Suspicious Transactions")
                fraud_display = fraud_transactions[[
                    'transaction_date', 'category', 'merchant', 
                    f'amount_{currency}', 'ensemble_score'
                ]].copy()
                fraud_display['transaction_date'] = fraud_display['transaction_date'].dt.strftime('%Y-%m-%d %H:%M')
                fraud_display = fraud_display.sort_values('ensemble_score', ascending=False)
                st.dataframe(fraud_display, use_container_width=True)
                
                # Fraud score distribution
                st.subheader("📊 Anomaly Score Distribution")
                fig = px.histogram(
                    user_transactions,
                    x='ensemble_score',
                    nbins=50,
                    title='Distribution of Anomaly Scores'
                )
                fig.add_vline(x=user_transactions['ensemble_score'].quantile(0.95), 
                            line_dash="dash", line_color="red",
                            annotation_text="95th Percentile")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No suspicious transactions detected!")
        else:
            st.info("ℹ️ Fraud detection models not yet trained. Run the fraud detector script first.")
    
    # TAB 3: Forecasting
    with tab3:
        st.subheader("📈 Spending Forecasts")
        
        # Check if forecaster is available
        forecaster_path = MODEL_PATHS['forecaster']
        if forecaster_path.exists():
            try:
                forecaster = SpendingForecaster()
                forecaster.load_models()
                
                # Get forecast summary
                summary = forecaster.get_monthly_summary()
                
                st.subheader("📊 3-Month Forecast Summary")
                st.dataframe(summary, use_container_width=True)
                
                # Select category to view detailed forecast
                st.subheader("📈 Detailed Category Forecast")
                selected_category = st.selectbox(
                    "Select Category",
                    list(forecaster.models.keys())
                )
                
                if selected_category:
                    forecast = forecaster.get_forecast(selected_category, periods=90)
                    
                    if forecast is not None:
                        # Plot forecast
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=forecast['ds'],
                            y=forecast['yhat'],
                            mode='lines',
                            name='Forecast',
                            line=dict(color='#1f77b4')
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=forecast['ds'],
                            y=forecast['yhat_upper'],
                            mode='lines',
                            name='Upper Bound',
                            line=dict(width=0),
                            showlegend=False
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=forecast['ds'],
                            y=forecast['yhat_lower'],
                            mode='lines',
                            name='Lower Bound',
                            fill='tonexty',
                            line=dict(width=0),
                            fillcolor='rgba(31, 119, 180, 0.2)'
                        ))
                        
                        fig.update_layout(
                            title=f'Spending Forecast: {selected_category}',
                            xaxis_title='Date',
                            yaxis_title=f'Amount ({currency})',
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading forecast: {str(e)}")
        else:
            st.info("ℹ️ Forecasting models not yet trained. Run the forecaster script first.")
    
    # TAB 4: Budget Recommendations
    with tab4:
        st.subheader("💡 Budget Recommendations (50/30/20 Rule)")
        
        # Allow user to input/update income
        col1, col2 = st.columns(2)
        with col1:
            income_amount = st.number_input(
                "Monthly Income",
                value=float(user['monthly_income']),
                min_value=0.0,
                step=100.0
            )
        with col2:
            income_currency = st.selectbox("Income Currency", ['USD', 'IDR', 'CNY'], index=0)
        
        # Get analysis and recommendations
        recommender = st.session_state.budget_recommender
        analysis = recommender.analyze_user_spending(transactions_df, user_id, months=3, target_currency=currency)
        
        if analysis:
            recommendations = recommender.generate_recommendations(
                {'amount': income_amount, 'currency': income_currency},
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
            st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.subheader("💡 Personalized Recommendations")
            for rec in recommendations['recommendations']:
                if rec['type'] == 'critical':
                    st.markdown(f"<div class='alert-box'>🚨 <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)
                elif rec['type'] == 'warning':
                    st.markdown(f"<div class='warning-box'>⚠️ <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='success-box'>✅ <strong>{rec['category'].title()}:</strong> {rec['message']}</div>", unsafe_allow_html=True)
    
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

if __name__ == "__main__":
    main()
    