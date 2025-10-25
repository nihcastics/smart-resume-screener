"""
Vercel serverless wrapper for FastAPI backend
Maps Vercel requests to the FastAPI app
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the FastAPI app
from main import app

# Export the app for Vercel
__all__ = ["app"]
