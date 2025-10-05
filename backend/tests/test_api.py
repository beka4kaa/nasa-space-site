"""
Integration tests for KOI API endpoints
"""

import unittest
import sys
import os
from pathlib import Path
import requests
import time
import threading
import uvicorn
import pandas as pd
import io

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app
from fastapi.testclient import TestClient

class TestKOIAPI(unittest.TestCase):
    """Test cases for KOI API endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = TestClient(app)
        cls.base_url = "http://testserver"

    def test_ping_endpoint(self):
        """Test ping endpoint"""
        response = self.client.get("/ping")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")

    def test_model_info_endpoint(self):
        """Test model info endpoint"""
        response = self.client.get("/api/koi/model-info")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get("success", False))
        self.assertIn("model_type", data)
        self.assertIn("classes", data)

    def test_validate_dataset_endpoint(self):
        """Test dataset validation endpoint"""
        # Create sample CSV data
        sample_data = pd.DataFrame({
            'kepid': [1, 2, 3],
            'koi_period': [10.0, 20.0, 30.0],
            'koi_prad': [1.0, 2.0, 3.0],
            'koi_teq': [300, 400, 500]
        })
        
        # Convert to CSV bytes
        csv_buffer = io.StringIO()
        sample_data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        # Test file upload
        files = {"file": ("test_data.csv", csv_content, "text/csv")}
        response = self.client.post("/api/koi/validate-dataset", files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("valid", data)

    def test_predict_dataset_endpoint(self):
        """Test dataset prediction endpoint"""
        # Create sample CSV with required columns
        sample_data = pd.DataFrame({
            'kepid': [10666592, 10666593],
            'koi_period': [9.488036, 54.418383],
            'koi_time0bk': [170.538750, 162.513840],
            'koi_impact': [0.146, 0.586],
            'koi_duration': [2.95750, 4.50700],
            'koi_depth': [874.8, 492.3],
            'koi_prad': [2.26, 1.89],
            'koi_teq': [1160.0, 797.0],
            'koi_insol': [136.5, 17.9],
            'koi_model_snr': [35.8, 28.4],
            'koi_steff': [5450, 5800],
            'koi_slogg': [4.38, 4.45],
            'koi_srad': [1.02, 0.98],
            'ra': [291.93423, 292.12345],
            'dec': [48.14808, 47.98765],
            'koi_kepmag': [14.731, 13.456],
            'koi_fpflag_nt': [0, 0],
            'koi_fpflag_ss': [0, 0],
            'koi_fpflag_co': [0, 0],
            'koi_fpflag_ec': [0, 0]
        })
        
        # Convert to CSV bytes
        csv_buffer = io.StringIO()
        sample_data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        # Test prediction
        files = {"file": ("test_koi_data.csv", csv_content, "text/csv")}
        response = self.client.post("/api/koi/predict", files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success", False))
        self.assertIn("data", data)
        
        predictions_data = data["data"]
        self.assertIn("predictions", predictions_data)
        self.assertIn("probabilities", predictions_data)
        
        predictions = predictions_data["predictions"]
        probabilities = predictions_data["probabilities"]
        
        self.assertEqual(len(predictions), 2)
        self.assertEqual(len(probabilities), 2)
        
        # Check prediction format
        valid_classes = ['CANDIDATE', 'CONFIRMED', 'FALSE POSITIVE']
        for pred in predictions:
            self.assertIn(pred, valid_classes)
        
        # Check probability format
        for prob_array in probabilities:
            self.assertEqual(len(prob_array), 3)
            self.assertAlmostEqual(sum(prob_array), 1.0, places=4)

    def test_predict_single_endpoint(self):
        """Test single prediction endpoint"""
        sample_features = {
            "features": {
                "koi_period": 9.488036,
                "koi_time0bk": 170.538750,
                "koi_impact": 0.146,
                "koi_duration": 2.95750,
                "koi_depth": 874.8,
                "koi_prad": 2.26,
                "koi_teq": 1160.0,
                "koi_insol": 136.5,
                "koi_model_snr": 35.8,
                "koi_steff": 5450,
                "koi_slogg": 4.38,
                "koi_srad": 1.02,
                "ra": 291.93423,
                "dec": 48.14808,
                "koi_kepmag": 14.731,
                "koi_fpflag_nt": 0,
                "koi_fpflag_ss": 0,
                "koi_fpflag_co": 0,
                "koi_fpflag_ec": 0
            }
        }
        
        response = self.client.post("/api/koi/predict-single", json=sample_features)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get("success", False))
        self.assertIn("data", data)
        
        prediction_data = data["data"]
        self.assertIn("prediction", prediction_data)
        self.assertIn("probabilities", prediction_data)
        
        prediction = prediction_data["prediction"]
        probabilities = prediction_data["probabilities"]
        
        valid_classes = ['CANDIDATE', 'CONFIRMED', 'FALSE POSITIVE']
        self.assertIn(prediction, valid_classes)
        self.assertEqual(len(probabilities), 3)
        self.assertAlmostEqual(sum(probabilities), 1.0, places=4)

    def test_upload_download_endpoints(self):
        """Test file upload and download endpoints"""
        # Create test CSV
        test_data = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        csv_buffer = io.StringIO()
        test_data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        # Test upload
        files = {"file": ("test_upload.csv", csv_content, "text/csv")}
        response = self.client.post("/upload", files=files)
        self.assertEqual(response.status_code, 200)
        
        upload_data = response.json()
        self.assertIn("filename", upload_data)
        filename = upload_data["filename"]
        
        # Test download
        response = self.client.get(f"/download/{filename}")
        self.assertEqual(response.status_code, 200)

    def test_error_handling(self):
        """Test API error handling"""
        # Test invalid endpoint
        response = self.client.get("/invalid-endpoint")
        self.assertEqual(response.status_code, 404)
        
        # Test malformed prediction request
        response = self.client.post("/api/koi/predict-single", json={"invalid": "data"})
        self.assertEqual(response.status_code, 422)  # Validation error
        
        # Test empty file upload
        files = {"file": ("empty.csv", b"", "text/csv")}
        response = self.client.post("/api/koi/predict", files=files)
        # Should handle gracefully (either 422 or 500 is acceptable)
        self.assertIn(response.status_code, [422, 500])

class TestKOIAPILive(unittest.TestCase):
    """Test cases for live API server"""
    
    BASE_URL = "http://localhost:8002"
    
    @classmethod
    def setUpClass(cls):
        """Check if live server is available"""
        try:
            response = requests.get(f"{cls.BASE_URL}/ping", timeout=2)
            cls.server_available = response.status_code == 200
        except:
            cls.server_available = False
    
    def setUp(self):
        """Skip tests if server not available"""
        if not self.server_available:
            self.skipTest("Live server not available")
    
    def test_live_ping(self):
        """Test ping on live server"""
        response = requests.get(f"{self.BASE_URL}/ping")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
    
    def test_live_model_info(self):
        """Test model info on live server"""
        response = requests.get(f"{self.BASE_URL}/api/koi/model-info")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data.get("success", False))
        self.assertIn("model_type", data)
        
    def test_live_prediction_performance(self):
        """Test prediction performance on live server"""
        sample_features = {
            "features": {
                "koi_period": 9.488036,
                "koi_prad": 2.26,
                "koi_teq": 1160.0,
                "koi_insol": 136.5,
                "koi_model_snr": 35.8,
                "koi_steff": 5450,
                "koi_slogg": 4.38,
                "koi_srad": 1.02,
                "ra": 291.93423,
                "dec": 48.14808,
                "koi_kepmag": 14.731,
                "koi_fpflag_nt": 0,
                "koi_fpflag_ss": 0,
                "koi_fpflag_co": 0,
                "koi_fpflag_ec": 0
            }
        }
        
        # Measure response time
        start_time = time.time()
        response = requests.post(f"{self.BASE_URL}/api/koi/predict-single", json=sample_features)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 5.0, f"Response time should be < 5s, got {response_time:.2f}s")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)