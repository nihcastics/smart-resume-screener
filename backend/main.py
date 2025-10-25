"""
FastAPI Backend for Smart Resume Screener
Modern REST API with authentication and resume analysis
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from contextlib import asynccontextmanager
import jwt
import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys
import logging
import time
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Global state
model = None
nlp = None
embedder = None
models_ok = False
db_conn = None
db_ok = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global model, nlp, embedder, models_ok, db_conn, db_ok
    
    # Startup
    print("🔄 Loading AI models...")
    model, nlp, embedder, models_ok = load_models()
    if models_ok:
        print("✅ AI models loaded successfully")
    else:
        print("❌ Failed to load AI models")
    
    print("🔄 Connecting to database...")
    db_conn, db_ok = init_postgresql()
    if db_ok:
        init_auth_tables(db_conn)
        print("✅ Database connected and initialized")
    else:
        print("❌ Failed to connect to database")
    
    yield
    
    # Shutdown
    if db_conn:
        db_conn.close()
        print("✅ Database connection closed")

# Initialize FastAPI with lifespan
app = FastAPI(
    title="Smart Resume Screener API",
    lifespan=lifespan,
    description="AI-powered resume screening with beautiful frontend",
    version="2.0.0"
)

# CORS configuration - allow all frontend ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

security = HTTPBearer()

# ============================================================================
# MODELS
# ============================================================================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AnalyzeRequest(BaseModel):
    jd_text: str

# ============================================================================
# AUTHENTICATION HELPERS
# ============================================================================

def create_access_token(user_data: dict) -> str:
    """Create JWT access token"""
    payload = {
        "user_id": user_data["user_id"],
        "email": user_data["email"],
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return user data"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "version": "2.0.0",
        "models_loaded": models_ok,
        "database_connected": db_ok
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "models": {
            "loaded": models_ok,
            "mode": "hybrid" if model else "local"
        },
        "database": {
            "connected": db_ok
        }
    }

@app.options("/api/auth/register")
async def register_options():
    """Handle CORS preflight for register"""
    return {"status": "ok"}

@app.options("/api/auth/login")
async def login_options():
    """Handle CORS preflight for login"""
    return {"status": "ok"}

@app.options("/api/analyze")
async def analyze_options():
    """Handle CORS preflight for analyze"""
    return {"status": "ok"}

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Register new user"""
    if not db_ok:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    # Create username from email
    username = request.email.split('@')[0]
    
    success, message, user_id = register_user(
        db_conn,
        username,
        request.email,
        request.password,
        request.name
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "success": True,
        "message": "Account created successfully",
        "user_id": user_id
    }

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login user and return JWT token"""
    if not db_ok:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    success, message, user_data = login_user(db_conn, request.email, request.password)
    
    if not success:
        raise HTTPException(status_code=401, detail=message)
    
    # Create JWT token (user_data is guaranteed to be dict if success is True)
    if user_data is None:
        raise HTTPException(status_code=500, detail="User data is missing")
    token = create_access_token(user_data)
    
    return {
        "success": True,
        "token": token,
        "user": user_data
    }

@app.get("/api/auth/me")
async def get_current_user(user_data: dict = Depends(verify_token)):
    """Get current user info"""
    return {
        "success": True,
        "user": user_data
    }

@app.post("/api/analyze")
async def analyze_resume(
    request: Request,
    file: Optional[UploadFile] = File(None),
    resume_text: str = Form(""),
    jd_text: str = Form(...),
    user_data: dict = Depends(verify_token)
):
    """Analyze resume against job description with enterprise-grade error handling and monitoring"""
    # Generate request ID for tracking
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(f"🚀 Starting analysis request {request_id} for user {user_data.get('user_id', 'unknown')}")
    
    # Set timeout for the entire analysis (5 minutes max)
    ANALYSIS_TIMEOUT = 300  # 5 minutes
    
    try:
        # Validate input - either file or text must be provided
        if not file and not resume_text.strip():
            raise HTTPException(status_code=400, detail="Either file upload or resume text is required")
        
        if file and resume_text.strip():
            raise HTTPException(status_code=400, detail="Provide either file upload OR resume text, not both")
        
        # Validate job description
        if not jd_text or not jd_text.strip():
            raise HTTPException(status_code=400, detail="Job description text is required")
        
        if len(jd_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Job description too short (minimum 50 characters)")
        
        if len(jd_text.strip()) > 50000:
            raise HTTPException(status_code=400, detail="Job description too long (maximum 50,000 characters)")
        
        # Determine input type for logging
        if file:
            input_type = "pdf" if (file.filename and file.filename.endswith('.pdf')) else "text_file"
        else:
            input_type = "text_input"
        
        logger.info(f"🔄 Starting resume analysis for input type: {input_type}")
        logger.info(f"📄 Job description length: {len(jd_text)} characters")
        
        # Check for timeout periodically
        def check_timeout():
            elapsed = time.time() - start_time
            if elapsed > ANALYSIS_TIMEOUT:
                logger.error(f"❌ Analysis timeout after {elapsed:.1f}s for request {request_id}")
                raise HTTPException(status_code=408, detail=f"Analysis timeout after {elapsed:.1f} seconds")
        
        # Resume parsing with timeout checks
        check_timeout()
        
        # Parse resume based on input type
        if file:
            # Read uploaded file
            contents = await file.read()
            
            # Check filename exists
            if not file.filename:
                raise HTTPException(status_code=400, detail="Filename is required")
            
            # Parse resume
            if file.filename and file.filename.endswith('.pdf'):
                import io
                resume_data = parse_resume_pdf(io.BytesIO(contents), nlp, embedder)
                if not resume_data:
                    raise HTTPException(status_code=400, detail="Failed to parse PDF resume")
                
                # ENTERPRISE VALIDATION: Validate parsed resume quality
                is_valid, validation_issues = validate_resume_data(resume_data)
                if not is_valid:
                    logger.error(f"Resume validation failed: {validation_issues}")
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Resume quality check failed: {'; '.join(validation_issues[:3])}"
                    )
                
                # SANITIZATION: Clean data before processing
                resume_data = sanitize_resume_data(resume_data)
                
                resume_text = resume_data.get('text', '')
                contacts = {
                    'name': resume_data.get('name', 'Unknown'),
                    'email': resume_data.get('email', 'Not found'),
                    'phone': resume_data.get('phone', 'Not found')
                }
                skills = resume_data.get('technical_skills', [])
                
                # OPTIMIZATION: Normalize skills using taxonomy
                skills = skill_taxonomy.normalize_skill_list(skills)
                logger.info(f"✅ Normalized {len(skills)} unique skills")
                
                chunks = resume_data.get('chunks', [])
                input_type = "pdf"
            else:
                resume_text = contents.decode('utf-8')
                
                # ENTERPRISE VALIDATION: Validate text resume quality
                text_valid, text_error = validate_text_quality(resume_text, min_length=100)
                if not text_valid:
                    raise HTTPException(status_code=400, detail=f"Resume validation failed: {text_error}")
                
                # Extract contacts for text file uploads
                contacts = parse_contacts(resume_text)
                skills = []
                chunks = []
                input_type = "text_file"
        else:
            # Direct text input
            resume_text = resume_text.strip()
            if len(resume_text) < 50:
                raise HTTPException(status_code=400, detail="Resume text too short (minimum 50 characters)")
            
            # ENTERPRISE VALIDATION: Validate text quality
            text_valid, text_error = validate_text_quality(resume_text, min_length=50)
            if not text_valid:
                raise HTTPException(status_code=400, detail=f"Resume validation failed: {text_error}")
            
            # Extract contacts for text resumes
            contacts = parse_contacts(resume_text)
            skills = []
            chunks = []
            input_type = "text_input"
        
        # Normalize texts
        logger.info("🔄 Normalizing job description and resume text...")
        jd_normalized = normalize_text(jd_text)
        resume_normalized = normalize_text(resume_text)
        logger.info("✅ Text normalization completed")
        
        check_timeout()
        
        # Initialize resume_data for later use
        resume_data = None
        if file and file.filename and file.filename.endswith('.pdf'):
            # Resume data was already set above
            pass
        
        # Extract contacts for text resumes (already done for PDFs above)
        if not (file and file.filename and file.filename.endswith('.pdf')):
            contacts = parse_contacts(resume_text)
        
        # Build search index if not already available from PDF parsing
        logger.info("🔄 Building semantic search index...")
        if not chunks:
            # Create chunks from resume text
            try:
                chunks = semantic_chunk_text(resume_normalized, nlp, embedder, max_chars=800, overlap=200)
                logger.info(f"✅ Created {len(chunks)} semantic chunks")
            except Exception as e:
                logger.warning(f"Semantic chunking failed, using basic chunking: {e}")
                chunks = chunk_text(resume_normalized, max_chars=800, nlp=nlp)
                logger.info(f"✅ Created {len(chunks)} basic chunks")
            index, _ = build_index(embedder, chunks)
            logger.info("✅ Search index built successfully")
        else:
            # Use chunks from PDF parsing and build index
            index, _ = build_index(embedder, chunks)
            logger.info(f"✅ Using {len(chunks)} pre-processed chunks from PDF")
        
        # Get JD requirements
        logger.info("🔄 Analyzing job description requirements...")
        if model:
            jd_plan = llm_json(model, jd_plan_prompt, {"jd": jd_normalized, "preview": resume_normalized[:1000]})
            raw_reqs = jd_plan.get("requirements", []) if jd_plan else []
            logger.info(f"✅ Extracted {len(raw_reqs)} job requirements")
        else:
            # Fallback when LLM not available - extract basic requirements from JD text
            logger.warning("LLM not available, using basic requirement extraction")
            jd_plan = {"requirements": ["basic technical skills"], "role_title": "Software Developer"}
            raw_reqs = ["Python", "JavaScript", "SQL", "Git", "problem solving", "communication"]
            logger.info("✅ Using fallback requirements extraction")
        
        check_timeout()
        
        # Atomicize requirements - extract from structured response
        logger.info("🔄 Breaking down requirements into atomic components...")
        if model:
            atoms_result = llm_json(model, atomicize_requirements_prompt, {"jd": jd_normalized, "resume_preview": resume_normalized[:1000]})
            
            # Extract requirements from structured response (hard_skills, fundamentals, experience, qualifications)
            atomic_reqs = []
            if atoms_result:
                # Extract from hard_skills
                hard_skills_must = atoms_result.get("hard_skills", {}).get("must", [])
                hard_skills_nice = atoms_result.get("hard_skills", {}).get("nice", [])
                
                # Extract from fundamentals
                fundamentals_must = atoms_result.get("fundamentals", {}).get("must", [])
                fundamentals_nice = atoms_result.get("fundamentals", {}).get("nice", [])
                
                # Extract from experience
                experience_must = atoms_result.get("experience", {}).get("must", [])
                experience_nice = atoms_result.get("experience", {}).get("nice", [])
                
                # Extract from qualifications
                qualifications_must = atoms_result.get("qualifications", {}).get("must", [])
                qualifications_nice = atoms_result.get("qualifications", {}).get("nice", [])
                
                # Combine all must-have requirements (these are the critical ones)
                all_must_reqs = (
                    hard_skills_must + fundamentals_must + 
                    experience_must + qualifications_must
                )
                
                # Combine all nice-to-have requirements
                all_nice_reqs = (
                    hard_skills_nice + fundamentals_nice + 
                    experience_nice + qualifications_nice
                )
                
                # For now, treat all as must-have for scoring (we'll distinguish later)
                atomic_reqs = all_must_reqs + all_nice_reqs
                
                logger.info(f"✅ Extracted {len(all_must_reqs)} must-have and {len(all_nice_reqs)} nice-to-have requirements")
                logger.info(f"   Hard skills (must): {len(hard_skills_must)}, Fundamentals (must): {len(fundamentals_must)}")
            else:
                atomic_reqs = []
                logger.warning("⚠️ Failed to extract atomic requirements from LLM response")
        else:
            # Fallback - use raw requirements as atomic requirements
            atomic_reqs = [{"requirement": req, "req_type": "hard_skill", "priority": "must"} for req in raw_reqs]
        
        # Get resume profile (skip if we already have skills from PDF parsing)
        if not skills:
            if model:
                profile_result = llm_json(model, resume_profile_prompt, {"full_resume_text": resume_normalized})
                skills = profile_result.get("skills", []) if profile_result else []
                experience_years = profile_result.get("experience_years", 0) if profile_result else 0
            else:
                # Fallback - extract basic skills from resume text
                logger.warning("LLM not available, using basic skill extraction")
                basic_skills = ["Python", "JavaScript", "HTML", "CSS", "SQL"]  # Common fallback skills
                skills = [skill for skill in basic_skills if skill.lower() in resume_normalized.lower()]
                experience_years = 2  # Default fallback
                profile_result = {"skills": skills, "experience_years": experience_years}
        else:
            # We have skills from PDF parsing, just get experience years
            if model:
                profile_result = llm_json(model, resume_profile_prompt, {"full_resume_text": resume_normalized})
                experience_years = profile_result.get("experience_years", 0) if profile_result else 0
            else:
                experience_years = 2  # Default fallback
                profile_result = {"skills": skills, "experience_years": experience_years}
        
        # Compute scores
        logger.info("🔄 Computing semantic similarity scores...")
        global_score = compute_global_semantic(jd_normalized, resume_normalized, embedder)
        logger.info(f"✅ Global semantic score: {global_score:.3f}")
        
        # Extract requirement strings - atomic_reqs is already a list of strings
        req_strings = [req for req in atomic_reqs if req and isinstance(req, str)]
        
        # Log the requirements being evaluated
        logger.info(f"📋 Evaluating {len(req_strings)} requirements:")
        if req_strings:
            logger.info(f"   Sample requirements: {req_strings[:5]}")
            
        # evaluate_requirement_coverage new signature: (atomic_reqs, resume_text, resume_chunks, embedder, model, faiss_index, nlp, jd_text)
        logger.info("🔄 Evaluating requirement coverage...")
        coverage_result = evaluate_requirement_coverage(
            req_strings, resume_normalized, chunks, embedder, model, index, nlp, jd_normalized
        )
        coverage_score = coverage_result.get("overall", 0.0)
        coverage_details = coverage_result
        must_coverage = coverage_result.get('must', 0.0)
        nice_coverage = coverage_result.get('nice', 1.0)
        
        # Calculate must-have fulfillment rate for calibration
        must_details = coverage_result.get('details', {}).get('must', {})
        must_present_count = sum(1 for d in must_details.values() if d.get("llm_present", False))
        must_total = len(must_details) if must_details else 1
        must_fulfillment_rate = must_present_count / must_total
        
        logger.info(f"✅ Coverage score: {coverage_score:.3f}")
        logger.info(f"   Must-have coverage: {must_coverage:.3f} ({must_present_count}/{must_total} fulfilled)")
        logger.info(f"   Nice-to-have coverage: {nice_coverage:.3f}")

        coverage_summary = {
            "must_present_count": must_present_count,
            "must_total": must_total,
            "must_percent": round(must_coverage * 100, 1),
            "nice_percent": round(nice_coverage * 100, 1),
            "overall_percent": round(coverage_score * 100, 1),
        }

        # Identify the top missing must-have requirements for clearer output
        missing_requirements = []
        must_details_map = coverage_result.get('details', {}).get('must', {})
        if isinstance(must_details_map, dict):
            for requirement, detail in must_details_map.items():
                llm_present = detail.get("llm_present")
                llm_confidence = float(detail.get("llm_confidence", 0.0) or 0.0)
                max_similarity = float(detail.get("max_similarity", 0.0) or 0.0)
                if not llm_present and (llm_confidence >= 0.4 or max_similarity < 0.5):
                    missing_requirements.append({
                        "requirement": requirement,
                        "llm_confidence": round(llm_confidence, 2),
                        "similarity": round(max_similarity, 3),
                        "resume_evidence": detail.get("resume_contexts", []),
                        "rationale": detail.get("llm_rationale", "")
                    })
        missing_requirements = missing_requirements[:5]

        coverage_details = dict(coverage_result)
        coverage_details['summary'] = {
            "must_present_count": must_present_count,
            "must_total": must_total,
            "must_coverage": must_coverage,
            "nice_coverage": nice_coverage,
            "overall": coverage_score
        }
        coverage_details['missing_requirements'] = missing_requirements
        
        # ENTERPRISE OPTIMIZATION: Use calibrated scoring
        logger.info("🔄 Calibrating final score with industry standards...")
        calibrated_score, score_tier, breakdown = calibrator.calibrate_final_score(
            coverage_score=coverage_score,
            semantic_score=global_score,
            must_fulfillment_rate=must_fulfillment_rate,
            nice_coverage=nice_coverage
        )
        
        logger.info(f"✅ Calibrated score: {calibrated_score}/10 (Tier: {score_tier})")
        logger.info(f"   Breakdown: Coverage={breakdown['coverage_points']:.1f}, Semantic={breakdown['semantic_points']:.1f}, Must={breakdown['must_points']:.1f}, Nice={breakdown['nice_points']:.1f}")
        if breakdown.get('penalties'):
            logger.warning(f"   Penalties: {', '.join(breakdown['penalties'])}")
        if breakdown.get('bonuses'):
            logger.info(f"   Bonuses: {', '.join(breakdown['bonuses'])}")

        score_breakdown = {
            "tier": score_tier,
            "final_score_out_of_10": round(calibrated_score, 2),
            "final_score_percent": round(calibrated_score * 10, 1),
            "semantic_match_percent": round(global_score * 100, 1),
            "requirement_coverage_percent": round(coverage_score * 100, 1),
            "must_have_coverage_percent": round(must_coverage * 100, 1),
            "nice_to_have_coverage_percent": round(nice_coverage * 100, 1),
            "must_fulfillment_rate_percent": round(must_fulfillment_rate * 100, 1),
            "breakdown_points": breakdown,
        }
        
        # Final analysis
        logger.info("🔄 Generating final analysis and recommendations...")
        if model:
            analysis_result = llm_json(model, analysis_prompt(jd_normalized, jd_plan, profile_result, coverage_details, {}, global_score, coverage_score))
            # Use calibrated score instead of LLM's fit_score
            final_score = calibrated_score
            strengths = analysis_result.get("top_strengths", []) if analysis_result else []
            gaps = analysis_result.get("improvement_areas", []) if analysis_result else []
            recommendation = analysis_result.get("overall_comment", "") if analysis_result else ""
            
            # Add tier-based recommendation prefix
            tier_messages = {
                'outstanding': "⭐ OUTSTANDING CANDIDATE - Immediate interview recommended.",
                'excellent': "✅ EXCELLENT FIT - Priority candidate for this role.",
                'strong': "👍 STRONG CANDIDATE - Definitely worth interviewing.",
                'good': "✓ GOOD MATCH - Consider for interview.",
                'fair': "~ BORDERLINE - May be suitable with development.",
                'weak': "✗ UNDER-QUALIFIED - Does not meet minimum requirements."
            }
            recommendation = f"{tier_messages.get(score_tier, '')} {recommendation}"
            
            logger.info(f"✅ Final analysis complete - Score: {final_score}/10 ({score_tier})")
        else:
            # Fallback analysis when LLM not available
            logger.warning("LLM not available, using calibrated score only")
            final_score = calibrated_score
            strengths = ["Basic technical skills present"] if skills else []
            gaps = ["Advanced analysis requires LLM"] if not skills else []
            recommendation = f"Score: {final_score}/10 ({score_tier}). Basic analysis completed. For detailed insights, configure Gemini API."
            logger.info(f"✅ Basic analysis complete - Score: {final_score}/10 ({score_tier})")

        # Use LLM-based skill extraction and comparison (more robust than pattern matching)
        logger.info("🤖 Using LLM for intelligent skill extraction and comparison...")
        
        # Extract JD requirements as fallback list
        jd_requirements_list = []
        requirements_source = locals().get('atoms_result', jd_plan)
        
        if requirements_source and isinstance(requirements_source, dict):
            for category in ['hard_skills', 'fundamentals', 'experience', 'qualifications']:
                cat_data = requirements_source.get(category, {})
                if isinstance(cat_data, dict):
                    must_items = cat_data.get('must', [])
                    nice_items = cat_data.get('nice', [])
                    if isinstance(must_items, list):
                        jd_requirements_list.extend([str(item) for item in must_items if item])
                    if isinstance(nice_items, list):
                        jd_requirements_list.extend([str(item) for item in nice_items if item])
        
        # Use LLM for skill extraction and intelligent comparison
        from modules.llm_operations import llm_extract_skills_comparison
        
        skill_match_result = llm_extract_skills_comparison(
            model=model,
            jd_text=jd_text[:3000],
            resume_text=resume_text[:4000],
            jd_requirements=jd_requirements_list[:30]  # Provide structured requirements as hint
        )
        
        # Extract results from LLM
        matched_skills = skill_match_result.get("matched_skills", [])[:15]
        missing_skills = skill_match_result.get("missing_skills", [])[:15]
        additional_skills = skill_match_result.get("additional_skills", [])[:15]
        skill_match_rate = skill_match_result.get("match_rate", 0.0)
        skill_analysis = skill_match_result.get("analysis", "")
        
        logger.info(f"✅ LLM skill comparison: {len(matched_skills)} matched, {len(missing_skills)} missing, {len(additional_skills)} additional ({skill_match_rate}% match rate)")
        if skill_analysis:
            logger.info(f"📝 Analysis: {skill_analysis[:200]}")
        
        # Semantic matching details with requirement-level analysis
        logger.info("🔍 Computing semantic matching details...")
        
        # Calculate average similarity per requirement (from coverage details)
        requirement_similarities = []
        if coverage_details and isinstance(coverage_details, dict):
            details_dict = coverage_details.get('details', {})
            for category in ['must', 'nice']:
                cat_details = details_dict.get(category, {})
                for req, req_data in cat_details.items():
                    if isinstance(req_data, dict):
                        sim = req_data.get('similarity', 0.0)
                        if isinstance(sim, (int, float)):
                            requirement_similarities.append(float(sim))
        
        # Calculate metrics
        avg_req_similarity = sum(requirement_similarities) / len(requirement_similarities) if requirement_similarities else 0.0
        semantic_alignment_score = (global_score + avg_req_similarity + coverage_score) / 3  # Balanced
        
        semantic_details = {
            "overall_similarity": round(global_score * 100, 1),
            "requirement_match_similarity": round(avg_req_similarity * 100, 1),
            "jd_resume_alignment": (
                "Excellent" if semantic_alignment_score >= 0.75 else 
                "Good" if semantic_alignment_score >= 0.60 else 
                "Fair" if semantic_alignment_score >= 0.45 else 
                "Weak"
            ),
            "language_compatibility": round(global_score * 100, 1),
            "context_relevance": round(semantic_alignment_score * 100, 1)
        }
        
        # Skills analysis with intelligent matching from LLM
        skills_analysis = {
            "resume_skills": skill_match_result.get("resume_skills", [])[:20],
            "resume_skills_count": len(skill_match_result.get("resume_skills", [])),
            "jd_requirements": skill_match_result.get("jd_skills", [])[:20],
            "jd_requirements_count": len(skill_match_result.get("jd_skills", [])),
            "matched_skills": matched_skills,
            "matched_skills_count": len(matched_skills),
            "missing_skills": missing_skills,
            "missing_skills_count": len(missing_skills),
            "additional_skills": additional_skills,
            "additional_skills_count": len(additional_skills),
            "skill_match_rate": skill_match_rate,
            "skill_analysis": skill_analysis
        }
        
        logger.info(f"✅ Semantic details computed - Alignment: {semantic_details['jd_resume_alignment']}, Match rate: {skill_match_rate}%")

        analysis_summary = {
            'strengths': strengths,
            'top_strengths': strengths,
            'gaps': gaps,
            'improvement_areas': gaps,
            'recommendation': recommendation,
            'overall_comment': recommendation,
            'score_tier': score_tier,
            'score_breakdown': score_breakdown,
            'coverage_summary': coverage_summary,
            'missing_requirements': missing_requirements,
            'semantic_details': semantic_details,
            'skills_analysis': skills_analysis
        }
        
        # Save to database
        if input_type == "pdf" and 'resume_data' in locals() and resume_data:
            # Use structured data from PDF parsing
            parsed_resume = {
                'name': resume_data.get('name', 'Unknown'),
                'email': resume_data.get('email', 'Not found'),
                'phone': resume_data.get('phone', 'Not found'),
                'text': resume_text,
                'chunks': resume_data.get('chunks', []),
                'entities': resume_data.get('entities', {}),
                'technical_skills': skills,
                'experience': [{"years": experience_years}],
                'projects': []
            }
        else:
            # For text resumes (file upload or direct input), create basic structure
            parsed_resume = {
                'name': contacts.get('name', 'Unknown'),
                'email': contacts.get('email', 'Not found'),
                'phone': contacts.get('phone', 'Not found'),
                'text': resume_text,
                'chunks': chunks,
                'entities': {},
                'technical_skills': skills,
                'experience': [{"years": experience_years}],
                'projects': []
            }
        
        analysis_data = {
            'plan': jd_plan,
            'profile': profile_result,
            'coverage': coverage_details,
            'cue_alignment': {},
            'final_analysis': analysis_summary,
            'semantic_score': global_score,
            'coverage_score': coverage_score,
            'llm_fit_score': final_score,
            'final_score': final_score,
            'fit_score': final_score,
            'calibration': breakdown,
            'score_breakdown': score_breakdown,
            'score_tier': score_tier,
            'coverage_summary': coverage_summary,
            'missing_requirements': missing_requirements,
            'requirement_details': coverage_details.get('details', {}),
            'must_present_count': must_present_count,
            'must_total': must_total,
            'semantic_details': semantic_details,
            'skills_analysis': skills_analysis
        }
        
        # ENTERPRISE VALIDATION: Validate analysis results before database insertion
        analysis_valid, analysis_issues = validate_analysis_results(analysis_data)
        if not analysis_valid:
            logger.error(f"Analysis validation failed: {analysis_issues}")
            # Still return results to user, but log the validation failure
            logger.warning("⚠️ Proceeding with analysis despite validation issues (for debugging)")
        
        # SANITIZATION: Clean analysis data before saving
        analysis_data = sanitize_analysis_data(analysis_data)
        
        resume_id, analysis_id = save_to_db(
            parsed_resume, jd_text, analysis_data, db_conn, db_ok, user_data['user_id']
        )
        logger.info(f"✅ Analysis saved - Resume ID: {resume_id}, Analysis ID: {analysis_id}")
        
        # Calculate total processing time
        total_time = time.time() - start_time
        logger.info(f"🎉 Analysis completed successfully in {total_time:.2f}s for request {request_id}")
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "resume_id": resume_id,
            "request_id": request_id,
            "processing_time_seconds": round(total_time, 2),
            "processing_steps": [
                "Resume parsing and text extraction",
                "Job description analysis and requirement extraction", 
                "Semantic chunking and search index building",
                "Resume profile and skills analysis",
                "Requirement coverage evaluation",
                "Semantic similarity scoring",
                "Final analysis and recommendations",
                "Results saved to database"
            ],
            "results": {
                "final_score": final_score,
                "global_score": global_score,
                "coverage_score": coverage_score,
                "score_tier": score_tier,
                "score_breakdown": score_breakdown,
                "coverage_summary": coverage_summary,
                "missing_requirements": missing_requirements,
                "strengths": strengths,
                "gaps": gaps,
                "recommendation": recommendation,
                "skills": skills,
                "experience_years": experience_years,
                "must_have_coverage": coverage_summary["must_percent"],
                "nice_to_have_coverage": coverage_summary["nice_percent"],
                "final_score_percent": score_breakdown["final_score_percent"],
                "semantic_details": semantic_details,
                "skills_analysis": skills_analysis,
                "candidate": {
                    "name": contacts.get('name', 'Unknown'),
                    "email": contacts.get('email', 'Not found'),
                    "phone": contacts.get('phone', 'Not found')
                }
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"❌ Analysis failed after {error_time:.2f}s for request {request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/analyses")
async def get_analyses(
    limit: int = 20,
    offset: int = 0,
    user_data: dict = Depends(verify_token)
):
    """Get user's analyses"""
    if not db_ok:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        analyses = get_user_analyses(db_conn, user_data['user_id'], limit, offset)
        return {
            "success": True,
            "analyses": analyses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
