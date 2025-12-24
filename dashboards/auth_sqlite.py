"""
Authentication Module for Smart Finance Dashboard with Multi-Storage Support
Supports: CSV, SQLite, and PostgreSQL
"""
import streamlit as st
import pandas as pd
import hashlib
from pathlib import Path
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.config import RAW_DATA_DIR
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get storage mode from environment
STORAGE_MODE = os.getenv('DATA_STORAGE_MODE', 'csv')  # 'csv', 'sqlite', or 'postgresql'


class AuthManager:
    """
    Universal Authentication Manager
    Supports: CSV, SQLite, PostgreSQL
    """

    def __init__(self, storage_mode=None):
        """
        Initialize AuthManager

        Args:
            storage_mode (str): 'csv', 'sqlite', or 'postgresql'
        """
        self.storage_mode = storage_mode or STORAGE_MODE
        self.users_file = RAW_DATA_DIR / 'users.csv'
        self.transactions_file = RAW_DATA_DIR / 'transactions.csv'
        self.db_manager = None

        print(f"🔧 Initializing AuthManager with mode: {self.storage_mode}")

        # Initialize database connection based on storage mode
        if self.storage_mode == 'sqlite':
            try:
                from src.database.sqlite_manager import get_db_manager
                self.db_manager = get_db_manager()
                print("✅ Using SQLite storage")
            except Exception as e:
                print(f"⚠️  Error connecting to SQLite: {e}")
                print("⚠️  Falling back to CSV storage")
                self.storage_mode = 'csv'

        elif self.storage_mode == 'postgresql':
            try:
                from src.database.postgres_manager import get_db_manager
                self.db_manager = get_db_manager()
                print("✅ Using PostgreSQL storage")
            except Exception as e:
                print(f"⚠️  Error connecting to PostgreSQL: {e}")
                print("⚠️  Falling back to CSV storage")
                self.storage_mode = 'csv'
        else:
            print("✅ Using CSV storage")

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    # ========================================
    # CSV STORAGE METHODS
    # ========================================

    def load_users_csv(self):
        """Load users from CSV"""
        if self.users_file.exists():
            return pd.read_csv(self.users_file)
        return pd.DataFrame(columns=['user_id', 'name', 'email', 'password_hash', 'monthly_income', 'preferred_currency'])

    def save_users_csv(self, users_df):
        """Save users to CSV"""
        users_df.to_csv(self.users_file, index=False)

    def get_next_user_id_csv(self):
        """Generate next user ID from CSV"""
        users_df = self.load_users_csv()
        if len(users_df) == 0:
            return 'U00001'

        last_id = users_df['user_id'].iloc[-1]
        number = int(last_id[1:]) + 1
        return f'U{number:05d}'

    def email_exists_csv(self, email):
        """Check if email already registered in CSV"""
        users_df = self.load_users_csv()
        return email.lower() in users_df['email'].str.lower().values

    def register_user_csv(self, name, email, password, monthly_income, currency='USD'):
        """Register a new user in CSV"""
        if not name or not email or not password:
            return False, "All fields are required"

        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        if self.email_exists_csv(email):
            return False, "Email already registered"

        users_df = self.load_users_csv()

        new_user = {
            'user_id': self.get_next_user_id_csv(),
            'name': name,
            'email': email.lower(),
            'password_hash': self.hash_password(password),
            'monthly_income': monthly_income,
            'preferred_currency': currency
        }

        users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
        self.save_users_csv(users_df)

        return True, "Registration successful!"

    def login_csv(self, email, password):
        """Login user from CSV"""
        users_df = self.load_users_csv()
        user_row = users_df[users_df['email'].str.lower() == email.lower()]

        if len(user_row) == 0:
            return False, None, "Email not found"

        user = user_row.iloc[0]

        if user['password_hash'] != self.hash_password(password):
            return False, None, "Incorrect password"

        return True, user['user_id'], "Login successful!"

    def get_user_info_csv(self, user_id):
        """Get user information from CSV"""
        users_df = self.load_users_csv()
        user_row = users_df[users_df['user_id'] == user_id]

        if len(user_row) == 0:
            return None

        return user_row.iloc[0].to_dict()

    # ========================================
    # DATABASE STORAGE METHODS (SQLite/PostgreSQL)
    # ========================================

    def register_user_db(self, name, email, password, monthly_income, currency='USD'):
        """Register a new user in database (SQLite/PostgreSQL)"""
        if not self.db_manager:
            return False, "Database not available"

        success, user_id, message = self.db_manager.create_user(
            name, email, password, monthly_income, currency
        )

        return success, message

    def login_db(self, email, password):
        """Login user from database (SQLite/PostgreSQL)"""
        if not self.db_manager:
            return False, None, "Database not available"

        return self.db_manager.verify_login(email, password)

    def get_user_info_db(self, user_id):
        """Get user information from database (SQLite/PostgreSQL)"""
        if not self.db_manager:
            return None

        return self.db_manager.get_user_by_id(user_id)

    # ========================================
    # UNIFIED INTERFACE (Auto-selects storage)
    # ========================================

    def register_user(self, name, email, password, monthly_income, currency='USD'):
        """
        Register a new user (auto-selects storage backend)
        """
        if self.storage_mode in ['sqlite', 'postgresql']:
            return self.register_user_db(name, email, password, monthly_income, currency)
        else:
            return self.register_user_csv(name, email, password, monthly_income, currency)

    def login(self, email, password):
        """
        Login user (auto-selects storage backend)
        """
        if self.storage_mode in ['sqlite', 'postgresql']:
            return self.login_db(email, password)
        else:
            return self.login_csv(email, password)

    def get_user_info(self, user_id):
        """
        Get user information (auto-selects storage backend)
        """
        if self.storage_mode in ['sqlite', 'postgresql']:
            return self.get_user_info_db(user_id)
        else:
            return self.get_user_info_csv(user_id)


