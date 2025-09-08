import React, { useState, useEffect } from 'react';
import { Search, Filter, Trash2, Edit, Eye } from 'lucide-react';
import { receiptApi } from '../services/api';
import { Receipt } from '../types';
import ReceiptCard from '../components/ReceiptCard';

const Receipts: React.FC = () => {
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [filteredReceipts, setFilteredReceipts] = useState<Receipt[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null);

  useEffect(() => {
    const fetchReceipts = async () => {
      try {
        const data = await receiptApi.getReceipts(0, 100);
        setReceipts(data);
        setFilteredReceipts(data);
      } catch (error) {
        console.error('Error fetching receipts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReceipts();
  }, []);

  useEffect(() => {
    let filtered = receipts;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(receipt =>
        receipt.merchant_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        receipt.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        receipt.raw_text?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by category
    if (selectedCategory) {
      filtered = filtered.filter(receipt =>
        receipt.items?.some(item => item.category === selectedCategory)
      );
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'oldest':
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        case 'amount_high':
          return (b.total_amount || 0) - (a.total_amount || 0);
        case 'amount_low':
          return (a.total_amount || 0) - (b.total_amount || 0);
        case 'merchant':
          return (a.merchant_name || '').localeCompare(b.merchant_name || '');
        default:
          return 0;
      }
    });

    setFilteredReceipts(filtered);
  }, [receipts, searchTerm, selectedCategory, sortBy]);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this receipt?')) {
      try {
        await receiptApi.deleteReceipt(id);
        setReceipts(receipts.filter(receipt => receipt.id !== id));
      } catch (error) {
        console.error('Error deleting receipt:', error);
        alert('Failed to delete receipt. Please try again.');
      }
    }
  };

  const getUniqueCategories = () => {
    const categories = new Set<string>();
    receipts.forEach(receipt => {
      receipt.items?.forEach(item => {
        if (item.category) {
          categories.add(item.category);
        }
      });
    });
    return Array.from(categories).sort();
  };

  const formatCurrency = (amount: number | null) => {
    if (amount === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
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
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Receipts</h1>
        <p className="text-secondary-600 mt-1">Manage and view all your uploaded receipts</p>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-secondary-400" />
            <input
              type="text"
              placeholder="Search receipts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="input-field"
          >
            <option value="">All Categories</option>
            {getUniqueCategories().map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="input-field"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="amount_high">Amount: High to Low</option>
            <option value="amount_low">Amount: Low to High</option>
            <option value="merchant">Merchant A-Z</option>
          </select>

          {/* Results Count */}
          <div className="flex items-center text-sm text-secondary-600">
            <Filter className="h-4 w-4 mr-2" />
            {filteredReceipts.length} of {receipts.length} receipts
          </div>
        </div>
      </div>

      {/* Receipts Grid */}
      {filteredReceipts.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredReceipts.map((receipt) => (
            <div key={receipt.id} className="relative group">
              <ReceiptCard
                receipt={receipt}
                onView={setSelectedReceipt}
              />
              
              {/* Action Buttons */}
              <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <div className="flex space-x-1">
                  <button
                    onClick={() => setSelectedReceipt(receipt)}
                    className="p-2 bg-white rounded-lg shadow-md hover:bg-secondary-50 text-secondary-600 hover:text-secondary-900"
                    title="View Details"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(receipt.id)}
                    className="p-2 bg-white rounded-lg shadow-md hover:bg-red-50 text-red-600 hover:text-red-900"
                    title="Delete Receipt"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Search className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-secondary-900 mb-2">
            {searchTerm || selectedCategory ? 'No receipts found' : 'No receipts uploaded yet'}
          </h3>
          <p className="text-secondary-600 mb-4">
            {searchTerm || selectedCategory 
              ? 'Try adjusting your search or filter criteria'
              : 'Upload your first receipt to get started'
            }
          </p>
        </div>
      )}

      {/* Receipt Detail Modal */}
      {selectedReceipt && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-secondary-900">
                  Receipt Details
                </h2>
                <button
                  onClick={() => setSelectedReceipt(null)}
                  className="text-secondary-400 hover:text-secondary-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-4">Receipt Information</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-secondary-600">Merchant</label>
                      <p className="text-secondary-900">{selectedReceipt.merchant_name || 'N/A'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-secondary-600">Total Amount</label>
                      <p className="text-secondary-900">{formatCurrency(selectedReceipt.total_amount)}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-secondary-600">Purchase Date</label>
                      <p className="text-secondary-900">
                        {selectedReceipt.purchase_date ? 
                          new Date(selectedReceipt.purchase_date).toLocaleDateString() : 
                          'N/A'
                        }
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-secondary-600">Upload Date</label>
                      <p className="text-secondary-900">
                        {new Date(selectedReceipt.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 mb-4">Items ({selectedReceipt.items?.length || 0})</h3>
                  {selectedReceipt.items && selectedReceipt.items.length > 0 ? (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {selectedReceipt.items.map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                          <div className="flex-1">
                            <p className="font-medium text-secondary-900">{item.item_name}</p>
                            <div className="flex items-center space-x-2 mt-1">
                              {item.category && (
                                <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full">
                                  {item.category}
                                </span>
                              )}
                              <span className="text-sm text-secondary-600">
                                Qty: {item.quantity}
                              </span>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-medium text-secondary-900">
                              {formatCurrency(item.total_price)}
                            </p>
                            <p className="text-sm text-secondary-600">
                              @ {formatCurrency(item.unit_price)}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-secondary-600">No items extracted from this receipt</p>
                  )}
                </div>
              </div>

              {selectedReceipt.raw_text && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-secondary-900 mb-4">Extracted Text</h3>
                  <div className="bg-secondary-50 p-4 rounded-lg">
                    <pre className="text-sm text-secondary-700 whitespace-pre-wrap">
                      {selectedReceipt.raw_text}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Receipts;
