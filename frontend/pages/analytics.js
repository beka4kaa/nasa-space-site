import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import Header from '../components/Header';
import { ThemeProvider } from '../hooks/useTheme';
import { 
  BarChart3, 
  TrendingUp, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  Download,
  ArrowLeft,
  Loader2,
  Activity,
  Zap
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

// Import new chart components
import { DistributionChart } from '../components/charts/DistributionChart';
import { PlanetCharacteristicsChart } from '../components/charts/PlanetCharacteristicsChart';
import { ConfidenceAnalysisChart } from '../components/charts/ConfidenceAnalysisChart';
import { AdvancedMetrics } from '../components/charts/AdvancedMetrics';
import { HeatmapChart } from '../components/charts/HeatmapChart';

// Prediction card component with animation
function PredictionCard({ prediction, index, total }) {
  const getIcon = () => {
    switch (prediction.prediction) {
      case 'CONFIRMED':
        return <CheckCircle2 className="h-6 w-6 text-green-500" />;
      case 'FALSE POSITIVE':
        return <XCircle className="h-6 w-6 text-red-500" />;
      case 'CANDIDATE':
        return <AlertCircle className="h-6 w-6 text-yellow-500" />;
      default:
        return <Activity className="h-6 w-6 text-primary" />;
    }
  };

  const getColor = () => {
    switch (prediction.prediction) {
      case 'CONFIRMED':
        return 'border-green-500/20 bg-green-500/5';
      case 'FALSE POSITIVE':
        return 'border-red-500/20 bg-red-500/5';
      case 'CANDIDATE':
        return 'border-yellow-500/20 bg-yellow-500/5';
      default:
        return 'border-primary/20 bg-primary/5';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.4, 
        delay: index * 0.05,
        ease: [0.25, 0.1, 0.25, 1]
      }}
      whileHover={{ scale: 1.02, y: -4 }}
    >
      <Card className={`overflow-hidden ${getColor()} relative group`}>
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        <CardContent className="p-4 relative z-10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              {getIcon()}
              <div>
                <h4 className="font-semibold text-sm">Sample {index + 1}</h4>
                <p className="text-xs text-muted-foreground">{prediction.prediction}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold">{(prediction.confidence * 100).toFixed(1)}%</div>
              <div className="text-xs text-muted-foreground">confidence</div>
            </div>
          </div>

          {/* Probability bars */}
          <div className="space-y-2">
            {Object.entries(prediction.probabilities || {}).map(([key, value], idx) => {
              const percentage = value * 100;
              const barColor = 
                key === 'CONFIRMED' ? 'bg-green-500' :
                key === 'FALSE_POSITIVE' ? 'bg-red-500' :
                'bg-yellow-500';
              
              return (
                <motion.div 
                  key={key} 
                  className="space-y-1"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + (idx * 0.1) }}
                >
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">{key.replace('_', ' ')}</span>
                    <span className="font-medium">{percentage.toFixed(1)}%</span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full ${barColor}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{ 
                        duration: 1, 
                        delay: 0.3 + (idx * 0.1),
                        ease: [0.25, 0.1, 0.25, 1]
                      }}
                    />
                  </div>
                </motion.div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// Summary stats component
function SummaryStats({ summary, total }) {
  const stats = [
    {
      label: 'Confirmed',
      value: summary?.CONFIRMED || 0,
      icon: CheckCircle2,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      label: 'Candidates',
      value: summary?.CANDIDATE || 0,
      icon: AlertCircle,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
    },
    {
      label: 'False Positives',
      value: summary?.FALSE_POSITIVE || 0,
      icon: XCircle,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        const percentage = total > 0 ? (stat.value / total * 100).toFixed(1) : 0;
        
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ 
              duration: 0.5, 
              delay: index * 0.1,
              ease: [0.25, 0.1, 0.25, 1]
            }}
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <Card className="overflow-hidden border-0 bg-card/50 backdrop-blur-sm relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <CardContent className="p-6 relative z-10">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="text-right">
                  <motion.div 
                    className="text-3xl font-bold"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ 
                      type: "spring", 
                      stiffness: 200, 
                      delay: index * 0.15 
                    }}
                  >
                    {stat.value}
                  </motion.div>
                  <div className="text-sm text-muted-foreground">{percentage}%</div>
                </div>
              </div>
              <h3 className="font-semibold text-sm text-muted-foreground">{stat.label}</h3>
              <div className="mt-2 h-1 bg-muted rounded-full overflow-hidden">
                <motion.div
                  className={`h-full ${stat.color.replace('text-', 'bg-')}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ 
                    duration: 1, 
                    delay: index * 0.2,
                    ease: [0.25, 0.1, 0.25, 1]
                  }}
                />
              </div>
            </CardContent>
          </Card>
          </motion.div>
        );
      })}
    </div>
  );
}

export default function Analytics() {
  const router = useRouter();
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Get predictions from sessionStorage
    const storedPredictions = sessionStorage.getItem('predictions');
    
    if (storedPredictions) {
      try {
        const data = JSON.parse(storedPredictions);
        setPredictions(data);
      } catch (err) {
        setError('Failed to load predictions');
      }
    } else {
      setError('No predictions found. Please upload a dataset first.');
    }
    
    setLoading(false);
  }, []);

  const handleBack = () => {
    router.push('/');
  };

  const handleExport = () => {
    if (!predictions) return;
    
    const dataStr = JSON.stringify(predictions, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'koi_predictions.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <ThemeProvider>
        <Head>
          <title>Loading Analytics - NASA Explorer</title>
        </Head>
        <div className="min-h-screen bg-background text-foreground">
          <Header />
          <div className="flex items-center justify-center min-h-[80vh]">
            <motion.div 
              className="text-center space-y-4"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
              >
                <Activity className="h-12 w-12 text-primary mx-auto" />
              </motion.div>
              <p className="text-muted-foreground">Loading predictions...</p>
            </motion.div>
          </div>
        </div>
      </ThemeProvider>
    );
  }

  if (error || !predictions) {
    return (
      <ThemeProvider>
        <Head>
          <title>Analytics Error - NASA Explorer</title>
        </Head>
        <div className="min-h-screen bg-background text-foreground">
          <Header />
          <div className="flex items-center justify-center min-h-[80vh]">
            <Card className="max-w-md">
              <CardContent className="p-8 text-center space-y-4">
                <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
                <h2 className="text-xl font-bold">No Data Available</h2>
                <p className="text-muted-foreground">{error}</p>
                <button
                  onClick={handleBack}
                  className="inline-flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/10 px-5 py-2.5 text-sm font-medium transition-all hover:bg-primary/20"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Upload
                </button>
              </CardContent>
            </Card>
          </div>
        </div>
      </ThemeProvider>
    );
  }

  const { predictions: predictionList = [], total_samples = 0, summary = {} } = predictions;

  return (
    <ThemeProvider>
      <Head>
        <title>Analytics Dashboard - NASA Explorer</title>
        <meta name="description" content="KOI prediction analytics and results" />
      </Head>

      <div className="min-h-screen bg-background text-foreground">
        <Header />

        {/* Hero Section */}
        <section className="relative py-12 border-b border-border/10">
          <div className="container mx-auto px-4 max-w-7xl">
            <div className="flex items-center justify-between mb-6">
              <button
                onClick={handleBack}
                className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </button>
              <button
                onClick={handleExport}
                className="inline-flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/10 px-4 py-2 text-sm font-medium transition-all hover:bg-primary/20"
              >
                <Download className="h-4 w-4" />
                Export Results
              </button>
            </div>

            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-sm">
                <BarChart3 className="h-4 w-4 text-primary" />
                <span>Analysis Complete</span>
              </div>
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
                Prediction Results
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl">
                AI-powered analysis of {total_samples} KOI samples using XGBoost classification model
              </p>
            </div>
          </div>
        </section>

        {/* Summary Stats */}
        <section className="py-12">
          <div className="container mx-auto px-4 max-w-7xl">
            <SummaryStats summary={summary} total={total_samples} />
          </div>
        </section>

        {/* Advanced Analytics */}
        <section className="py-12 bg-muted/20">
          <div className="container mx-auto px-4 max-w-7xl">
            <div className="mb-8">
              <h2 className="text-3xl font-bold mb-2">Advanced Analytics</h2>
              <p className="text-muted-foreground">
                Comprehensive analysis of KOI data with interactive visualizations
              </p>
            </div>

            <div className="space-y-8">
              {/* Advanced Metrics */}
              <AdvancedMetrics 
                data={predictions.original_data || []} 
                predictions={predictionList} 
              />

              {/* Distribution and Characteristics */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                <DistributionChart 
                  data={predictionList}
                  title="Classification Distribution"
                />
                <PlanetCharacteristicsChart 
                  data={predictions.original_data || []}
                  title="Planet Characteristics"
                />
              </div>

              {/* Confidence Analysis */}
              <ConfidenceAnalysisChart 
                data={predictionList}
                title="Model Confidence Analysis"
              />

              {/* Heatmap */}
              <HeatmapChart 
                data={predictions.original_data || []}
                title="Discovery Heatmap: Period vs Radius"
              />
            </div>
          </div>
        </section>

        {/* Predictions Grid */}
        <section className="py-12 bg-muted/30">
          <div className="container mx-auto px-4 max-w-7xl">
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-2">Detailed Predictions</h2>
              <p className="text-muted-foreground">
                Individual classification results with confidence scores
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {predictionList.slice(0, 50).map((prediction, index) => (
                <PredictionCard
                  key={index}
                  prediction={prediction}
                  index={index}
                  total={total_samples}
                />
              ))}
            </div>

            {predictionList.length > 50 && (
              <div className="mt-8 text-center">
                <p className="text-muted-foreground">
                  Showing 50 of {predictionList.length} predictions
                </p>
              </div>
            )}
          </div>
        </section>
      </div>
    </ThemeProvider>
  );
}
