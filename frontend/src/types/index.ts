export interface ReceiptItem {
  id: number;
  receipt_id: number;
  item_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  category: string | null;
  description: string | null;
}

export interface Receipt {
  id: number;
  filename: string;
  file_path: string;
  total_amount: number | null;
  merchant_name: string | null;
  purchase_date: string | null;
  created_at: string;
  updated_at: string | null;
  raw_text: string | null;
  items: ReceiptItem[];
}

export interface Analytics {
  total_expenses: number;
  monthly_expenses: MonthlyExpense[];
  category_breakdown: CategoryBreakdown[];
  recent_receipts: Receipt[];
}

export interface MonthlyExpense {
  year: number;
  month: number;
  total: number;
}

export interface CategoryBreakdown {
  category: string;
  total: number;
}

export interface UploadResponse {
  id: number;
  filename: string;
  file_path: string;
  total_amount: number | null;
  merchant_name: string | null;
  purchase_date: string | null;
  created_at: string;
  updated_at: string | null;
  raw_text: string | null;
  items: ReceiptItem[];
}
