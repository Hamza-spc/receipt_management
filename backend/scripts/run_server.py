#!/usr/bin/env python3
"""
Development server runner
Starts the FastAPI server with auto-reload
"""

import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Change to the backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
