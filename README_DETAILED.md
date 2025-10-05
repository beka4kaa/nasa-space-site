# NASA Space Apps KOI Data Portal - Comprehensive Analytics Platform

## 🎯 Project Overview

A full-stack web application for analyzing Kepler Objects of Interest (KOI) data using advanced machine learning and interactive visualizations. Built for the NASA Space Apps Challenge with modern web technologies and AI-powered predictions.

## ✨ Key Features

### 🔬 **Advanced Analytics Dashboard**
- **Interactive Visualizations**: Distribution charts, scatter plots, confidence analysis, and heatmaps
- **Real-time Metrics**: Advanced performance indicators and model confidence scores
- **Data Quality Assessment**: Completeness analysis and missing data reporting
- **Export Capabilities**: JSON export of predictions and analytics results

### 🤖 **AI-Powered Predictions**
- **XGBoost Classification**: State-of-the-art machine learning model for KOI disposition prediction
- **Confidence Scoring**: Probabilistic predictions with uncertainty quantification
- **Batch Processing**: Analyze entire datasets with detailed per-object predictions
- **Feature Engineering**: Advanced preprocessing with stellar density calculations

### 🎨 **Modern User Experience**
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Dark/Light Themes**: Automatic theme switching with user preference
- **Drag & Drop Upload**: Intuitive file upload with real-time validation
- **Interactive Animations**: Smooth transitions with Framer Motion
- **Galaxy Background**: Custom WebGL space visualization

### 📊 **Data Processing & Validation**
- **Multi-format Support**: CSV, XLS, and XLSX file handling
- **Data Cleaning**: Automatic handling of missing values and outliers
- **Encoding Detection**: Smart encoding detection for international datasets
- **Schema Validation**: Real-time validation of required KOI features

## 🏗️ Technical Architecture

### **Frontend Stack**
- **Framework**: Next.js 14 with React 18
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Custom component library with shadcn/ui
- **Animations**: Framer Motion for smooth interactions
- **Visualizations**: Custom chart components with responsive design
- **State Management**: React hooks with session storage persistence

### **Backend Stack**
- **Framework**: FastAPI with async/await support
- **ML Framework**: XGBoost with scikit-learn preprocessing
- **Data Processing**: Pandas with advanced feature engineering
- **File Handling**: Multi-format support with charset detection
- **API Documentation**: Automatic OpenAPI/Swagger generation
- **Error Handling**: Comprehensive exception management

### **DevOps & Deployment**
- **Containerization**: Multi-stage Docker build for production
- **Health Checks**: Built-in monitoring endpoints
- **Hot Reload**: Development environment with live reloading
- **Process Management**: Concurrent backend/frontend serving
- **Static Assets**: Optimized builds with asset compression

## 🚀 Quick Start

### Prerequisites
- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **Docker** (optional, for containerized deployment)

### Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/beka4kaa/nasa-space-site.git
   cd nasa-space-site
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Deployment

1. **Build Container**
   ```bash
   docker build -t nasa-koi-portal .
   ```

2. **Run Application**
   ```bash
   docker run -p 3000:3000 -p 8000:8000 nasa-koi-portal
   ```

## 📈 Analytics Features

### **Distribution Analysis**
- Classification breakdown (Confirmed, Candidates, False Positives)
- Confidence level distributions with visual indicators
- Statistical summaries with percentile calculations

### **Planet Characteristics**
- Period vs. Radius analysis with temperature indicators
- Physical parameter statistics (mean, median, ranges)
- Multi-dimensional data exploration

### **Model Performance**
- Confidence score analysis across prediction categories
- High/Low confidence prediction identification
- Model reliability metrics and validation scores

### **Interactive Heatmaps**
- Discovery rate visualization by parameter ranges
- Confirmation probability mapping
- Parameter space exploration with hover details

## 🔧 API Endpoints

### **Core Endpoints**
- `POST /upload` - Upload and process CSV/Excel files
- `GET /download/{filename}` - Download processed datasets
- `GET /health` - System health check

### **KOI Prediction Endpoints**
- `POST /api/koi/predict` - Batch prediction for datasets
- `POST /api/koi/predict-single` - Single object prediction
- `POST /api/koi/validate-dataset` - Dataset structure validation
- `GET /api/koi/model-info` - Model metadata and requirements

### **Analytics Endpoints**
- `POST /api/koi/analytics` - Generate comprehensive analytics
- `GET /api/data/stats` - Dataset statistics overview

## 🎨 UI Components

### **Chart Components**
- **DistributionChart**: Classification breakdown with progress bars
- **PlanetCharacteristicsChart**: Physical parameter analysis
- **ConfidenceAnalysisChart**: Model confidence visualization
- **AdvancedMetrics**: KPI dashboard with trend indicators
- **HeatmapChart**: Parameter space heatmap visualization

### **Interactive Elements**
- **Galaxy Background**: WebGL-powered space visualization
- **Drag & Drop Upload**: Multi-format file handling
- **Progress Indicators**: Real-time processing feedback
- **Theme Toggle**: Dark/light mode switching
- **Responsive Tables**: Sortable, filterable data tables

## 📱 Responsive Design

- **Mobile-First**: Optimized for mobile devices with touch interactions
- **Tablet Support**: Adaptive layouts for medium screens
- **Desktop Experience**: Full-featured interface with advanced interactions
- **High-DPI Support**: Crisp visuals on retina displays

## 🧪 Data Science Features

### **Feature Engineering**
- Stellar density calculations from surface gravity
- Planet-to-star radius ratios
- Semi-major axis to stellar radius ratios
- Temperature-based habitability indicators

### **Preprocessing Pipeline**
- Missing value imputation with iterative methods
- Feature scaling and normalization
- Categorical encoding for disposition labels
- Outlier detection and handling

### **Model Performance**
- Cross-validation with stratified sampling
- Precision, recall, and F1-score metrics
- Confusion matrix analysis
- Feature importance rankings

## 🌟 Advanced Features

### **Real-time Analytics**
- Live data processing with progress indicators
- Streaming results for large datasets
- Memory-efficient batch processing
- Error recovery and retry mechanisms

### **Data Export**
- JSON format with structured predictions
- CSV export with added prediction columns
- Confidence intervals and probability distributions
- Metadata preservation and audit trails

### **Visualization Insights**
- Automated insight generation from data patterns
- Statistical significance testing
- Correlation analysis and reporting
- Interactive parameter exploration

## 🔒 Security & Performance

### **Security Measures**
- Input validation and sanitization
- File type restrictions and size limits
- Error message sanitization
- CORS configuration for cross-origin requests

### **Performance Optimizations**
- Lazy loading for large datasets
- Memory-efficient data processing
- Concurrent request handling
- Static asset optimization and caching

## 🤝 Contributing

We welcome contributions to improve the NASA KOI Data Portal! Please follow these guidelines:

1. Fork the repository and create a feature branch
2. Ensure all tests pass and add new tests for features
3. Follow the existing code style and conventions
4. Update documentation for new features
5. Submit a pull request with detailed description

## 📄 License

This project is open source and available under the MIT License. See LICENSE file for details.

## 🏆 NASA Space Apps Challenge

This project was developed for the NASA Space Apps Challenge, demonstrating the power of open data and collaborative innovation in space exploration and planetary science.

---

**Built with ❤️ for space exploration and scientific discovery**

For questions or support, please open an issue on GitHub or contact the development team.