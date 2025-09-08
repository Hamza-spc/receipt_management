# Scan&Track - Receipt Management App

A comprehensive web application for managing receipts using OCR technology to extract and categorize expenses.

## Features

- 📸 **Receipt Upload**: Upload receipt images via drag-and-drop interface
- 🔍 **OCR Processing**: Extract text from receipts using Tesseract OCR
- 🏷️ **Auto Categorization**: Automatically categorize items and expenses
- 📊 **Expense Tracking**: Track expenses over time with visual analytics
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Chart.js
- **Backend**: FastAPI, Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **OCR**: Tesseract OCR with pytesseract
- **Image Processing**: Pillow (PIL)

## Prerequisites

Before running the application, ensure you have:

1. **Python 3.9+** installed
2. **Node.js 16+** and npm installed
3. **PostgreSQL** database server running
4. **Tesseract OCR** installed on your system

### Installing Tesseract OCR

#### macOS (using Homebrew):

```bash
brew install tesseract
```

#### Ubuntu/Debian:

```bash
sudo apt-get install tesseract-ocr
```

#### Windows:

Download from: https://github.com/UB-Mannheim/tesseract/wiki

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Hamza-spc/receipt_management.git
cd receipt_management
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb scan_track_db

# Run migrations
alembic upgrade head
```

### 4. Environment Variables

Create `backend/.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/scan_track_db
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=uploads
```

### 5. Frontend Setup

```bash
cd frontend
npm install
```

### 6. Run the Application

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

The application will be available at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
receipt_management/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── api/
│   ├── alembic/
│   ├── uploads/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## API Endpoints

- `POST /api/receipts/upload` - Upload receipt image
- `GET /api/receipts` - Get all receipts
- `GET /api/receipts/{id}` - Get specific receipt
- `PUT /api/receipts/{id}` - Update receipt
- `DELETE /api/receipts/{id}` - Delete receipt
- `GET /api/analytics/expenses` - Get expense analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
