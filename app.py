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
st.set_page_config(layout="wide", page_title="Resume Screener Pro", page_icon="🎯", initial_sidebar_state="collapsed")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
html,body,[class*="css"],.main,.stApp{background:#0a0e27!important}
.stApp{background:linear-gradient(135deg,#0a0e27 0%,#16213e 50%,#0a0e27 100%)!important}
h1,h2,h3,h4,h5,h6{color:#e2e8f0!important;font-weight:700!important;letter-spacing:-.02em!important}
p,span,div{color:#94a3b8!important}
.stTabs [data-baseweb="tab-list"]{gap:16px;background:transparent;border-bottom:2px solid rgba(148,163,184,.1)}
.stTabs [data-baseweb="tab"]{height:60px;padding:0 32px;background:rgba(22,33,62,.6);border:1px solid rgba(148,163,184,.15);border-radius:12px 12px 0 0;color:#94a3b8;font-weight:600;font-size:16px;transition:all .3s cubic-bezier(.4,0,.2,1);backdrop-filter:blur(10px)}
.stTabs [data-baseweb="tab"]:hover{background:rgba(102,126,234,.15);border-color:rgba(102,126,234,.3);transform:translateY(-2px)}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)!important;color:#fff!important;border-color:transparent!important;box-shadow:0 10px 40px rgba(102,126,234,.4),0 0 20px rgba(118,75,162,.3)}
.stButton>button{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;border-radius:12px;padding:16px 48px;font-weight:700;font-size:18px;letter-spacing:.5px;text-transform:uppercase;transition:all .3s cubic-bezier(.4,0,.2,1);box-shadow:0 10px 30px rgba(102,126,234,.4)}
.stButton>button:hover{transform:translateY(-3px);box-shadow:0 15px 50px rgba(102,126,234,.6),0 0 30px rgba(118,75,162,.4)}
.stFileUploader{background:rgba(22,33,62,.5);border:2px dashed rgba(102,126,234,.3);border-radius:12px;padding:24px;transition:all .3s ease}
.stFileUploader:hover{background:rgba(22,33,62,.7);border-color:rgba(102,126,234,.6)}
.stTextArea textarea{background:rgba(22,33,62,.8)!important;border:1px solid rgba(148,163,184,.2)!important;border-radius:12px!important;color:#e2e8f0!important;font-size:15px!important;padding:16px!important}
.stTextArea textarea:focus{border-color:rgba(102,126,234,.6)!important;box-shadow:0 0 0 2px rgba(102,126,234,.1)!important}
.metric-card{background:linear-gradient(135deg,rgba(22,33,62,.8) 0%,rgba(22,33,62,.6) 100%);border:1px solid rgba(148,163,184,.2);border-radius:16px;padding:24px;transition:all .3s ease;backdrop-filter:blur(10px)}
.metric-card:hover{border-color:rgba(102,126,234,.4);transform:translateY(-2px);box-shadow:0 10px 30px rgba(102,126,234,.15)}
.analysis-card{background:linear-gradient(135deg,rgba(22,33,62,.8) 0%,rgba(16,21,46,.6) 100%);border:1px solid rgba(148,163,184,.2);border-radius:16px;padding:24px;transition:all .3s ease;backdrop-filter:blur(10px)}
.analysis-card:hover{border-color:rgba(102,126,234,.4);box-shadow:0 10px 30px rgba(102,126,234,.1)}
.score-badge{display:inline-block;padding:16px 32px;border-radius:24px;font-weight:900;font-size:40px;box-shadow:0 10px 30px rgba(0,0,0,.3);transition:all .3s ease}
.score-excellent{background:linear-gradient(135deg,#10b981 0%,#059669 100%);color:#fff;box-shadow:0 10px 30px rgba(16,185,129,.4)}
.score-good{background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%);color:#fff;box-shadow:0 10px 30px rgba(59,130,246,.4)}
.score-fair{background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);color:#fff;box-shadow:0 10px 30px rgba(245,158,11,.4)}
.score-poor{background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%);color:#fff;box-shadow:0 10px 30px rgba(239,68,68,.4)}
.chip{display:inline-block;margin:4px 6px 0 0;padding:6px 12px;border-radius:20px;background:rgba(102,126,234,.15);border:1px solid rgba(102,126,234,.3);font-size:12px;color:#cbd5e1;transition:all .3s ease}
.chip:hover{background:rgba(102,126,234,.25);border-color:rgba(102,126,234,.6)}
hr{border:none;height:2px;background:linear-gradient(90deg,transparent,rgba(148,163,184,.3),transparent);margin:24px 0}
.small{font-size:12px;color:#9aa5b1}
.stExpander{background:rgba(22,33,62,.6)!important;border:1px solid rgba(148,163,184,.2)!important;border-radius:12px!important}
.stExpander [data-testid="stExpanderToggleButton"]{color:#e2e8f0!important}
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
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key: return None, None, None, False
    genai.configure(api_key=api_key)

    preferred = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
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

    # spaCy
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = spacy.blank("en")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")

    # Stronger default embedder
    s_name = os.getenv("SENTENCE_MODEL_NAME", "all-mpnet-base-v2")
    embedder = SentenceTransformer(s_name, device='cpu')

    return model, nlp, embedder, True

@st.cache_resource(show_spinner=False)
def init_mongodb():
    uri = os.getenv("MONGO_URI", "").strip()
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
    a = normalize_text(atom)
    if len(a) < 2: return False
    # exact substring check (normalized)
    if a in " ".join(sorted(list(text_tokens))):  # cheap containment space-joined
        return True
    # all tokens present?
    a_tok = set(re.findall(r'[a-z0-9][a-z0-9+.#-]*', a))
    if not a_tok: return False
    return a_tok.issubset(text_tokens)

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
    if hasattr(doc, "noun_chunks"):
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
st.markdown("""
<div style="text-align:center;padding:36px 0 16px 0;">
<h1 style="font-size:52px;margin:0;background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-weight:900;letter-spacing:-2px;">🎯 Resume Screener Pro</h1>
<p style="font-size:18px;color:#94a3b8;margin-top:10px;">Evidence-free, RAG-lite scoring • Dynamic atomic requirements • No lexicons</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Settings")
    dbg = st.toggle("Show debug details", value=False)
    st.caption("Tip: Turn on for atoms/coverage internals.")

with st.spinner('Initializing models...'):
    model, nlp, embedder, models_ok = load_models()
    resumes_collection, analyses_collection, mongo_ok = init_mongodb()

if not models_ok:
    st.error("Gemini model unavailable. Set GEMINI_API_KEY and a valid GEMINI_MODEL_NAME.")
    st.stop()

if st.session_state.get("gemini_model_name"):
    st.caption(f"Using Gemini: {st.session_state['gemini_model_name']} • Embedder: {os.getenv('SENTENCE_MODEL_NAME','all-mpnet-base-v2')}")

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

        # ===== Clean Header: Name + Score Badge =====
        c_name, c_fill, c_score = st.columns([2, 1, 1], gap="medium")
        with c_name:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="margin:0;color:#e2e8f0;font-size:32px;font-weight:800;">{resume['name']}</h2>
                <p style="margin:8px 0 0 0;color:#94a3b8;font-size:14px;">
                    📧 {resume['email']}<br>📱 {resume['phone']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        with c_fill:
            pass  # spacer
        with c_score:
            sc = analysis['score']
            cls = 'score-excellent' if sc>=8 else 'score-good' if sc>=6 else 'score-fair' if sc>=4 else 'score-poor'
            lab = '🌟 Excellent' if sc>=8 else '👍 Good' if sc>=6 else '⚠️ Fair' if sc>=4 else '❌ Poor'
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;border:3px solid #667eea;">
                <div class="score-badge {cls}" style="font-size:48px;margin:8px 0;">{sc}</div>
                <p style="margin:4px 0 0 0;font-size:13px;font-weight:700;color:#e2e8f0;text-transform:uppercase;">{lab}</p>
                <p style="margin:8px 0 0 0;font-size:12px;color:#7a8b99;">Overall Match</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        
        # ===== Key Metrics Dashboard =====
        section("Match Metrics", "📊")
        m1, m2, m3 = st.columns(3, gap="medium")
        
        metrics_style = """
        <div class="metric-card" style="text-align:center;border-left:4px solid #667eea;">
            <p style="margin:0;font-size:12px;color:#7a8b99;text-transform:uppercase;letter-spacing:0.5px;">%s</p>
            <h3 style="margin:8px 0 0 0;font-size:36px;color:#10b981;">%.1f</h3>
            <p style="margin:4px 0 0 0;font-size:12px;color:#94a3b8;">out of 10</p>
        </div>
        """
        
        with m1:
            st.markdown(metrics_style % ("Semantic Match", analysis['semantic_score']), unsafe_allow_html=True)
        with m2:
            st.markdown(metrics_style % ("Coverage", analysis['coverage_score']), unsafe_allow_html=True)
        with m3:
            st.markdown(metrics_style % ("LLM Fit Assessment", analysis['llm_fit_score']), unsafe_allow_html=True)
        
        # ===== Beautiful Visualizations =====
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        section("Detailed Assessment", "📈")
        
        v1, v2 = st.columns(2, gap="large")
        
        with v1:
            # Enhanced gauge with gradient
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=analysis['score'],
                domain={'x': [0,1], 'y': [0,1]},
                title={'text': "Overall Fit Score", 'font': {'size': 20, 'color': '#e2e8f0', 'family': 'Inter'}},
                number={'suffix': "/10", 'font': {'size': 40, 'color': '#10b981', 'family': 'Inter'}},
                gauge={
                    'axis': {'range': [0,10], 'tickwidth': 2, 'tickcolor': '#475569', 'tickfont': {'size': 12, 'color': '#94a3b8'}},
                    'bar': {'color': '#667eea', 'thickness': 0.8},
                    'bgcolor': 'rgba(22,33,62,.3)',
                    'borderwidth': 3,
                    'bordercolor': '#667eea',
                    'steps': [
                        {'range': [0,3], 'color': 'rgba(239,68,68,.15)'},
                        {'range': [3,6], 'color': 'rgba(245,158,11,.15)'},
                        {'range': [6,9], 'color': 'rgba(59,130,246,.15)'},
                        {'range': [9,10], 'color': 'rgba(16,185,129,.15)'}
                    ]
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#e2e8f0', 'family': 'Inter'},
                height=360,
                margin=dict(l=20,r=20,t=60,b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
        
        with v2:
            # Enhanced radar chart
            cats = ['Semantic', 'Coverage', 'LLM Fit']
            vals = [analysis['semantic_score'], analysis['coverage_score'], analysis['llm_fit_score']]
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=vals + [vals[0]],
                theta=cats + [cats[0]],
                fill='toself',
                name='Match Profile',
                line=dict(color='#667eea', width=3),
                fillcolor='rgba(102,126,234,.25)',
                hoverinfo='r+theta'
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0,10],
                        gridcolor='rgba(148,163,184,.2)',
                        tickfont=dict(color='#94a3b8', size=12),
                        ticksuffix=''
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(148,163,184,.2)',
                        tickfont=dict(color='#e2e8f0', size=14),
                        rotation=90
                    ),
                    bgcolor='rgba(22,33,62,.2)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#e2e8f0', size=13),
                height=360,
                showlegend=False,
                margin=dict(l=40,r=40,t=40,b=20)
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        
        # ===== Requirement Coverage =====
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        section("Requirement Coverage", "✅")
        
        must = analysis["atoms"]["must"][:8]
        nice = analysis["atoms"]["nice"][:5]
        resume_text = resume.get("text", "")
        tok = token_set(resume_text)
        
        cov_list = []
        for a in must:
            cov_list.append({"Requirement": a[:40], "Status": "✓" if contains_atom(a, tok) else "✗", "Type": "Must-Have"})
        for a in nice:
            cov_list.append({"Requirement": a[:40], "Status": "✓" if contains_atom(a, tok) else "✗", "Type": "Nice-to-Have"})
        
        if cov_list:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            for item in cov_list[:12]:
                status_color = "#10b981" if item["Status"] == "✓" else "#ef4444"
                status_label = "Covered" if item["Status"] == "✓" else "Missing"
                type_badge = "🔴" if item["Type"] == "Must-Have" else "⭐"
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:10px;border-bottom:1px solid rgba(148,163,184,.1);">
                    <span style="font-size:16px;">{type_badge}</span>
                    <span style="flex:1;color:#e2e8f0;">{item['Requirement']}</span>
                    <span style="color:{status_color};font-weight:700;font-size:14px;">{status_label}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # ===== Assessment Cards =====
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        section("Candidate Assessment", "🎯")
        
        llm = analysis['llm_analysis']
        
        # Two-column layout for strengths & gaps
        left, right = st.columns(2, gap="large")
        
        with left:
            st.markdown("""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(16,185,129,.08),rgba(5,150,105,.08));border-left:4px solid #10b981;">
                <h4 style="margin:0;color:#10b981;font-size:16px;text-transform:uppercase;">💪 Top Strengths</h4>
                <div style="margin-top:12px;font-size:13px;color:#cbd5e1;line-height:1.7;">
            """, unsafe_allow_html=True)
            for s in llm.get('top_strengths', [])[:4]:
                st.markdown(f"✓ {s}")
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card" style="margin-top:12px;background:linear-gradient(135deg,rgba(245,158,11,.08),rgba(217,119,6,.08));border-left:4px solid #f59e0b;">
                <h4 style="margin:0;color:#f59e0b;font-size:16px;text-transform:uppercase;">📈 Development Areas</h4>
                <div style="margin-top:12px;font-size:13px;color:#cbd5e1;line-height:1.7;">
            """, unsafe_allow_html=True)
            for a in llm.get('improvement_areas', [])[:3]:
                st.markdown(f"• {a}")
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        with right:
            st.markdown("""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(102,126,234,.08),rgba(88,80,236,.08));border-left:4px solid #667eea;">
                <h4 style="margin:0;color:#667eea;font-size:16px;text-transform:uppercase;">🤝 Cultural Fit</h4>
                <p style="margin:12px 0 0 0;font-size:13px;color:#cbd5e1;line-height:1.6;">
            """ + str(llm.get('cultural_fit', 'N/A'))[:300] + """
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card" style="margin-top:12px;background:linear-gradient(135deg,rgba(139,92,246,.08),rgba(168,85,247,.08));border-left:4px solid #a855f7;">
                <h4 style="margin:0;color:#a855f7;font-size:16px;text-transform:uppercase;">⚙️ Technical Fit</h4>
                <p style="margin:12px 0 0 0;font-size:13px;color:#cbd5e1;line-height:1.6;">
            """ + str(llm.get('technical_strength', 'N/A'))[:300] + """
                </p>
            </div>
            """, unsafe_allow_html=True)
        
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
