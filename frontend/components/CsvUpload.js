import * as React from 'react';
import axios from 'axios';
import { Upload, FileText, Loader2, AlertCircle, CheckCircle2, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import ModernCsvTable from './ModernCsvTable';

export default function CsvUpload() {
  const [file, setFile] = React.useState(null);
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');
  const [filename, setFilename] = React.useState('');

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError('');
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file.');
      return;
    }
    if (!(file.name.endsWith('.csv') || file.name.endsWith('.xls') || file.name.endsWith('.xlsx'))) {
      setError('Only CSV, XLS, and XLSX files are allowed.');
      return;
    }
    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setData(res.data);
      setFilename(res.data.filename);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!filename) return;
    axios({
      url: `http://localhost:8000/download/${filename}`,
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
      <div className="text-center space-y-3">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
          <Sparkles className="h-8 w-8 text-primary" />
        </div>
        <h2 className="text-3xl font-bold tracking-tight">Upload Astronomical Data</h2>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Analyze exoplanet data from the Kepler mission and discover hidden patterns in the cosmos
        </p>
      </div>

      {/* Upload Card */}
      <Card className="overflow-hidden border-0 shadow-lg bg-card/50 backdrop-blur-sm">
        <CardContent className="p-8">
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
              file 
                ? 'border-primary bg-primary/5 scale-[1.02]' 
                : 'border-border/50 hover:border-primary/50 hover:bg-accent/5'
            }`}
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
          </div>
          
          <div className="mt-8">
            <Button
              onClick={handleUpload}
              disabled={loading || !file}
              className="w-full h-12 text-base font-medium"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing cosmic data...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-5 w-5" />
                  Launch Analysis
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
              <div>
                <p className="font-medium text-destructive">Upload Error</p>
                <p className="text-sm text-destructive/80 mt-1">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

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
