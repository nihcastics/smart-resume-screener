# ============================
# Resume Screener Pro — Final
# Focus: Accurate parsing & analysis (no evidence UI, no lexicons)
# ============================

# --- Silence noisy libs before imports ---
import os, sys
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TORCH_CPP_LOG_LEVEL'] = 'ERROR'
os.environ['PYTORCH_JIT'] = '0'

import warnings, logging, io
stderr_backup = sys.stderr
sys.stderr = io.StringIO()
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)

# --- Core deps ---
import streamlit as st
import fitz  # PyMuPDF
import spacy
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import json, time, re, tempfile
from datetime import datetime
from collections import Counter
from pymongo import MongoClient
import plotly.graph_objects as go
import plotly.express as px

sys.stderr = stderr_backup
load_dotenv()

# --- Streamlit page ---
st.set_page_config(layout="wide", page_title="Smart Resume Screener", page_icon="🎯", initial_sidebar_state="collapsed")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');

/* ===== GLOBAL RESET & BASE ===== */
*{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif}
html,body,[class*="css"],.main,.stApp{background:#0a0e27!important;overflow-x:hidden}

/* ===== ANIMATED GRADIENT BACKGROUND ===== */
.stApp{
    background:linear-gradient(-45deg,#0a0e27,#1a1f3a,#16213e,#0f1728)!important;
    background-size:400% 400%!important;
    animation:gradientShift 15s ease infinite!important;
    position:relative;
    min-height:100vh;
}
@keyframes gradientShift{
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}

/* ===== FLOATING PARTICLES EFFECT ===== */
.stApp::before{
    content:'';
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background-image:radial-gradient(circle at 20% 50%,rgba(102,126,234,.06) 0%,transparent 50%),
                     radial-gradient(circle at 80% 80%,rgba(118,75,162,.06) 0%,transparent 50%),
                     radial-gradient(circle at 40% 20%,rgba(16,185,129,.04) 0%,transparent 50%);
    pointer-events:none;
    z-index:0;
    animation:particleFloat 20s ease-in-out infinite;
}
@keyframes particleFloat{
    0%,100%{transform:translate(0,0) scale(1)}
    33%{transform:translate(30px,-30px) scale(1.1)}
    66%{transform:translate(-20px,20px) scale(0.9)}
}

/* ===== TYPOGRAPHY ===== */
h1,h2,h3{font-family:'Poppins',sans-serif!important;color:#f1f5f9!important;font-weight:800!important;letter-spacing:-.03em!important;text-shadow:0 2px 10px rgba(0,0,0,.3)}
h4,h5,h6{font-family:'Poppins',sans-serif!important;color:#e2e8f0!important;font-weight:700!important}
p,span,div{color:#94a3b8!important;line-height:1.7!important}

/* ===== TABS WITH MODERN DESIGN ===== */
.stTabs [data-baseweb="tab-list"]{
    gap:20px;
    background:rgba(15,23,42,.6);
    border-bottom:none;
    padding:12px 24px;
    border-radius:20px 20px 0 0;
    backdrop-filter:blur(20px);
    box-shadow:0 -10px 30px rgba(0,0,0,.3);
}
.stTabs [data-baseweb="tab"]{
    height:56px;
    padding:0 36px;
    background:rgba(30,41,59,.5);
    border:2px solid rgba(148,163,184,.1);
    border-radius:14px;
    color:#94a3b8;
    font-weight:600;
    font-size:15px;
    letter-spacing:.3px;
    transition:all .4s cubic-bezier(.4,0,.2,1);
    backdrop-filter:blur(10px);
    position:relative;
    overflow:hidden;
}
.stTabs [data-baseweb="tab"]::before{
    content:'';
    position:absolute;
    top:0;
    left:-100%;
    width:100%;
    height:100%;
    background:linear-gradient(90deg,transparent,rgba(102,126,234,.2),transparent);
    transition:left .6s ease;
}
.stTabs [data-baseweb="tab"]:hover::before{left:100%}
.stTabs [data-baseweb="tab"]:hover{
    background:rgba(102,126,234,.12);
    border-color:rgba(102,126,234,.4);
    transform:translateY(-4px) scale(1.02);
    box-shadow:0 10px 30px rgba(102,126,234,.2);
}
.stTabs [aria-selected="true"]{
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)!important;
    color:#fff!important;
    border-color:rgba(102,126,234,.6)!important;
    box-shadow:0 15px 50px rgba(102,126,234,.5),inset 0 1px 0 rgba(255,255,255,.2)!important;
    transform:translateY(-2px);
}

/* ===== BUTTONS WITH GLOW EFFECT ===== */
.stButton>button{
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    color:#fff;
    border:none;
    border-radius:16px;
    padding:18px 52px;
    font-weight:700;
    font-size:16px;
    letter-spacing:1px;
    text-transform:uppercase;
    transition:all .4s cubic-bezier(.4,0,.2,1);
    box-shadow:0 12px 40px rgba(102,126,234,.4),inset 0 1px 0 rgba(255,255,255,.2);
    position:relative;
    overflow:hidden;
}
.stButton>button::before{
    content:'';
    position:absolute;
    top:50%;
    left:50%;
    width:0;
    height:0;
    border-radius:50%;
    background:rgba(255,255,255,.3);
    transform:translate(-50%,-50%);
    transition:width .6s,height .6s;
}
.stButton>button:hover::before{width:300px;height:300px}
.stButton>button:hover{
    transform:translateY(-4px) scale(1.02);
    box-shadow:0 20px 60px rgba(102,126,234,.6),0 0 40px rgba(118,75,162,.4),inset 0 1px 0 rgba(255,255,255,.3);
}
.stButton>button:active{transform:translateY(-2px) scale(.98)}

/* ===== FILE UPLOADER ===== */
.stFileUploader{
    background:rgba(30,41,59,.6);
    border:3px dashed rgba(102,126,234,.4);
    border-radius:20px;
    padding:32px;
    transition:all .4s cubic-bezier(.4,0,.2,1);
    backdrop-filter:blur(15px);
}
.stFileUploader:hover{
    background:rgba(102,126,234,.08);
    border-color:rgba(102,126,234,.7);
    transform:scale(1.01);
    box-shadow:0 15px 40px rgba(102,126,234,.15);
}

/* ===== TEXT AREA ===== */
.stTextArea textarea{
    background:rgba(30,41,59,.8)!important;
    border:2px solid rgba(148,163,184,.2)!important;
    border-radius:16px!important;
    color:#e2e8f0!important;
    font-size:15px!important;
    padding:20px!important;
    transition:all .3s ease!important;
    line-height:1.8!important;
}
.stTextArea textarea:focus{
    border-color:rgba(102,126,234,.8)!important;
    box-shadow:0 0 0 4px rgba(102,126,234,.15),0 10px 30px rgba(102,126,234,.2)!important;
    background:rgba(30,41,59,.95)!important;
}

/* ===== METRIC CARDS WITH GLASSMORPHISM ===== */
.metric-card{
    background:linear-gradient(135deg,rgba(30,41,59,.85) 0%,rgba(15,23,42,.85) 100%);
    border:1px solid rgba(148,163,184,.15);
    border-radius:24px;
    padding:28px;
    transition:all .5s cubic-bezier(.4,0,.2,1);
    backdrop-filter:blur(20px) saturate(180%);
    box-shadow:0 8px 32px rgba(0,0,0,.3);
    position:relative;
    overflow:hidden;
}
.metric-card::before{
    content:'';
    position:absolute;
    top:0;
    left:0;
    right:0;
    height:2px;
    background:linear-gradient(90deg,transparent,rgba(102,126,234,.6),transparent);
    opacity:0;
    transition:opacity .5s ease;
}
.metric-card:hover::before{opacity:1}
.metric-card:hover{
    border-color:rgba(102,126,234,.5);
    transform:translateY(-6px) scale(1.01);
    box-shadow:0 20px 50px rgba(102,126,234,.25),inset 0 1px 0 rgba(255,255,255,.05);
}

/* ===== ANALYSIS CARDS ===== */
.analysis-card{
    background:linear-gradient(135deg,rgba(30,41,59,.9) 0%,rgba(15,23,42,.85) 100%);
    border:1px solid rgba(148,163,184,.2);
    border-radius:20px;
    padding:28px;
    transition:all .4s cubic-bezier(.4,0,.2,1);
    backdrop-filter:blur(20px);
    box-shadow:0 10px 40px rgba(0,0,0,.3);
}
.analysis-card:hover{
    border-color:rgba(102,126,234,.5);
    transform:translateY(-4px);
    box-shadow:0 15px 50px rgba(102,126,234,.2);
}

/* ===== SCORE BADGES WITH 3D EFFECT ===== */
.score-badge{
    display:inline-block;
    padding:20px 40px;
    border-radius:28px;
    font-family:'Poppins',sans-serif;
    font-weight:900;
    font-size:48px;
    box-shadow:0 15px 40px rgba(0,0,0,.4),inset 0 2px 0 rgba(255,255,255,.3),inset 0 -2px 0 rgba(0,0,0,.3);
    transition:all .4s cubic-bezier(.4,0,.2,1);
    position:relative;
}
.score-badge:hover{transform:scale(1.08) rotate(-2deg);box-shadow:0 20px 60px rgba(0,0,0,.5),inset 0 2px 0 rgba(255,255,255,.4)}
.score-excellent{background:linear-gradient(135deg,#10b981 0%,#059669 100%);color:#fff;box-shadow:0 15px 50px rgba(16,185,129,.6)}
.score-good{background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%);color:#fff;box-shadow:0 15px 50px rgba(59,130,246,.6)}
.score-fair{background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);color:#fff;box-shadow:0 15px 50px rgba(245,158,11,.6)}
.score-poor{background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%);color:#fff;box-shadow:0 15px 50px rgba(239,68,68,.6)}

/* ===== CHIPS ===== */
.chip{
    display:inline-block;
    margin:4px 8px 4px 0;
    padding:8px 16px;
    border-radius:24px;
    background:rgba(102,126,234,.18);
    border:1px solid rgba(102,126,234,.4);
    font-size:13px;
    font-weight:600;
    color:#cbd5e1;
    transition:all .3s cubic-bezier(.4,0,.2,1);
    box-shadow:0 2px 8px rgba(102,126,234,.15);
}
.chip:hover{
    background:rgba(102,126,234,.3);
    border-color:rgba(102,126,234,.7);
    transform:translateY(-2px);
    box-shadow:0 6px 16px rgba(102,126,234,.3);
}

/* ===== DIVIDERS ===== */
hr{
    border:none;
    height:2px;
    background:linear-gradient(90deg,transparent,rgba(148,163,184,.4),transparent);
    margin:32px 0;
    position:relative;
}
hr::before{
    content:'';
    position:absolute;
    top:-1px;
    left:50%;
    transform:translateX(-50%);
    width:80px;
    height:4px;
    background:linear-gradient(90deg,#667eea,#764ba2);
    border-radius:2px;
    box-shadow:0 2px 10px rgba(102,126,234,.5);
}

/* ===== EXPANDERS ===== */
.stExpander{
    background:rgba(30,41,59,.7)!important;
    border:1px solid rgba(148,163,184,.2)!important;
    border-radius:16px!important;
    transition:all .3s ease!important;
    backdrop-filter:blur(10px)!important;
}
.stExpander:hover{border-color:rgba(102,126,234,.5)!important;box-shadow:0 8px 24px rgba(102,126,234,.15)!important}
.stExpander [data-testid="stExpanderToggleButton"]{color:#e2e8f0!important;font-weight:600!important}

/* ===== PROGRESS BARS ===== */
.stProgress>div>div{
    background:linear-gradient(90deg,#667eea,#764ba2)!important;
    border-radius:10px!important;
    box-shadow:0 2px 10px rgba(102,126,234,.5)!important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:rgba(15,23,42,.8);border-radius:10px}
::-webkit-scrollbar-thumb{background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;border:2px solid rgba(15,23,42,.8)}
::-webkit-scrollbar-thumb:hover{background:linear-gradient(135deg,#764ba2,#667eea)}

/* ===== SECTION HEADERS ===== */
.section-header{
    font-size:24px;
    font-weight:800;
    color:#f1f5f9!important;
    margin-bottom:20px;
    text-transform:uppercase;
    letter-spacing:1.2px;
    text-shadow:0 2px 10px rgba(102,126,234,.6);
    font-family:'Poppins',sans-serif!important;
}

/* ===== FADE IN ANIMATION ===== */
@keyframes fadeInUp{
    from{opacity:0;transform:translateY(30px)}
    to{opacity:1;transform:translateY(0)}
}
.metric-card,.analysis-card{animation:fadeInUp .6s ease-out backwards}
.metric-card:nth-child(2){animation-delay:.1s}
.metric-card:nth-child(3){animation-delay:.2s}

/* ===== HIDE STREAMLIT DEFAULT ELEMENTS ===== */
#MainMenu{visibility:hidden}
footer{visibility:hidden}
header{visibility:hidden}
.stDeployButton{display:none}
[data-testid="stToolbar"]{display:none}

/* ===== UTILITIES ===== */
.small{font-size:12px;color:#9aa5b1;letter-spacing:.3px}
.glow-text{text-shadow:0 0 20px rgba(102,126,234,.8),0 0 40px rgba(102,126,234,.6)}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- Session state ---
if 'models_loaded' not in st.session_state: st.session_state.models_loaded = False
if 'analysis_history' not in st.session_state: st.session_state.analysis_history = []
if 'uploads_history' not in st.session_state: st.session_state.uploads_history = []
if 'current_analysis' not in st.session_state: st.session_state.current_analysis = None

# --- UI helper ---
def section(title, emoji=""):
    st.markdown(
        f"<div class='analysis-card'><h3 style='margin-top:0;font-size:22px;color:#e2e8f0;'>{emoji} {title}</h3></div>",
        unsafe_allow_html=True
    )

# --- Config (weights) ---
DEFAULT_WEIGHTS = {"semantic":0.35, "coverage":0.50, "llm_fit":0.15}

# --- Models / DB ---
@st.cache_resource(show_spinner=False)
def load_models():
    # Try Streamlit secrets first (for cloud deployment), then fall back to environment variables
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, AttributeError):
        api_key = os.getenv("GEMINI_API_KEY", "")
    
    api_key = api_key.strip() if api_key else ""
    if not api_key: return None, None, None, False
    genai.configure(api_key=api_key)

    try:
        preferred = st.secrets.get("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    except (KeyError, AttributeError):
        preferred = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    
    preferred = (preferred.strip() if preferred else "gemini-2.5-flash") or "gemini-2.5-flash"
    fallbacks = [
        preferred, "gemini-2.5-pro", "gemini-flash-latest", "gemini-pro-latest",
        "gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-1.0-pro"
    ]
    try:
        available = {
            m.name.split('/')[-1]
            for m in genai.list_models()
            if getattr(m, "supported_generation_methods", []) and "generateContent" in m.supported_generation_methods
        }
    except Exception:
        available = set()

    model = None
    for cand in fallbacks:
        simple = cand.replace("models/", "")
        if available and simple not in available: continue
        try:
            candidate = genai.GenerativeModel(simple)
            candidate.count_tokens("health check")
            model = candidate
            st.session_state["gemini_model_name"] = simple
            break
        except Exception:
            continue
    if not model: return None, None, None, False

    # spaCy - load full model with parser (required)
    nlp = spacy.load("en_core_web_sm")
    
    # Verify all required components are available
    if "parser" not in nlp.pipe_names:
        raise RuntimeError("spaCy parser component not available. Please ensure en_core_web_sm is properly installed.")
    if "tagger" not in nlp.pipe_names:
        raise RuntimeError("spaCy tagger component not available. Please ensure en_core_web_sm is properly installed.")

    # Stronger default embedder
    s_name = os.getenv("SENTENCE_MODEL_NAME", "all-mpnet-base-v2")
    embedder = SentenceTransformer(s_name, device='cpu')

    return model, nlp, embedder, True

@st.cache_resource(show_spinner=False)
def init_mongodb():
    # Try Streamlit secrets first (for cloud deployment), then fall back to environment variables
    try:
        uri = st.secrets["MONGO_URI"]
    except (KeyError, AttributeError):
        uri = os.getenv("MONGO_URI", "")
    
    uri = uri.strip() if uri else ""
    if not uri: return None, None, False
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000)
        client.admin.command('ping')
        db = client["resume_db"]
        return db["resumes"], db["analyses"], True
    except Exception:
        return None, None, False

# --- NLP / utils ---
def normalize_text(s):
    s = s.lower().strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def chunk_text(t, max_chars=1200, overlap=150, nlp=None):
    t = re.sub(r'\n{3,}', '\n\n', t).strip()
    if "sentencizer" not in nlp.pipe_names:
        try: nlp.add_pipe("sentencizer")
        except: pass
    doc = nlp(t)
    sents = [s.text.strip() for s in getattr(doc, "sents", []) if s.text.strip()]
    chunks, buf = [], ""
    for s in sents:
        if len(buf) + len(s) + 1 <= max_chars:
            buf = (buf + " " + s).strip()
        else:
            if buf: chunks.append(buf)
            if overlap > 0 and len(buf) > overlap:
                buf = buf[-overlap:] + " " + s
            else:
                buf = s
    if buf: chunks.append(buf)
    return chunks

def parse_contacts(txt):
    emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', txt)
    phones = re.findall(r'(\+?\d[\d\s().-]{8,}\d)', txt)
    return (emails[0] if emails else "Not found"), (phones[0] if phones else "Not found")

def build_index(embedder, chunks):
    embs = embedder.encode(chunks, batch_size=32, convert_to_numpy=True, normalize_embeddings=True)
    dim = embs.shape[1]
    idx = faiss.IndexFlatIP(dim)
    idx.add(embs.astype(np.float32))
    return idx, embs

def compute_global_semantic(embedder, resume_embs, jd_text):
    """Global semantic: top-5 avg of resume embeddings vs. JD (normalized to [0,1])."""
    if resume_embs is None or len(resume_embs)==0: 
        return 0.0
    try:
        job_vec = embedder.encode(jd_text, convert_to_numpy=True, normalize_embeddings=True)
        if job_vec.ndim>1: 
            job_vec = job_vec[0]
        sims = np.dot(resume_embs, job_vec)
        if sims.size == 0: 
            return 0.0
        topk = np.sort(sims)[-5:] if sims.size >=5 else sims
        return float(np.clip(np.mean(topk), 0.0, 1.0))
    except Exception:
        return 0.0

def extract_sections(text):
    """Heuristic section splitter (no lexicons)."""
    lines = [l.strip() for l in text.splitlines()]
    blocks, cur, cur_title = [], [], "header"
    for l in lines:
        if re.match(r'^[A-Z][A-Za-z ]{1,40}:$|^[A-Z][A-Za-z &/]{1,50}$', l) and len(l.split())<=8:
            if cur:
                blocks.append((cur_title, "\n".join(cur).strip()))
                cur = []
            cur_title = l.strip(':').lower()
        else:
            cur.append(l)
    if cur:
        blocks.append((cur_title, "\n".join(cur).strip()))
    # fallback single block
    if not blocks:
        blocks = [("content", text)]
    return blocks

def token_set(text):
    return set(re.findall(r'[a-z0-9][a-z0-9+.#-]*', normalize_text(text)))

def contains_atom(atom, text_tokens):
    """Enhanced detection with better fuzzy matching for compound terms."""
    a = normalize_text(atom)
    if len(a) < 2: return False
    
    # exact substring check (normalized)
    text_str = " ".join(sorted(list(text_tokens)))
    if a in text_str:
        return True
    
    # Check for partial matches with common variations
    # e.g., "ai ml technologies" -> check for "ai", "ml", "technologies"
    a_tok = set(re.findall(r'[a-z0-9][a-z0-9+.#-]*', a))
    if not a_tok: return False
    
    # Full match: all tokens present
    if a_tok.issubset(text_tokens):
        return True
    
    # Fuzzy match: at least 70% of tokens present for compound terms
    if len(a_tok) > 1:
        matched = sum(1 for t in a_tok if t in text_tokens)
        if matched / len(a_tok) >= 0.7:
            return True
    
    return False

def coverage_from_atoms_semantic(must_atoms, nice_atoms, resume_chunks, embedder, threshold=0.30):
    """Semantic-based coverage: each requirement matched via embedding similarity with fuzzy scoring."""
    if not resume_chunks or (not must_atoms and not nice_atoms):
        return 0.0, 0.0, 0.0, [], []
    try:
        chunk_embs = embedder.encode(resume_chunks, convert_to_numpy=True, normalize_embeddings=True)
        if chunk_embs.ndim == 1:
            chunk_embs = chunk_embs.reshape(1, -1)
    except Exception:
        return 0.0, 0.0, 0.0, [], []
    
    must_hits, nice_hits = [], []
    
    # Process must-have requirements with fuzzy scoring
    for atom in must_atoms:
        try:
            atom_emb = embedder.encode(atom, convert_to_numpy=True, normalize_embeddings=True)
            if atom_emb.ndim > 1:
                atom_emb = atom_emb[0]
            # Compute similarities
            sims = np.dot(chunk_embs, atom_emb)
            max_sim = float(np.max(sims)) if sims.size > 0 else 0.0
            
            # Fuzzy scoring: give partial credit for near-matches
            if max_sim >= threshold:
                score = 1.0  # Full match
            elif max_sim >= (threshold - 0.10):
                score = 0.6  # Partial match (60% credit)
            elif max_sim >= (threshold - 0.15):
                score = 0.3  # Weak match (30% credit)
            else:
                score = 0.0  # No match
            must_hits.append(score)
        except Exception:
            must_hits.append(0.0)
    
    # Process nice-to-have requirements with same fuzzy logic
    for atom in nice_atoms:
        try:
            atom_emb = embedder.encode(atom, convert_to_numpy=True, normalize_embeddings=True)
            if atom_emb.ndim > 1:
                atom_emb = atom_emb[0]
            sims = np.dot(chunk_embs, atom_emb)
            max_sim = float(np.max(sims)) if sims.size > 0 else 0.0
            
            # Same fuzzy scoring
            if max_sim >= threshold:
                score = 1.0
            elif max_sim >= (threshold - 0.10):
                score = 0.6
            elif max_sim >= (threshold - 0.15):
                score = 0.3
            else:
                score = 0.0
            nice_hits.append(score)
        except Exception:
            nice_hits.append(0.0)
    
    must_cov = float(np.mean(must_hits)) if must_hits else 0.0
    nice_cov = float(np.mean(nice_hits)) if nice_hits else 0.0
    cov = 0.75*must_cov + 0.25*nice_cov if (must_hits or nice_hits) else 0.0
    return cov, must_cov, nice_cov, must_hits, nice_hits

def extract_atoms_from_text(text, nlp, max_atoms=60):
    """Dynamic atom candidates from JD (no lexicons): noun-chunks + list parsing + compact phrases."""
    text = text.strip()
    doc = nlp(text)
    cands = []
    
    # Extract noun chunks (parser is required and verified at startup)
    for nc in doc.noun_chunks:
        s = normalize_text(nc.text)
        if 2 <= len(s) <= 50: cands.append(s)

    for seg in re.split(r'[\n]', text):
        parts = re.split(r'[|/•;,:()]', seg)
        for p in parts:
            p = normalize_text(p.strip(" -/•|,;:"))
            if 2 <= len(p) <= 50 and len(p.split()) <= 5:
                cands.append(p)

    pattern = re.compile(r'[a-z0-9][a-z0-9+.#-]*(?:\s+[a-z0-9][a-z0-9+.#-]*){0,4}')
    for m in pattern.finditer(normalize_text(text)):
        s = m.group(0).strip()
        if 2 <= len(s) <= 50:
            cands.append(s)

    generic = set(["experience","skills","tools","technologies","knowledge","projects","project",
                   "responsibilities","requirements","good to have","must have","engineer","engineering",
                   "developer","analyst","internship","intern","fresher"])
    cands = [c for c in cands if c not in generic and not c.isdigit()]
    freq = Counter(cands)
    scored = []
    for k,v in freq.items():
        tokens = k.split()
        boost = 1.15 if 1 <= len(tokens) <= 3 else 1.0
        scored.append((v*boost, -len(k), k))
    scored.sort(reverse=True)
    dedup, seen = [], set()
    for _,__,k in scored:
        if k not in seen:
            seen.add(k); dedup.append(k)
        if len(dedup) >= max_atoms: break
    return dedup

# ---- LLM wrappers / prompts ----
def llm_json(model, prompt):
    try:
        resp = model.generate_content(
            prompt,
            generation_config={"response_mime_type":"application/json","temperature":0.15,"top_p":0.9}
        )
        text = resp.text or ""
    except TypeError:
        resp = model.generate_content(prompt); text = resp.text or ""
    s = text.strip()
    if not s.startswith("{"):
        m = re.search(r"\{.*\}", s, re.S)
        s = m.group(0) if m else s
    try:
        return json.loads(s)
    except:
        s = s.replace("```json","").replace("```","").strip()
        try: return json.loads(s)
        except: return {}

def llm_verify_requirements(model, requirements, resume_text, req_type="must-have"):
    """
    LLM-assisted verification to enhance local model detection.
    This is a post-processing step that helps catch semantic matches the local model might miss.
    """
    if not requirements or not resume_text:
        return {}
    
    req_list = "\n".join([f"- {r}" for r in requirements])
    prompt = f"""
Analyze if the following {req_type} requirements are present in the resume.
For each requirement, return "true" if found (even if implied or using synonyms), "false" otherwise.

REQUIREMENTS:
{req_list}

RESUME EXCERPT (first 2000 chars):
{resume_text[:2000]}

Return ONLY JSON format: {{"requirement_text": true/false, ...}}
Be generous with semantic matches (e.g., "AI/ML" matches "artificial intelligence", "machine learning", "deep learning").
"""
    
    try:
        result = llm_json(model, prompt)
        return result if isinstance(result, dict) else {}
    except:
        return {}

def jd_plan_prompt(jd, preview):
    return f"""
Return ONLY JSON with:
role_title, seniority (strings);
must_have, good_to_have, soft_skills, certifications, red_flags, questions_to_ask, enrichment_cues (string arrays);
scoring_weights (object with keys semantic, coverage, llm_fit; sum=1.0).
Keep phrases concise. No fluff.

JOB_DESCRIPTION:
{jd}

RESUME_PREVIEW:
{preview}
"""

def resume_profile_prompt(full_resume_text):
    return f"""
Return ONLY JSON with:
summary (<=30 words),
core_skills (8-15 strings),
projects ([{{name, description, impact}}]),
cloud_experience (string[]),
ml_ai_experience (string[]),
certifications (string[]),
tools (string[]),
notable_metrics (string[]).
Do not invent facts.

RESUME_TEXT:
{full_resume_text}
"""

def atomicize_requirements_prompt(jd, resume_preview):
    return f"""
Return ONLY JSON with:
- must_atoms: 10-30 short atomic requirements strictly derived from the JOB DESCRIPTION (<=4 words each).
- nice_atoms: 5-20 atomic nice-to-haves strictly from the JOB DESCRIPTION.
Avoid vague items like "cloud engineering", "good communication". Use concise, concrete tokens (e.g., "python", "linux admin", "vpc", "api design").

JOB DESCRIPTION:
{jd}

RESUME PREVIEW (for context only; do NOT add atoms not present in JD):
{resume_preview}
"""

def analysis_prompt(jd, plan, profile, global_sem, cov_final, cov_parts):
    return f"""
Return ONLY JSON with:
cultural_fit, technical_strength, experience_relevance (<=60 words each),
top_strengths (string[]),
improvement_areas (string[]),
overall_comment (<=80 words),
risk_flags (string[]),
followup_questions (string[]),
fit_score (0..10 number; reflect semantic + coverage + LLM judgment; do not output strings).

SCORING GUIDANCE (IMPORTANT - Use holistic assessment):
- If semantic >= 0.70 (high semantic match), start with fit_score 7-8 baseline
- If semantic >= 0.60 and coverage_final >= 0.40, fit_score should be 6-7
- If semantic >= 0.50 and coverage_final >= 0.30, fit_score should be 5-6
- Coverage includes partial matches (0.6 weight for near-matches); don't penalize too harshly for slightly lower coverage
- Prioritize semantic match over exact keyword coverage - semantic shows actual relevance
- Low coverage (<0.30) AND low semantic (<0.40) → fit_score 3-4
- Focus on overall competency alignment, not just keyword matching

CONTEXT:
- JOB_DESCRIPTION: {jd}
- PLAN: {json.dumps(plan, ensure_ascii=False)}
- RESUME_PROFILE: {json.dumps(profile, ensure_ascii=False)}
- GLOBAL_SEMANTIC (0..1): {global_sem:.4f}
- COVERAGE_FINAL (0..1): {cov_final:.4f}
- COVERAGE_PARTS: {json.dumps(cov_parts, ensure_ascii=False)}
"""

# ---- File parsing ----
def parse_resume_pdf(path, nlp, embedder):
    doc = fitz.open(path)
    text = "\n".join([p.get_text() for p in doc])
    doc.close()
    if not text.strip(): return None

    # Name extraction that avoids emails/phones
    first_line = (text.splitlines() or [""])[0][:120]
    first_line = re.sub(r'\S+@\S+','', first_line)
    first_line = re.sub(r'\+?\d[\d\s().-]{8,}\d','', first_line).strip()
    name = None
    if re.match(r'^[A-Za-z][A-Za-z .-]{1,60}$', first_line):
        name = first_line
    if not name:
        try:
            dn = nlp(text[:600])
            cand = [e.text for e in dn.ents if e.label_=="PERSON" and len(e.text) <= 60 and '@' not in e.text]
            name = cand[0] if cand else "Unknown"
        except:
            name = "Unknown"

    email, phone = parse_contacts(text)
    chunks = chunk_text(text, nlp=nlp)
    idx, embs = build_index(embedder, chunks)
    return {"name":name,"email":email,"phone":phone,"text":text,"chunks":chunks,"faiss":idx,"embs":embs}

# ---- Mongo helpers ----
def _sanitize_for_mongo(value):
    import numpy as _np
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (_np.integer,)): return int(value)
    if isinstance(value, (_np.floating,)): return float(value)
    if isinstance(value, _np.ndarray): return value.tolist()
    if isinstance(value, (list, tuple)): return [_sanitize_for_mongo(v) for v in value]
    if isinstance(value, dict): return {str(k): _sanitize_for_mongo(v) for k,v in value.items()}
    return str(value)

def save_to_db(resume_doc, jd, analysis, resumes_collection, analyses_collection, mongo_ok):
    rid = None
    try:
        if mongo_ok and resumes_collection:
            rdoc = {k:resume_doc[k] for k in ["name","email","phone"]}
            rdoc["file_name"] = resume_doc.get("file_name","unknown")
            rdoc["timestamp"] = time.time()
            r = resumes_collection.insert_one(rdoc)
            rid = str(r.inserted_id)
        if mongo_ok and analyses_collection:
            adoc = {"resume_id":rid,
                    "candidate":resume_doc.get("name","Unknown"),
                    "email":resume_doc.get("email","N/A"),
                    "file_name":resume_doc.get("file_name","unknown"),
                    "job_desc":jd,
                    "analysis":_sanitize_for_mongo(analysis),
                    "timestamp":time.time()}
            analyses_collection.insert_one(adoc)
    except Exception as exc:
        st.warning(f"MongoDB persistence skipped: {exc}")

def get_recent(analyses_collection, mongo_ok, limit=20):
    items = []
    try:
        if mongo_ok and analyses_collection:
            for x in analyses_collection.find({}, sort=[("timestamp",-1)]).limit(limit):
                items.append(x)
    except: pass
    return items

# =======================
# =======  UI  ==========
# =======================

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    dbg = st.toggle("Show debug details", value=False)
    st.caption("Tip: Turn on for atoms/coverage internals.")

with st.spinner('Initializing models...'):
    model, nlp, embedder, models_ok = load_models()
    resumes_collection, analyses_collection, mongo_ok = init_mongodb()

if not models_ok:
    st.error("Gemini model unavailable. Set GEMINI_API_KEY and a valid GEMINI_MODEL_NAME.")
    st.stop()

# ===== HERO HEADER =====
st.markdown("""
<div style="text-align:center;padding:40px 0 20px 0;position:relative;">
    <div style="display:inline-block;position:relative;">
        <h1 class="glow-text" style="font-size:52px;margin:0;font-weight:900;background:linear-gradient(135deg,#667eea 0%,#764ba2 50%,#10b981 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;letter-spacing:-0.02em;">
            🎯 Smart Resume Screener
        </h1>
        <p style="font-size:18px;color:#94a3b8;margin:12px 0 0 0;font-weight:500;letter-spacing:0.5px;">
            AI-Powered Resume Analysis • Semantic Matching • Intelligent Insights
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("gemini_model_name"):
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:24px;">
        <span class="chip">🤖 {st.session_state['gemini_model_name']}</span>
        <span class="chip">🧠 {os.getenv('SENTENCE_MODEL_NAME','all-mpnet-base-v2')}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin:20px 0 32px 0'/>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📄 Analyze", "🕒 Recent"])

# --- Analyze tab ---
with tab1:
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1,1], gap="large")
    with c1:
        section("Upload Resume (PDF)", "📤")
        up = st.file_uploader("pdf", type=['pdf'], label_visibility="collapsed")
    with c2:
        section("Job Description", "📝")
        jd = st.text_area("jd", height=220, label_visibility="collapsed", placeholder="Paste a detailed job description...")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    go_analyze = st.button("🚀 Analyze Resume", use_container_width=True)

    if go_analyze:
        if not up:
            st.error("Upload a resume PDF.")
        elif not jd or len(jd)<50:
            st.error("Enter a detailed job description (min 50 chars).")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(up.getvalue())
                tmp_path = tmp.name
            try:
                prog = st.empty()
                stat = st.empty()

                # ---------- Parse resume ----------
                prog.progress(0.12); stat.info("Parsing resume...")
                parsed = parse_resume_pdf(tmp_path, nlp, embedder)
                if not parsed:
                    st.error("No text parsed from the PDF."); st.stop()
                parsed["file_name"] = up.name
                preview = "\n".join(parsed["chunks"][:2])[:1200]
                st.session_state.uploads_history.insert(0, {"file_name":up.name,"name":parsed["name"],"email":parsed["email"],"phone":parsed["phone"],"timestamp":time.time()})

                # ---------- Plan & profile ----------
                prog.progress(0.28); stat.info("Deriving analysis plan...")
                plan = llm_json(model, jd_plan_prompt(jd, preview))
                if not plan or not isinstance(plan, dict):
                    plan = {"role_title":"","seniority":"",
                            "must_have":[],"good_to_have":[],"soft_skills":[],"certifications":[],
                            "scoring_weights":DEFAULT_WEIGHTS.copy(),
                            "red_flags":[],"questions_to_ask":[],"enrichment_cues":[]}
                # sane weights fallback
                w = plan.get("scoring_weights") or {}
                if not isinstance(w, dict) or not all(k in w for k in ("semantic","coverage","llm_fit")):
                    plan["scoring_weights"] = DEFAULT_WEIGHTS.copy()

                prog.progress(0.36); stat.info("Parsing resume profile...")
                profile = llm_json(model, resume_profile_prompt(parsed["text"])) or {}
                parsed["llm_profile"] = profile

                # ---------- Atomic requirements (LLM + heuristic) ----------
                prog.progress(0.46); stat.info("Extracting atomic requirements...")
                atoms_llm = llm_json(model, atomicize_requirements_prompt(jd, preview)) or {}
                jd_atoms_raw = extract_atoms_from_text(jd, nlp, max_atoms=60)

                def clean_atoms(xs):
                    out, seen = [], set()
                    for a in xs:
                        if not isinstance(a, str): continue
                        a = normalize_text(a)
                        if 2 <= len(a) <= 50 and a not in seen:
                            seen.add(a); out.append(a)
                    return out

                must_atoms = clean_atoms((atoms_llm.get("must_atoms") or []) + jd_atoms_raw[:30])
                nice_atoms = clean_atoms((atoms_llm.get("nice_atoms") or []) + jd_atoms_raw[30:60])

                # ---------- Coverage (semantic similarity over chunks) ----------
                prog.progress(0.58); stat.info("Scoring requirement coverage...")
                cov_final, must_cov, nice_cov, must_hits, nice_hits = coverage_from_atoms_semantic(
                    must_atoms, nice_atoms, parsed.get("chunks", []), embedder, threshold=0.28
                )

                # ---------- Global semantic ----------
                prog.progress(0.68); stat.info("Computing semantic similarity...")
                global_sem = compute_global_semantic(embedder, parsed.get("embs"), jd)
                global_sem01 = (global_sem + 1.0) / 2.0  # map [-1,1] -> [0,1]

                # ---------- LLM narrative & fit ----------
                prog.progress(0.78); stat.info("LLM narrative assessment...")
                cov_parts = {
                    "must_coverage": round(must_cov,3),
                    "nice_coverage": round(nice_cov,3),
                    "must_atoms_count": len(must_atoms),
                    "nice_atoms_count": len(nice_atoms)
                }
                llm_out = llm_json(model, analysis_prompt(jd, plan, profile, global_sem01, cov_final, cov_parts))
                fit_score = llm_out.get("fit_score")
                if not isinstance(fit_score, (int, float)):
                    # fallback: calibrated blend
                    fit_score = round(10*(0.5*global_sem01 + 0.5*cov_final), 1)
                fit_score = float(np.clip(fit_score, 0, 10))

                # ---------- Final score (bounded, interpretable) ----------
                weights = plan.get("scoring_weights", DEFAULT_WEIGHTS)
                sem10, cov10 = round(10*global_sem01,1), round(10*cov_final,1)
                w_sem, w_cov, w_llm = float(weights["semantic"]), float(weights["coverage"]), float(weights["llm_fit"])
                W = w_sem + w_cov + w_llm
                if W <= 1e-9:
                    w_sem, w_cov, w_llm = DEFAULT_WEIGHTS["semantic"], DEFAULT_WEIGHTS["coverage"], DEFAULT_WEIGHTS["llm_fit"]
                    W = w_sem + w_cov + w_llm
                w_sem, w_cov, w_llm = w_sem/W, w_cov/W, w_llm/W
                final_score = float(np.clip(w_sem*sem10 + w_cov*cov10 + w_llm*fit_score, 0, 10))
                components = {"Semantic": round(w_sem*sem10,1), "Coverage": round(w_cov*cov10,1), "LLM Fit": round(w_llm*fit_score,1)}

                # ---------- Package result ----------
                result = {
                    "score": round(final_score,1),
                    "semantic_score": round(sem10,1),
                    "coverage_score": round(cov10,1),
                    "llm_fit_score": round(fit_score,1),
                    "coverage_parts": cov_parts,
                    "atoms": {"must": must_atoms, "nice": nice_atoms},
                    "plan": plan,
                    "resume_profile": profile,
                    "llm_analysis":{
                        "cultural_fit": llm_out.get("cultural_fit",""),
                        "technical_strength": llm_out.get("technical_strength",""),
                        "experience_relevance": llm_out.get("experience_relevance",""),
                        "top_strengths": llm_out.get("top_strengths",[]),
                        "improvement_areas": llm_out.get("improvement_areas",[]),
                        "overall_comment": llm_out.get("overall_comment",""),
                        "risk_flags": llm_out.get("risk_flags",[]),
                        "followup_questions": llm_out.get("followup_questions",[])
                    },
                    "components": components,
                    "resume_meta":{"name":parsed["name"],"email":parsed["email"],"phone":parsed["phone"],"file_name":parsed["file_name"]},
                    "timestamp": time.time()
                }

                save_to_db(parsed, jd, result, resumes_collection, analyses_collection, mongo_ok)
                st.session_state.analysis_history.insert(0, result)
                st.session_state.analysis_history = st.session_state.analysis_history[:100]
                st.session_state.current_analysis = (parsed, result)

                prog.progress(1.0); stat.success("Done")
                time.sleep(0.2); prog.empty(); stat.empty()
                st.rerun()
            finally:
                try: os.unlink(tmp_path)
                except: pass

    # ------- Render current analysis -------
    if st.session_state.current_analysis:
        resume, analysis = st.session_state.current_analysis
        st.markdown("<hr>", unsafe_allow_html=True)

        # ===== Stunning Header: Candidate + Score Badge =====
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(102,126,234,.15) 0%,rgba(118,75,162,.15) 100%);
                    border:2px solid rgba(102,126,234,.3);border-radius:28px;padding:32px;margin-bottom:32px;
                    box-shadow:0 20px 60px rgba(102,126,234,.25);position:relative;overflow:hidden;">
            <div style="position:absolute;top:-50px;right:-50px;width:200px;height:200px;
                        background:radial-gradient(circle,rgba(102,126,234,.2) 0%,transparent 70%);
                        border-radius:50%;"></div>
            <div style="display:grid;grid-template-columns:1fr auto;gap:32px;align-items:center;position:relative;z-index:1;">
                <div>
                    <h2 style="margin:0;color:#f1f5f9;font-size:42px;font-weight:900;font-family:'Poppins',sans-serif;
                               text-shadow:0 2px 10px rgba(0,0,0,.3);">
                        {resume['name']}
                    </h2>
                    <div style="margin-top:16px;display:flex;gap:20px;flex-wrap:wrap;">
                        <span class="chip" style="font-size:14px;">
                            <span style="opacity:0.7;">�</span> {resume['email']}
                        </span>
                        <span class="chip" style="font-size:14px;">
                            <span style="opacity:0.7;">📱</span> {resume['phone']}
                        </span>
                    </div>
                </div>
                <div style="text-align:center;padding:24px;background:rgba(15,23,42,.6);border-radius:24px;
                            border:3px solid {'rgba(16,185,129,.6)' if analysis['score']>=8 else 'rgba(59,130,246,.6)' if analysis['score']>=6 else 'rgba(245,158,11,.6)' if analysis['score']>=4 else 'rgba(239,68,68,.6)'};
                            box-shadow:0 10px 40px {'rgba(16,185,129,.4)' if analysis['score']>=8 else 'rgba(59,130,246,.4)' if analysis['score']>=6 else 'rgba(245,158,11,.4)' if analysis['score']>=4 else 'rgba(239,68,68,.4)'};
                            backdrop-filter:blur(10px);">
                    <p style="margin:0;font-size:12px;color:#94a3b8;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;">Overall Match</p>
                    <div class="score-badge {'score-excellent' if analysis['score']>=8 else 'score-good' if analysis['score']>=6 else 'score-fair' if analysis['score']>=4 else 'score-poor'}" 
                         style="font-size:56px;margin:12px 0;padding:16px 36px;">
                        {analysis['score']}
                    </div>
                    <p style="margin:0;font-size:16px;font-weight:800;color:#f1f5f9;text-transform:uppercase;letter-spacing:1px;">
                        {'🌟 Excellent' if analysis['score']>=8 else '👍 Good' if analysis['score']>=6 else '⚠️ Fair' if analysis['score']>=4 else '❌ Poor'}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== Key Metrics Dashboard =====
        st.markdown("""
        <div style="text-align:center;margin:32px 0 24px 0;">
            <h3 class="section-header" style="display:inline-block;padding:12px 32px;background:rgba(102,126,234,.1);
                       border-radius:16px;border:2px solid rgba(102,126,234,.3);">
                📊 Match Metrics
            </h3>
        </div>
        """, unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3, gap="medium")
        
        def metric_card(title, value, icon, color):
            return f"""
            <div class="metric-card" style="text-align:center;border-left:5px solid {color};position:relative;overflow:hidden;">
                <div style="position:absolute;top:-20px;right:-20px;font-size:80px;opacity:0.08;">{icon}</div>
                <p style="margin:0;font-size:13px;color:#7a8b99;text-transform:uppercase;letter-spacing:1px;font-weight:700;">{title}</p>
                <h3 style="margin:16px 0 8px 0;font-size:48px;font-weight:900;color:{color};font-family:'Poppins',sans-serif;text-shadow:0 2px 10px {color}50;">{value:.1f}</h3>
                <p style="margin:0;font-size:13px;color:#94a3b8;font-weight:600;">out of 10</p>
                <div style="margin-top:12px;height:6px;background:rgba(148,163,184,.1);border-radius:10px;overflow:hidden;">
                    <div style="width:{value*10}%;height:100%;background:linear-gradient(90deg,{color},{color}dd);border-radius:10px;transition:width 1s ease;box-shadow:0 0 10px {color}80;"></div>
                </div>
            </div>
            """
        
        with m1:
            st.markdown(metric_card("Semantic Match", analysis['semantic_score'], "🧠", "#667eea"), unsafe_allow_html=True)
        with m2:
            st.markdown(metric_card("Coverage Score", analysis['coverage_score'], "✓", "#10b981"), unsafe_allow_html=True)
        with m3:
            st.markdown(metric_card("LLM Assessment", analysis['llm_fit_score'], "⚡", "#f59e0b"), unsafe_allow_html=True)
        
        # ===== Beautiful Visualizations =====
        st.markdown("""
        <div style="text-align:center;margin:40px 0 28px 0;">
            <h3 class="section-header" style="display:inline-block;padding:12px 32px;background:rgba(102,126,234,.1);
                       border-radius:16px;border:2px solid rgba(102,126,234,.3);">
                📈 Detailed Assessment
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        v1, v2 = st.columns(2, gap="large")
        
        with v1:
            # Stunning gauge chart with 3D effect
            score_val = analysis['score']
            gauge_color = '#10b981' if score_val >= 8 else '#3b82f6' if score_val >= 6 else '#f59e0b' if score_val >= 4 else '#ef4444'
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score_val,
                domain={'x': [0,1], 'y': [0,1]},
                title={
                    'text': "<b>Overall Fit Score</b>",
                    'font': {'size': 24, 'color': '#f1f5f9', 'family': 'Poppins'}
                },
                number={
                    'suffix': "<span style='font-size:0.6em;color:#94a3b8'>/10</span>",
                    'font': {'size': 56, 'color': gauge_color, 'family': 'Poppins'},
                    'valueformat': '.1f'
                },
                delta={'reference': 5, 'increasing': {'color': '#10b981'}, 'decreasing': {'color': '#ef4444'}},
                gauge={
                    'axis': {
                        'range': [0,10],
                        'tickwidth': 3,
                        'tickcolor': '#475569',
                        'tickfont': {'size': 14, 'color': '#cbd5e1', 'family': 'Inter'},
                        'tickmode': 'linear',
                        'tick0': 0,
                        'dtick': 2
                    },
                    'bar': {
                        'color': gauge_color,
                        'thickness': 0.85,
                        'line': {'color': 'rgba(255,255,255,.2)', 'width': 2}
                    },
                    'bgcolor': 'rgba(30,41,59,.6)',
                    'borderwidth': 4,
                    'bordercolor': 'rgba(102,126,234,.5)',
                    'steps': [
                        {'range': [0,3], 'color': 'rgba(239,68,68,.12)', 'line': {'color': 'rgba(239,68,68,.3)', 'width': 1}},
                        {'range': [3,5], 'color': 'rgba(245,158,11,.12)', 'line': {'color': 'rgba(245,158,11,.3)', 'width': 1}},
                        {'range': [5,7], 'color': 'rgba(59,130,246,.12)', 'line': {'color': 'rgba(59,130,246,.3)', 'width': 1}},
                        {'range': [7,10], 'color': 'rgba(16,185,129,.12)', 'line': {'color': 'rgba(16,185,129,.3)', 'width': 1}}
                    ],
                    'threshold': {
                        'line': {'color': '#f1f5f9', 'width': 4},
                        'thickness': 0.75,
                        'value': score_val
                    }
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#e2e8f0', 'family': 'Inter', 'size': 13},
                height=380,
                margin=dict(l=30,r=30,t=80,b=30),
                showlegend=False
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False})
        
        with v2:
            # Beautiful multi-layer radar chart
            cats = ['Semantic', 'Coverage', 'LLM Fit']
            vals = [analysis['semantic_score'], analysis['coverage_score'], analysis['llm_fit_score']]
            
            # Create gradient effect with multiple traces
            fig_radar = go.Figure()
            
            # Outer glow layer
            fig_radar.add_trace(go.Scatterpolar(
                r=[v * 1.05 for v in vals] + [vals[0] * 1.05],
                theta=cats + [cats[0]],
                fill='toself',
                fillcolor='rgba(102,126,234,.08)',
                line=dict(color='rgba(102,126,234,.3)', width=1),
                hoverinfo='skip',
                showlegend=False
            ))
            
            # Main profile
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=cats + [cats[0]],
                fill='toself',
                name='Match Profile',
                line=dict(
                    color='#667eea',
                    width=4,
                    shape='spline'
                ),
                fillcolor='rgba(102,126,234,.35)',
                marker=dict(
                    size=12,
                    color=['#10b981', '#3b82f6', '#f59e0b'],
                    line=dict(color='#fff', width=2),
                    symbol='circle'
                ),
                hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}/10<extra></extra>',
                hoverlabel=dict(
                    bgcolor='rgba(30,41,59,.95)',
                    font=dict(size=14, color='#f1f5f9', family='Inter'),
                    bordercolor='rgba(102,126,234,.8)'
                )
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0,10],
                        gridcolor='rgba(148,163,184,.25)',
                        gridwidth=2,
                        tickfont=dict(color='#cbd5e1', size=13, family='Inter'),
                        tickmode='linear',
                        tick0=0,
                        dtick=2,
                        showline=False
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(148,163,184,.25)',
                        gridwidth=2,
                        tickfont=dict(color='#f1f5f9', size=15, family='Poppins', weight=600),
                        rotation=90,
                        direction='clockwise'
                    ),
                    bgcolor='rgba(30,41,59,.3)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#e2e8f0', size=13),
                height=380,
                showlegend=False,
                margin=dict(l=50,r=50,t=50,b=30),
                title=dict(
                    text='<b>Assessment Profile</b>',
                    font=dict(size=22, color='#f1f5f9', family='Poppins'),
                    x=0.5,
                    xanchor='center'
                )
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False, 'staticPlot': False})
        
        # ===== Requirement Coverage =====
        st.markdown("""
        <div style="text-align:center;margin:40px 0 28px 0;">
            <h3 class="section-header" style="display:inline-block;padding:12px 32px;background:rgba(16,185,129,.1);
                       border-radius:16px;border:2px solid rgba(16,185,129,.3);">
                ✅ Requirement Coverage
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        must = analysis["atoms"]["must"][:10]
        nice = analysis["atoms"]["nice"][:6]
        resume_text = resume.get("text", "")
        tok = token_set(resume_text)
        
        # Enhanced coverage detection with LLM assistance
        # Step 1: Local model detection (primary)
        must_local = {req: contains_atom(req, tok) for req in must}
        nice_local = {req: contains_atom(req, tok) for req in nice}
        
        # Step 2: LLM verification for missed requirements (enhancement)
        must_missed = [req for req, covered in must_local.items() if not covered]
        nice_missed = [req for req, covered in nice_local.items() if not covered]
        
        llm_must_verify = {}
        llm_nice_verify = {}
        
        try:
            if must_missed and model:
                llm_must_verify = llm_verify_requirements(model, must_missed, resume_text, "must-have")
            if nice_missed and model:
                llm_nice_verify = llm_verify_requirements(model, nice_missed, resume_text, "nice-to-have")
        except:
            pass  # Silently fall back to local model only
        
        # Merge results: Local model takes precedence, LLM enhances
        must_final = {req: must_local[req] or llm_must_verify.get(req, False) for req in must}
        nice_final = {req: nice_local[req] or llm_nice_verify.get(req, False) for req in nice}
        
        # Calculate coverage stats
        must_covered = sum(1 for covered in must_final.values() if covered)
        must_missing = len(must) - must_covered
        nice_covered = sum(1 for covered in nice_final.values() if covered)
        nice_missing = len(nice) - nice_covered
        total_covered = must_covered + nice_covered
        total_req = len(must) + len(nice)
        coverage_pct = int(total_covered/total_req*100) if total_req > 0 else 0
        
        # Summary stats - Clean and aligned
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:32px;">
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(16,185,129,.12),rgba(5,150,105,.08));
                        border:2px solid rgba(16,185,129,.35);text-align:center;padding:20px;">
                <p style="margin:0;font-size:11px;color:#6ee7b7;text-transform:uppercase;letter-spacing:1.2px;font-weight:600;">Total</p>
                <h3 style="margin:8px 0 4px 0;font-size:36px;color:#10b981;font-weight:900;">{total_req}</h3>
                <p style="margin:0;font-size:12px;color:#94a3b8;"><span style="color:#10b981;font-weight:700;">{total_covered}</span> / {total_req - total_covered}</p>
            </div>
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(239,68,68,.12),rgba(220,38,38,.08));
                        border:2px solid rgba(239,68,68,.35);text-align:center;padding:20px;">
                <p style="margin:0;font-size:11px;color:#fca5a5;text-transform:uppercase;letter-spacing:1.2px;font-weight:600;">Must-Have</p>
                <h3 style="margin:8px 0 4px 0;font-size:36px;color:#ef4444;font-weight:900;">{len(must)}</h3>
                <p style="margin:0;font-size:12px;color:#94a3b8;"><span style="color:#10b981;font-weight:700;">{must_covered}</span> / <span style="color:#ef4444;font-weight:700;">{must_missing}</span></p>
            </div>
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(59,130,246,.12),rgba(37,99,235,.08));
                        border:2px solid rgba(59,130,246,.35);text-align:center;padding:20px;">
                <p style="margin:0;font-size:11px;color:#93c5fd;text-transform:uppercase;letter-spacing:1.2px;font-weight:600;">Nice-to-Have</p>
                <h3 style="margin:8px 0 4px 0;font-size:36px;color:#3b82f6;font-weight:900;">{len(nice) if len(nice) > 0 else '—'}</h3>
                <p style="margin:0;font-size:12px;color:#94a3b8;">{'<span style="color:#10b981;font-weight:700;">' + str(nice_covered) + '</span> / <span style="color:#3b82f6;font-weight:700;">' + str(nice_missing) + '</span>' if len(nice) > 0 else 'None'}</p>
            </div>
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(245,158,11,.12),rgba(217,119,6,.08));
                        border:2px solid rgba(245,158,11,.35);text-align:center;padding:20px;">
                <p style="margin:0;font-size:11px;color:#fcd34d;text-transform:uppercase;letter-spacing:1.2px;font-weight:600;">Coverage</p>
                <h3 style="margin:8px 0 4px 0;font-size:36px;color:#f59e0b;font-weight:900;">{coverage_pct}%</h3>
                <p style="margin:0;font-size:12px;color:#94a3b8;">{'Excellent' if coverage_pct >= 80 else 'Good' if coverage_pct >= 60 else 'Fair' if coverage_pct >= 40 else 'Low'}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Clean, well-structured requirements list
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(30,41,59,.85),rgba(15,23,42,.90));
                    border:2px solid rgba(102,126,234,.3);border-radius:16px;padding:28px;margin-bottom:32px;
                    box-shadow:0 10px 40px rgba(0,0,0,.3);">
        """, unsafe_allow_html=True)
        
        # Must-Have Requirements
        st.markdown(f"""
        <div style="margin-bottom:28px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;padding-bottom:12px;
                        border-bottom:2px solid rgba(239,68,68,.3);">
                <span style="font-size:24px;">🔴</span>
                <h3 style="margin:0;color:#fca5a5;font-size:18px;font-weight:800;
                           text-transform:uppercase;letter-spacing:1.2px;font-family:'Poppins',sans-serif;">
                    Must-Have Requirements
                </h3>
                <span style="background:rgba(239,68,68,.2);color:#fca5a5;padding:4px 12px;border-radius:12px;
                             font-size:12px;font-weight:700;">{len(must)}</span>
            </div>
        """, unsafe_allow_html=True)
        
        for idx, (req, is_covered) in enumerate(must_final.items(), 1):
            icon = "✓" if is_covered else "✗"
            icon_color = "#10b981" if is_covered else "#ef4444"
            bg_color = "rgba(16,185,129,.08)" if is_covered else "rgba(239,68,68,.08)"
            border_color = "#10b981" if is_covered else "#ef4444"
            
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:16px;padding:14px 18px;margin-bottom:10px;
                        background:{bg_color};border-left:3px solid {border_color};border-radius:8px;
                        transition:all .2s ease;">
                <span style="min-width:28px;height:28px;display:flex;align-items:center;justify-content:center;
                             background:{icon_color};color:#0f172a;font-weight:900;border-radius:50%;
                             font-size:16px;flex-shrink:0;">{icon}</span>
                <span style="flex:1;color:#f1f5f9;font-size:15px;font-weight:600;line-height:1.5;">{req}</span>
                <span style="color:{icon_color};font-size:11px;font-weight:700;text-transform:uppercase;
                             padding:6px 10px;background:rgba(0,0,0,.2);border-radius:6px;white-space:nowrap;">
                    {'Covered' if is_covered else 'Missing'}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Nice-to-Have Requirements
        if len(nice) > 0:
            st.markdown(f"""
            <div style="margin-bottom:16px;">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;padding-bottom:12px;
                            border-bottom:2px solid rgba(59,130,246,.3);">
                    <span style="font-size:24px;">⭐</span>
                    <h3 style="margin:0;color:#93c5fd;font-size:18px;font-weight:800;
                               text-transform:uppercase;letter-spacing:1.2px;font-family:'Poppins',sans-serif;">
                        Nice-to-Have
                    </h3>
                    <span style="background:rgba(59,130,246,.2);color:#93c5fd;padding:4px 12px;border-radius:12px;
                                 font-size:12px;font-weight:700;">{len(nice)}</span>
                </div>
            """, unsafe_allow_html=True)
            
            for idx, (req, is_covered) in enumerate(nice_final.items(), 1):
                icon = "✓" if is_covered else "○"
                icon_color = "#10b981" if is_covered else "#3b82f6"
                bg_color = "rgba(16,185,129,.08)" if is_covered else "rgba(59,130,246,.06)"
                border_color = "#10b981" if is_covered else "#3b82f6"
                
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:16px;padding:14px 18px;margin-bottom:10px;
                            background:{bg_color};border-left:3px solid {border_color};border-radius:8px;
                            transition:all .2s ease;">
                    <span style="min-width:28px;height:28px;display:flex;align-items:center;justify-content:center;
                                 background:{icon_color};color:#0f172a;font-weight:900;border-radius:50%;
                                 font-size:16px;flex-shrink:0;">{icon}</span>
                    <span style="flex:1;color:#cbd5e1;font-size:15px;font-weight:600;line-height:1.5;">{req}</span>
                    <span style="color:{icon_color};font-size:11px;font-weight:700;text-transform:uppercase;
                                 padding:6px 10px;background:rgba(0,0,0,.2);border-radius:6px;white-space:nowrap;">
                        {'Covered' if is_covered else 'Not Found'}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="padding:24px;background:rgba(59,130,246,.06);border:2px dashed rgba(59,130,246,.25);
                        border-radius:8px;text-align:center;">
                <p style="margin:0;color:#7a8b99;font-size:14px;font-style:italic;">
                    No nice-to-have requirements specified for this position
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ===== Beautiful Candidate Assessment =====
        st.markdown("""
        <div style="text-align:center;margin:48px 0 32px 0;">
            <h3 class="section-header" style="display:inline-block;padding:16px 40px;background:rgba(139,92,246,.15);
                       border-radius:20px;border:3px solid rgba(139,92,246,.4);box-shadow:0 8px 24px rgba(139,92,246,.3);">
                🎯 CANDIDATE ASSESSMENT
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        llm = analysis['llm_analysis']
        
        # Top Strengths Section - Full Width, Prominent
        strengths = llm.get('top_strengths', [])[:4]
        if strengths:
            st.markdown("""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(16,185,129,.12),rgba(5,150,105,.12));
                        border:2px solid rgba(16,185,129,.4);border-radius:24px;padding:32px;
                        box-shadow:0 12px 40px rgba(16,185,129,.25);margin-bottom:24px;">
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
                    <div style="width:56px;height:56px;background:linear-gradient(135deg,#10b981,#059669);
                                border-radius:16px;display:flex;align-items:center;justify-content:center;
                                font-size:28px;box-shadow:0 8px 20px rgba(16,185,129,.4);">
                        💪
                    </div>
                    <h3 style="margin:0;color:#6ee7b7;font-size:24px;font-weight:800;font-family:'Poppins',sans-serif;
                               text-transform:uppercase;letter-spacing:1px;">
                        Top Strengths
                    </h3>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin-top:20px;">
            """, unsafe_allow_html=True)
            
            for idx, s in enumerate(strengths, 1):
                st.markdown(f"""
                <div style="background:rgba(15,23,42,.7);padding:20px;border-radius:16px;
                            border-left:4px solid #10b981;backdrop-filter:blur(10px);
                            transition:all .3s ease;position:relative;">
                    <div style="position:absolute;top:12px;right:12px;width:32px;height:32px;
                                background:rgba(16,185,129,.2);border-radius:50%;display:flex;
                                align-items:center;justify-content:center;font-size:14px;font-weight:700;
                                color:#6ee7b7;border:2px solid rgba(16,185,129,.5);">
                        {idx}
                    </div>
                    <p style="margin:0;color:#e2e8f0;font-size:15px;line-height:1.7;padding-right:40px;">
                        ✓ {s}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Grid Layout for Cultural & Technical Fit
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            cultural_fit = str(llm.get('cultural_fit', 'N/A'))
            st.markdown(f"""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(102,126,234,.12),rgba(88,80,236,.12));
                        border:2px solid rgba(102,126,234,.4);border-radius:24px;padding:32px;
                        box-shadow:0 12px 40px rgba(102,126,234,.25);height:100%;">
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
                    <div style="width:56px;height:56px;background:linear-gradient(135deg,#667eea,#764ba2);
                                border-radius:16px;display:flex;align-items:center;justify-content:center;
                                font-size:28px;box-shadow:0 8px 20px rgba(102,126,234,.4);">
                        🤝
                    </div>
                    <h3 style="margin:0;color:#93bbfd;font-size:22px;font-weight:800;font-family:'Poppins',sans-serif;
                               text-transform:uppercase;letter-spacing:1px;">
                        Cultural Fit
                    </h3>
                </div>
                <div style="background:rgba(15,23,42,.6);padding:24px;border-radius:16px;
                            border-left:4px solid #667eea;backdrop-filter:blur(10px);">
                    <p style="margin:0;color:#cbd5e1;font-size:15px;line-height:1.8;">
                        {cultural_fit}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            technical_strength = str(llm.get('technical_strength', 'N/A'))
            st.markdown(f"""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(139,92,246,.12),rgba(168,85,247,.12));
                        border:2px solid rgba(139,92,246,.4);border-radius:24px;padding:32px;
                        box-shadow:0 12px 40px rgba(139,92,246,.25);height:100%;">
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
                    <div style="width:56px;height:56px;background:linear-gradient(135deg,#a855f7,#9333ea);
                                border-radius:16px;display:flex;align-items:center;justify-content:center;
                                font-size:28px;box-shadow:0 8px 20px rgba(139,92,246,.4);">
                        ⚙️
                    </div>
                    <h3 style="margin:0;color:#d8b4fe;font-size:22px;font-weight:800;font-family:'Poppins',sans-serif;
                               text-transform:uppercase;letter-spacing:1px;">
                        Technical Fit
                    </h3>
                </div>
                <div style="background:rgba(15,23,42,.6);padding:24px;border-radius:16px;
                            border-left:4px solid #a855f7;backdrop-filter:blur(10px);">
                    <p style="margin:0;color:#cbd5e1;font-size:15px;line-height:1.8;">
                        {technical_strength}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Development Areas Section
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        dev_areas = llm.get('improvement_areas', [])[:3]
        if dev_areas:
            st.markdown("""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(245,158,11,.12),rgba(217,119,6,.12));
                        border:2px solid rgba(245,158,11,.4);border-radius:24px;padding:32px;
                        box-shadow:0 12px 40px rgba(245,158,11,.25);">
                <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;">
                    <div style="width:56px;height:56px;background:linear-gradient(135deg,#f59e0b,#d97706);
                                border-radius:16px;display:flex;align-items:center;justify-content:center;
                                font-size:28px;box-shadow:0 8px 20px rgba(245,158,11,.4);">
                        📈
                    </div>
                    <h3 style="margin:0;color:#fcd34d;font-size:24px;font-weight:800;font-family:'Poppins',sans-serif;
                               text-transform:uppercase;letter-spacing:1px;">
                        Development Areas
                    </h3>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:20px;">
            """, unsafe_allow_html=True)
            
            for idx, area in enumerate(dev_areas, 1):
                st.markdown(f"""
                <div style="background:rgba(15,23,42,.7);padding:20px;border-radius:16px;
                            border-left:4px solid #f59e0b;backdrop-filter:blur(10px);
                            display:flex;align-items:start;gap:12px;">
                    <span style="flex-shrink:0;width:28px;height:28px;background:rgba(245,158,11,.2);
                                border-radius:50%;display:flex;align-items:center;justify-content:center;
                                font-size:14px;font-weight:700;color:#fcd34d;border:2px solid rgba(245,158,11,.5);">
                        {idx}
                    </span>
                    <p style="margin:0;color:#e2e8f0;font-size:15px;line-height:1.7;">
                        {area}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # ===== Final Recommendation =====
        st.markdown("""
        <div class="metric-card" style="margin-top:20px;background:linear-gradient(135deg,rgba(102,126,234,.15),rgba(118,75,162,.15));border:2px solid rgba(102,126,234,.3);border-radius:12px;">
            <h3 style="margin:0;color:#667eea;font-size:18px;text-transform:uppercase;">📋 Final Recommendation</h3>
            <p style="margin:14px 0 0 0;font-size:14px;line-height:1.8;color:#cbd5e1;">
        """ + str(llm.get('overall_comment', 'Pending analysis'))[:500] + """
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ===== Download Results =====
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        payload = json.dumps(analysis, ensure_ascii=False, indent=2)
        st.download_button(
            "📥 Download Full Analysis (JSON)",
            data=payload.encode('utf-8'),
            file_name=f"analysis_{resume['name'].replace(' ','_')}_{int(time.time())}.json",
            use_container_width=True,
            help="Download the complete analysis with all metrics and details"
        )

# --- Recent tab ---
with tab2:
    section("Recent Uploads", "📥")
    if not st.session_state.uploads_history:
        st.info("No uploads yet.")
    else:
        for u in st.session_state.uploads_history[:12]:
            t = datetime.fromtimestamp(u["timestamp"]).strftime('%b %d, %Y • %I:%M %p')
            st.markdown(f"""
            <div class="metric-card">
                <p><strong>File:</strong> {u['file_name']}</p>
                <p><strong>Name:</strong> {u['name']}</p>
                <p><strong>Contact:</strong> <span class="chip">{u['email']}</span> <span class="chip">{u['phone']}</span></p>
                <p class="small">{t}</p>
            </div>
            """, unsafe_allow_html=True)

    section("Recent Analyses", "🧾")
    recent_db = get_recent(analyses_collection, mongo_ok, limit=15)
    merged = []
    for x in recent_db:
        merged.append({"candidate":x.get("analysis",{}).get("resume_meta",{}).get("name","Unknown") or x.get("candidate","Unknown"),
                       "score":x.get("analysis",{}).get("score","-"),
                       "email":x.get("analysis",{}).get("resume_meta",{}).get("email",""),
                       "file":x.get("analysis",{}).get("resume_meta",{}).get("file_name",""),
                       "ts":x.get("timestamp",0)})
    if not merged and not st.session_state.analysis_history:
        st.info("No analyses yet.")
    else:
        for i,entry in enumerate((st.session_state.analysis_history[:10] if st.session_state.analysis_history else [])):
            t = datetime.fromtimestamp(entry["timestamp"]).strftime('%b %d, %Y • %I:%M %p')
            with st.expander(f"{entry['resume_meta']['name']} • Score: {entry['score']:.1f} • {t}", expanded=(i==0)):
                c1,c2 = st.columns([1,2])
                with c1:
                    sc = entry['score']
                    cls = 'score-excellent' if sc>=8 else 'score-good' if sc>=6 else 'score-fair' if sc>=4 else 'score-poor'
                    st.markdown(f"""<div style="text-align:center;"><div class="score-badge {cls}" style="font-size:34px;">{sc}</div></div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <p><strong>Email:</strong> {entry['resume_meta']['email']}</p>
                        <p><strong>Semantic:</strong> {entry['semantic_score']:.1f}/10</p>
                        <p><strong>Coverage:</strong> {entry['coverage_score']:.1f}/10</p>
                        <p><strong>LLM Fit:</strong> {entry['llm_fit_score']:.1f}/10</p>
                    </div>
                    """, unsafe_allow_html=True)
        if merged:
            st.markdown("<hr>", unsafe_allow_html=True)
            for x in merged:
                t = datetime.fromtimestamp(x["ts"]).strftime('%b %d, %Y • %I:%M %p') if x["ts"] else ""
                st.markdown(f"""
                <div class="metric-card">
                    <p><strong>Candidate:</strong> {x['candidate']} • <strong>Score:</strong> {x['score']}</p>
                    <p><strong>Email:</strong> {x['email']} • <strong>File:</strong> {x['file']}</p>
                    <p class="small">{t}</p>
                </div>
                """, unsafe_allow_html=True)
