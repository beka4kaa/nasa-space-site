"""
Model utilities for KOI dataset prediction
Handles model loading, data preprocessing, and predictions
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.base import BaseEstimator, TransformerMixin
import os
import pickle

class AdvancedFeatureEngineer(BaseEstimator, TransformerMixin):
    """Custom transformer for advanced feature engineering"""
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        df = X.copy()
        
        # Calculate stellar density
        df['stellar_density'] = 10**df['koi_slogg']
        
        # Calculate planet to star radius ratio
        df['prad_srad_ratio'] = df['koi_prad'] / df['koi_srad']
        
        # Calculate semi-major axis to stellar radius ratio
        G = 6.67430e-11  # Gravitational constant
        period_sec = df['koi_period'] * 86400  # Convert days to seconds
        mass_star = (10**df['koi_slogg'] * (df['koi_srad'] * 6.957e+8)**2) / G
        radius_star_m = df['koi_srad'] * 6.957e+8
        df['a_div_Rs'] = ((G * mass_star * period_sec**2) / (4 * np.pi**2))**(1/3) / radius_star_m
        
        # Drop original columns used for feature engineering
        return df.drop(columns=['koi_slogg', 'koi_srad', 'koi_period'], errors='ignore')


class KOIModelPredictor:
    """Handles KOI model predictions with preprocessing pipeline"""
    
    def __init__(self, model_path='models/boost_test_model.json'):
        self.model_path = model_path
        self.model = None
        self.imputer = None
        self.scaler = None
        self.feature_engineer = None
        self.encoder = None
        self.feature_columns = None
        self.is_fitted = False
        self.label_mapping = {
            0: 'CANDIDATE',
            1: 'CONFIRMED',
            2: 'FALSE POSITIVE'
        }
        
    def load_model(self):
        """Load the trained XGBoost model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        
        # Load model with feature validation disabled
        self.model = xgb.XGBClassifier()
        self.model.load_model(self.model_path)
        # Disable feature name validation
        self.model.get_booster().feature_names = None
        
        # Initialize preprocessing components
        self.imputer = IterativeImputer(max_iter=10, random_state=4)
        self.scaler = StandardScaler()
        self.feature_engineer = AdvancedFeatureEngineer()
        self.encoder = OrdinalEncoder()
        
        return True
    
    def preprocess_data(self, df, fit=False):
        """
        Preprocess the input dataframe using the same pipeline as training
        
        Args:
            df: Input dataframe
            fit: Whether to fit the preprocessors (True for training, False for prediction)
        
        Returns:
            Preprocessed numpy array
        """
        # 1. Select only numeric columns
        X_numeric = df.select_dtypes(include=np.number)
        
        # 2. Remove ID columns
        del_cols = ['kepid', 'rowid']
        X_temp = X_numeric.drop(columns=del_cols, errors='ignore')
        
        # 3. Remove columns that are completely NaN
        X_clean = X_temp.dropna(axis=1, how='all')
        
        # Auto-fit on first use if not fitted
        if not self.is_fitted and not fit:
            fit = True
        
        if fit:
            # Store the feature columns for later use
            self.feature_columns = X_clean.columns.tolist()
            self.is_fitted = True
        else:
            # Ensure we have the same columns as training
            if self.feature_columns:
                # Add missing columns with NaN
                for col in self.feature_columns:
                    if col not in X_clean.columns:
                        X_clean[col] = np.nan
                # Keep only training columns in the same order
                X_clean = X_clean[self.feature_columns]
        
        # 4. Impute missing values
        if fit:
            X_imputed = pd.DataFrame(
                self.imputer.fit_transform(X_clean),
                columns=X_clean.columns
            )
        else:
            X_imputed = pd.DataFrame(
                self.imputer.transform(X_clean),
                columns=X_clean.columns
            )
        
        # 5. Feature engineering
        if fit:
            X_featured = self.feature_engineer.fit_transform(X_imputed)
        else:
            X_featured = self.feature_engineer.transform(X_imputed)
        
        # 6. Scale features
        # Convert to numpy to avoid feature name issues
        X_featured_array = X_featured.values if isinstance(X_featured, pd.DataFrame) else X_featured
        
        if fit:
            X_scaled = self.scaler.fit_transform(X_featured_array)
        else:
            X_scaled = self.scaler.transform(X_featured_array)
        
        return X_scaled
    
    def predict(self, df):
        """
        Make predictions on the input dataframe
        
        Args:
            df: Input dataframe with KOI features
        
        Returns:
            Dictionary with predictions and probabilities
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Preprocess the data
        X_processed = self.preprocess_data(df, fit=False)
        
        # Make predictions
        predictions = self.model.predict(X_processed)
        probabilities = self.model.predict_proba(X_processed)
        
        # Convert predictions to labels
        labels = [self.label_mapping.get(int(pred), 'UNKNOWN') for pred in predictions]
        
        # Create result dictionary
        results = []
        for idx, (label, pred, probs) in enumerate(zip(labels, predictions, probabilities)):
            result = {
                'index': idx,
                'prediction': label,
                'prediction_code': int(pred),
                'confidence': float(max(probs)),
                'probabilities': {
                    'CANDIDATE': float(probs[0]),
                    'CONFIRMED': float(probs[1]),
                    'FALSE_POSITIVE': float(probs[2])
                }
            }
            results.append(result)
        
        return {
            'predictions': results,
            'total_samples': len(results),
            'summary': {
                'CANDIDATE': sum(1 for r in results if r['prediction'] == 'CANDIDATE'),
                'CONFIRMED': sum(1 for r in results if r['prediction'] == 'CONFIRMED'),
                'FALSE_POSITIVE': sum(1 for r in results if r['prediction'] == 'FALSE POSITIVE')
            },
            'original_data': df.to_dict('records')  # Include original data for analytics
        }
    
    def predict_single(self, features_dict):
        """
        Make prediction on a single sample
        
        Args:
            features_dict: Dictionary of feature values
        
        Returns:
            Dictionary with prediction and probabilities
        """
        df = pd.DataFrame([features_dict])
        result = self.predict(df)
        return result['predictions'][0] if result['predictions'] else None


# Global model instance
_model_instance = None

def get_model():
    """Get or create the global model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = KOIModelPredictor()
        _model_instance.load_model()
    return _model_instance
