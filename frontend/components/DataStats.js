import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { TrendingUp, Database, FileText, Clock } from 'lucide-react';

export const StatsCard = ({ icon: Icon, title, value, description, trend }) => {
  return (
    <Card className="relative overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
        {trend && (
          <div className="flex items-center pt-1">
            <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
            <span className="text-xs text-green-500">{trend}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export const DataStats = ({ data }) => {
  if (!data || !data.data) return null;

  const rowCount = data.data.length;
  const columnCount = data.columns ? data.columns.length : 0;
  const fileSize = ((JSON.stringify(data).length / 1024) / 1024).toFixed(2);

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <StatsCard
        icon={Database}
        title="Total Records"
        value={rowCount.toLocaleString()}
        description="Rows of data"
      />
      <StatsCard
        icon={FileText}
        title="Columns"
        value={columnCount}
        description="Data fields"
      />
      <StatsCard
        icon={TrendingUp}
        title="File Size"
        value={`${fileSize} MB`}
        description="Memory usage"
      />
      <StatsCard
        icon={Clock}
        title="Status"
        value="Ready"
        description="Analysis complete"
        trend="100% processed"
      />
    </div>
  );
};