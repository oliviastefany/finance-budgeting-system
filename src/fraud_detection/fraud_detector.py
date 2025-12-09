"""
Fraud Detection Module
Uses PyOD (IsolationForest and AutoEncoder) for anomaly detection
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from pyod.models.iforest import IForest
from pyod.models.auto_encoder import AutoEncoder
import joblib
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_PATHS, FRAUD_CONFIG


class FraudDetector:
    def __init__(self):
        self.iforest_model = None
        self.autoencoder_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []

    def load_data(self):
        """Load transaction data"""
        print("\n[1/6] Loading transaction data...")
        transactions_path = RAW_DATA_DIR / 'transactions.csv'
        df = pd.read_csv(transactions_path)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        print(f"  Loaded {len(df)} transactions")
        return df

    def engineer_features(self, df):
        """Create features for fraud detection"""
        print("\n[2/6] Engineering features for fraud detection...")

        # Time-based features
        df['hour'] = pd.to_datetime(df['transaction_date']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['transaction_date']).dt.dayofweek
        df['day_of_month'] = pd.to_datetime(df['transaction_date']).dt.day
        df['month'] = pd.to_datetime(df['transaction_date']).dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(int)

        # Amount-based features (using USD equivalent for consistency)
        df['amount_log'] = np.log1p(df['amount_usd'])
        df['amount_squared'] = df['amount_usd'] ** 2

        # User-level aggregations
        user_stats = df.groupby('user_id')['amount_usd'].agg([
            ('user_mean_amount', 'mean'),
            ('user_std_amount', 'std'),
            ('user_max_amount', 'max'),
            ('user_transaction_count', 'count')
        ]).reset_index()
        df = df.merge(user_stats, on='user_id', how='left')

        # Deviation from user's normal behavior
        df['amount_deviation'] = np.abs(df['amount_usd'] - df['user_mean_amount'])
        df['amount_zscore'] = (df['amount_usd'] - df['user_mean_amount']) / (df['user_std_amount'] + 1e-5)

        # Category-based features
        category_stats = df.groupby('category')['amount_usd'].agg([
            ('category_mean_amount', 'mean'),
            ('category_std_amount', 'std')
        ]).reset_index()
        df = df.merge(category_stats, on='category', how='left')

        # Encode categorical variables
        categorical_cols = ['category', 'payment_method', 'currency']
        for col in categorical_cols:
            le = LabelEncoder()
            df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le

        # Transaction velocity (transactions per hour per user)
        df = df.sort_values(['user_id', 'transaction_date'])
        df['time_diff_seconds'] = df.groupby('user_id')['transaction_date'].diff().dt.total_seconds()
        df['time_diff_seconds'] = df['time_diff_seconds'].fillna(86400)  # 24 hours default
        df['is_rapid_transaction'] = (df['time_diff_seconds'] < 300).astype(int)  # Less than 5 minutes

        # Round amount detection (potential fraud indicator)
        df['is_round_amount'] = ((df['amount_usd'] % 100 == 0) & (df['amount_usd'] > 0)).astype(int)

        print(f"  Created {len(df.columns)} total features")

        return df

    def prepare_features(self, df):
        """Select and prepare features for modeling"""
        print("\n[3/6] Preparing feature matrix...")

        # Select features for modeling
        self.feature_columns = [
            'amount_usd', 'amount_log', 'amount_squared',
            'hour', 'day_of_week', 'day_of_month', 'month',
            'is_weekend', 'is_night',
            'user_mean_amount', 'user_std_amount', 'user_max_amount',
            'user_transaction_count',
            'amount_deviation', 'amount_zscore',
            'category_mean_amount', 'category_std_amount',
            'category_encoded', 'payment_method_encoded', 'currency_encoded',
            'time_diff_seconds', 'is_rapid_transaction', 'is_round_amount'
        ]

        X = df[self.feature_columns].copy()
        X = X.fillna(0)  # Handle any remaining NaNs
        y = df['is_fraud'].values

        print(f"  Feature matrix shape: {X.shape}")
        print(f"  Fraud rate: {y.mean()*100:.2f}%")

        return X, y

    def train_models(self, X, y):
        """Train both IsolationForest and AutoEncoder models"""
        print("\n[4/6] Training anomaly detection models...")

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Split data (we'll use all data for training anomaly detectors, but keep test set for evaluation)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )

        # 1. Isolation Forest
        print("\n  Training Isolation Forest...")
        self.iforest_model = IForest(
            contamination=FRAUD_CONFIG['contamination'],
            random_state=42,
            n_estimators=100,
            max_features=1.0
        )
        self.iforest_model.fit(X_train)

        # 2. AutoEncoder
        print("  Training AutoEncoder...")
        self.autoencoder_model = AutoEncoder(
            contamination=FRAUD_CONFIG['contamination']
        )
        self.autoencoder_model.fit(X_train)

        print("  Models trained successfully!")

        return X_train, X_test, y_train, y_test, X_scaled

    def evaluate_models(self, X_test, y_test):
        """Evaluate model performance"""
        print("\n[5/6] Evaluating models...")

        from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

        # Isolation Forest predictions
        iforest_pred = self.iforest_model.predict(X_test)
        iforest_scores = self.iforest_model.decision_function(X_test)

        # AutoEncoder predictions
        ae_pred = self.autoencoder_model.predict(X_test)
        ae_scores = self.autoencoder_model.decision_function(X_test)

        # Ensemble: Average of both models' scores
        ensemble_scores = (iforest_scores + ae_scores) / 2
        ensemble_pred = (ensemble_scores > 0).astype(int)

        print("\n  === Isolation Forest Results ===")
        print(classification_report(y_test, iforest_pred, target_names=['Normal', 'Fraud']))
        print(f"  ROC-AUC Score: {roc_auc_score(y_test, iforest_scores):.4f}")

        print("\n  === AutoEncoder Results ===")
        print(classification_report(y_test, ae_pred, target_names=['Normal', 'Fraud']))
        print(f"  ROC-AUC Score: {roc_auc_score(y_test, ae_scores):.4f}")

        print("\n  === Ensemble Results ===")
        print(classification_report(y_test, ensemble_pred, target_names=['Normal', 'Fraud']))
        print(f"  ROC-AUC Score: {roc_auc_score(y_test, ensemble_scores):.4f}")

        # Confusion Matrix for Ensemble
        cm = confusion_matrix(y_test, ensemble_pred)
        print(f"\n  Confusion Matrix (Ensemble):")
        print(f"    True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
        print(f"    False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")

        return {
            'iforest_scores': iforest_scores,
            'ae_scores': ae_scores,
            'ensemble_scores': ensemble_scores
        }

    def predict(self, X):
        """Predict fraud scores for new transactions"""
        X_scaled = self.scaler.transform(X[self.feature_columns])

        # Get scores from both models
        iforest_scores = self.iforest_model.decision_function(X_scaled)
        ae_scores = self.autoencoder_model.decision_function(X_scaled)

        # Ensemble score
        ensemble_scores = (iforest_scores + ae_scores) / 2

        # Predictions (1 = fraud, 0 = normal)
        predictions = (ensemble_scores > 0).astype(int)

        # Normalize scores to 0-1 range (fraud probability)
        fraud_probability = 1 / (1 + np.exp(-ensemble_scores))

        return predictions, fraud_probability, ensemble_scores

    def save_models(self):
        """Save trained models"""
        print("\n[6/6] Saving models...")

        model_data = {
            'iforest_model': self.iforest_model,
            'autoencoder_model': self.autoencoder_model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns
        }

        joblib.dump(model_data, MODEL_PATHS['fraud_detector'])
        print(f"  Models saved to: {MODEL_PATHS['fraud_detector']}")

    def load_models(self):
        """Load trained models"""
        model_data = joblib.load(MODEL_PATHS['fraud_detector'])
        self.iforest_model = model_data['iforest_model']
        self.autoencoder_model = model_data['autoencoder_model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        print(f"Models loaded from: {MODEL_PATHS['fraud_detector']}")

    def train_and_save(self):
        """Complete training pipeline"""
        print("\n" + "="*60)
        print("  FRAUD DETECTION MODEL TRAINING")
        print("="*60)

        # Load and prepare data
        df = self.load_data()
        df = self.engineer_features(df)
        X, y = self.prepare_features(df)

        # Train models
        X_train, X_test, y_train, y_test, X_scaled = self.train_models(X, y)

        # Evaluate
        scores = self.evaluate_models(X_test, y_test)

        # Save models
        self.save_models()

        # Save processed data with fraud scores
        print("\nSaving processed data with fraud scores...")
        df_processed = df.copy()
        predictions, probabilities, ensemble_scores = self.predict(df)
        df_processed['fraud_score'] = ensemble_scores
        df_processed['fraud_probability'] = probabilities
        df_processed['fraud_prediction'] = predictions

        processed_path = PROCESSED_DATA_DIR / 'transactions_with_fraud_scores.csv'
        df_processed.to_csv(processed_path, index=False)
        print(f"  Processed data saved to: {processed_path}")

        print("\n" + "="*60)
        print("  FRAUD DETECTION TRAINING COMPLETE")
        print("="*60 + "\n")

        return df_processed


if __name__ == "__main__":
    detector = FraudDetector()
    df_processed = detector.train_and_save()
