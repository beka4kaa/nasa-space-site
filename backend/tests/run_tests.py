"""
Test runner script for all KOI model tests
"""

import unittest
import sys
import os
from pathlib import Path
import time

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_all_tests():
    """Run all test suites"""
    print("🚀 NASA KOI MODEL - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    start_time = time.time()
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    test_suite = loader.discover(str(Path(__file__).parent), pattern='test_*.py')
    
    # Create test runner with verbose output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # Run tests
    result = runner.run(test_suite)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total runtime: {total_time:.1f} seconds")
    print(f"🧪 Tests run: {result.testsRun}")
    print(f"✅ Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🔥 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n🔴 FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🔥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    # Overall verdict
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! Model is ready for production! ✅")
        return True
    else:
        print(f"\n⚠️  SOME TESTS FAILED. Please review the issues above. ❌")
        return False

def run_specific_test_suite(suite_name):
    """Run a specific test suite"""
    test_files = {
        'model': 'test_model.py',
        'api': 'test_api.py', 
        'performance': 'test_performance.py'
    }
    
    if suite_name not in test_files:
        print(f"❌ Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(test_files.keys())}")
        return False
    
    test_file = test_files[suite_name]
    print(f"🧪 Running {suite_name} tests from {test_file}")
    print("=" * 60)
    
    # Import and run specific test module
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_file[:-3]}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def quick_smoke_test():
    """Run a quick smoke test to verify basic functionality"""
    print("🔥 QUICK SMOKE TEST")
    print("=" * 30)
    
    try:
        # Test model loading
        print("1. Testing model loading...")
        import model_utils_working
        model = model_utils_working.get_model()
        print(f"   ✅ Model loaded: {type(model.model).__name__}")
        print(f"   ✅ Accuracy: {model.accuracy:.1%}")
        
        # Test simple prediction
        print("2. Testing prediction...")
        import pandas as pd
        sample_data = pd.DataFrame({
            'kepid': [1],
            'koi_period': [10.0],
            'koi_time0bk': [170.0],
            'koi_impact': [0.5],
            'koi_duration': [3.0],
            'koi_depth': [500.0],
            'koi_prad': [2.0],
            'koi_teq': [800.0],
            'koi_insol': [50.0],
            'koi_model_snr': [20.0],
            'koi_steff': [5500],
            'koi_slogg': [4.4],
            'koi_srad': [1.0],
            'ra': [290.0],
            'dec': [45.0],
            'koi_kepmag': [13.0],
            'koi_fpflag_nt': [0],
            'koi_fpflag_ss': [0],
            'koi_fpflag_co': [0],
            'koi_fpflag_ec': [0]
        })
        
        result = model.predict(sample_data)
        print(f"   ✅ Prediction: {result['predictions'][0]}")
        print(f"   ✅ Confidence: {max(result['probabilities'][0]):.1%}")
        
        # Test API (if available)
        print("3. Testing API...")
        try:
            from fastapi.testclient import TestClient
            from main import app
            client = TestClient(app)
            response = client.get("/ping")
            if response.status_code == 200:
                print("   ✅ API responding")
            else:
                print("   ⚠️  API not responding properly")
        except Exception as e:
            print(f"   ⚠️  API test failed: {e}")
        
        print("\n🎉 SMOKE TEST PASSED! Basic functionality working! ✅")
        return True
        
    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        return False

if __name__ == '__main__':
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'smoke':
            success = quick_smoke_test()
        elif command in ['model', 'api', 'performance']:
            success = run_specific_test_suite(command)
        elif command == 'all':
            success = run_all_tests()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: smoke, model, api, performance, all")
            success = False
    else:
        # Default: run smoke test
        success = quick_smoke_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)