"""
Performance and load tests for KOI model
"""

import unittest
import time
import threading
import concurrent.futures
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from statistics import mean, median

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import model_utils_working

class TestKOIModelPerformance(unittest.TestCase):
    """Performance tests for KOI model"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.model = model_utils_working.get_model()
        
        # Create test data of different sizes
        cls.small_data = cls._create_test_data(10)
        cls.medium_data = cls._create_test_data(100)
        cls.large_data = cls._create_test_data(1000)
        
        # Load real data if available
        data_path = backend_dir / 'uploads' / 'NewKepler (8) (1).xls'
        if data_path.exists():
            cls.real_data = pd.read_csv(data_path)
            cls.has_real_data = True
        else:
            cls.has_real_data = False

    @staticmethod
    def _create_test_data(size):
        """Create synthetic test data"""
        np.random.seed(42)  # For reproducibility
        
        data = {
            'kepid': range(1, size + 1),
            'koi_period': np.random.uniform(1, 1000, size),
            'koi_time0bk': np.random.uniform(100, 200, size),
            'koi_impact': np.random.uniform(0, 1, size),
            'koi_duration': np.random.uniform(1, 10, size),
            'koi_depth': np.random.uniform(10, 2000, size),
            'koi_prad': np.random.uniform(0.5, 10, size),
            'koi_teq': np.random.uniform(200, 2000, size),
            'koi_insol': np.random.uniform(0.1, 1000, size),
            'koi_model_snr': np.random.uniform(5, 100, size),
            'koi_steff': np.random.uniform(3000, 8000, size),
            'koi_slogg': np.random.uniform(3.5, 5.0, size),
            'koi_srad': np.random.uniform(0.5, 3.0, size),
            'ra': np.random.uniform(0, 360, size),
            'dec': np.random.uniform(-90, 90, size),
            'koi_kepmag': np.random.uniform(8, 20, size),
            'koi_fpflag_nt': np.random.choice([0, 1], size),
            'koi_fpflag_ss': np.random.choice([0, 1], size),
            'koi_fpflag_co': np.random.choice([0, 1], size),
            'koi_fpflag_ec': np.random.choice([0, 1], size)
        }
        
        return pd.DataFrame(data)

    def _measure_prediction_time(self, data, iterations=3):
        """Measure prediction time with multiple iterations"""
        times = []
        for _ in range(iterations):
            start_time = time.time()
            result = self.model.predict(data)
            end_time = time.time()
            times.append(end_time - start_time)
        
        return {
            'mean_time': mean(times),
            'median_time': median(times),
            'min_time': min(times),
            'max_time': max(times),
            'times': times,
            'predictions_count': len(result['predictions'])
        }

    def test_small_batch_performance(self):
        """Test performance on small batch (10 samples)"""
        stats = self._measure_prediction_time(self.small_data)
        
        # Should complete in < 1 second
        self.assertLess(stats['mean_time'], 1.0, 
                       f"Small batch should complete in < 1s, got {stats['mean_time']:.3f}s")
        
        # Check throughput (predictions per second)
        throughput = stats['predictions_count'] / stats['mean_time']
        self.assertGreater(throughput, 5, 
                          f"Small batch throughput should be > 5 pred/s, got {throughput:.1f}")

    def test_medium_batch_performance(self):
        """Test performance on medium batch (100 samples)"""
        stats = self._measure_prediction_time(self.medium_data)
        
        # Should complete in < 5 seconds
        self.assertLess(stats['mean_time'], 5.0, 
                       f"Medium batch should complete in < 5s, got {stats['mean_time']:.3f}s")
        
        # Check throughput
        throughput = stats['predictions_count'] / stats['mean_time']
        self.assertGreater(throughput, 10, 
                          f"Medium batch throughput should be > 10 pred/s, got {throughput:.1f}")

    def test_large_batch_performance(self):
        """Test performance on large batch (1000 samples)"""
        stats = self._measure_prediction_time(self.large_data)
        
        # Should complete in < 30 seconds
        self.assertLess(stats['mean_time'], 30.0, 
                       f"Large batch should complete in < 30s, got {stats['mean_time']:.3f}s")
        
        # Check throughput
        throughput = stats['predictions_count'] / stats['mean_time']
        self.assertGreater(throughput, 20, 
                          f"Large batch throughput should be > 20 pred/s, got {throughput:.1f}")

    def test_real_data_performance(self):
        """Test performance on real data"""
        if not self.has_real_data:
            self.skipTest("Real data not available")
        
        # Test on first 500 samples of real data
        sample = self.real_data.head(500)
        stats = self._measure_prediction_time(sample)
        
        # Should complete in reasonable time
        self.assertLess(stats['mean_time'], 15.0, 
                       f"Real data batch should complete in < 15s, got {stats['mean_time']:.3f}s")
        
        print(f"Real data performance: {stats['mean_time']:.3f}s for {stats['predictions_count']} predictions")
        print(f"Throughput: {stats['predictions_count'] / stats['mean_time']:.1f} predictions/sec")

    def test_memory_usage(self):
        """Test memory usage doesn't grow significantly"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run multiple predictions
        for _ in range(10):
            self.model.predict(self.medium_data)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB)
        memory_increase_mb = memory_increase / (1024 * 1024)
        self.assertLess(memory_increase_mb, 100, 
                       f"Memory increase should be < 100MB, got {memory_increase_mb:.1f}MB")

    def test_concurrent_predictions(self):
        """Test concurrent prediction performance"""
        def run_prediction():
            return self.model.predict(self.small_data)
        
        # Test with 5 concurrent predictions
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_prediction) for _ in range(5)]
            results = [future.result() for future in futures]
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # All predictions should complete
        self.assertEqual(len(results), 5)
        
        # Should complete in reasonable time (not much slower than sequential)
        self.assertLess(total_time, 10.0, 
                       f"Concurrent predictions should complete in < 10s, got {total_time:.3f}s")
        
        # All results should be valid
        for result in results:
            self.assertIn('predictions', result)
            self.assertIn('probabilities', result)

    def test_model_loading_time(self):
        """Test model loading performance"""
        start_time = time.time()
        new_model = model_utils_working.get_model()
        end_time = time.time()
        
        loading_time = end_time - start_time
        
        # Model should load quickly (< 3 seconds)
        self.assertLess(loading_time, 3.0, 
                       f"Model loading should take < 3s, got {loading_time:.3f}s")
        
        # Model should be functional
        self.assertIsNotNone(new_model.model)
        self.assertGreater(new_model.accuracy, 0.8)

