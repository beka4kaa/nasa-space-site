#!/usr/bin/env python3
"""
Production startup script for NASA KOI Portal API
Handles environment setup, model loading, and server startup
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pandas
        import numpy
        import sklearn
        import xgboost
        import dotenv
        logger.info("✅ All main dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def check_model_files():
    """Check if model files exist"""
    model_dir = Path("models")
    required_files = [
        "simple_test_model.pkl",
        "boost_test_model.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not (model_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.warning(f"Missing model files: {missing_files}")
        logger.info("Attempting to create missing models...")
        try:
            # Try to create simple model
            subprocess.run([sys.executable, "test_model_simple.py"], check=True)
            logger.info("✅ Model files created successfully")
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to create model files")
            return False
    else:
        logger.info("✅ All model files exist")
    
    return True

def setup_directories():
    """Create necessary directories"""
    dirs = ["uploads", "models", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        logger.info(f"✅ Directory '{dir_name}' ready")

def load_environment():
    """Load environment variables from .env file"""
    from dotenv import load_dotenv
    
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        logger.info("✅ Environment variables loaded from .env")
    else:
        logger.warning("⚠️  No .env file found, using defaults")
    
    # Set defaults if not present
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8001")
    os.environ.setdefault("DEBUG", "False")
    
    return {
        "host": os.getenv("HOST"),
        "port": int(os.getenv("PORT")),
        "debug": os.getenv("DEBUG").lower() == "true"
    }

def test_model_loading():
    """Test if the model can be loaded successfully"""
    try:
        from model_utils_working import get_model
        predictor = get_model()
        logger.info(f"✅ Model loaded successfully - Accuracy: {predictor.accuracy:.3f}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        return False

def start_server(config):
    """Start the FastAPI server"""
    try:
        import uvicorn
        logger.info(f"🚀 Starting server on {config['host']}:{config['port']}")
        
        # Use uvicorn programmatically for better control
        uvicorn.run(
            "main:app",
            host=config['host'],
            port=config['port'],
            reload=config['debug'],
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        return False

def main():
    """Main startup function"""
    logger.info("🌟 NASA KOI Portal API - Production Startup")
    logger.info("=" * 50)
    
    # Pre-flight checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Model Files", check_model_files),
        ("Model Loading", test_model_loading)
    ]
    
    for check_name, check_func in checks:
        logger.info(f"Checking {check_name}...")
        if not check_func():
            logger.error(f"❌ {check_name} check failed")
            sys.exit(1)
    
    # Setup
    setup_directories()
    config = load_environment()
    
    logger.info("✅ All checks passed!")
    logger.info(f"Server configuration: {config}")
    
    # Start server
    start_server(config)

if __name__ == "__main__":
    main()