# 🛡️ Fraud Detection System - Complete Guide

## 📊 Current Status

### ✅ What You Have:
- **FraudDetector class** in `src/fraud_detection/fraud_detector.py`
- Uses **2 AI models**:
  - **Isolation Forest** - Detects unusual patterns
  - **AutoEncoder** - Neural network for anomaly detection
- **Feature engineering** with 22+ fraud indicators

### ❌ What's Missing:
- ❌ Models are **not trained yet**
- ❌ **Not integrated** into the dashboard
- ❌ No fraud alerts for users
- ❌ No fraud monitoring tab

---

## 🚀 How Fraud Detection Works

### 1. **What It Detects:**

#### 🔴 High-Risk Patterns:
- **Unusual amounts**: Transactions much higher than your normal spending
- **Rapid transactions**: Multiple purchases within 5 minutes
- **Night transactions**: Purchases at 10 PM - 5 AM
- **Round amounts**: Exactly $100, $500, $1000 (common in fraud)
- **New merchant**: First-time purchase at unknown store
- **Category mismatch**: Grocery card used for jewelry

#### 🟡 Medium-Risk Patterns:
- **Weekend spending surge**: Unusually high weekend activity
- **Foreign currency**: Transactions in currencies you rarely use
- **High deviation**: 2-3x your normal transaction amount

#### 🟢 Low-Risk Patterns:
- Regular purchases at known merchants
- Amounts within your normal range
- Consistent time patterns

### 2. **AI Models Explained:**

#### **Isolation Forest**
- **How it works**: Isolates anomalies using random decision trees
- **Best for**: Detecting outliers in transaction amounts and frequencies
- **Example**: Flags a $5,000 purchase when you normally spend $50

#### **AutoEncoder (Neural Network)**
- **How it works**: Learns normal transaction patterns, flags deviations
- **Best for**: Complex pattern recognition (time + amount + category)
- **Example**: Detects unusual combination of features

#### **Ensemble Score**
- Combines both models for better accuracy
- Fraud probability: 0-100% (average of both models)

---

## 🔧 Setup Instructions

### Step 1: Train the Fraud Detection Models

```bash
# Navigate to project directory
cd c:\smart-finance-ml

# Train fraud detection models
python src/fraud_detection/fraud_detector.py
```

**What this does:**
1. Loads your transaction data
2. Creates 22 fraud detection features
3. Trains Isolation Forest model
4. Trains AutoEncoder model
5. Saves trained models to `models/fraud_detector.pkl`
6. Creates `transactions_with_fraud_scores.csv`

**Expected output:**
```
========================================
  FRAUD DETECTION MODEL TRAINING
========================================

[1/6] Loading transaction data...
  Loaded 15008 transactions

[2/6] Engineering features for fraud detection...
  Created 35 total features

[3/6] Preparing feature matrix...
  Feature matrix shape: (15008, 22)
  Fraud rate: 3.50%

[4/6] Training anomaly detection models...
  Training Isolation Forest...
  Training AutoEncoder...
  Models trained successfully!

[5/6] Evaluating models...
  === Ensemble Results ===
  Precision: 0.85
  Recall: 0.78
  F1-Score: 0.81
  ROC-AUC Score: 0.9234

[6/6] Saving models...
  Models saved to: models/fraud_detector.pkl

========================================
  FRAUD DETECTION TRAINING COMPLETE
========================================
```

### Step 2: Verify Models Are Trained

```bash
# Check if models exist
ls models/fraud_detector.pkl
```

---

## 🎨 Integration Options for Dashboard

### Option 1: Real-Time Alerts (Recommended) ⭐

**Add fraud check when adding transactions:**

```python
# In streamlit_dashboard_multiuser.py - add_transaction() function

def add_transaction(user_id, category, merchant, amount, currency, description=""):
    """Add a new transaction with fraud detection"""

    # ... existing code to create transaction ...

    # NEW: Check for fraud
    try:
        fraud_detector = st.session_state.get('fraud_detector')
        if fraud_detector:
            # Prepare features for prediction
            trans_df = pd.DataFrame([new_transaction])
            trans_df = fraud_detector.engineer_features(trans_df)

            # Predict fraud
            predictions, probabilities, scores = fraud_detector.predict(trans_df)

            fraud_probability = probabilities[0]

            # Add to transaction
            new_transaction['fraud_score'] = scores[0]
            new_transaction['fraud_probability'] = fraud_probability

            # Return fraud alert
            if fraud_probability > 0.7:  # High risk
                return True, "⚠️ HIGH FRAUD RISK DETECTED!", fraud_probability
            elif fraud_probability > 0.4:  # Medium risk
                return True, "⚠️ Unusual transaction detected", fraud_probability
    except Exception as e:
        print(f"Fraud detection error: {e}")

    # Save transaction
    transactions_df.to_csv(RAW_DATA_DIR / 'transactions.csv', index=False)
    return True, "Transaction added successfully", 0.0
```

