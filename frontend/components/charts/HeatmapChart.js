import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

export function HeatmapChart({ data, title }) {
  // Create heatmap data for period vs radius bins
  const heatmapData = React.useMemo(() => {
    if (!data || !data.length) return { matrix: [], xLabels: [], yLabels: [] };
    
    // Filter valid data
    const validData = data.filter(d => 
      d.koi_period && d.koi_prad && 
      !isNaN(parseFloat(d.koi_period)) && !isNaN(parseFloat(d.koi_prad))
    );

    if (validData.length === 0) return { matrix: [], xLabels: [], yLabels: [] };

    // Define bins
    const periodBins = [0, 10, 50, 100, 300, 1000, 5000];
    const radiusBins = [0, 0.5, 1, 2, 4, 8, 20];
    
    const xLabels = [
      '0-10 days', '10-50 days', '50-100 days', 
      '100-300 days', '300-1000 days', '1000+ days'
    ];
    
    const yLabels = [
      '< 0.5 R⊕', '0.5-1 R⊕', '1-2 R⊕', 
      '2-4 R⊕', '4-8 R⊕', '8+ R⊕'
    ];

    // Initialize matrix
    const matrix = Array(yLabels.length).fill().map(() => 
      Array(xLabels.length).fill().map(() => ({ count: 0, confirmed: 0 }))
    );

    // Populate matrix
    validData.forEach(d => {
      const period = parseFloat(d.koi_period);
      const radius = parseFloat(d.koi_prad);
      const isConfirmed = d.prediction === 'CONFIRMED' || d.koi_disposition === 'CONFIRMED';

      // Find period bin
      let periodBin = periodBins.length - 1;
      for (let i = 0; i < periodBins.length - 1; i++) {
        if (period >= periodBins[i] && period < periodBins[i + 1]) {
          periodBin = i;
          break;
        }
      }

      // Find radius bin
      let radiusBin = radiusBins.length - 1;
      for (let i = 0; i < radiusBins.length - 1; i++) {
        if (radius >= radiusBins[i] && radius < radiusBins[i + 1]) {
          radiusBin = i;
          break;
        }
      }

      if (periodBin < xLabels.length && radiusBin < yLabels.length) {
        matrix[radiusBin][periodBin].count++;
        if (isConfirmed) matrix[radiusBin][periodBin].confirmed++;
      }
    });

    return { matrix, xLabels, yLabels };
  }, [data]);

  // Find max count for color scaling
  const maxCount = React.useMemo(() => {
    if (!heatmapData.matrix.length) return 1;
    return Math.max(...heatmapData.matrix.flat().map(cell => cell.count));
  }, [heatmapData]);

  const getColor = (count, confirmed) => {
    if (count === 0) return 'bg-muted/20';
    const intensity = Math.min(count / maxCount, 1);
    const confirmedRatio = confirmed / count;
    
    if (confirmedRatio > 0.7) {
      // High confirmation rate - green
      return `bg-green-500` + (intensity > 0.5 ? '' : '/50');
    } else if (confirmedRatio > 0.3) {
      // Medium confirmation rate - yellow
      return `bg-yellow-500` + (intensity > 0.5 ? '' : '/50');
    } else {
      // Low confirmation rate - red
      return `bg-red-500` + (intensity > 0.5 ? '' : '/50');
    }
  };

  const getOpacity = (count) => {
    if (count === 0) return 0.1;
    return Math.min(0.3 + (count / maxCount) * 0.7, 1);
  };

  if (!heatmapData.matrix.length) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>{title || 'Planet Distribution Heatmap'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            No data available for heatmap visualization
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded-full"></div>
          {title || 'Planet Distribution: Period vs Radius'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Heatmap */}
          <div className="overflow-x-auto">
            <div className="min-w-[600px]">
              {/* X-axis labels */}
              <div className="flex mb-2">
                <div className="w-24"></div> {/* Space for Y-axis labels */}
                {heatmapData.xLabels.map((label, i) => (
                  <div key={i} className="flex-1 text-center text-xs text-muted-foreground px-1">
                    {label}
                  </div>
                ))}
              </div>
              
              {/* Matrix */}
              {heatmapData.matrix.map((row, i) => (
                <div key={i} className="flex items-center mb-1">
                  {/* Y-axis label */}
                  <div className="w-24 text-xs text-muted-foreground pr-3 text-right">
                    {heatmapData.yLabels[i]}
                  </div>
                  
                  {/* Row cells */}
                  {row.map((cell, j) => (
                    <div
                      key={j}
                      className="flex-1 mx-0.5 aspect-square relative group cursor-pointer"
                    >
                      <div
                        className={`w-full h-full rounded transition-all duration-200 ${getColor(cell.count, cell.confirmed)} hover:scale-110 hover:z-10 relative`}
                        style={{ opacity: getOpacity(cell.count) }}
                      >
                        {/* Tooltip */}
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className="text-xs font-bold text-white drop-shadow-sm">
                            {cell.count > 0 ? cell.count : ''}
                          </span>
                        </div>
                        
                        {/* Hover tooltip */}
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-background border border-border rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-20 whitespace-nowrap">
                          <div className="text-sm font-medium">
                            {heatmapData.yLabels[i]} × {heatmapData.xLabels[j]}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            <div>Total: {cell.count}</div>
                            <div>Confirmed: {cell.confirmed}</div>
                            <div>Rate: {cell.count > 0 ? ((cell.confirmed / cell.count) * 100).toFixed(1) : 0}%</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Legend */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Legend</span>
              <span className="text-xs text-muted-foreground">Brightness = Count, Color = Confirmation Rate</span>
            </div>
            
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span>High confirmation ({'>'} 70%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                <span>Medium confirmation (30-70%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span>Low confirmation ({'<'} 30%)</span>
              </div>
            </div>
          </div>

          {/* Insights */}
          <div className="mt-6 p-4 rounded-lg bg-muted/30 border border-border/50">
            <h4 className="font-semibold mb-2 flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              Insights
            </h4>
            <div className="text-sm text-muted-foreground space-y-1">
              <p>• Each cell represents the intersection of orbital period and planet radius ranges</p>
              <p>• Brighter cells indicate higher planet counts in that parameter space</p>
              <p>• Color indicates confirmation rate: green = high reliability, red = many false positives</p>
              <p>• Hover over cells for detailed statistics</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}