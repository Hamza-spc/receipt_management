import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';
import FileUpload from '../components/FileUpload';
import { receiptApi } from '../services/api';
import { Receipt } from '../types';

const Upload: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<Receipt | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setError(null);
    setUploadResult(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);

    try {
      const result = await receiptApi.uploadReceipt(selectedFile);
      setUploadResult(result);
      setSelectedFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setError(null);
    setUploadResult(null);
  };

  const formatCurrency = (amount: number | null) => {
    if (amount === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <button
            onClick={() => navigate(-1)}
            className="mr-4 p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-lg"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-secondary-900">Upload Receipt</h1>
            <p className="text-secondary-600 mt-1">Upload a receipt image to extract and categorize expenses</p>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <div className="card">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-secondary-900 mb-2">Select Receipt</h2>
          <p className="text-sm text-secondary-600">
            Choose a clear image of your receipt. Supported formats: JPG, PNG, PDF (max 10MB)
          </p>
        </div>

        <FileUpload
          onFileSelect={handleFileSelect}
          isUploading={isUploading}
          error={error}
        />

        {selectedFile && !isUploading && !uploadResult && (
          <div className="mt-6 p-4 bg-secondary-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <UploadIcon className="h-5 w-5 text-secondary-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-secondary-900">{selectedFile.name}</p>
                  <p className="text-xs text-secondary-600">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleReset}
                  className="btn-secondary text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  className="btn-primary text-sm"
                >
                  Process Receipt
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Upload Result */}
      {uploadResult && (
        <div className="card">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
            <h2 className="text-lg font-semibold text-secondary-900">Receipt Processed Successfully!</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-secondary-700 mb-2">Receipt Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-secondary-600">Merchant:</span>
                  <span className="font-medium">{uploadResult.merchant_name || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Total Amount:</span>
                  <span className="font-medium">{formatCurrency(uploadResult.total_amount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Purchase Date:</span>
                  <span className="font-medium">
                    {uploadResult.purchase_date ? 
                      new Date(uploadResult.purchase_date).toLocaleDateString() : 
                      'N/A'
                    }
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-secondary-600">Items Found:</span>
                  <span className="font-medium">{uploadResult.items?.length || 0}</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-secondary-700 mb-2">Extracted Items</h3>
              {uploadResult.items && uploadResult.items.length > 0 ? (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {uploadResult.items.map((item, index) => (
                    <div key={index} className="flex items-center justify-between text-sm p-2 bg-secondary-50 rounded">
                      <div className="flex-1">
                        <p className="font-medium text-secondary-900">{item.item_name}</p>
                        {item.category && (
                          <p className="text-xs text-secondary-600">{item.category}</p>
                        )}
                      </div>
                      <p className="font-medium text-secondary-900">
                        {formatCurrency(item.total_price)}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-secondary-600">No items extracted</p>
              )}
            </div>
          </div>

          <div className="mt-6 flex space-x-4">
            <button
              onClick={handleReset}
              className="btn-primary"
            >
              Upload Another Receipt
            </button>
            <button
              onClick={() => navigate('/receipts')}
              className="btn-secondary"
            >
              View All Receipts
            </button>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-sm font-medium text-blue-900 mb-2">Tips for Better Results</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Ensure the receipt is well-lit and in focus</li>
          <li>• Avoid shadows or glare on the receipt</li>
          <li>• Make sure all text is clearly visible</li>
          <li>• For best results, use high-resolution images</li>
        </ul>
      </div>
    </div>
  );
};

export default Upload;
