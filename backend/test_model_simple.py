"""
Simple model test to verify accuracy with correct feature dimensions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from collections import Counter
import pickle

def create_and_test_simple_model():
    """Create a simple model with the correct number of features for testing"""
    
    print("=== CREATING SIMPLE TEST MODEL ===")
    
    # Load the data
    df = pd.read_csv('uploads/NewKepler (8) (1).xls')
    print(f"Dataset shape: {df.shape}")
    
    # Separate features and target
    target_col = 'koi_disposition'
    X = df.drop(columns=[target_col, 'kepid'])  # Remove target and ID
    y = df[target_col]
    
    print(f"Features shape: {X.shape}")
    print(f"Target distribution: {dict(Counter(y))}")
    
    # Handle missing values
    X_filled = X.fillna(X.median())
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_filled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
    
    # Create and train model
    print("\n=== TRAINING MODEL ===")
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    
    # Make predictions
    print("\n=== TESTING MODEL ===")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✓ ACCURACY: {accuracy:.3f}")
    
    # Detailed classification report
    print("\n=== CLASSIFICATION REPORT ===")
    label_mapping = {0: 'FALSE POSITIVE', 1: 'CANDIDATE', 2: 'CONFIRMED'}
    y_test_labels = [label_mapping[label] for label in y_test]
    y_pred_labels = [label_mapping[label] for label in y_pred]
    
    print(classification_report(y_test_labels, y_pred_labels))
    
    # Feature importance
    print("\n=== TOP 10 MOST IMPORTANT FEATURES ===")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for i, row in feature_importance.head(10).iterrows():
        print(f"{row['feature']:20s}: {row['importance']:.4f}")
    
    # Test prediction on small sample
    print("\n=== SAMPLE PREDICTIONS ===")
    sample_indices = np.random.choice(len(X_test), 5, replace=False)
    for idx in sample_indices:
        actual = label_mapping[y_test.iloc[idx]]
        predicted = label_mapping[y_pred[idx]]
        confidence = max(y_pred_proba[idx])
        print(f"Actual: {actual:15s} | Predicted: {predicted:15s} | Confidence: {confidence:.3f}")
    
    # Save the simple model for testing
    model_data = {
        'model': model,
        'feature_names': list(X.columns),
        'label_mapping': label_mapping,
        'accuracy': accuracy
    }
    
    with open('models/simple_test_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n✓ Simple model saved to models/simple_test_model.pkl")
    print(f"✓ Model accuracy: {accuracy:.3f}")
    print(f"✓ Features used: {len(X.columns)}")
    
    return model, X.columns, label_mapping, accuracy

if __name__ == "__main__":
    create_and_test_simple_model()