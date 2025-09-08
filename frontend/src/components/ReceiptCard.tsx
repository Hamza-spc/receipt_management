import React from 'react';
import { Receipt } from '../types';
import { Calendar, Store, DollarSign, FileText, Eye } from 'lucide-react';
import { format } from 'date-fns';

interface ReceiptCardProps {
  receipt: Receipt;
  onView?: (receipt: Receipt) => void;
}

const ReceiptCard: React.FC<ReceiptCardProps> = ({ receipt, onView }) => {
  const formatCurrency = (amount: number | null) => {
    if (amount === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return 'N/A';
    }
  };

  const getCategoryColor = (category: string | null) => {
    if (!category) return 'bg-secondary-100 text-secondary-800';
    
    const colors: { [key: string]: string } = {
      'Food & Dining': 'bg-green-100 text-green-800',
      'Transportation': 'bg-blue-100 text-blue-800',
      'Shopping': 'bg-purple-100 text-purple-800',
      'Healthcare': 'bg-red-100 text-red-800',
      'Entertainment': 'bg-yellow-100 text-yellow-800',
      'Utilities': 'bg-orange-100 text-orange-800',
      'Office & Business': 'bg-indigo-100 text-indigo-800',
      'Travel': 'bg-pink-100 text-pink-800',
      'Other': 'bg-gray-100 text-gray-800',
    };
    
    return colors[category] || colors['Other'];
  };

  return (
    <div className="card hover:shadow-lg transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-secondary-900 mb-1">
            {receipt.merchant_name || 'Unknown Merchant'}
          </h3>
          <p className="text-sm text-secondary-600 mb-2">{receipt.filename}</p>
          
          <div className="flex items-center space-x-4 text-sm text-secondary-500">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              {formatDate(receipt.purchase_date)}
            </div>
            <div className="flex items-center">
              <DollarSign className="h-4 w-4 mr-1" />
              {formatCurrency(receipt.total_amount || 0)}
            </div>
          </div>
        </div>
        
        {onView && (
          <button
            onClick={() => onView(receipt)}
            className="btn-secondary flex items-center text-sm"
          >
            <Eye className="h-4 w-4 mr-1" />
            View
          </button>
        )}
      </div>

      {/* Items preview */}
      {receipt.items && receipt.items.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-secondary-700 flex items-center">
            <FileText className="h-4 w-4 mr-1" />
            Items ({receipt.items.length})
          </h4>
          <div className="space-y-1">
            {receipt.items.slice(0, 3).map((item, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="text-secondary-600 truncate flex-1 mr-2">
                  {item.item_name}
                </span>
                <div className="flex items-center space-x-2">
                  {item.category && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(item.category)}`}>
                      {item.category}
                    </span>
                  )}
                  <span className="font-medium text-secondary-900">
                    {formatCurrency(item.total_price)}
                  </span>
                </div>
              </div>
            ))}
            {receipt.items.length > 3 && (
              <p className="text-xs text-secondary-500">
                +{receipt.items.length - 3} more items
              </p>
            )}
          </div>
        </div>
      )}

      {/* Raw text preview */}
      {receipt.raw_text && (
        <div className="mt-4 pt-4 border-t border-secondary-200">
          <h4 className="text-sm font-medium text-secondary-700 mb-2">Extracted Text</h4>
          <p className="text-xs text-secondary-600 line-clamp-3">
            {receipt.raw_text.substring(0, 150)}
            {receipt.raw_text.length > 150 && '...'}
          </p>
        </div>
      )}
    </div>
  );
};

export default ReceiptCard;
