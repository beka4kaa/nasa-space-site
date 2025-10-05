import React, { useState } from 'react';
import { Download, Upload, BarChart3, CheckCircle, AlertTriangle, XCircle, Info, TrendingUp, Target, Zap, Brain, Eye, BookOpen, HelpCircle } from 'lucide-react';
import { API_ENDPOINTS } from '../lib/api';

const Instructions = () => {
  const [activeTab, setActiveTab] = useState('dataset');

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
    { id: 'dataset', label: 'Kepler Dataset', icon: Download },
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
                <h3 className="text-2xl font-bold mb-6 flex items-center">
                  <Brain className="w-6 h-6 mr-3 text-primary" />
                  Understanding Your AI Analysis Results
                </h3>
                
                <div className="space-y-8">
                  {/* Prediction Categories - Enhanced */}
                  <div>
                    <h4 className="text-lg font-semibold mb-4 flex items-center">
                      <Target className="w-5 h-5 mr-2 text-primary" />
                      KOI Classification Categories
                    </h4>
                    <p className="text-muted-foreground mb-4">
                      Our XGBoost machine learning model classifies each Kepler Object of Interest into one of three categories based on 19 astronomical parameters:
                    </p>
                    <div className="space-y-4">
                      <div className="border border-green-500/30 bg-green-500/5 rounded-lg p-4">
                        <div className="flex items-start space-x-4">
                          <CheckCircle className="w-6 h-6 text-green-500 mt-1 flex-shrink-0" />
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <strong className="text-green-600 text-lg">CONFIRMED EXOPLANET</strong>
                              <span className="bg-green-500/20 text-green-700 px-2 py-1 rounded-full text-xs font-medium">High Confidence</span>
                            </div>
                            <p className="text-sm text-muted-foreground mb-3">
                              Objects with high probability of being genuine exoplanets. These have passed rigorous statistical validation and show consistent transit signatures.
                            </p>
                            <div className="bg-green-500/10 rounded p-3 text-xs">
                              <strong className="text-green-700">Typical Characteristics:</strong>
                              <ul className="mt-1 space-y-1 text-muted-foreground">
                                <li>• Strong, periodic transit signals</li>
                                <li>• Consistent orbital parameters</li>
                                <li>• Low false positive probability flags</li>
                                <li>• High signal-to-noise ratio (SNR {'>'} 15)</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="border border-yellow-500/30 bg-yellow-500/5 rounded-lg p-4">
                        <div className="flex items-start space-x-4">
                          <AlertTriangle className="w-6 h-6 text-yellow-500 mt-1 flex-shrink-0" />
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <strong className="text-yellow-600 text-lg">PLANET CANDIDATE</strong>
                              <span className="bg-yellow-500/20 text-yellow-700 px-2 py-1 rounded-full text-xs font-medium">Needs Verification</span>
                            </div>
                            <p className="text-sm text-muted-foreground mb-3">
                              Potential exoplanets showing promising signals but requiring additional observations or analysis for confirmation.
                            </p>
                            <div className="bg-yellow-500/10 rounded p-3 text-xs">
                              <strong className="text-yellow-700">Typical Characteristics:</strong>
                              <ul className="mt-1 space-y-1 text-muted-foreground">
                                <li>• Detectable transit signals with some uncertainty</li>
                                <li>• Moderate signal-to-noise ratio (SNR 7-15)</li>
                                <li>• May have minor inconsistencies in data</li>
                                <li>• Requires follow-up observations</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="border border-red-500/30 bg-red-500/5 rounded-lg p-4">
                        <div className="flex items-start space-x-4">
                          <XCircle className="w-6 h-6 text-red-500 mt-1 flex-shrink-0" />
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <strong className="text-red-600 text-lg">FALSE POSITIVE</strong>
                              <span className="bg-red-500/20 text-red-700 px-2 py-1 rounded-full text-xs font-medium">Not a Planet</span>
                            </div>
                            <p className="text-sm text-muted-foreground mb-3">
                              Objects that initially appeared as planetary transits but are likely caused by astrophysical phenomena mimicking planet signatures.
                            </p>
                            <div className="bg-red-500/10 rounded p-3 text-xs">
                              <strong className="text-red-700">Common Causes:</strong>
                              <ul className="mt-1 space-y-1 text-muted-foreground">
                                <li>• Eclipsing binary star systems</li>
                                <li>• Background/foreground star contamination</li>
                                <li>• Stellar activity (starspots, flares)</li>
                                <li>• Instrumental artifacts or noise</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Confidence Scores - Enhanced */}
                  <div>
                    <h4 className="text-lg font-semibold mb-4 flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2 text-primary" />
                      Interpreting Confidence Scores
                    </h4>
                    <p className="text-muted-foreground text-sm mb-4">
                      Each prediction includes probability scores (0.0 to 1.0) for all three categories. The sum always equals 1.0, representing the model's confidence distribution:
                    </p>
                    
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="bg-muted/30 rounded-lg p-4">
                        <h5 className="font-semibold mb-3 flex items-center">
                          <Zap className="w-4 h-4 mr-2 text-green-500" />
                          High Confidence Example
                        </h5>
                        <div className="bg-background rounded p-3 font-mono text-sm space-y-1">
                          <div className="flex justify-between">
                            <span>CONFIRMED:</span>
                            <span className="text-green-600 font-bold">0.94 (94%)</span>
                          </div>
                          <div className="flex justify-between">
                            <span>CANDIDATE:</span>
                            <span className="text-yellow-600">0.04 (4%)</span>
                          </div>
                          <div className="flex justify-between">
                            <span>FALSE POSITIVE:</span>
                            <span className="text-red-600">0.02 (2%)</span>
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground mt-2">
                          <strong>Interpretation:</strong> Very likely a confirmed exoplanet with strong evidence.
                        </p>
                      </div>
                      
                      <div className="bg-muted/30 rounded-lg p-4">
                        <h5 className="font-semibold mb-3 flex items-center">
                          <Eye className="w-4 h-4 mr-2 text-yellow-500" />
                          Uncertain Prediction Example
                        </h5>
                        <div className="bg-background rounded p-3 font-mono text-sm space-y-1">
                          <div className="flex justify-between">
                            <span>CONFIRMED:</span>
                            <span className="text-green-600">0.45 (45%)</span>
                          </div>
                          <div className="flex justify-between">
                            <span>CANDIDATE:</span>
                            <span className="text-yellow-600 font-bold">0.35 (35%)</span>
                          </div>
                          <div className="flex justify-between">
                            <span>FALSE POSITIVE:</span>
                            <span className="text-red-600">0.20 (20%)</span>
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground mt-2">
                          <strong>Interpretation:</strong> Ambiguous case requiring careful review and additional data.
                        </p>
                      </div>
                    </div>
                    
                    <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                      <h5 className="font-semibold text-blue-600 mb-2 flex items-center">
                        <Info className="w-4 h-4 mr-2" />
                        Confidence Score Guidelines
                      </h5>
                      <div className="grid md:grid-cols-3 gap-4 text-xs">
                        <div>
                          <strong className="text-green-600">High Confidence ({'>'} 80%)</strong>
                          <p className="text-muted-foreground mt-1">Strong evidence for the predicted classification. Suitable for scientific analysis.</p>
                        </div>
                        <div>
                          <strong className="text-yellow-600">Moderate Confidence (50-80%)</strong>
                          <p className="text-muted-foreground mt-1">Reasonable evidence but consider reviewing the object parameters manually.</p>
                        </div>
                        <div>
                          <strong className="text-red-600">Low Confidence ({'<'} 50%)</strong>
                          <p className="text-muted-foreground mt-1">Uncertain prediction. Check data quality and consider additional analysis.</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Analytics Dashboard */}
                  <div>
                    <h4 className="text-lg font-semibold mb-4 flex items-center">
                      <BarChart3 className="w-5 h-5 mr-2 text-primary" />
                      Your Analytics Dashboard
                    </h4>
                    <p className="text-muted-foreground text-sm mb-4">
                      After analysis, you'll receive a comprehensive dashboard with multiple visualization and insights:
                    </p>
                    
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
                          <h5 className="font-semibold mb-3">Summary Statistics</h5>
                          <div className="grid grid-cols-3 gap-3">
                            <div className="bg-background rounded p-2 text-center">
                              <div className="font-bold text-lg text-primary">156</div>
                              <div className="text-xs text-muted-foreground">Total Objects</div>
                            </div>
                            <div className="bg-background rounded p-2 text-center">
                              <div className="font-bold text-lg text-green-600">91.2%</div>
                              <div className="text-xs text-muted-foreground">Model Accuracy</div>
                            </div>
                            <div className="bg-background rounded p-2 text-center">
                              <div className="font-bold text-lg text-blue-600">19</div>
                              <div className="text-xs text-muted-foreground">Parameters</div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-4">
                          <h5 className="font-semibold mb-2 text-green-600">Classification Breakdown</h5>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span>Confirmed Exoplanets:</span>
                              <span className="font-mono">42 (26.9%)</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Planet Candidates:</span>
                              <span className="font-mono">67 (42.9%)</span>
                            </div>
                            <div className="flex justify-between">
                              <span>False Positives:</span>
                              <span className="font-mono">47 (30.1%)</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-4">
                          <h5 className="font-semibold mb-3 text-yellow-600">Interactive Visualizations</h5>
                          <ul className="text-sm space-y-2 text-muted-foreground">
                            <li className="flex items-center"><CheckCircle className="w-3 h-3 mr-2 text-green-500" />Distribution charts with filtering options</li>
                            <li className="flex items-center"><CheckCircle className="w-3 h-3 mr-2 text-green-500" />Planet characteristics scatter plots</li>
                            <li className="flex items-center"><CheckCircle className="w-3 h-3 mr-2 text-green-500" />Confidence analysis histograms</li>
                            <li className="flex items-center"><CheckCircle className="w-3 h-3 mr-2 text-green-500" />Parameter correlation heatmaps</li>
                            <li className="flex items-center"><CheckCircle className="w-3 h-3 mr-2 text-green-500" />Detailed results table with sorting</li>
                          </ul>
                        </div>
                        
                        <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-4">
                          <h5 className="font-semibold mb-3 text-blue-600">Export Options</h5>
                          <ul className="text-sm space-y-2 text-muted-foreground">
                            <li className="flex items-center"><Download className="w-3 h-3 mr-2 text-blue-500" />JSON format with full results</li>
                            <li className="flex items-center"><Download className="w-3 h-3 mr-2 text-blue-500" />CSV format for further analysis</li>
                            <li className="flex items-center"><Download className="w-3 h-3 mr-2 text-blue-500" />High-resolution chart images</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Troubleshooting */}
                  <div>
                    <h4 className="text-lg font-semibold mb-4 flex items-center">
                      <HelpCircle className="w-5 h-5 mr-2 text-primary" />
                      Common Questions & Troubleshooting
                    </h4>
                    
                    <div className="space-y-4">
                      <div className="border rounded-lg p-4">
                        <h5 className="font-semibold mb-2">Why do I see mostly "CANDIDATE" predictions?</h5>
                        <p className="text-sm text-muted-foreground">
                          This is normal! In real astronomical surveys, most objects are candidates requiring further verification. 
                          Confirmed exoplanets represent only a small fraction after rigorous validation processes.
                        </p>
                      </div>
                      
                      <div className="border rounded-lg p-4">
                        <h5 className="font-semibold mb-2">What if confidence scores are very low across all categories?</h5>
                        <p className="text-sm text-muted-foreground">
                          Low confidence typically indicates: incomplete data, unusual parameter combinations, or objects at the 
                          boundary between categories. Check your input data for missing values or outliers.
                        </p>
                      </div>
                      
                      <div className="border rounded-lg p-4">
                        <h5 className="font-semibold mb-2">How accurate is the AI model?</h5>
                        <p className="text-sm text-muted-foreground">
                          Our XGBoost model achieves ~91% accuracy on NASA's validated KOI dataset. However, individual predictions 
                          should be interpreted alongside confidence scores and validated with additional observations when possible.
                        </p>
                      </div>
                      
                      <div className="border rounded-lg p-4">
                        <h5 className="font-semibold mb-2">Can I trust single-object predictions?</h5>
                        <p className="text-sm text-muted-foreground">
                          Yes, but with caution. For critical decisions, always consider the confidence scores, parameter values, 
                          and cross-reference with additional data sources. The model is a powerful tool but not infallible.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Best Practices */}
                  <div className="bg-gradient-to-r from-primary/5 to-primary/10 border border-primary/20 rounded-lg p-6">
                    <h4 className="text-lg font-semibold mb-4 flex items-center text-primary">
                      <BookOpen className="w-5 h-5 mr-2" />
                      Best Practices for Result Interpretation
                    </h4>
                    
                    <div className="grid md:grid-cols-2 gap-6 text-sm">
                      <div>
                        <h5 className="font-semibold mb-3 text-green-600">✅ Recommended Approach</h5>
                        <ul className="space-y-2 text-muted-foreground">
                          <li>• Always check confidence scores alongside predictions</li>
                          <li>• Focus on high-confidence results for initial analysis</li>
                          <li>• Use summary statistics to understand dataset trends</li>
                          <li>• Cross-reference with known astronomical catalogs</li>
                          <li>• Consider parameter ranges and physical plausibility</li>
                          <li>• Export results for further statistical analysis</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h5 className="font-semibold mb-3 text-red-600">❌ Common Pitfalls</h5>
                        <ul className="space-y-2 text-muted-foreground">
                          <li>• Don't ignore low-confidence predictions entirely</li>
                          <li>• Avoid using predictions without validating input data</li>
                          <li>• Don't assume all "FALSE POSITIVE" results are incorrect</li>
                          <li>• Avoid over-interpreting small confidence differences</li>
                          <li>• Don't use results for mission-critical decisions alone</li>
                          <li>• Avoid conclusions based on single-object analysis</li>
                        </ul>
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