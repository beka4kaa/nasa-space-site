"""
Test KOI API with the real dataset from datasets/koi.csv
"""

import requests
import pandas as pd
import json
import sys
import time

BASE_URL = "http://localhost:8000"
DATASET_PATH = "datasets/koi.csv"

def wait_for_server(max_attempts=10):
    """Wait for server to be ready"""
    print("Checking if server is ready...")
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/ping", timeout=2)
            if response.status_code == 200:
                print("✓ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            print(f"  Waiting for server... (attempt {i+1}/{max_attempts})")
            time.sleep(2)
    return False

def test_model_info():
    """Test model info endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Model Info")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/koi/model-info")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Model Type: {data.get('model_type')}")
            print(f"✓ Classes: {data.get('classes')}")
            print(f"✓ Number of required features: {len(data.get('required_features', []))}")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def test_validate_dataset():
    """Test dataset validation with real data"""
    print("\n" + "="*60)
    print("TEST 2: Validate Real KOI Dataset")
    print("="*60)
    
    try:
        # Read the dataset
        print(f"Loading dataset from: {DATASET_PATH}")
        df = pd.read_csv(DATASET_PATH, comment='#')
        print(f"✓ Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Save a small sample for testing
        sample = df.head(10)
        sample_path = '/tmp/koi_sample.csv'
        sample.to_csv(sample_path, index=False)
        print(f"✓ Created sample with {len(sample)} rows")
        
        # Validate the sample
        with open(sample_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/koi/validate-dataset",
                files={'file': ('koi_sample.csv', f, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Valid: {data.get('valid')}")
            print(f"✓ Total rows: {data.get('total_rows')}")
            print(f"✓ Total columns: {data.get('total_columns')}")
            print(f"✓ Numeric columns: {data.get('numeric_columns')}")
            
            if data.get('missing_required_features'):
                print(f"⚠ Missing features: {data.get('missing_required_features')}")
            
            print(f"✓ Message: {data.get('message')}")
            return True, sample_path
        else:
            print(f"✗ Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False, None

def test_predict_sample(sample_path):
    """Test prediction on real data sample"""
    print("\n" + "="*60)
    print("TEST 3: Predict on Real KOI Sample")
    print("="*60)
    
    try:
        with open(sample_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/koi/predict",
                files={'file': ('koi_sample.csv', f, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                predictions = data.get('data', {})
                print(f"✓ Message: {data.get('message')}")
                print(f"✓ Total samples predicted: {predictions.get('total_samples')}")
                
                print("\n📊 Prediction Summary:")
                summary = predictions.get('summary', {})
                for class_name, count in summary.items():
                    print(f"  • {class_name}: {count}")
                
                print("\n🔍 Sample Predictions (first 5):")
                for pred in predictions.get('predictions', [])[:5]:
                    idx = pred.get('index')
                    prediction = pred.get('prediction')
                    confidence = pred.get('confidence', 0) * 100
                    print(f"  [{idx}] {prediction} (confidence: {confidence:.1f}%)")
                    
                    probs = pred.get('probabilities', {})
                    print(f"      - CANDIDATE: {probs.get('CANDIDATE', 0)*100:.1f}%")
                    print(f"      - CONFIRMED: {probs.get('CONFIRMED', 0)*100:.1f}%")
                    print(f"      - FALSE_POSITIVE: {probs.get('FALSE_POSITIVE', 0)*100:.1f}%")
                
                return True
            else:
                print(f"✗ Error: {data}")
                return False
        else:
            print(f"✗ Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_predict_larger_sample():
    """Test prediction on a larger sample"""
    print("\n" + "="*60)
    print("TEST 4: Predict on Larger Sample (100 rows)")
    print("="*60)
    
    try:
        df = pd.read_csv(DATASET_PATH, comment='#')
        large_sample = df.head(100)
        large_sample_path = '/tmp/koi_large_sample.csv'
        large_sample.to_csv(large_sample_path, index=False)
        print(f"✓ Created sample with {len(large_sample)} rows")
        
        with open(large_sample_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/koi/predict",
                files={'file': ('koi_large_sample.csv', f, 'text/csv')}
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                predictions = data.get('data', {})
                print(f"✓ Message: {data.get('message')}")
                print(f"✓ Total samples predicted: {predictions.get('total_samples')}")
                
                print("\n📊 Prediction Summary:")
                summary = predictions.get('summary', {})
                total = sum(summary.values())
                for class_name, count in summary.items():
                    percentage = (count / total * 100) if total > 0 else 0
                    print(f"  • {class_name}: {count} ({percentage:.1f}%)")
                
                return True
            else:
                print(f"✗ Error: {data}")
                return False
        else:
            print(f"✗ Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def compare_with_actual_labels():
    """Compare predictions with actual labels from dataset"""
    print("\n" + "="*60)
    print("TEST 5: Compare Predictions with Actual Labels")
    print("="*60)
    
    try:
        df = pd.read_csv(DATASET_PATH, comment='#')
        sample = df.head(20)
        
        # Save actual labels
        actual_labels = sample['koi_disposition'].tolist() if 'koi_disposition' in sample.columns else []
        
        sample_path = '/tmp/koi_comparison.csv'
        sample.to_csv(sample_path, index=False)
        
        with open(sample_path, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/api/koi/predict",
                files={'file': ('koi_comparison.csv', f, 'text/csv')}
            )
        
        if response.status_code == 200:
            data = response.json()
            predictions = data.get('data', {}).get('predictions', [])
            
            print(f"✓ Comparing {len(predictions)} predictions with actual labels\n")
            
            matches = 0
            for i, (pred, actual) in enumerate(zip(predictions, actual_labels)):
                predicted_label = pred.get('prediction')
                confidence = pred.get('confidence', 0) * 100
                
                match = "✓" if predicted_label == actual else "✗"
                if predicted_label == actual:
                    matches += 1
                
                print(f"{match} [{i}] Predicted: {predicted_label:15} | Actual: {actual:15} | Confidence: {confidence:.1f}%")
            
            accuracy = (matches / len(actual_labels) * 100) if actual_labels else 0
            print(f"\n📊 Accuracy on sample: {matches}/{len(actual_labels)} ({accuracy:.1f}%)")
            
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("KOI Model API - Real Dataset Testing")
    print("="*60)
    print(f"Dataset: {DATASET_PATH}")
    print(f"Server: {BASE_URL}")
    print("="*60)
    
    # Check if server is ready
    if not wait_for_server():
        print("\n✗ Server is not responding. Please start the server with:")
        print("  uvicorn main:app --reload")
        sys.exit(1)
    
    results = {}
    
    # Run tests
    results['Model Info'] = test_model_info()
    
    valid, sample_path = test_validate_dataset()
    results['Validate Dataset'] = valid
    
    if valid and sample_path:
        results['Predict Sample'] = test_predict_sample(sample_path)
        results['Predict Larger Sample'] = test_predict_larger_sample()
        results['Compare with Labels'] = compare_with_actual_labels()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! API is working correctly with real data!")
        return 0
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
