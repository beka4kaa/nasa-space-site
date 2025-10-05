import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

export function ConfidenceAnalysisChart({ data, title }) {
  // Process confidence distribution data
  const confidenceData = React.useMemo(() => {
    if (!data || !data.length) return [];
    
    // Create confidence bins
    const bins = [];
    for (let i = 0; i < 10; i++) {
      bins.push({
        range: `${i * 10}-${(i + 1) * 10}%`,
        min: i * 0.1,
        max: (i + 1) * 0.1,
        confirmed: 0,
        falsePositive: 0,
        candidate: 0,
        total: 0
      });
    }
    
    // Categorize predictions by confidence ranges
    data.forEach(item => {
      const confidence = item.confidence || 0;
      const prediction = item.prediction || 'CANDIDATE';
      
      const binIndex = Math.min(Math.floor(confidence * 10), 9);
      bins[binIndex].total++;
      
      switch (prediction) {
        case 'CONFIRMED':
          bins[binIndex].confirmed++;
          break;
        case 'FALSE POSITIVE':
          bins[binIndex].falsePositive++;
          break;
        default:
          bins[binIndex].candidate++;
      }
    });
    
    return bins;
  }, [data]);

  // Average confidence by prediction type
  const avgConfidenceData = React.useMemo(() => {
    if (!data || !data.length) return [];
    
    const grouped = data.reduce((acc, item) => {
      const prediction = item.prediction || 'CANDIDATE';
      if (!acc[prediction]) {
        acc[prediction] = { sum: 0, count: 0 };
      }
      acc[prediction].sum += item.confidence || 0;
      acc[prediction].count++;
      return acc;
    }, {});
    
    return Object.entries(grouped).map(([prediction, stats]) => ({
      prediction,
      avgConfidence: stats.sum / stats.count,
      count: stats.count
    }));
  }, [data]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Confidence Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-3 h-3 bg-primary rounded-full"></div>
            Confidence Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {confidenceData.map((bin, index) => {
              const maxTotal = Math.max(...confidenceData.map(b => b.total));
              const width = maxTotal > 0 ? (bin.total / maxTotal) * 100 : 0;
              
              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="font-medium">{bin.range}</span>
                    <span className="text-muted-foreground">Total: {bin.total}</span>
                  </div>
                  
                  <div className="relative h-8 bg-muted rounded-lg overflow-hidden">
                    {/* Stacked bars */}
                    <div className="absolute inset-0 flex">
                      {bin.confirmed > 0 && (
                        <div 
                          className="bg-green-500 h-full flex items-center justify-center text-xs text-white font-medium"
                          style={{ width: `${(bin.confirmed / bin.total) * width}%` }}
                        >
                          {bin.confirmed > 2 ? bin.confirmed : ''}
                        </div>
                      )}
                      {bin.candidate > 0 && (
                        <div 
                          className="bg-yellow-500 h-full flex items-center justify-center text-xs text-white font-medium"
                          style={{ width: `${(bin.candidate / bin.total) * width}%` }}
                        >
                          {bin.candidate > 2 ? bin.candidate : ''}
                        </div>
                      )}
                      {bin.falsePositive > 0 && (
                        <div 
                          className="bg-red-500 h-full flex items-center justify-center text-xs text-white font-medium"
                          style={{ width: `${(bin.falsePositive / bin.total) * width}%` }}
                        >
                          {bin.falsePositive > 2 ? bin.falsePositive : ''}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>C: {bin.confirmed}</span>
                    <span>Ca: {bin.candidate}</span>
                    <span>FP: {bin.falsePositive}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Average Confidence by Type */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-3 h-3 bg-primary rounded-full"></div>
            Average Confidence by Type
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {avgConfidenceData.map((item, index) => {
              const color = 
                item.prediction === 'CONFIRMED' ? 'bg-green-500' :
                item.prediction === 'FALSE POSITIVE' ? 'bg-red-500' :
                'bg-yellow-500';
              
              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{item.prediction}</span>
                    <div className="text-right">
                      <span className="text-lg font-bold text-primary">
                        {(item.avgConfidence * 100).toFixed(1)}%
                      </span>
                      <span className="text-sm text-muted-foreground ml-2">
                        ({item.count} samples)
                      </span>
                    </div>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${color} transition-all duration-1000 ease-out`}
                      style={{ width: `${item.avgConfidence * 100}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Model Performance Metrics */}
          <div className="mt-6 p-4 rounded-lg bg-muted/30 border border-border/50">
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              Model Performance
            </h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground mb-1">High Confidence ({'>'}80%)</p>
                <p className="font-bold text-primary">
                  {confidenceData.slice(8).reduce((sum, bin) => sum + bin.total, 0)} predictions
                </p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1">Low Confidence ({'<'}50%)</p>
                <p className="font-bold text-primary">
                  {confidenceData.slice(0, 5).reduce((sum, bin) => sum + bin.total, 0)} predictions
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}