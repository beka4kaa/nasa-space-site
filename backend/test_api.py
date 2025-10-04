"""
Test script for KOI prediction API endpoints
Run this after starting the FastAPI server
"""

import requests
import pandas as pd
import json

BASE_URL = "http://localhost:8000"

def test_ping():
    """Test basic connectivity"""
    print("\n=== Testing /ping endpoint ===")
    response = requests.get(f"{BASE_URL}/ping")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_model_info():
    """Test model info endpoint"""
    print("\n=== Testing /api/koi/model-info endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/api/koi/model-info")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Model Type: {data.get('model_type')}")
        print(f"Classes: {data.get('classes')}")
        print(f"Number of features: {len(data.get('required_features', []))}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_predict_single():
    """Test single prediction endpoint"""
    print("\n=== Testing /api/koi/predict-single endpoint ===")
    
    # Sample KOI features
    sample_features = {
        "koi_period": 9.488036,
        "koi_time0bk": 170.538750,
        "koi_impact": 0.146,
        "koi_duration": 2.95750,
        "koi_depth": 874.8,
        "koi_prad": 2.26,
        "koi_teq": 1160.0,
        "koi_insol": 136.5,
        "koi_model_snr": 35.8,
        "koi_tce_plnt_num": 1.0,
        "koi_steff": 6117.0,
        "koi_slogg": 4.467,
        "koi_srad": 1.046,
        "ra": 291.93423,
        "dec": 48.141651,
        "koi_kepmag": 15.347
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/koi/predict-single",
            json={"features": sample_features}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get('success'):
            prediction_data = data.get('data', {})
            print(f"Prediction: {prediction_data.get('prediction')}")
            print(f"Confidence: {prediction_data.get('confidence'):.2%}")
            print(f"Probabilities:")
            for class_name, prob in prediction_data.get('probabilities', {}).items():
                print(f"  {class_name}: {prob:.2%}")
        else:
            print(f"Error: {data}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_validate_dataset():
    """Test dataset validation endpoint"""
    print("\n=== Testing /api/koi/validate-dataset endpoint ===")
    
    # Create a sample CSV file
    sample_data = pd.DataFrame({
        'kepid': [10797460],
        'koi_period': [9.488036],
        'koi_srad': [1.046],
        'koi_slogg': [4.467],
        'koi_prad': [2.26],
        'koi_teq': [1160.0],
        'koi_insol': [136.5]
    })
    
    # Save to temporary file
    temp_file = '/tmp/test_koi.csv'
    sample_data.to_csv(temp_file, index=False)
    
    try:
        with open(temp_file, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/koi/validate-dataset",
                files={'file': f}
            )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Valid: {data.get('valid')}")
        print(f"Total rows: {data.get('total_rows')}")
        print(f"Total columns: {data.get('total_columns')}")
        print(f"Message: {data.get('message')}")
        
        if data.get('missing_required_features'):
            print(f"Missing features: {data.get('missing_required_features')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_predict_dataset():
    """Test dataset prediction endpoint"""
    print("\n=== Testing /api/koi/predict endpoint ===")
    
    # Create a sample CSV file with multiple rows
    sample_data = pd.DataFrame({
        'kepid': [10797460, 10811496, 10848459],
        'koi_period': [9.488036, 42.333, 20.86588],
        'koi_srad': [1.046, 1.261, 1.191],
        'koi_slogg': [4.467, 4.340, 4.395],
        'koi_prad': [2.26, 2.47, 1.30],
        'koi_teq': [1160.0, 754.0, 911.0],
        'koi_insol': [136.5, 20.5, 52.0],
        'koi_model_snr': [35.8, 18.3, 12.5],
        'koi_steff': [6117.0, 5904.0, 5933.0],
        'ra': [291.93423, 297.00482, 298.31531],
        'dec': [48.141651, 46.997200, 47.145142],
        'koi_kepmag': [15.347, 15.436, 15.597]
    })
    
    # Save to temporary file
    temp_file = '/tmp/test_koi_dataset.csv'
    sample_data.to_csv(temp_file, index=False)
    
    try:
        with open(temp_file, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/koi/predict",
                files={'file': f}
            )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if data.get('success'):
            predictions = data.get('data', {})
            print(f"Message: {data.get('message')}")
            print(f"Total samples: {predictions.get('total_samples')}")
            print(f"\nSummary:")
            for class_name, count in predictions.get('summary', {}).items():
                print(f"  {class_name}: {count}")
            
            print(f"\nFirst prediction:")
            first_pred = predictions.get('predictions', [])[0]
            print(f"  Prediction: {first_pred.get('prediction')}")
            print(f"  Confidence: {first_pred.get('confidence'):.2%}")
        else:
            print(f"Error: {data}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("KOI Model API Test Suite")
    print("=" * 60)
    
    tests = [
        ("Ping", test_ping),
        ("Model Info", test_model_info),
        ("Single Prediction", test_predict_single),
        ("Validate Dataset", test_validate_dataset),
        ("Predict Dataset", test_predict_dataset)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\nTest '{name}' failed with exception: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    return total_passed == total_tests

if __name__ == "__main__":
    print("\nMake sure the FastAPI server is running on http://localhost:8000")
    print("Start it with: uvicorn main:app --reload\n")
    
    input("Press Enter to start tests...")
    
    success = run_all_tests()
    exit(0 if success else 1)