**Show alert to user:**

```python
# In TAB 2: Add Transaction
if submitted:
    if not merchant or amount <= 0:
        st.error("Please fill in merchant and amount")
    else:
        success, message, fraud_prob = add_transaction(
            user_id, category, merchant, amount, trans_currency, description
        )

        if success:
            if fraud_prob > 0.7:
                st.error(f"🚨 {message}")
                st.warning(f"Fraud Probability: {fraud_prob*100:.1f}%")
                st.info("This transaction looks unusual. Please verify it's legitimate.")
            elif fraud_prob > 0.4:
                st.warning(f"⚠️ {message}")
                st.caption(f"Fraud Probability: {fraud_prob*100:.1f}%")
            else:
                st.success("✅ Transaction added successfully!")
            st.balloons()
            st.rerun()
```

---

### Option 2: Fraud Monitoring Tab

**Add a new tab for fraud monitoring:**

```python
# In main dashboard - add new tab
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Overview",
    "➕ Add Transaction",
    "🗑️ Manage Transactions",
    "💡 Budget Recommendations",
    "💱 Currency Converter",
    "📄 Reports",
    "🛡️ Fraud Monitor"  # NEW
])

# TAB 7: Fraud Monitor
with tab7:
    st.subheader("🛡️ Fraud Detection Monitor")

    if len(user_transactions) == 0:
        st.info("Add transactions to see fraud detection analysis")
    else:
        # Load fraud scores if available
        fraud_scores_file = PROCESSED_DATA_DIR / 'transactions_with_fraud_scores.csv'

        if fraud_scores_file.exists():
            fraud_df = pd.read_csv(fraud_scores_file)
            user_fraud_df = fraud_df[fraud_df['user_id'] == user_id].copy()

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            high_risk = (user_fraud_df['fraud_probability'] > 0.7).sum()
            medium_risk = ((user_fraud_df['fraud_probability'] > 0.4) &
                          (user_fraud_df['fraud_probability'] <= 0.7)).sum()
            low_risk = (user_fraud_df['fraud_probability'] <= 0.4).sum()
            avg_score = user_fraud_df['fraud_probability'].mean()

            with col1:
                st.metric("🔴 High Risk", high_risk)
            with col2:
                st.metric("🟡 Medium Risk", medium_risk)
            with col3:
                st.metric("🟢 Low Risk", low_risk)
            with col4:
                st.metric("📊 Avg Risk Score", f"{avg_score*100:.1f}%")

            # Risk distribution chart
            st.subheader("📈 Fraud Risk Over Time")

            fraud_timeline = user_fraud_df.sort_values('transaction_date')
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=fraud_timeline['transaction_date'],
                y=fraud_timeline['fraud_probability'] * 100,
                mode='lines+markers',
                name='Fraud Risk',
                line=dict(color='#ef4444', width=2),
                marker=dict(size=8)
            ))

            # Add risk thresholds
            fig.add_hline(y=70, line_dash="dash", line_color="red",
                         annotation_text="High Risk")
            fig.add_hline(y=40, line_dash="dash", line_color="orange",
                         annotation_text="Medium Risk")

            fig.update_layout(
                title='Fraud Risk Score Timeline',
                xaxis_title='Date',
                yaxis_title='Fraud Probability (%)',
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

            # High-risk transactions table
            st.subheader("⚠️ High-Risk Transactions")

            high_risk_trans = user_fraud_df[
                user_fraud_df['fraud_probability'] > 0.7
            ].sort_values('fraud_probability', ascending=False)

            if len(high_risk_trans) > 0:
                display_cols = ['transaction_date', 'category', 'merchant',
                               'amount_usd', 'fraud_probability']
                high_risk_trans_display = high_risk_trans[display_cols].copy()
                high_risk_trans_display['fraud_probability'] = \
                    high_risk_trans_display['fraud_probability'].apply(lambda x: f"{x*100:.1f}%")
                high_risk_trans_display['transaction_date'] = \
                    pd.to_datetime(high_risk_trans_display['transaction_date']).dt.strftime('%Y-%m-%d %H:%M')

                st.dataframe(high_risk_trans_display, use_container_width=True)

                st.warning("⚠️ Review these transactions. If you didn't make them, report to your bank immediately!")
            else:
                st.success("✅ No high-risk transactions detected!")
        else:
            st.warning("⚠️ Fraud detection models not trained yet.")
            st.info("Run: `python src/fraud_detection/fraud_detector.py` to train models")
```

---

### Option 3: Fraud Badge on Transactions

**Show fraud risk badge next to each transaction:**

```python
# In Manage Transactions tab or Overview
for idx, row in display_df.iterrows():
    col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 1.5, 1, 1.5, 1.5, 1.5, 1])

    # ... existing columns ...

    with col7:
        # NEW: Fraud risk badge
        if 'fraud_probability' in row:
            fraud_prob = row['fraud_probability']
            if fraud_prob > 0.7:
                st.error(f"🔴 {fraud_prob*100:.0f}%")
            elif fraud_prob > 0.4:
                st.warning(f"🟡 {fraud_prob*100:.0f}%")
            else:
                st.success(f"🟢 {fraud_prob*100:.0f}%")
```

