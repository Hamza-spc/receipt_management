import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Upload, 
  Receipt, 
  DollarSign, 
  TrendingUp, 
  Calendar,
  ArrowRight 
} from 'lucide-react';
import { receiptApi, analyticsApi } from '../services/api';
import { Receipt as ReceiptType, Analytics } from '../types';
import ReceiptCard from '../components/ReceiptCard';

const Dashboard: React.FC = () => {
  const [recentReceipts, setRecentReceipts] = useState<ReceiptType[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [receiptsData, analyticsData] = await Promise.all([
          receiptApi.getReceipts(0, 5),
          analyticsApi.getExpenseAnalytics(6)
        ]);
        
        setRecentReceipts(receiptsData);
        setAnalytics(analyticsData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getTotalItems = () => {
    return recentReceipts.reduce((total, receipt) => total + (receipt.items?.length || 0), 0);
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
          <h1 className="text-3xl font-bold text-secondary-900">Dashboard</h1>
          <p className="text-secondary-600 mt-1">Track your expenses and manage receipts</p>
        </div>
        <Link
          to="/upload"
          className="btn-primary flex items-center"
        >
          <Upload className="h-5 w-5 mr-2" />
          Upload Receipt
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DollarSign className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Total Expenses</p>
              <p className="text-2xl font-semibold text-secondary-900">
                {analytics ? formatCurrency(analytics.total_expenses) : '$0.00'}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Receipt className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Total Receipts</p>
              <p className="text-2xl font-semibold text-secondary-900">
                {recentReceipts.length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Items Tracked</p>
              <p className="text-2xl font-semibold text-secondary-900">
                {getTotalItems()}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">This Month</p>
              <p className="text-2xl font-semibold text-secondary-900">
                {analytics?.monthly_expenses.length ? 
                  formatCurrency(analytics.monthly_expenses[analytics.monthly_expenses.length - 1]?.total || 0) : 
                  '$0.00'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Receipts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-secondary-900">Recent Receipts</h2>
            <Link
              to="/receipts"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center"
            >
              View all
              <ArrowRight className="h-4 w-4 ml-1" />
            </Link>
          </div>
          
          {recentReceipts.length > 0 ? (
            <div className="space-y-4">
              {recentReceipts.map((receipt) => (
                <ReceiptCard key={receipt.id} receipt={receipt} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Receipt className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
              <p className="text-secondary-600 mb-4">No receipts uploaded yet</p>
              <Link
                to="/upload"
                className="btn-primary"
              >
                Upload Your First Receipt
              </Link>
            </div>
          )}
        </div>

        {/* Category Breakdown */}
        <div className="card">
          <h2 className="text-lg font-semibold text-secondary-900 mb-4">Expense Categories</h2>
          
          {analytics?.category_breakdown && analytics.category_breakdown.length > 0 ? (
            <div className="space-y-3">
              {analytics.category_breakdown.slice(0, 5).map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-secondary-700">
                    {category.category}
                  </span>
                  <span className="text-sm font-semibold text-secondary-900">
                    {formatCurrency(category.total)}
                  </span>
                </div>
              ))}
              {analytics.category_breakdown.length > 5 && (
                <Link
                  to="/analytics"
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center justify-center mt-4"
                >
                  View all categories
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Link>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <TrendingUp className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
              <p className="text-secondary-600">No category data available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
