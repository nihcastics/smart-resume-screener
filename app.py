"""
FastAPI Backend for Smart Resume Screener - Hugging Face Spaces Version
Deployed on HF Spaces with Gradio interface
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from contextlib import asynccontextmanager
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import time
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from modules.models import load_models
from modules.database import init_postgresql, save_to_db
from modules.auth import init_auth_tables, register_user, login_user, get_user_analyses
from modules.text_processing import normalize_text, parse_contacts, build_index, chunk_text, semantic_chunk_text
from modules.llm_operations import llm_json, jd_plan_prompt, resume_profile_prompt, atomicize_requirements_prompt, analysis_prompt
from modules.scoring import compute_global_semantic, evaluate_requirement_coverage
from modules.resume_parser import parse_resume_pdf, parse_resume_text
from modules.validation import (
    validate_resume_data, validate_jd_data, validate_analysis_results,
    sanitize_resume_data, sanitize_analysis_data, validate_text_quality
)
from modules.scoring_optimization import calibrator, skill_taxonomy
from modules.abbreviation_mapping import (
    match_requirements_to_resume, extract_skills_from_text, 
    deduplicate_requirements, terms_match
)

load_dotenv()

# Global models storage
models_storage = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - load models on startup"""
    print("Loading ML models...")
    models_storage['models'] = load_models()
    print("ML models loaded successfully!")
    yield
    print("Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Smart Resume Screener API",
    description="AI-powered resume screening and job matching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Hugging Face Spaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://*.huggingface.space",  # Allow all HF Spaces
        "*"  # Allow all origins (HF Spaces requires this)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
PYTHONUNBUFFERED = os.getenv("PYTHONUNBUFFERED", "1")

# ==================== Pydantic Models ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AnalysisRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: Optional[str] = None
    weights: Optional[dict] = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    overall_score: float
    skill_coverage: float
    experience_match: float
    matched_requirements: list
    missing_requirements: list
    resume_summary: dict
    recommendations: list
    timestamp: str

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Smart Resume Screener Backend",
        "deployed_on": "Hugging Face Spaces"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Resume Screener API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ==================== Authentication ====================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        init_auth_tables()
        result = register_user(user_data.email, user_data.password, user_data.full_name)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("message", "Registration failed"))
        
        # Generate JWT token
        token_payload = {
            "sub": result["user_id"],
            "email": user_data.email,
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        return TokenResponse(access_token=token)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login user"""
    try:
        init_auth_tables()
        result = login_user(user_data.email, user_data.password)
        
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result.get("message", "Login failed"))
        
        # Generate JWT token
        token_payload = {
            "sub": result["user_id"],
            "email": user_data.email,
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        return TokenResponse(access_token=token)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me")
async def get_me(user_id: str = Depends(verify_token)):
    """Get current user info"""
    return {"user_id": user_id, "authenticated": True}

# ==================== Resume Analysis ====================

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    job_title: Optional[str] = Form(None),
    user_id: str = Depends(verify_token)
):
    """Analyze resume against job description"""
    try:
        analysis_id = str(uuid.uuid4())
        
        # Parse resume
        resume_content = await resume_file.read()
        if resume_file.filename.lower().endswith('.pdf'):
            resume_text = parse_resume_pdf(resume_content)
        else:
            resume_text = parse_resume_text(resume_content.decode('utf-8'))
        
        # Validate inputs
        validate_resume_data(resume_text)
        validate_jd_data(job_description)
        
        # Process resume and JD
        models = models_storage.get('models', {})
        
        # Extract resume profile using LLM
        resume_prompt = resume_profile_prompt(resume_text)
        resume_profile = llm_json(resume_prompt)
        
        # Extract requirements from JD using LLM
        jd_prompt = atomicize_requirements_prompt(job_description)
        requirements = llm_json(jd_prompt)
        
        # Match requirements to resume
        matched = match_requirements_to_resume(resume_text, requirements.get("requirements", []))
        
        # Calculate semantic similarity
        semantic_score = compute_global_semantic(
            resume_text, 
            job_description,
            models.get('sentence_model')
        )
        
        # Evaluate coverage
        coverage = evaluate_requirement_coverage(matched, requirements.get("requirements", []))
        
        # Generate analysis
        analysis_prompt_text = analysis_prompt(
            resume_text, 
            job_description, 
            matched, 
            coverage
        )
        analysis_result = llm_json(analysis_prompt_text)
        
        # Prepare response
        response = AnalysisResponse(
            analysis_id=analysis_id,
            overall_score=semantic_score * 100,
            skill_coverage=coverage.get("skill_coverage", 0),
            experience_match=coverage.get("experience_match", 0),
            matched_requirements=matched.get("matched", []),
            missing_requirements=matched.get("missing", []),
            resume_summary=resume_profile,
            recommendations=analysis_result.get("recommendations", []),
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save to database
        try:
            init_postgresql()
            save_to_db(analysis_id, user_id, resume_text, job_description, response.dict())
        except Exception as db_error:
            logger.warning(f"Database save failed: {str(db_error)}, continuing without persistence")
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analyses")
async def get_analyses(user_id: str = Depends(verify_token)):
    """Get user's analysis history"""
    try:
        init_postgresql()
        analyses = get_user_analyses(user_id)
        return {"analyses": analyses}
    except Exception as e:
        logger.warning(f"Could not retrieve analyses: {str(e)}")
        return {"analyses": []}

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow().isoformat()
    }

# ==================== Startup ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))  # HF Spaces default port
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=1,  # Single worker for HF Spaces free tier
        log_level="info"
    )
