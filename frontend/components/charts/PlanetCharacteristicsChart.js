import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

export function PlanetCharacteristicsChart({ data, title }) {
  // Process data for scatter plot
  const processedData = React.useMemo(() => {
    if (!data || !data.length) return [];
    
    return data
      .filter(item => 
        item.koi_period && 
        item.koi_prad && 
        !isNaN(parseFloat(item.koi_period)) && 
        !isNaN(parseFloat(item.koi_prad))
      )
      .map((item, index) => ({
        period: parseFloat(item.koi_period),
        radius: parseFloat(item.koi_prad),
        temp: item.koi_teq ? parseFloat(item.koi_teq) : 0,
        prediction: item.prediction || item.koi_disposition || 'CANDIDATE',
        name: item.kepler_name || item.kepoi_name || `KOI-${index + 1}`,
        id: index
      }))
      .slice(0, 500); // Limit points for performance
  }, [data]);

  const getColor = (prediction) => {
    const colors = {
      'CONFIRMED': '#22c55e',
      'FALSE POSITIVE': '#ef4444',
      'CANDIDATE': '#f59e0b',
      'NOT EVALUATED': '#6b7280'
    };
    return colors[prediction] || colors['NOT EVALUATED'];
  };

  // Calculate statistics for display
  const stats = React.useMemo(() => {
    if (!processedData.length) return null;
    
    const periods = processedData.map(d => d.period);
    const radii = processedData.map(d => d.radius);
    const temps = processedData.filter(d => d.temp > 0).map(d => d.temp);
    
    return {
      avgPeriod: periods.reduce((sum, p) => sum + p, 0) / periods.length,
      avgRadius: radii.reduce((sum, r) => sum + r, 0) / radii.length,
      avgTemp: temps.length > 0 ? temps.reduce((sum, t) => sum + t, 0) / temps.length : 0,
      minPeriod: Math.min(...periods),
      maxPeriod: Math.max(...periods),
      minRadius: Math.min(...radii),
      maxRadius: Math.max(...radii),
      totalCount: processedData.length
    };
  }, [processedData]);

  if (!stats) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>{title || 'Planet Characteristics'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            No data available for characteristics analysis
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
          {title || 'Planet Characteristics Analysis'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Key Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
              <h4 className="font-semibold mb-2 text-sm text-muted-foreground">Orbital Period</h4>
              <div className="space-y-1">
                <p className="text-lg font-bold text-primary">{stats.avgPeriod.toFixed(1)} days</p>
                <p className="text-xs text-muted-foreground">
                  Range: {stats.minPeriod.toFixed(1)} - {stats.maxPeriod.toFixed(1)} days
                </p>
              </div>
            </div>
            
            <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
              <h4 className="font-semibold mb-2 text-sm text-muted-foreground">Planet Radius</h4>
              <div className="space-y-1">
                <p className="text-lg font-bold text-primary">{stats.avgRadius.toFixed(2)} R⊕</p>
                <p className="text-xs text-muted-foreground">
                  Range: {stats.minRadius.toFixed(2)} - {stats.maxRadius.toFixed(2)} R⊕
                </p>
              </div>
            </div>
            
            <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
              <h4 className="font-semibold mb-2 text-sm text-muted-foreground">Temperature</h4>
              <div className="space-y-1">
                <p className="text-lg font-bold text-primary">
                  {stats.avgTemp > 0 ? `${stats.avgTemp.toFixed(0)} K` : 'N/A'}
                </p>
                <p className="text-xs text-muted-foreground">
                  Equilibrium temperature
                </p>
              </div>
            </div>
          </div>

          {/* Classification Breakdown */}
          <div className="space-y-4">
            <h4 className="font-semibold">Classification Breakdown</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {['CONFIRMED', 'FALSE POSITIVE', 'CANDIDATE', 'NOT EVALUATED'].map(prediction => {
                const count = processedData.filter(d => d.prediction === prediction).length;
                if (count === 0) return null;
                
                const percentage = (count / stats.totalCount) * 100;
                
                return (
                  <div key={prediction} className="p-3 rounded-lg bg-muted/50 text-center">
                    <div 
                      className="w-4 h-4 rounded-full mx-auto mb-2"
                      style={{ backgroundColor: getColor(prediction) }}
                    ></div>
                    <p className="text-sm font-medium">{prediction}</p>
                    <p className="text-lg font-bold text-primary">{count}</p>
                    <p className="text-xs text-muted-foreground">{percentage.toFixed(1)}%</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sample Data Preview */}
          <div className="space-y-4">
            <h4 className="font-semibold">Sample Objects</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-64 overflow-y-auto">
              {processedData.slice(0, 6).map((item, index) => (
                <div key={index} className="p-3 rounded-lg border border-border/50 bg-background">
                  <div className="flex items-center gap-2 mb-2">
                    <div 
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: getColor(item.prediction) }}
                    ></div>
                    <span className="font-medium text-sm">{item.name}</span>
                  </div>
                  <div className="space-y-1 text-xs text-muted-foreground">
                    <p>Period: {item.period.toFixed(1)} days</p>
                    <p>Radius: {item.radius.toFixed(2)} R⊕</p>
                    {item.temp > 0 && <p>Temperature: {item.temp.toFixed(0)} K</p>}
                    <p className="font-medium text-foreground">{item.prediction}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Insights */}
          <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
            <h4 className="font-semibold mb-2 flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              Key Insights
            </h4>
            <div className="text-sm text-muted-foreground space-y-1">
              <p>• Analyzed {stats.totalCount} objects with period and radius measurements</p>
              <p>• Confirmed planets tend to have well-constrained orbital and physical parameters</p>
              <p>• Period-radius relationship helps distinguish planet types (rocky vs gaseous)</p>
              <p>• Temperature estimates help identify potentially habitable worlds</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}