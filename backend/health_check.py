#!/usr/bin/env python3
"""
Health check script for NASA KOI Portal API
Performs comprehensive system and API testing
"""

import requests
import time
import sys
import os
from pathlib import Path

def check_server_health(base_url="http://localhost:8001", timeout=30):
    """Check if the server is running and healthy"""
    print("🏥 Health Check - NASA KOI Portal API")
    print("=" * 40)
    
    # Wait for server to start
    print(f"⏳ Waiting for server at {base_url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/ping", timeout=5)
            if response.status_code == 200:
                print("✅ Server is responding!")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    else:
        print("❌ Server failed to start within timeout")
        return False
    
    # Test endpoints
    tests = [
        ("Ping", "/ping"),
        ("Root", "/"),
        ("Model Info", "/api/kepler/model-info")
    ]
    
    all_passed = True
    for test_name, endpoint in tests:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {test_name}: OK")
            else:
                print(f"❌ {test_name}: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name}: Error - {e}")
            all_passed = False
    
    # Test file upload if test file exists
    test_file = Path("uploads/NewKepler (8) (1).xls")
    if test_file.exists():
        try:
            with open(test_file, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{base_url}/api/kepler/validate-dataset", files=files, timeout=30)
            if response.status_code == 200:
                print("✅ File Upload/Validation: OK")
            else:
                print(f"❌ File Upload/Validation: HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ File Upload/Validation: Error - {e}")
            all_passed = False
    else:
        print("⚠️  Test file not found, skipping upload test")
    
    if all_passed:
        print("\n🎉 All health checks passed!")
        print(f"🌐 API is ready at: {base_url}")
        print(f"📚 Documentation: {base_url}/docs")
        return True
    else:
        print("\n❌ Some health checks failed")
        return False

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8001"
    success = check_server_health(base_url)
    sys.exit(0 if success else 1)