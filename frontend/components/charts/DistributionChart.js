import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

const COLORS = {
  'CONFIRMED': '#22c55e',
  'FALSE POSITIVE': '#ef4444', 
  'CANDIDATE': '#f59e0b',
  'NOT EVALUATED': '#6b7280'
};

export function DistributionChart({ data, title }) {
  // Process data for bar chart
  const processedData = React.useMemo(() => {
    if (!data || !data.length) return [];
    
    const distribution = data.reduce((acc, item) => {
      const prediction = item.prediction || item.koi_disposition || 'NOT EVALUATED';
      acc[prediction] = (acc[prediction] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(distribution).map(([name, value]) => ({
      name: name.replace('_', ' '),
      value,
      color: COLORS[name] || COLORS['NOT EVALUATED']
    }));
  }, [data]);

  const totalCount = processedData.reduce((sum, item) => sum + item.value, 0);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded-full"></div>
          {title || 'Classification Distribution'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Simple Bar Chart */}
          <div className="space-y-4">
            {processedData.map((item, index) => {
              const percentage = totalCount > 0 ? (item.value / totalCount) * 100 : 0;
              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      ></div>
                      <span className="font-medium">{item.name}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-bold text-primary">{item.value}</span>
                      <span className="text-sm text-muted-foreground ml-2">
                        ({percentage.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                  <div className="h-3 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full transition-all duration-1000 ease-out rounded-full"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: item.color
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Summary Statistics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-border/50">
            {processedData.map((item, index) => (
              <div key={index} className="text-center p-3 rounded-lg bg-muted/50">
                <div 
                  className="w-4 h-4 rounded-full mx-auto mb-2"
                  style={{ backgroundColor: item.color }}
                ></div>
                <p className="text-sm font-medium">{item.name}</p>
                <p className="text-lg font-bold text-primary">{item.value}</p>
              </div>
            ))}
          </div>

          {/* Insights */}
          <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
            <h4 className="font-semibold mb-2 flex items-center gap-2">
              <div className="w-2 h-2 bg-primary rounded-full"></div>
              Classification Summary
            </h4>
            <div className="text-sm text-muted-foreground space-y-1">
              <p>• Total objects analyzed: <span className="font-medium text-foreground">{totalCount}</span></p>
              <p>• Confirmed planets make up the highest confidence predictions</p>
              <p>• Candidates require additional observations for confirmation</p>
              <p>• False positives help refine detection algorithms</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}