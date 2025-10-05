"""
Working model utilities for KOI dataset prediction
Uses a simple RandomForest model that works with the available data
"""

import pandas as pd
import numpy as np
import pickle
import os
from typing import Dict, List, Any

class SimpleKOIModelPredictor:
    """Simple KOI model predictor that actually works with our data"""
    
    def __init__(self, model_path='models/simple_test_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.label_mapping = None
        self.accuracy = None
        
    def load_model(self):
        """Load the simple working model"""
        if not os.path.exists(self.model_path):
            # If simple model doesn't exist, create it first
            print("Simple model not found, creating it...")
            from test_model_simple import create_and_test_simple_model
            create_and_test_simple_model()
        
        with open(self.model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.feature_names = model_data['feature_names']
        self.label_mapping = model_data['label_mapping']
        self.accuracy = model_data['accuracy']
        
        return True
    
    def preprocess_data(self, df):
        """Simple preprocessing - just select features and handle missing values"""
        # Remove non-feature columns
        feature_df = df.copy()
        
        # Remove target and ID columns if present
        columns_to_remove = ['koi_disposition', 'kepid']
        for col in columns_to_remove:
            if col in feature_df.columns:
                feature_df = feature_df.drop(columns=[col])
        
        # Ensure we have the right columns
        if self.feature_names:
            # Only keep features that were used in training
            available_features = [col for col in self.feature_names if col in feature_df.columns]
            feature_df = feature_df[available_features]
        
        # Fill missing values with median
        feature_df = feature_df.fillna(feature_df.median())
        
        return feature_df
    
    def predict(self, df):
        """Make predictions on the dataframe"""
        if self.model is None:
            self.load_model()
        
        # Preprocess data
        X = self.preprocess_data(df)
        
        # Make predictions
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        # Convert predictions to strings using label mapping
        prediction_labels = [self.label_mapping[pred] for pred in predictions]
        
        # Include original data for analytics
        original_data = df.to_dict('records')
        
        return {
            'predictions': prediction_labels,
            'probabilities': probabilities.tolist(),
            'original_data': original_data,
            'model_accuracy': self.accuracy,
            'feature_count': len(self.feature_names) if self.feature_names else 0
        }

# Global model instance
_model_instance = None

def get_model():
    """Get or create the global model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = SimpleKOIModelPredictor()
        _model_instance.load_model()
    return _model_instance

# Keep the old class for compatibility, but make it use the simple model
class KOIModelPredictor(SimpleKOIModelPredictor):
    """Alias for backward compatibility"""
    pass