"""
Unit tests for KOI model functionality
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import model_utils_working

class TestKOIModel(unittest.TestCase):
    """Test cases for KOI model"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.model = model_utils_working.get_model()
        cls.sample_data = pd.DataFrame({
            'kepid': [10666592, 10666593, 10666594],
            'koi_disposition': [1, 2, 0],  # CANDIDATE, CONFIRMED, FALSE POSITIVE
            'koi_period': [9.488036, 54.418383, 123.456],
            'koi_time0bk': [170.538750, 162.513840, 180.123],
            'koi_impact': [0.146, 0.586, 0.234],
            'koi_duration': [2.95750, 4.50700, 3.456],
            'koi_depth': [874.8, 492.3, 1200.5],
            'koi_prad': [2.26, 1.89, 3.45],
            'koi_teq': [1160.0, 797.0, 650.0],
            'koi_insol': [136.5, 17.9, 8.2],
            'koi_model_snr': [35.8, 28.4, 15.6],
            'koi_steff': [5450, 5800, 6100],
            'koi_slogg': [4.38, 4.45, 4.12],
            'koi_srad': [1.02, 0.98, 1.15],
            'ra': [291.93423, 292.12345, 290.87654],
            'dec': [48.14808, 47.98765, 48.34567],
            'koi_kepmag': [14.731, 13.456, 15.234],
            'koi_fpflag_nt': [0, 0, 1],
            'koi_fpflag_ss': [0, 0, 1],
            'koi_fpflag_co': [0, 0, 1],
            'koi_fpflag_ec': [0, 0, 0]
        })
        cls.expected_classes = ['CANDIDATE', 'CONFIRMED', 'FALSE POSITIVE']
        cls.label_mapping = {0: 'FALSE POSITIVE', 1: 'CANDIDATE', 2: 'CONFIRMED'}

    def test_model_loading(self):
        """Test that model loads correctly"""
        self.assertIsNotNone(self.model)
        self.assertIsNotNone(self.model.model)
        self.assertIsNotNone(self.model.feature_names)
        self.assertIsNotNone(self.model.label_mapping)

    def test_model_accuracy(self):
        """Test model accuracy is reasonable"""
        self.assertGreater(self.model.accuracy, 0.8, "Model accuracy should be > 80%")
        self.assertLessEqual(self.model.accuracy, 1.0, "Model accuracy should be <= 100%")

    def test_feature_count(self):
        """Test that model has expected number of features"""
        self.assertGreater(len(self.model.feature_names), 10, "Should have more than 10 features")
        self.assertLess(len(self.model.feature_names), 50, "Should have less than 50 features")

    def test_prediction_on_sample_data(self):
        """Test predictions on sample data"""
        result = self.model.predict(self.sample_data)
        
        # Check result structure
        self.assertIn('predictions', result)
        self.assertIn('probabilities', result)
        self.assertIn('original_data', result)
        
        predictions = result['predictions']
        probabilities = result['probabilities']
        
        # Check predictions format
        self.assertEqual(len(predictions), 3, "Should have 3 predictions")
        for pred in predictions:
            self.assertIn(pred, self.expected_classes, f"Prediction {pred} should be valid class")
        
        # Check probabilities format
        self.assertEqual(len(probabilities), 3, "Should have 3 probability arrays")
        for prob_array in probabilities:
            self.assertEqual(len(prob_array), 3, "Each probability array should have 3 values")
            self.assertAlmostEqual(sum(prob_array), 1.0, places=5, msg="Probabilities should sum to 1")
            for prob in prob_array:
                self.assertGreaterEqual(prob, 0.0, "Probabilities should be >= 0")
                self.assertLessEqual(prob, 1.0, "Probabilities should be <= 1")

    def test_prediction_consistency(self):
        """Test that predictions are consistent"""
        result1 = self.model.predict(self.sample_data)
        result2 = self.model.predict(self.sample_data)
        
        self.assertEqual(result1['predictions'], result2['predictions'], 
                        "Predictions should be consistent")

    def test_single_sample_prediction(self):
        """Test prediction on single sample"""
        single_sample = self.sample_data.head(1)
        result = self.model.predict(single_sample)
        
        self.assertEqual(len(result['predictions']), 1)
        self.assertEqual(len(result['probabilities']), 1)
        self.assertIn(result['predictions'][0], self.expected_classes)

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_data = pd.DataFrame()
        with self.assertRaises(Exception):
            self.model.predict(empty_data)

    def test_missing_columns_handling(self):
        """Test handling of missing columns"""
        incomplete_data = self.sample_data[['kepid', 'koi_period']].copy()
        # Should not crash - model should handle missing columns gracefully
        try:
            result = self.model.predict(incomplete_data)
            # If it doesn't crash, check the result is valid
            self.assertIn('predictions', result)
        except Exception as e:
            # If it does crash, that's also acceptable behavior
            self.assertIsInstance(e, (KeyError, ValueError))

    def test_prediction_confidence(self):
        """Test prediction confidence levels"""
        result = self.model.predict(self.sample_data)
        probabilities = result['probabilities']
        
        for prob_array in probabilities:
            max_prob = max(prob_array)
            self.assertGreater(max_prob, 0.3, "Maximum probability should be > 30%")

