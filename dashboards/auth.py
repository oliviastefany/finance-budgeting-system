"""
Authentication Module for Smart Finance Dashboard
Handles user registration, login, and session management
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


class AuthManager:
    def __init__(self):
        self.users_file = RAW_DATA_DIR / 'users.csv'
        self.transactions_file = RAW_DATA_DIR / 'transactions.csv'

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        """Load users from CSV"""
        if self.users_file.exists():
            return pd.read_csv(self.users_file)
        return pd.DataFrame(columns=['user_id', 'name', 'email', 'password_hash', 'monthly_income', 'preferred_currency'])

    def save_users(self, users_df):
        """Save users to CSV"""
        users_df.to_csv(self.users_file, index=False)

    def get_next_user_id(self):
        """Generate next user ID"""
        users_df = self.load_users()
        if len(users_df) == 0:
            return 'U00001'

        # Get last user ID and increment
        last_id = users_df['user_id'].iloc[-1]
        number = int(last_id[1:]) + 1
        return f'U{number:05d}'

    def email_exists(self, email):
        """Check if email already registered"""
        users_df = self.load_users()
        return email.lower() in users_df['email'].str.lower().values

    def register_user(self, name, email, password, monthly_income, currency='USD'):
        """Register a new user"""
        # Validate inputs
        if not name or not email or not password:
            return False, "All fields are required"

        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        if self.email_exists(email):
            return False, "Email already registered"

        # Load existing users
        users_df = self.load_users()

        # Create new user
        new_user = {
            'user_id': self.get_next_user_id(),
            'name': name,
            'email': email.lower(),
            'password_hash': self.hash_password(password),
            'monthly_income': monthly_income,
            'preferred_currency': currency
        }

        # Append new user
        users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)

        # Save
        self.save_users(users_df)

        return True, "Registration successful!"

    def login(self, email, password):
        """Login user"""
        users_df = self.load_users()

        # Find user by email
        user_row = users_df[users_df['email'].str.lower() == email.lower()]

        if len(user_row) == 0:
            return False, None, "Email not found"

        user = user_row.iloc[0]

        # Check password
        if user['password_hash'] != self.hash_password(password):
            return False, None, "Incorrect password"

        return True, user['user_id'], "Login successful!"

    def get_user_info(self, user_id):
        """Get user information"""
        users_df = self.load_users()
        user_row = users_df[users_df['user_id'] == user_id]

        if len(user_row) == 0:
            return None

        return user_row.iloc[0].to_dict()


def show_login_page():
    """Display login page"""
    st.markdown('<h1 class="main-header">💰 Smart Finance - Login</h1>', unsafe_allow_html=True)

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
