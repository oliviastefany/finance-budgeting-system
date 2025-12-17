

"""
Test script to verify dashboard fixes
"""
import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import RAW_DATA_DIR
from src.currency.currency_converter import CurrencyConverter
from src.budgeting.budget_recommender import BudgetRecommender

print("=" * 70)
print("TESTING DASHBOARD FIXES")
print("=" * 70)

# Test 1: CurrencyConverter
print("\n[1] Testing CurrencyConverter...")
try:
    converter = CurrencyConverter()

    # Test convert_dataframe
    test_df = pd.DataFrame({
        'amount': [100, 200, 300],
        'currency': ['USD', 'IDR', 'CNY']
    })

    result_df = converter.convert_dataframe(test_df, 'amount', 'currency', 'USD')
    assert 'amount_USD' in result_df.columns, "convert_dataframe failed: missing amount_USD column"

    # Test get_rate_matrix
    rate_matrix = converter.get_rate_matrix()
    assert rate_matrix.shape == (3, 3), "get_rate_matrix failed: wrong shape"

    # Test last_update attribute
    assert hasattr(converter, 'last_update'), "Missing last_update attribute"

    # Test force_update parameter
    converter.fetch_rates(force_update=True)

    print("   PASS: All CurrencyConverter tests passed!")

except Exception as e:
    print(f"   FAIL: {str(e)}")
    sys.exit(1)

# Test 2: BudgetRecommender
print("\n[2] Testing BudgetRecommender...")
try:
    recommender = BudgetRecommender()

    # Load test data
    transactions_df = pd.read_csv(RAW_DATA_DIR / 'transactions.csv')
    users_df = pd.read_csv(RAW_DATA_DIR / 'users.csv')

    test_user_id = users_df['user_id'].iloc[0]

    # Test analyze_user_spending
    analysis = recommender.analyze_user_spending(
        transactions_df,
        test_user_id,
        months=3,
        target_currency='USD'
    )

    assert 'spending' in analysis, "analyze_user_spending failed: missing spending"
    assert 'essentials' in analysis['spending'], "analyze_user_spending failed: missing essentials"

    # Test new generate_recommendations signature
    income_info = {'amount': 5000, 'currency': 'USD'}
    recommendations = recommender.generate_recommendations(
        income_info=income_info,
        analysis=analysis,
        target_currency='USD'
    )

    assert 'budget_health_score' in recommendations, "Missing budget_health_score"
    assert 'recommendations' in recommendations, "Missing recommendations"
    assert 'overall' in recommendations['budget_health_score'], "Missing overall score"

    print("   PASS: All BudgetRecommender tests passed!")

except Exception as e:
    print(f"   FAIL: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Integration test
print("\n[3] Testing Dashboard Integration...")
try:
    # Simulate dashboard workflow
    user_id = users_df['user_id'].iloc[0]
    user = users_df[users_df['user_id'] == user_id].iloc[0]

    # Filter and convert transactions
    user_transactions = transactions_df[transactions_df['user_id'] == user_id].copy()
    user_transactions = converter.convert_dataframe(
        user_transactions,
        amount_column='amount',
        currency_column='currency',
        target_currency='USD'
    )

    # Analyze spending
    analysis = recommender.analyze_user_spending(
        transactions_df,
        user_id,
        months=3,
        target_currency='USD'
    )

    # Generate recommendations
    recommendations = recommender.generate_recommendations(
        income_info={'amount': user['monthly_income'], 'currency': 'USD'},
        analysis=analysis,
        target_currency='USD'
    )

    print("   PASS: Dashboard integration test passed!")
    print(f"\n   User: {user['name']}")
    print(f"   Health Score: {recommendations['budget_health_score']['overall']:.1f}/100")
    print(f"   Recommendations: {len(recommendations['recommendations'])}")

except Exception as e:
    print(f"   FAIL: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)
print("\nThe dashboard should now work without errors.")
print("Run it with: streamlit run dashboards/streamlit_dashboard.py")
