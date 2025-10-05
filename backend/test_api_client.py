#!/usr/bin/env python3
"""
API Test Script for NASA KOI Backend
Tests the model prediction functionality
"""

import requests
import json
import time

# API endpoint
BASE_URL = "http://localhost:8001"

def test_api():
    print("🧪 NASA KOI API TEST")
    print("=" * 40)
    
    # Sample exoplanet data (Earth-like) - with all required features
    sample_data = {
        "features": {
            "koi_period": 365.25,      # Earth orbital period
            "koi_time0bk": 131.5,      # Transit epoch
            "koi_impact": 0.5,         # Impact parameter
            "koi_duration": 6.0,       # Transit duration
            "koi_depth": 1000.0,       # Transit depth
            "koi_prad": 1.0,           # Planet radius (Earth radii)
            "koi_teq": 288.0,          # Equilibrium temperature
            "koi_insol": 1.0,          # Insolation flux
            "koi_model_snr": 20.0,     # Signal-to-noise ratio
            "koi_steff": 5778.0,       # Stellar effective temperature
            "koi_slogg": 4.44,         # Stellar surface gravity
            "koi_srad": 1.0,           # Stellar radius
            "ra": 290.0,               # Right ascension
            "dec": 42.0,               # Declination
            "koi_kepmag": 12.0,        # Kepler magnitude
            "koi_fpflag_nt": 0,        # False positive flag - not transit-like
            "koi_fpflag_ss": 0,        # False positive flag - stellar eclipse
            "koi_fpflag_co": 0,        # False positive flag - centroid offset
            "koi_fpflag_ec": 0         # False positive flag - ephemeris match
        }
    }
    
    try:
        print("🔍 Testing API health...")
        response = requests.get(f"{BASE_URL}/ping", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy!")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return
            
        print("\n🤖 Testing model prediction...")
        response = requests.post(
            f"{BASE_URL}/api/koi/predict-single",
            json=sample_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction successful!")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
            
            # Extract key information
            if result.get('success') and 'data' in result:
                data = result['data']
                print(f"\n🎯 PREDICTION RESULTS:")
                print(f"   Disposition: {data.get('prediction', 'Unknown')}")
                print(f"   Confidence: {data.get('confidence', 0):.2%}")
                print(f"   Model Accuracy: {data.get('model_accuracy', 0):.2%}")
                print(f"   Features Used: {data.get('feature_count', 0)}")
                
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is the server running?")
    except requests.exceptions.Timeout:
        print("❌ API request timed out")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_api()