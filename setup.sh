#!/bin/bash

# Scan&Track Setup Script
echo "🚀 Setting up Scan&Track Receipt Management App..."

# Check if required tools are installed
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    else
        echo "✅ $1 is installed"
    fi
}

echo "📋 Checking prerequisites..."
check_command "python3"
check_command "node"
check_command "npm"
check_command "psql"

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

echo "✅ PostgreSQL is running"

# Backend setup
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install wheel setuptools

# Install dependencies one by one to handle compatibility issues
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"
pip install sqlalchemy==2.0.23
pip install alembic==1.12.1
pip install psycopg2-binary==2.9.9
pip install python-multipart==0.0.6
pip install "python-jose[cryptography]==3.3.0"
pip install "passlib[bcrypt]==1.7.4"
pip install pytesseract==0.3.10

# Install Pillow with pre-compiled wheel to avoid build issues
pip install --only-binary=Pillow Pillow

# Install remaining dependencies
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install python-dotenv==1.0.0
pip install pandas==2.1.4
pip install numpy==1.25.2
pip install scikit-learn==1.3.2

echo "✅ Python dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ Environment file created (please update with your database credentials)"
fi

# Create uploads directory
mkdir -p uploads
echo "✅ Uploads directory created"

# Initialize database
echo "🗄️  Initializing database..."
python scripts/init_db.py --with-sample-data
echo "✅ Database initialized with sample data"

cd ..

# Frontend setup
echo "⚛️  Setting up React frontend..."
cd frontend

# Install Node.js dependencies
npm install
echo "✅ Node.js dependencies installed"

cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && source venv/bin/activate && python scripts/run_server.py"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Or use Docker: docker-compose up"
echo ""
echo "The app will be available at:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
