// API configuration and utilities
// frontend/lib/api.js

// Get API URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION || 'v1';

// Debug logging for development
if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
  console.log('🔧 API Configuration:', {
    API_BASE_URL,
    API_VERSION,
    NODE_ENV: process.env.NODE_ENV
  });
}

// API endpoints
export const API_ENDPOINTS = {
  // Health check
  ping: `${API_BASE_URL}/ping`,
  
  // File operations
  upload: `${API_BASE_URL}/upload`,
  download: (filename) => `${API_BASE_URL}/download/${filename}`,
  
  // Kepler API endpoints
  validateDataset: `${API_BASE_URL}/api/kepler/validate-dataset`,
  predict: `${API_BASE_URL}/api/kepler/predict`,
  modelInfo: `${API_BASE_URL}/api/kepler/model-info`,
};

// Default axios configuration
export const API_CONFIG = {
  timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT) || 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// File upload configuration
export const FILE_UPLOAD_CONFIG = {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
  timeout: parseInt(process.env.NEXT_PUBLIC_PREDICTION_TIMEOUT) || 120000,
};

// API utility functions
export const apiUtils = {
  // Handle API errors consistently
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error';
      throw new Error(`API Error (${error.response.status}): ${message}`);
    } else if (error.request) {
      // Request made but no response
      throw new Error('Network error: Unable to connect to server');
    } else {
      // Something else happened
      throw new Error(`Request error: ${error.message}`);
    }
  },

  // Check if server is healthy
  healthCheck: async () => {
    try {
      const response = await fetch(API_ENDPOINTS.ping);
      if (response.ok) {
        const data = await response.json();
        return data.status === 'ok';
      }
      return false;
    } catch {
      return false;
    }
  },

  // Validate file before upload
  validateFile: (file) => {
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const allowedExtensions = process.env.NEXT_PUBLIC_ALLOWED_EXTENSIONS 
      ? process.env.NEXT_PUBLIC_ALLOWED_EXTENSIONS.split(',').map(ext => `.${ext.trim()}`)
      : ['.csv', '.xls', '.xlsx'];
    const maxSize = parseInt(process.env.NEXT_PUBLIC_MAX_FILE_SIZE) || (100 * 1024 * 1024); // Default 100MB

    if (!file) {
      throw new Error('No file selected');
    }

    if (file.size > maxSize) {
      throw new Error('File size exceeds 100MB limit');
    }

    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedExtensions.includes(fileExtension)) {
      throw new Error('Invalid file type. Only CSV, XLS, and XLSX files are allowed.');
    }

    return true;
  },

  // Format prediction data for consistent usage
  formatPredictionData: (rawData) => {
    if (!rawData) return null;

    // Handle different response formats
    if (rawData.predictions && Array.isArray(rawData.predictions)) {
      return {
        predictions: rawData.predictions,
        probabilities: rawData.probabilities || [],
        summary: rawData.summary || {},
        metadata: rawData.metadata || {},
        total: rawData.predictions.length
      };
    }

    // Legacy format support
    if (Array.isArray(rawData)) {
      return {
        predictions: rawData,
        probabilities: [],
        summary: {},
        metadata: {},
        total: rawData.length
      };
    }

    return rawData;
  }
};

export default API_ENDPOINTS;