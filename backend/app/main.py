from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from typing import List
import uvicorn

from .database import get_db, engine
from .models import Base, Receipt, ReceiptItem
from .schemas import ReceiptResponse, ReceiptCreate, ReceiptItemResponse, AnalyticsResponse
from .services.ocr_service import OCRService
from .services.categorization_service import CategorizationService
from .api import receipts, analytics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Scan&Track API",
    description="Receipt management and expense tracking API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API routers
app.include_router(receipts.router, prefix="/api/receipts", tags=["receipts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Welcome to Scan&Track API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
