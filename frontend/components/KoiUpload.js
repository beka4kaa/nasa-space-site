import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Upload, CheckCircle2, FileText, Activity, AlertCircle, Download } from 'lucide-react';

export default function KoiUpload() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success', 'error', null

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    // Check file extension
    const validExtensions = ['.csv', '.fits', '.txt', '.dat'];
    const fileName = selectedFile.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (isValid) {
      setFile(selectedFile);
      setUploadStatus('success');
    } else {
      setFile(null);
      setUploadStatus('error');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const clearFile = () => {
    setFile(null);
    setUploadStatus(null);
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-8" id="koi-upload">
      {/* Header Section */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
          <Activity className="h-8 w-8 text-primary" />
        </div>
        <h2 className="text-3xl font-bold tracking-tight">KOI Light Curves Analysis</h2>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Upload Kepler Object of Interest (KOI) light curve data for advanced exoplanet transit analysis
        </p>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="border-primary/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <h4 className="font-semibold text-sm mb-1">Accepted Formats</h4>
                <p className="text-xs text-muted-foreground">CSV, FITS, TXT, DAT</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-primary/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Activity className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <h4 className="font-semibold text-sm mb-1">Light Curve Data</h4>
                <p className="text-xs text-muted-foreground">Time series flux measurements</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-primary/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <h4 className="font-semibold text-sm mb-1">Auto Detection</h4>
                <p className="text-xs text-muted-foreground">Transit events & periodicity</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upload Card */}
      <Card className="overflow-hidden border-0 shadow-lg bg-card/50 backdrop-blur-sm">
        <CardContent className="p-8">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
              isDragging
                ? 'border-primary bg-primary/10 scale-[1.02]'
                : file && uploadStatus === 'success'
                ? 'border-green-500/50 bg-green-500/5 scale-[1.02]'
                : uploadStatus === 'error'
                ? 'border-red-500/50 bg-red-500/5'
                : 'border-border/50 hover:border-primary/50 hover:bg-accent/5'
            }`}
          >
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-5">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,_rgba(255,255,255,0.15)_1px,_transparent_0)] bg-[length:20px_20px]"></div>
            </div>
            
            <div className="relative">
              <div className={`mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full transition-all duration-300 ${
                file && uploadStatus === 'success'
                  ? 'bg-green-500 text-white'
                  : uploadStatus === 'error'
                  ? 'bg-red-500 text-white'
                  : 'bg-muted text-muted-foreground'
              }`}>
                {file && uploadStatus === 'success' ? (
                  <CheckCircle2 className="h-8 w-8" />
                ) : uploadStatus === 'error' ? (
                  <AlertCircle className="h-8 w-8" />
                ) : (
                  <Upload className="h-8 w-8" />
                )}
              </div>
              
              <div className="space-y-3">
                <h3 className="text-xl font-semibold">
                  {file && uploadStatus === 'success' ? (
                    <span className="flex items-center justify-center gap-2 text-green-500">
                      <FileText className="h-5 w-5" />
                      {file.name}
                    </span>
                  ) : uploadStatus === 'error' ? (
                    <span className="text-red-500">Invalid File Format</span>
                  ) : (
                    'Drop your KOI light curve file here'
                  )}
                </h3>
                <p className="text-muted-foreground">
                  {file && uploadStatus === 'success' ? (
                    `File size: ${(file.size / (1024 * 1024)).toFixed(2)} MB`
                  ) : uploadStatus === 'error' ? (
                    'Please upload CSV, FITS, TXT, or DAT files only'
                  ) : (
                    'Supports CSV, FITS, TXT, DAT files with time series data'
                  )}
                </p>
              </div>
              
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                <label className="inline-flex items-center justify-center gap-2 rounded-lg border border-primary/20 bg-primary/10 px-5 py-2.5 text-sm font-medium text-foreground backdrop-blur-sm transition-all duration-300 hover:border-primary/40 hover:bg-primary/20 cursor-pointer">
                  <Upload className="h-4 w-4" />
                  <span>Browse Files</span>
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".csv,.fits,.txt,.dat"
                    className="hidden"
                  />
                </label>
                
                {file && uploadStatus === 'success' && (
                  <>
                    <button
                      onClick={clearFile}
                      className="inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-background/50 px-5 py-2.5 text-sm font-medium text-foreground backdrop-blur-sm transition-all duration-300 hover:bg-accent"
                    >
                      Clear
                    </button>
                    
                    <button className="inline-flex items-center justify-center gap-2 rounded-lg border border-green-500/20 bg-green-500/10 px-5 py-2.5 text-sm font-medium text-green-500 backdrop-blur-sm transition-all duration-300 hover:border-green-500/40 hover:bg-green-500/20">
                      <Activity className="h-4 w-4" />
                      <span>Analyze Light Curve</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Additional Info */}
          {file && uploadStatus === 'success' && (
            <div className="mt-6 p-4 rounded-lg border border-primary/20 bg-primary/5">
              <div className="flex items-start gap-3">
                <Activity className="h-5 w-5 text-primary mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-semibold text-sm mb-2">Ready for Analysis</h4>
                  <p className="text-xs text-muted-foreground">
                    Your KOI light curve data is ready. Click "Analyze Light Curve" to detect transit events, 
                    measure orbital periods, and identify potential exoplanet candidates.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Sample Data Link */}
      <div className="text-center">
        <button className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <Download className="h-4 w-4" />
          <span>Download sample KOI light curve dataset</span>
        </button>
      </div>
    </div>
  );
}