class TestKOIModelStress(unittest.TestCase):
    """Stress tests for KOI model"""

    @classmethod
    def setUpClass(cls):
        """Set up stress test fixtures"""
        cls.model = model_utils_working.get_model()

    def test_repeated_predictions(self):
        """Test model stability under repeated predictions"""
        test_data = TestKOIModelPerformance._create_test_data(50)
        
        results = []
        errors = []
        
        # Run 50 predictions
        for i in range(50):
            try:
                start_time = time.time()
                result = self.model.predict(test_data)
                end_time = time.time()
                
                results.append({
                    'iteration': i,
                    'time': end_time - start_time,
                    'predictions_count': len(result['predictions'])
                })
            except Exception as e:
                errors.append({
                    'iteration': i,
                    'error': str(e)
                })
        
        # Should have no errors
        self.assertEqual(len(errors), 0, f"Got {len(errors)} errors: {errors}")
        
        # All results should be consistent
        prediction_counts = [r['predictions_count'] for r in results]
        self.assertTrue(all(count == prediction_counts[0] for count in prediction_counts),
                       "Prediction counts should be consistent")
        
        # Performance should remain stable
        times = [r['time'] for r in results]
        avg_time = mean(times)
        max_time = max(times)
        
        # Max time shouldn't be more than 3x average time
        self.assertLess(max_time, avg_time * 3, 
                       f"Max time {max_time:.3f}s shouldn't be > 3x avg time {avg_time:.3f}s")

    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Create largest dataset we can reasonably test
        large_data = TestKOIModelPerformance._create_test_data(5000)
        
        try:
            start_time = time.time()
            result = self.model.predict(large_data)
            end_time = time.time()
            
            prediction_time = end_time - start_time
            
            # Should complete successfully
            self.assertEqual(len(result['predictions']), 5000)
            self.assertEqual(len(result['probabilities']), 5000)
            
            # Should complete in reasonable time (< 2 minutes)
            self.assertLess(prediction_time, 120.0, 
                           f"Large dataset should complete in < 2min, got {prediction_time:.1f}s")
            
            print(f"Large dataset performance: {prediction_time:.1f}s for 5000 predictions")
            print(f"Throughput: {5000 / prediction_time:.1f} predictions/sec")
            
        except MemoryError:
            self.skipTest("Not enough memory for large dataset test")
        except Exception as e:
            self.fail(f"Large dataset test failed with error: {e}")

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)