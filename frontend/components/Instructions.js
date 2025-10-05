import React, { useState } from 'react';
import { Download, FileText, Upload, BarChart3, CheckCircle, Info, ExternalLink, Telescope } from 'lucide-react';
import { API_ENDPOINTS } from '../lib/api';

const Instructions = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const handleDownloadDataset = () => {
    // Create a link to download the Kepler dataset
    const link = document.createElement('a');
    link.href = `${API_ENDPOINTS.validateDataset.replace('/validate-dataset', '/dataset/sample')}`;
    link.download = 'kepler_sample_dataset.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Info },
    { id: 'dataset', label: 'Sample Dataset', icon: Download },
    { id: 'upload', label: 'How to Upload', icon: Upload },
    { id: 'results', label: 'Understanding Results', icon: BarChart3 },
  ];

  return (
    <section className="py-16 bg-card/50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
            How to Use NASA KOI Portal
          </h2>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Analyze Kepler Objects of Interest (KOI) data using our AI-powered planet classification system
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap justify-center mb-8 border-b">
          {tabs.map((tab) => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-6 py-3 font-medium transition-colors border-b-2 ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <IconComponent className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="max-w-4xl mx-auto">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="bg-card border rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <Telescope className="w-5 h-5 mr-2 text-primary" />
                  What is KOI Analysis?
                </h3>
                <p className="text-muted-foreground mb-4">
                  Kepler Objects of Interest (KOI) are astronomical objects identified by NASA's Kepler mission as potential exoplanets. 
                  Our AI system analyzes 19 different astronomical measurements to classify these objects as:
                </p>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                    <CheckCircle className="w-8 h-8 text-green-500 mb-2" />
                    <h4 className="font-semibold text-green-500 mb-1">CONFIRMED</h4>
                    <p className="text-sm text-muted-foreground">Verified exoplanets</p>
                  </div>
                  <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
                    <FileText className="w-8 h-8 text-yellow-500 mb-2" />
                    <h4 className="font-semibold text-yellow-500 mb-1">CANDIDATE</h4>
                    <p className="text-sm text-muted-foreground">Potential exoplanets</p>
                  </div>
                  <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                    <ExternalLink className="w-8 h-8 text-red-500 mb-2" />
                    <h4 className="font-semibold text-red-500 mb-1">FALSE POSITIVE</h4>
                    <p className="text-sm text-muted-foreground">Not actual planets</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-primary/5 border border-primary/20 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-2 text-primary">Model Performance</h3>
                <p className="text-muted-foreground">
                  Our machine learning model achieves <strong>91% accuracy</strong> using NASA Kepler mission data, 
                  trained on thousands of astronomical observations and measurements.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'dataset' && (
            <div className="space-y-6">
              <div className="bg-card border rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <Download className="w-5 h-5 mr-2 text-primary" />
                  Download Sample Kepler Dataset
                </h3>
                <p className="text-muted-foreground mb-6">
                  Get started with our sample dataset containing real NASA Kepler Objects of Interest data. 
                  This file includes all 19 required astronomical measurements for analysis.
                </p>
                
                <div className="bg-muted/50 rounded-lg p-4 mb-6">
                  <h4 className="font-semibold mb-2">Dataset Features:</h4>
                  <div className="grid md:grid-cols-2 gap-2 text-sm text-muted-foreground">
                    <div>• Orbital period (koi_period)</div>
                    <div>• Transit epoch (koi_time0bk)</div>
                    <div>• Impact parameter (koi_impact)</div>
                    <div>• Transit duration (koi_duration)</div>
                    <div>• Transit depth (koi_depth)</div>
                    <div>• Planetary radius (koi_prad)</div>
                    <div>• Equilibrium temperature (koi_teq)</div>
                    <div>• Insolation flux (koi_insol)</div>
                    <div>• Signal-to-noise ratio (koi_model_snr)</div>
                    <div>• Stellar effective temperature (koi_steff)</div>
                    <div>• Stellar surface gravity (koi_slogg)</div>
                    <div>• Stellar radius (koi_srad)</div>
                    <div>• Right ascension (ra)</div>
                    <div>• Declination (dec)</div>
                    <div>• Kepler magnitude (koi_kepmag)</div>
                    <div>• False positive flags (4 types)</div>
                  </div>
                </div>

                <button
                  onClick={handleDownloadDataset}
                  className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Complete Kepler Dataset (CSV)
                </button>
                
                <p className="text-sm text-muted-foreground mt-4">
                  File size: ~1.3MB | Contains: 9,564 KOI objects | Format: CSV with headers
                </p>
              </div>
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="space-y-6">
              <div className="bg-card border rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <Upload className="w-5 h-5 mr-2 text-primary" />
                  Step-by-Step Upload Guide
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">
                      1
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Prepare Your Data</h4>
                      <p className="text-muted-foreground text-sm">
                        Ensure your file contains all 19 required KOI columns. Use our sample dataset as a reference for the correct format.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">
                      2
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Choose File Format</h4>
                      <p className="text-muted-foreground text-sm">
                        Supported formats: CSV (.csv), Excel (.xls, .xlsx). Our system automatically detects the format regardless of extension.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">
                      3
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Upload & Analyze</h4>
                      <p className="text-muted-foreground text-sm">
                        Click "Browse Files" above, select your file, and click "Launch AI Analysis". The system will validate and process your data.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">
                      4
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Review Results</h4>
                      <p className="text-muted-foreground text-sm">
                        View predictions for each KOI object with confidence scores and detailed analysis. Export results if needed.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <h4 className="font-semibold text-yellow-600 mb-2">💡 Pro Tips:</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• NASA files with comment headers (starting with #) are automatically supported</li>
                    <li>• Files with incorrect extensions (.csv content in .xls file) work perfectly</li>
                    <li>• Maximum file size: 50MB | Processing time: 30-60 seconds for large datasets</li>
                    <li>• Missing values in non-critical columns are automatically handled</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'results' && (
            <div className="space-y-6">
              <div className="bg-card border rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-primary" />
                  Understanding Your Results
                </h3>
                
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-3">Prediction Categories</h4>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3 p-3 bg-green-500/10 rounded-lg">
                        <CheckCircle className="w-5 h-5 text-green-500" />
                        <div>
                          <strong className="text-green-600">CONFIRMED</strong>
                          <p className="text-sm text-muted-foreground">Objects with high confidence of being actual exoplanets. These have passed rigorous validation criteria.</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3 p-3 bg-yellow-500/10 rounded-lg">
                        <FileText className="w-5 h-5 text-yellow-500" />
                        <div>
                          <strong className="text-yellow-600">CANDIDATE</strong>
                          <p className="text-sm text-muted-foreground">Potential exoplanets that require further observation and analysis for confirmation.</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3 p-3 bg-red-500/10 rounded-lg">
                        <ExternalLink className="w-5 h-5 text-red-500" />
                        <div>
                          <strong className="text-red-600">FALSE POSITIVE</strong>
                          <p className="text-sm text-muted-foreground">Objects that initially appeared as planets but are likely caused by other phenomena.</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-3">Confidence Scores</h4>
                    <p className="text-muted-foreground text-sm mb-3">
                      Each prediction includes probability scores for all three categories, showing the model's confidence:
                    </p>
                    <div className="bg-muted/50 rounded-lg p-4 font-mono text-sm">
                      <div className="mb-2"><strong>Example:</strong></div>
                      <div>CONFIRMED: 0.95 (95% confidence)</div>
                      <div>CANDIDATE: 0.04 (4% confidence)</div>
                      <div>FALSE POSITIVE: 0.01 (1% confidence)</div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-3">Summary Statistics</h4>
                    <p className="text-muted-foreground text-sm mb-3">
                      Your results include an overview showing the distribution of predictions across your dataset:
                    </p>
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="bg-muted/50 rounded-lg p-3 text-center">
                        <div className="font-bold text-lg">42</div>
                        <div className="text-sm text-muted-foreground">Total Objects</div>
                      </div>
                      <div className="bg-muted/50 rounded-lg p-3 text-center">
                        <div className="font-bold text-lg">91%</div>
                        <div className="text-sm text-muted-foreground">Model Accuracy</div>
                      </div>
                      <div className="bg-muted/50 rounded-lg p-3 text-center">
                        <div className="font-bold text-lg">19</div>
                        <div className="text-sm text-muted-foreground">Features Analyzed</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Instructions;