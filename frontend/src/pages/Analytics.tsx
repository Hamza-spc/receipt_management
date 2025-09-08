import React, { useState, useEffect } from 'react';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { 
  TrendingUp, 
  DollarSign, 
  Calendar, 
  PieChart,
  BarChart3,
  LineChart
} from 'lucide-react';
import { analyticsApi } from '../services/api';
import { Analytics } from '../types';

const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [categoryStats, setCategoryStats] = useState<any[]>([]);
  const [monthlyTrends, setMonthlyTrends] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(12);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [analyticsData, categoryData, trendsData] = await Promise.all([
          analyticsApi.getExpenseAnalytics(timeRange),
          analyticsApi.getCategoryStats(timeRange),
          analyticsApi.getMonthlyTrends(timeRange)
        ]);
        
        setAnalytics(analyticsData);
        setCategoryStats(categoryData);
        setMonthlyTrends(trendsData);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [timeRange]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatMonth = (year: number, month: number) => {
    const date = new Date(year, month - 1);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  };

  // Chart data for monthly expenses
  const monthlyExpensesData = {
    labels: analytics?.monthly_expenses.map(expense => 
      formatMonth(expense.year, expense.month)
    ) || [],
    datasets: [
      {
        label: 'Monthly Expenses',
        data: analytics?.monthly_expenses.map(expense => expense.total) || [],
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Chart data for category breakdown
  const categoryBreakdownData = {
    labels: analytics?.category_breakdown.map(category => category.category) || [],
    datasets: [
      {
        data: analytics?.category_breakdown.map(category => category.total) || [],
        backgroundColor: [
          '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
          '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
        ],
        borderWidth: 0,
      },
    ],
  };

  // Chart data for category trends
  const categoryTrendsData = {
    labels: Object.keys(monthlyTrends).map(key => {
      const [year, month] = key.split('-');
      return formatMonth(parseInt(year), parseInt(month));
    }),
    datasets: Object.keys(monthlyTrends).length > 0 ? 
      Object.keys(monthlyTrends[Object.keys(monthlyTrends)[0]]).map((category, index) => ({
        label: category,
        data: Object.values(monthlyTrends).map((monthData: any) => monthData[category] || 0),
        backgroundColor: `hsl(${index * 40}, 70%, 50%)`,
        borderColor: `hsl(${index * 40}, 70%, 40%)`,
        borderWidth: 2,
        fill: false,
        tension: 0.4,
      })) : []
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return formatCurrency(value);
          },
        },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
      },
    },
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Analytics</h1>
          <p className="text-secondary-600 mt-1">Track your spending patterns and trends</p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(parseInt(e.target.value))}
          className="input-field w-48"
        >
          <option value={3}>Last 3 months</option>
          <option value={6}>Last 6 months</option>
          <option value={12}>Last 12 months</option>
          <option value={24}>Last 24 months</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Total Expenses</p>
              <p className="text-2xl font-semibold text-secondary-900">
                {formatCurrency(analytics?.total_expenses || 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Average Monthly</p>
              <p className="text-2xl font-semibold text-secondary-900">
                {formatCurrency(
                  analytics?.monthly_expenses.length 
                    ? analytics.monthly_expenses.reduce((sum, month) => sum + month.total, 0) / analytics.monthly_expenses.length
                    : 0
                )}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Receipts Processed</p>
              <p className="text-2xl font-semibold text-secondary-900">
                {analytics?.recent_receipts.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Expenses Chart */}
        <div className="card">
          <div className="flex items-center mb-4">
            <LineChart className="h-5 w-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold text-secondary-900">Monthly Expenses</h3>
          </div>
          <div className="h-80">
            <Line data={monthlyExpensesData} options={chartOptions} />
          </div>
        </div>

        {/* Category Breakdown Chart */}
        <div className="card">
          <div className="flex items-center mb-4">
            <PieChart className="h-5 w-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold text-secondary-900">Expense Categories</h3>
          </div>
          <div className="h-80">
            <Doughnut data={categoryBreakdownData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* Category Trends Chart */}
      {Object.keys(monthlyTrends).length > 0 && (
        <div className="card">
          <div className="flex items-center mb-4">
            <BarChart3 className="h-5 w-5 text-primary-600 mr-2" />
            <h3 className="text-lg font-semibold text-secondary-900">Category Trends</h3>
          </div>
          <div className="h-80">
            <Line data={categoryTrendsData} options={chartOptions} />
          </div>
        </div>
      )}

      {/* Category Statistics Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Category Statistics</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-secondary-200">
            <thead className="bg-secondary-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Items
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Total Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Average
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                  Percentage
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-secondary-200">
              {categoryStats.map((category, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-secondary-900">
                    {category.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-600">
                    {category.item_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                    {formatCurrency(category.total_amount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-600">
                    {formatCurrency(category.avg_amount)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-600">
                    {analytics?.total_expenses 
                      ? `${((category.total_amount / analytics.total_expenses) * 100).toFixed(1)}%`
                      : '0%'
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Receipts */}
      {analytics?.recent_receipts && analytics.recent_receipts.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Recent Receipts</h3>
          <div className="space-y-3">
            {analytics.recent_receipts.slice(0, 5).map((receipt) => (
              <div key={receipt.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium text-secondary-900">
                    {receipt.merchant_name || 'Unknown Merchant'}
                  </p>
                  <p className="text-sm text-secondary-600">
                    {receipt.purchase_date ? 
                      new Date(receipt.purchase_date).toLocaleDateString() : 
                      'No date'
                    }
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-secondary-900">
                    {formatCurrency(receipt.total_amount || 0)}
                  </p>
                  <p className="text-sm text-secondary-600">
                    {receipt.items?.length || 0} items
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsPage;