class TestKOIModelAccuracy(unittest.TestCase):
    """Test cases for KOI model accuracy on real data"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures with real data"""
        cls.model = model_utils_working.get_model()
        cls.data_path = Path(__file__).parent.parent / 'uploads' / 'NewKepler (8) (1).xls'
        
        if cls.data_path.exists():
            cls.real_data = pd.read_csv(cls.data_path)
            cls.has_real_data = True
        else:
            cls.has_real_data = False

    def setUp(self):
        """Skip tests if no real data available"""
        if not self.has_real_data:
            self.skipTest("Real KOI dataset not available")

    def test_accuracy_on_small_sample(self):
        """Test accuracy on small sample of real data"""
        sample = self.real_data.head(100)
        result = self.model.predict(sample)
        
        actual_labels = sample['koi_disposition'].values
        predicted_labels = result['predictions']
        
        # Map numeric to string labels
        label_mapping = {0: 'FALSE POSITIVE', 1: 'CANDIDATE', 2: 'CONFIRMED'}
        actual_str = [label_mapping[label] for label in actual_labels]
        
        # Calculate accuracy
        correct = sum(1 for a, p in zip(actual_str, predicted_labels) if a == p)
        accuracy = correct / len(actual_str)
        
        self.assertGreater(accuracy, 0.7, f"Accuracy on 100 samples should be > 70%, got {accuracy:.1%}")

    def test_accuracy_on_medium_sample(self):
        """Test accuracy on medium sample of real data"""
        sample = self.real_data.head(500)
        result = self.model.predict(sample)
        
        actual_labels = sample['koi_disposition'].values
        predicted_labels = result['predictions']
        
        # Map numeric to string labels
        label_mapping = {0: 'FALSE POSITIVE', 1: 'CANDIDATE', 2: 'CONFIRMED'}
        actual_str = [label_mapping[label] for label in actual_labels]
        
        # Calculate accuracy
        correct = sum(1 for a, p in zip(actual_str, predicted_labels) if a == p)
        accuracy = correct / len(actual_str)
        
        self.assertGreater(accuracy, 0.8, f"Accuracy on 500 samples should be > 80%, got {accuracy:.1%}")

    def test_class_distribution_reasonable(self):
        """Test that predicted class distribution is reasonable"""
        sample = self.real_data.head(1000)
        result = self.model.predict(sample)
        
        predictions = result['predictions']
        from collections import Counter
        pred_dist = Counter(predictions)
        
        # Check that all classes are predicted at least once
        for class_name in ['CANDIDATE', 'CONFIRMED', 'FALSE POSITIVE']:
            self.assertGreater(pred_dist.get(class_name, 0), 0, 
                             f"Class {class_name} should be predicted at least once")
        
        # Check that no single class dominates too much (> 95%)
        max_count = max(pred_dist.values())
        max_ratio = max_count / len(predictions)
        self.assertLess(max_ratio, 0.95, 
                       "No single class should represent > 95% of predictions")

    def test_confidence_distribution(self):
        """Test confidence score distribution"""
        sample = self.real_data.head(200)
        result = self.model.predict(sample)
        
        probabilities = result['probabilities']
        max_confidences = [max(prob) for prob in probabilities]
        
        avg_confidence = np.mean(max_confidences)
        min_confidence = min(max_confidences)
        
        self.assertGreater(avg_confidence, 0.6, 
                          f"Average confidence should be > 60%, got {avg_confidence:.1%}")
        self.assertGreater(min_confidence, 0.33, 
                          f"Minimum confidence should be > 33% (random chance), got {min_confidence:.1%}")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)