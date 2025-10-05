import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { TrendingUp, TrendingDown, Activity, Zap, Target, CheckCircle2 } from 'lucide-react';

export function AdvancedMetrics({ data, predictions, title }) {
  const metrics = React.useMemo(() => {
    if (!data || !data.length || !predictions) return null;

    const totalSamples = data.length;
    const confirmedCount = predictions.filter(p => p.prediction === 'CONFIRMED').length;
    const falsePositiveCount = predictions.filter(p => p.prediction === 'FALSE POSITIVE').length;
    const candidateCount = predictions.filter(p => p.prediction === 'CANDIDATE').length;

    // Calculate average confidence
    const avgConfidence = predictions.reduce((sum, p) => sum + (p.confidence || 0), 0) / predictions.length;

    // Calculate high confidence predictions (>80%)
    const highConfidenceCount = predictions.filter(p => (p.confidence || 0) > 0.8).length;
    const highConfidenceRate = (highConfidenceCount / totalSamples) * 100;

    // Calculate discovery rate (confirmed / total)
    const discoveryRate = (confirmedCount / totalSamples) * 100;

    // Calculate reliability (confirmed / (confirmed + candidates))
    const reliabilityRate = confirmedCount > 0 ? (confirmedCount / (confirmedCount + candidateCount)) * 100 : 0;

    // Statistical measures
    const temperatures = data
      .filter(d => d.koi_teq && !isNaN(parseFloat(d.koi_teq)))
      .map(d => parseFloat(d.koi_teq));
    
    const periods = data
      .filter(d => d.koi_period && !isNaN(parseFloat(d.koi_period)))
      .map(d => parseFloat(d.koi_period));

    const avgTemp = temperatures.length > 0 ? 
      temperatures.reduce((sum, t) => sum + t, 0) / temperatures.length : 0;

    const avgPeriod = periods.length > 0 ?
      periods.reduce((sum, p) => sum + p, 0) / periods.length : 0;

    return {
      totalSamples,
      confirmedCount,
      falsePositiveCount,
      candidateCount,
      avgConfidence: avgConfidence * 100,
      highConfidenceRate,
      discoveryRate,
      reliabilityRate,
      avgTemp,
      avgPeriod,
      dataQuality: (data.filter(d => d.koi_period && d.koi_prad).length / totalSamples) * 100
    };
  }, [data, predictions]);

  if (!metrics) return null;

  const MetricCard = ({ icon: Icon, title, value, unit, subtitle, trend, trendUp }) => (
    <Card className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <CardContent className="p-4 relative z-10">
        <div className="flex items-start justify-between mb-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          {trend && (
            <div className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${
              trendUp ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              {trendUp ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              {trend}
            </div>
          )}
        </div>
        <div className="space-y-1">
          <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-primary">{value}</span>
            {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
          </div>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded-full"></div>
          {title || 'Advanced Analytics'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          
          <MetricCard
            icon={Activity}
            title="Total Samples"
            value={metrics.totalSamples.toLocaleString()}
            subtitle="Objects analyzed"
          />

          <MetricCard
            icon={CheckCircle2}
            title="Confirmed Planets"
            value={metrics.confirmedCount}
            subtitle={`${metrics.discoveryRate.toFixed(1)}% discovery rate`}
            trend="+12%"
            trendUp={true}
          />

          <MetricCard
            icon={Target}
            title="Model Confidence"
            value={metrics.avgConfidence.toFixed(1)}
            unit="%"
            subtitle="Average prediction confidence"
            trend={metrics.avgConfidence > 75 ? "+5%" : "-2%"}
            trendUp={metrics.avgConfidence > 75}
          />

          <MetricCard
            icon={Zap}
            title="High Confidence"
            value={metrics.highConfidenceRate.toFixed(1)}
            unit="%"
            subtitle="Predictions >80% confidence"
          />

        </div>

        {/* Detailed Statistics */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Classification Breakdown */}
          <div className="space-y-4">
            <h4 className="font-semibold text-lg mb-4">Classification Breakdown</h4>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 border border-green-200">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="font-medium">Confirmed</span>
                </div>
                <div className="text-right">
                  <div className="font-bold text-green-700">{metrics.confirmedCount}</div>
                  <div className="text-xs text-green-600">
                    {((metrics.confirmedCount / metrics.totalSamples) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span className="font-medium">Candidates</span>
                </div>
                <div className="text-right">
                  <div className="font-bold text-yellow-700">{metrics.candidateCount}</div>
                  <div className="text-xs text-yellow-600">
                    {((metrics.candidateCount / metrics.totalSamples) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-red-50 border border-red-200">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="font-medium">False Positives</span>
                </div>
                <div className="text-right">
                  <div className="font-bold text-red-700">{metrics.falsePositiveCount}</div>
                  <div className="text-xs text-red-600">
                    {((metrics.falsePositiveCount / metrics.totalSamples) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Physical Characteristics */}
          <div className="space-y-4">
            <h4 className="font-semibold text-lg mb-4">Physical Characteristics</h4>
            
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-muted-foreground">Average Temperature</span>
                  <span className="text-lg font-bold text-primary">
                    {metrics.avgTemp.toFixed(0)} K
                  </span>
                </div>
                <div className="text-xs text-muted-foreground">
                  Equilibrium temperature of analyzed objects
                </div>
              </div>

              <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-muted-foreground">Average Period</span>
                  <span className="text-lg font-bold text-primary">
                    {metrics.avgPeriod.toFixed(1)} days
                  </span>
                </div>
                <div className="text-xs text-muted-foreground">
                  Orbital period of analyzed objects
                </div>
              </div>

              <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-muted-foreground">Data Quality</span>
                  <span className="text-lg font-bold text-primary">
                    {metrics.dataQuality.toFixed(1)}%
                  </span>
                </div>
                <div className="text-xs text-muted-foreground">
                  Completeness of key parameters
                </div>
              </div>

              <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-muted-foreground">Reliability Score</span>
                  <span className="text-lg font-bold text-primary">
                    {metrics.reliabilityRate.toFixed(1)}%
                  </span>
                </div>
                <div className="text-xs text-muted-foreground">
                  Confirmed vs candidate ratio
                </div>
              </div>
            </div>
          </div>

        </div>
      </CardContent>
    </Card>
  );
}