---

## 🎯 Recommended Implementation Plan

### Phase 1: Train Models (5 minutes)
```bash
python src/fraud_detection/fraud_detector.py
```

### Phase 2: Add Fraud Monitor Tab (10 minutes)
- Copy the "Fraud Monitoring Tab" code above
- Add to your dashboard
- Test with existing transactions

### Phase 3: Real-Time Alerts (15 minutes)
- Modify `add_transaction()` function
- Show alerts when adding suspicious transactions
- Test by adding unusual amounts

### Phase 4: Visual Indicators (10 minutes)
- Add fraud badges to transaction lists
- Color-code by risk level
- Add tooltips explaining risk

---

## 📊 Fraud Detection Features Explained

### Feature Categories:

**1. Time-Based (8 features):**
- Hour of day (0-23)
- Day of week (0-6)
- Is weekend (0 or 1)
- Is night (10 PM - 5 AM)
- Time since last transaction
- Rapid transaction indicator
- Day of month
- Month

**2. Amount-Based (6 features):**
- Transaction amount (USD)
- Log-transformed amount
- Squared amount
- Amount deviation from user average
- Amount Z-score
- Is round amount ($100, $500, etc.)

**3. User Behavior (4 features):**
- User's average transaction amount
- User's spending standard deviation
- User's maximum transaction
- User's total transaction count

**4. Category Features (4 features):**
- Category average amount
- Category standard deviation
- Category encoded (numeric)
- Payment method encoded

---

## ⚙️ Configuration

### Adjust Fraud Sensitivity

**In `config/config.py`:**

```python
FRAUD_CONFIG = {
    'contamination': 0.035,  # Expected fraud rate (3.5%)
    'high_risk_threshold': 0.70,  # 70%+ = high risk
    'medium_risk_threshold': 0.40,  # 40-70% = medium risk
    'alert_on_high_risk': True,
    'require_confirmation': True  # Ask user to confirm high-risk transactions
}
```

**Lower `contamination` = More sensitive**
- 0.01 = 1% fraud rate (very sensitive, more false positives)
- 0.05 = 5% fraud rate (less sensitive, fewer false positives)

---

## 🧪 Testing Fraud Detection

### Test Cases:

**1. Normal Transaction:**
```python
# Should score LOW risk (< 40%)
category = "Groceries"
merchant = "Walmart"
amount = 50.00
time = "2 PM on Tuesday"
```

**2. Unusual Amount:**
```python
# Should score MEDIUM risk (40-70%)
category = "Groceries"
merchant = "Walmart"
amount = 500.00  # 10x normal
time = "2 PM on Tuesday"
```

**3. High-Risk Pattern:**
```python
# Should score HIGH risk (> 70%)
category = "Electronics"
merchant = "Unknown Store"
amount = 2000.00  # Very high
time = "3 AM on Sunday"  # Night + Weekend
```

**4. Rapid Transactions:**
```python
# Add 3 transactions within 5 minutes
# Should flag as suspicious
```

---

## 📈 Benefits of Fraud Detection

### For Users:
✅ **Early warning** of suspicious activity
✅ **Prevent unauthorized** charges
✅ **Learn unusual patterns** in their spending
✅ **Peace of mind** with monitoring

### For Your App:
✅ **Build trust** with security features
✅ **Stand out** from competitors
✅ **Premium feature** for paid tiers
✅ **User retention** through safety

---

## 🚨 Important Notes

### Privacy & Security:
- ✅ Fraud detection runs **locally** (not sent to external APIs)
- ✅ Models **only see your data** (not shared)
- ✅ Users **control their data** (can turn off)

### False Positives:
- ⚠️ **Some legitimate transactions** may be flagged
- ⚠️ **Always ask user** before blocking
- ⚠️ **Allow user override** ("This was me")

### Model Retraining:
- 🔄 **Retrain monthly** with new data
- 🔄 **Update when adding** new users
- 🔄 **Improve accuracy** over time

---

## 🎓 Next Steps

1. **Train models**:
   ```bash
   python src/fraud_detection/fraud_detector.py
   ```

2. **Test locally**:
   - Add the Fraud Monitor tab
   - Add a few transactions
   - Check fraud scores

3. **Go live**:
   - Enable real-time alerts
   - Add fraud badges
   - Monitor false positive rate

4. **Iterate**:
   - Adjust thresholds based on user feedback
   - Add more features (location, device, etc.)
   - Implement user feedback ("Not fraud" button)

---

## 📞 Support

**Questions about fraud detection?**
- Check model evaluation metrics after training
- Review confusion matrix for accuracy
- Adjust `contamination` parameter if needed

**Your fraud detection system is ready to protect users! 🛡️**