# ========================================
# STREAMLIT UI FUNCTIONS
# ========================================

def show_login_page():
    """Display login page"""
    st.markdown('<h1 class="main-header">💰 Smart Finance - Login</h1>', unsafe_allow_html=True)

    # Show storage mode
    storage_mode = os.getenv('DATA_STORAGE_MODE', 'csv')

    if storage_mode == 'sqlite':
        st.info("🗄️ Using SQLite Database (Simple & Fast)")
    elif storage_mode == 'postgresql':
        st.info("🗄️ Using PostgreSQL Database")
    else:
        st.info("📁 Using CSV File Storage")

    tab1, tab2 = st.tabs(["Login", "Register"])

    auth = AuthManager()

    with tab1:
        st.subheader("Welcome Back!")

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                success, user_id, message = auth.login(email, password)

                if success:
                    st.success(message)
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = user_id
                    st.session_state['user_email'] = email
                    st.rerun()
                else:
                    st.error(message)

    with tab2:
        st.subheader("Create Account")

        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password (min 6 characters)", type="password", key="reg_password")
            password_confirm = st.text_input("Confirm Password", type="password")

            col1, col2 = st.columns(2)
            with col1:
                monthly_income = st.number_input("Monthly Income", min_value=0.0, value=5000.0, step=100.0)
            with col2:
                currency = st.selectbox("Currency", ['USD', 'IDR', 'CNY'])

            submit = st.form_submit_button("Register")

            if submit:
                if password != password_confirm:
                    st.error("Passwords do not match")
                else:
                    success, message = auth.register_user(name, email, password, monthly_income, currency)

                    if success:
                        st.success(message + " Please login.")
                    else:
                        st.error(message)


def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        show_login_page()
        return False

    return True


def logout():
    """Logout current user"""
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None
    st.session_state['user_email'] = None
    st.rerun()


def get_current_user_id():
    """Get current logged-in user ID"""
    return st.session_state.get('user_id', None)


def get_current_user_email():
    """Get current logged-in user email"""
    return st.session_state.get('user_email', None)
