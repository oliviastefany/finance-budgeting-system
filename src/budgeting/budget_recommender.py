"""
Budget Recommendation Engine
Implements 50/30/20 budgeting rule with personalized recommendations
"""
import pandas as pd
import numpy as np
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.config import RAW_DATA_DIR, BUDGET_CONFIG, TRANSACTION_CATEGORIES
from src.currency.currency_converter import CurrencyConverter


class BudgetRecommender:
    def __init__(self):
        self.budget_rules = BUDGET_CONFIG
        self.categories = TRANSACTION_CATEGORIES
        self.converter = CurrencyConverter()

    def load_user_data(self, user_id=None):
        """Load user and transaction data"""
        users_df = pd.read_csv(RAW_DATA_DIR / 'users.csv')
        transactions_df = pd.read_csv(RAW_DATA_DIR / 'transactions.csv')
        
        if user_id:
            user = users_df[users_df['user_id'] == user_id].iloc[0]
            user_transactions = transactions_df[transactions_df['user_id'] == user_id]
            return user, user_transactions
        
        return users_df, transactions_df

    def calculate_budget_allocation(self, monthly_income, currency='USD'):
        """Calculate 50/30/20 budget allocation"""
        allocation = {
            'essentials': monthly_income * self.budget_rules['essentials'],
            'discretionary': monthly_income * self.budget_rules['discretionary'],
            'savings': monthly_income * self.budget_rules['savings']
        }
        
        allocation['total'] = monthly_income
        allocation['currency'] = currency
        
        return allocation

    def categorize_spending(self, transactions_df, amount_column='amount_usd'):
        """Categorize transactions into essentials/discretionary/savings"""
        categorized = {'essentials': 0, 'discretionary': 0, 'savings': 0}

        for _, row in transactions_df.iterrows():
            category = row['category']
            amount = row[amount_column] if amount_column in transactions_df.columns else row.get('amount', 0)

            if category in self.categories['essentials']:
                categorized['essentials'] += amount
            elif category in self.categories['discretionary']:
                categorized['discretionary'] += amount
            elif category in self.categories['savings']:
                categorized['savings'] += amount

        categorized['total'] = sum(categorized.values())
        return categorized

    def analyze_user_spending(self, transactions_df, user_id, months=3, target_currency='USD'):
        """Analyze user spending over specified months"""
        # Filter transactions for the user
        user_transactions = transactions_df[transactions_df['user_id'] == user_id].copy()

        # Ensure date column is datetime
        if 'transaction_date' in user_transactions.columns:
            user_transactions['transaction_date'] = pd.to_datetime(user_transactions['transaction_date'])

            # Filter for recent months
            cutoff_date = pd.Timestamp.now() - pd.DateOffset(months=months)
            user_transactions = user_transactions[user_transactions['transaction_date'] >= cutoff_date]

        # Determine amount column to use
        amount_column = f'amount_{target_currency}'
        if amount_column not in user_transactions.columns:
            # Try to convert if we have currency info
            if 'currency' in user_transactions.columns and 'amount' in user_transactions.columns:
                user_transactions = self.converter.convert_dataframe(
                    user_transactions,
                    amount_column='amount',
                    currency_column='currency',
                    target_currency=target_currency
                )
            else:
                amount_column = 'amount'

        # Categorize spending
        spending = self.categorize_spending(user_transactions, amount_column=amount_column)

        return {
            'user_id': user_id,
            'months_analyzed': months,
            'currency': target_currency,
            'spending': spending,
            'transaction_count': len(user_transactions),
            'categories_breakdown': user_transactions.groupby('category')[amount_column].sum().to_dict() if amount_column in user_transactions.columns else {}
        }

    def generate_recommendations(self, income_info=None, analysis=None, target_currency='USD', user_id=None):
        """Generate personalized budget recommendations

        Can be called in two ways:
        1. Legacy: generate_recommendations(user_id=123)
        2. New: generate_recommendations(income_info={'amount': 5000, 'currency': 'USD'}, analysis={...}, target_currency='USD')
        """
        # New calling pattern (from dashboard)
        if income_info is not None and analysis is not None:
            income_amount = income_info['amount']
            income_currency = income_info['currency']

            # Convert income to target currency
            income_converted = self.converter.convert(income_amount, income_currency, target_currency)

            # Calculate ideal budget
            ideal_budget = self.calculate_budget_allocation(income_converted, target_currency)

            # Get actual spending from analysis
            actual_spending = analysis['spending']

            # Calculate budget health score
            budget_health_score = self._calculate_health_score(ideal_budget, actual_spending, income_converted)

            # Generate recommendations
            recommendations = {
                'user_id': analysis.get('user_id', 'unknown'),
                'monthly_income': income_amount,
                'currency': target_currency,
                'ideal_budget': ideal_budget,
                'current_spending': actual_spending,
                'budget_health_score': budget_health_score,
                'recommendations': []
            }

            # Compare actual vs ideal
            for category in ['essentials', 'discretionary', 'savings']:
                ideal = ideal_budget[category]
                actual = actual_spending[category]
                difference = actual - ideal
                percentage = (actual / income_converted * 100) if income_converted > 0 else 0

                rec_type = 'good'
                if difference > ideal * 0.2:  # More than 20% over
                    rec_type = 'critical'
                    message = f"Spending is {abs(difference):.2f} {target_currency} over budget. Consider reducing {category} expenses."
                elif difference > 0:
                    rec_type = 'warning'
                    message = f"Slightly over budget by {abs(difference):.2f} {target_currency}. Try to cut back on {category}."
                elif difference < -ideal * 0.2:  # More than 20% under
                    rec_type = 'good'
                    message = f"Great job! You have {abs(difference):.2f} {target_currency} extra room in your {category} budget."
                else:
                    rec_type = 'good'
                    message = f"Your {category} spending is well balanced!"

                recommendations['recommendations'].append({
                    'type': rec_type,
                    'category': category,
                    'ideal': ideal,
                    'actual': actual,
                    'difference': difference,
                    'percentage': percentage,
                    'message': message
                })

            return recommendations

        # Legacy calling pattern
        elif user_id is not None:
            user, transactions = self.load_user_data(user_id)

            monthly_income = user['monthly_income']
            currency = user['preferred_currency']

            # Convert income to USD for analysis
            income_usd = self.converter.convert(monthly_income, currency, 'USD')

            # Calculate ideal budget
            ideal_budget = self.calculate_budget_allocation(income_usd, 'USD')

            # Calculate actual spending (last 30 days)
            transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])
            recent_transactions = transactions[
                transactions['transaction_date'] >= transactions['transaction_date'].max() - pd.Timedelta(days=30)
            ]

            actual_spending = self.categorize_spending(recent_transactions)

            # Generate recommendations
            recommendations = {
                'user_id': user_id,
                'user_name': user['name'],
                'monthly_income': monthly_income,
                'currency': currency,
                'income_usd': income_usd,
                'ideal_budget': ideal_budget,
                'actual_spending': actual_spending,
                'recommendations': []
            }

            # Compare actual vs ideal
            for category in ['essentials', 'discretionary', 'savings']:
                ideal = ideal_budget[category]
                actual = actual_spending[category]
                difference = actual - ideal
                percentage = (actual / income_usd * 100) if income_usd > 0 else 0

                if difference > 0:
                    status = "OVER BUDGET"
                    message = f"Reduce {category} spending by ${abs(difference):.2f}"
                elif difference < -ideal * 0.1:  # More than 10% under
                    status = "UNDER BUDGET"
                    message = f"You have ${abs(difference):.2f} extra in {category}"
                else:
                    status = "ON TRACK"
                    message = f"{category.capitalize()} spending is well balanced"

                recommendations['recommendations'].append({
                    'category': category,
                    'ideal': ideal,
                    'actual': actual,
                    'difference': difference,
                    'percentage': percentage,
                    'status': status,
                    'message': message
                })

            return recommendations
        else:
            raise ValueError("Must provide either (income_info and analysis) or user_id")

    def _calculate_health_score(self, ideal_budget, actual_spending, income):
        """Calculate budget health scores (0-100)"""
        scores = {}

        for category in ['essentials', 'discretionary', 'savings']:
            ideal = ideal_budget[category]
            actual = actual_spending[category]

            if ideal == 0:
                score = 100 if actual == 0 else 0
            else:
                # Score based on how close to ideal (100 = perfect, 0 = very bad)
                deviation = abs(actual - ideal) / ideal
                score = max(0, 100 - (deviation * 100))

            scores[category] = score

        # Overall score is weighted average
        scores['overall'] = (
            scores['essentials'] * 0.4 +
            scores['discretionary'] * 0.3 +
            scores['savings'] * 0.3
        )

        return scores

    def print_recommendations(self, recommendations):
        """Pretty print budget recommendations"""
        print("\n" + "="*70)
        print(f"  BUDGET RECOMMENDATIONS: {recommendations['user_name']}")
        print("="*70)
        print(f"\nUser ID: {recommendations['user_id']}")
        print(f"Monthly Income: {self.converter.format_amount(recommendations['monthly_income'], recommendations['currency'])}")
        print(f"Income (USD): ${recommendations['income_usd']:,.2f}")
        
        print("\n" + "-"*70)
        print("50/30/20 BUDGET BREAKDOWN")
        print("-"*70)
        
        for rec in recommendations['recommendations']:
            print(f"\n{rec['category'].upper():15} | {rec['status']:15}")
            print(f"  Ideal Budget:   ${rec['ideal']:>10,.2f} USD")
            print(f"  Actual Spent:   ${rec['actual']:>10,.2f} USD ({rec['percentage']:.1f}% of income)")
            print(f"  Difference:     ${rec['difference']:>10,.2f}")
            print(f"  -> {rec['message']}")
        
        total_spent = recommendations['actual_spending']['total']
        savings_rate = ((recommendations['income_usd'] - total_spent) / recommendations['income_usd'] * 100) if recommendations['income_usd'] > 0 else 0
        
        print("\n" + "="*70)
        print(f"TOTAL SPENDING: ${total_spent:,.2f} USD")
        print(f"SAVINGS RATE: {savings_rate:.1f}%")
        print("="*70 + "\n")


if __name__ == "__main__":
    recommender = BudgetRecommender()

    # Test with first user
    users_df, _ = recommender.load_user_data()
    test_user_id = users_df['user_id'].iloc[0]

    recommendations = recommender.generate_recommendations(user_id=test_user_id)
    recommender.print_recommendations(recommendations)
