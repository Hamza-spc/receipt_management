#!/bin/bash

echo "🔧 Fixing setup issues..."

cd backend

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing missing dependencies..."

# Install core dependencies first
pip install --upgrade pip
pip install wheel setuptools

# Install FastAPI and core dependencies
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-multipart

# Install authentication dependencies
pip install "python-jose[cryptography]" "passlib[bcrypt]"

# Install OCR dependencies
pip install pytesseract

# Install Pillow (image processing) - try different approaches
echo "Installing Pillow (this might take a moment)..."
pip install --only-binary=Pillow Pillow || pip install Pillow

# Install remaining dependencies
pip install pydantic pydantic-settings python-dotenv pandas numpy scikit-learn

echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ Environment file created"
fi

# Create uploads directory
mkdir -p uploads

# Initialize database
echo "🗄️  Initializing database..."
python scripts/init_db.py --with-sample-data

echo "✅ Setup fixed! You can now run the application."
echo ""
echo "To start:"
echo "1. Backend: cd backend && source venv/bin/activate && python scripts/run_server.py"
echo "2. Frontend: cd frontend && npm start"
