import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Search, Download, ArrowUpDown, ChevronLeft, ChevronRight, Eye, Filter, MoreHorizontal } from 'lucide-react';
import { DataStats } from './DataStats';

export default function CsvTable({ data, onDownload, filename }) {
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(15);
  const [orderBy, setOrderBy] = React.useState('');
  const [order, setOrder] = React.useState('asc');
  const [filter, setFilter] = React.useState('');
  const [selectedRows, setSelectedRows] = React.useState(new Set());

  if (!data || !data.data || !data.columns) {
    return null;
  }

  const { columns, data: rows } = data;

  const handleSort = (column) => {
    const isAsc = orderBy === column && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(column);
    setPage(0); // Reset to first page when sorting
  };

  const filteredRows = rows.filter(row =>
    Object.values(row).some(value =>
      value && String(value).toLowerCase().includes(filter.toLowerCase())
    )
  );

  const sortedRows = React.useMemo(() => {
    if (!orderBy) return filteredRows;
    
    return [...filteredRows].sort((a, b) => {
      const aVal = a[orderBy];
      const bVal = b[orderBy];
      
      // Handle numeric values
      const aNum = parseFloat(aVal);
      const bNum = parseFloat(bVal);
      
      if (!isNaN(aNum) && !isNaN(bNum)) {
        return order === 'asc' ? aNum - bNum : bNum - aNum;
      }
      
      // Handle string values
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      
      if (order === 'asc') {
        return aStr < bStr ? -1 : aStr > bStr ? 1 : 0;
      } else {
        return aStr > bStr ? -1 : aStr < bStr ? 1 : 0;
      }
    });
  }, [filteredRows, orderBy, order]);

  const paginatedRows = sortedRows.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const totalPages = Math.ceil(sortedRows.length / rowsPerPage);

  const formatCellValue = (value) => {
    if (value === null || value === undefined || value === '') {
      return <span className="text-muted-foreground italic">—</span>;
    }
    
    // Check if it's a number
    const num = parseFloat(value);
    if (!isNaN(num) && isFinite(num)) {
      // Format large numbers with commas and limit decimals
      if (Math.abs(num) >= 1000) {
        return num.toLocaleString(undefined, { maximumFractionDigits: 3 });
      } else if (num % 1 !== 0) {
        return num.toFixed(6).replace(/\.?0+$/, '');
      }
      return num.toString();
    }
    
    return String(value);
  };

  const getCellClassName = (value, columnName) => {
    const baseClass = "px-4 py-3 text-sm";
    
    // Check if it's a number for right alignment
    const num = parseFloat(value);
    if (!isNaN(num) && isFinite(num)) {
      return `${baseClass} text-right font-mono`;
    }
    
    return baseClass;
  };

  return (
    <div className="space-y-6">
      {/* Stats */}
      <DataStats data={data} />

      {/* Header */}
      <Card className="border-0 shadow-lg bg-card/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-primary" />
                Data Explorer
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                {filename ? `Viewing: ${filename}` : 'Astronomical dataset analysis'}
              </p>
            </div>
            
            {onDownload && (
              <Button onClick={onDownload} variant="outline" className="gap-2">
                <Download className="h-4 w-4" />
                Download
              </Button>
            )}
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Search and Controls */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <input
                type="text"
                placeholder="Search data..."
                value={filter}
                onChange={(e) => {
                  setFilter(e.target.value);
                  setPage(0); // Reset to first page when filtering
                }}
                className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-md text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground">
                {sortedRows.length} rows
              </div>
              
              <select
                value={rowsPerPage}
                onChange={(e) => {
                  setRowsPerPage(Number(e.target.value));
                  setPage(0);
                }}
                className="px-3 py-1 text-sm bg-background border border-border rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value={10}>10</option>
                <option value={15}>15</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>

          {/* Table */}
          <div className="rounded-lg border overflow-hidden">
            <div className="overflow-x-auto max-h-[600px]">
              <table className="w-full text-sm">
                <thead className="bg-muted/50 sticky top-0 z-10">
                  <tr className="border-b">
                    {columns.map((column) => (
                      <th
                        key={column}
                        className="px-4 py-3 text-left font-medium text-muted-foreground cursor-pointer hover:bg-muted/80 transition-colors group"
                        onClick={() => handleSort(column)}
                      >
                        <div className="flex items-center gap-2">
                          <span className="truncate max-w-[150px]" title={column}>
                            {column}
                          </span>
                          <ArrowUpDown className={`h-3 w-3 transition-all ${
                            orderBy === column 
                              ? 'text-primary opacity-100' 
                              : 'text-muted-foreground opacity-0 group-hover:opacity-50'
                          }`} />
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {paginatedRows.map((row, index) => (
                    <tr
                      key={`row-${page * rowsPerPage + index}`}
                      className="hover:bg-muted/30 transition-colors"
                    >
                      {columns.map((column) => (
                        <td
                          key={`${column}-${index}`}
                          className={getCellClassName(row[column], column)}
                          title={String(row[column] || '')}
                        >
                          <div className="max-w-[200px] truncate">
                            {formatCellValue(row[column])}
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4">
              <div className="text-sm text-muted-foreground">
                Showing {page * rowsPerPage + 1} to {Math.min((page + 1) * rowsPerPage, sortedRows.length)} of {sortedRows.length} results
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="gap-1"
                >
                  <ChevronLeft className="h-3 w-3" />
                  Previous
                </Button>
                
                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const pageNumber = Math.max(0, Math.min(totalPages - 5, page - 2)) + i;
                    return (
                      <Button
                        key={pageNumber}
                        variant={page === pageNumber ? "default" : "ghost"}
                        size="sm"
                        onClick={() => setPage(pageNumber)}
                        className="w-8 h-8 p-0"
                      >
                        {pageNumber + 1}
                      </Button>
                    );
                  })}
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page >= totalPages - 1}
                  className="gap-1"
                >
                  Next
                  <ChevronRight className="h-3 w-3" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}