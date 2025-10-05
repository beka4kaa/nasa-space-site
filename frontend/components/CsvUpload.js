import * as React from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Loader2, AlertCircle, CheckCircle2, BarChart3, Activity } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import ModernCsvTable from './ModernCsvTable';
import { API_ENDPOINTS, FILE_UPLOAD_CONFIG, apiUtils } from '../lib/api';

export default function CsvUpload() {
  const router = useRouter();
  const [file, setFile] = React.useState(null);
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [predicting, setPredicting] = React.useState(false);
  const [error, setError] = React.useState('');
  const [filename, setFilename] = React.useState('');
  const [loadingMessage, setLoadingMessage] = React.useState('');

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError('');
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      try {
        const selectedFile = e.target.files[0];
        apiUtils.validateFile(selectedFile);
        setFile(selectedFile);
        setError('');
      } catch (err) {
        setError(err.message);
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file.');
      return;
    }
    const allowedExtensions = ['.csv', '.xls', '.xlsx'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedExtensions.includes(fileExtension)) {
      setError('Only CSV, XLS, and XLSX files are supported for KOI analysis.');
      return;
    }
    
    setLoading(true);
    setPredicting(true);
    setError('');
    setLoadingMessage('Validating file format...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      // Валидация датасета перед предсказанием
      setLoadingMessage('Validating dataset structure...');
      try {
        await axios.post(API_ENDPOINTS.validateDataset, formData, FILE_UPLOAD_CONFIG);
      } catch (validationErr) {
        throw {
          response: {
            status: 400,
            data: {
              detail: validationErr.response?.data?.detail || 
                     'Invalid file format. Please ensure the file (CSV/XLS/XLSX) is properly formatted and contains the required KOI columns.'
            }
          }
        };
      }
      
      // Теперь отправляем на endpoint предсказаний
      setLoadingMessage('Running AI model predictions...');
      const predictRes = await axios.post(API_ENDPOINTS.predict, formData, FILE_UPLOAD_CONFIG);
      
            // Format and store predictions for analytics
      const formattedData = apiUtils.formatPredictionData(predictRes.data);
      sessionStorage.setItem('predictions', JSON.stringify(formattedData));
      sessionStorage.setItem('filename', filename);
      
      // Небольшая задержка для красоты
      setLoadingMessage('Preparing analytics...');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Перенаправляем на страницу аналитики
      router.push('/analytics');
      
    } catch (err) {
      setPredicting(false);
      setLoading(false);
      
      let errorMessage = 'Failed to analyze data. Please try again.';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
        
        // Улучшенные сообщения об ошибках
        if (errorMessage.includes('tokenizing') || errorMessage.includes('C error')) {
          errorMessage = 'File format is invalid. The file may be corrupted or have inconsistent columns. Please check that:\n• All rows have the same number of columns\n• No extra commas or line breaks in data (for CSV)\n• File is not password protected (for XLS/XLSX)\n• File encoding is UTF-8 (for CSV)';
        } else if (errorMessage.includes('required columns')) {
          errorMessage = 'Dataset is missing required KOI columns. Please use the official Kepler KOI dataset.';
        }
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error during prediction. Please try again or contact support.';
      }
      
      setError(errorMessage);
    }
  };

  const handleDownload = () => {
    if (!filename) return;
    axios({
      url: API_ENDPOINTS.download(filename),
      method: 'GET',
      responseType: 'blob',
    }).then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    });
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8" id="upload">
      {/* Header Section */}
      <motion.div 
        className="text-center space-y-3"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <motion.div 
          className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4 relative"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <div className="absolute inset-0 rounded-full bg-primary/20 blur-xl animate-pulse" />
          <Activity className="h-8 w-8 text-primary relative z-10" />
        </motion.div>
        <h2 className="text-3xl font-bold tracking-tight">Upload Astronomical Data</h2>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Analyze exoplanet data from the Kepler mission and discover hidden patterns in the cosmos
        </p>
        <motion.div 
          className="text-xs text-muted-foreground max-w-xl mx-auto mt-2 p-3 bg-muted/30 rounded-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <p className="font-medium mb-1">File Requirements:</p>
          <p>• File must be properly formatted with consistent columns</p>
          <p>• Use UTF-8 encoding</p>
          <p>• Compatible with Kepler KOI dataset format</p>
        </motion.div>
      </motion.div>

      {/* Upload Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Card className="overflow-hidden border-0 shadow-lg bg-card/50 backdrop-blur-sm">
          <CardContent className="p-8">
            <motion.div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
                file 
                  ? 'border-primary bg-primary/5' 
                  : 'border-border/50 hover:border-primary/50 hover:bg-accent/5'
              }`}
              whileHover={!file ? { scale: 1.01 } : {}}
              animate={file ? { scale: 1.02 } : { scale: 1 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-5">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,_rgba(255,255,255,0.15)_1px,_transparent_0)] bg-[length:20px_20px]"></div>
              </div>
            
            <div className="relative">
              <div className={`mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full transition-all duration-300 ${
                file ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
              }`}>
                {file ? (
                  <CheckCircle2 className="h-8 w-8" />
                ) : (
                  <Upload className="h-8 w-8" />
                )}
              </div>
              
              <div className="space-y-3">
                <h3 className="text-xl font-semibold">
                  {file ? (
                    <span className="flex items-center justify-center gap-2">
                      <FileText className="h-5 w-5" />
                      {file.name}
                    </span>
                  ) : (
                    'Drop your files here'
                  )}
                </h3>
                <p className="text-muted-foreground">
                  {file ? (
                    `File size: ${(file.size / (1024 * 1024)).toFixed(2)} MB`
                  ) : (
                    'Supports CSV, XLS, XLSX files up to 50MB'
                  )}
                </p>
              </div>
              
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                <Button variant="outline" size="lg" asChild className="min-w-[160px]">
                  <label className="cursor-pointer">
                    <FileText className="mr-2 h-4 w-4" />
                    Browse Files
                    <input 
                      type="file" 
                      accept=".csv,.xls,.xlsx" 
                      hidden 
                      onChange={handleFileChange} 
                    />
                  </label>
                </Button>
                
                {file && (
                  <Button
                    onClick={() => {setFile(null); setError(''); setData(null);}}
                    variant="ghost"
                    size="lg"
                    className="min-w-[160px]"
                  >
                    Clear Selection
                  </Button>
                )}
              </div>
            </div>
          </motion.div>
          
          <div className="mt-8 space-y-4">
            <motion.div
              whileHover={{ scale: file && !loading ? 1.02 : 1 }}
              whileTap={{ scale: file && !loading ? 0.98 : 1 }}
            >
              <Button
                onClick={handleUpload}
                disabled={loading || !file}
                className="w-full h-12 text-base font-medium group relative overflow-hidden"
                size="lg"
              >
                <span className="relative z-10 flex items-center justify-center">
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                      <span>{loadingMessage}</span>
                    </>
                  ) : (
                    <>
                      <BarChart3 className="mr-2 h-5 w-5 transition-transform group-hover:scale-110" />
                      Launch AI Analysis
                    </>
                  )}
                </span>
              </Button>
            </motion.div>
            
            {/* Progress indicator */}
            <AnimatePresence>
              {predicting && (
                <motion.div 
                  className="space-y-2"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="w-full h-1 bg-muted rounded-full overflow-hidden relative">
                    <motion.div 
                      className="absolute inset-0 bg-primary"
                      initial={{ x: "-100%" }}
                      animate={{ x: "100%" }}
                      transition={{ 
                        repeat: Infinity, 
                        duration: 1.5, 
                        ease: "easeInOut" 
                      }}
                    />
                  </div>
                  <motion.p 
                    className="text-sm text-center text-muted-foreground"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    Processing {file?.name}...
                  </motion.p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </CardContent>
      </Card>
      </motion.div>

      {/* Error Alert */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="border-destructive/50 bg-destructive/5">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <motion.div
                    animate={{ rotate: [0, 10, -10, 10, 0] }}
                    transition={{ duration: 0.5 }}
                    className="mt-0.5"
                  >
                    <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
                  </motion.div>
                  <div className="flex-1">
                    <p className="font-medium text-destructive">Upload Error</p>
                    <div className="text-sm text-destructive/80 mt-1 whitespace-pre-line">
                      {error}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      {data && (
        <div className="animate-in fade-in-50 slide-in-from-bottom-4 duration-700" id="data">
          <ModernCsvTable 
            data={data} 
            onDownload={handleDownload}
            filename={filename}
          />
        </div>
      )}
    </div>
  );
}
