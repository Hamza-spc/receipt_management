import axios from 'axios';
import { Receipt, Analytics, UploadResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Receipt API
export const receiptApi = {
  // Upload receipt
  uploadReceipt: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/receipts/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Get all receipts
  getReceipts: async (skip: number = 0, limit: number = 100): Promise<Receipt[]> => {
    const response = await api.get(`/api/receipts?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  // Get single receipt
  getReceipt: async (id: number): Promise<Receipt> => {
    const response = await api.get(`/api/receipts/${id}`);
    return response.data;
  },

  // Update receipt
  updateReceipt: async (id: number, data: Partial<Receipt>): Promise<Receipt> => {
    const response = await api.put(`/api/receipts/${id}`, data);
    return response.data;
  },

  // Delete receipt
  deleteReceipt: async (id: number): Promise<void> => {
    await api.delete(`/api/receipts/${id}`);
  },
};

// Analytics API
export const analyticsApi = {
  // Get expense analytics
  getExpenseAnalytics: async (months: number = 12): Promise<Analytics> => {
    const response = await api.get(`/api/analytics/expenses?months=${months}`);
    return response.data;
  },

  // Get category statistics
  getCategoryStats: async (months: number = 12) => {
    const response = await api.get(`/api/analytics/categories?months=${months}`);
    return response.data;
  },

  // Get monthly trends
  getMonthlyTrends: async (months: number = 12) => {
    const response = await api.get(`/api/analytics/monthly-trends?months=${months}`);
    return response.data;
  },
};

export default api;
