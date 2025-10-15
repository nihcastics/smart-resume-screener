# Fix torch warnings before any imports
import os, sys
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import warnings, logging, io
stderr_backup = sys.stderr
sys.stderr = io.StringIO()
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)

import streamlit as st
import fitz
import spacy
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
import json, time, re, tempfile, uuid
from datetime import datetime
from collections import Counter, defaultdict
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import plotly.graph_objects as go
import plotly.express as px

sys.stderr = stderr_backup
load_dotenv()

st.set_page_config(layout="wide", page_title="Resume Screener Pro", page_icon="🎯", initial_sidebar_state="collapsed")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
html,body,[class*="css"],.main,.stApp{background:#0a0e27!important}
.stApp{background:linear-gradient(135deg,#0a0e27 0%,#16213e 50%,#0a0e27 100%)!important}
@keyframes slideInDown{from{opacity:0;transform:translateY(-30px)}to{opacity:1;transform:translateY(0)}}
@keyframes slideInUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes glow{0%,100%{box-shadow:0 0 20px rgba(102,126,234,.3)}50%{box-shadow:0 0 30px rgba(102,126,234,.6),0 0 40px rgba(118,75,162,.4)}}
h1,h2,h3,h4,h5,h6{color:#e2e8f0!important;font-weight:700!important;letter-spacing:-.02em!important}
p,span,div{color:#94a3b8!important}
.stTabs [data-baseweb="tab-list"]{gap:16px;background:transparent;border-bottom:2px solid rgba(148,163,184,.1)}
.stTabs [data-baseweb="tab"]{height:60px;padding:0 32px;background:rgba(22,33,62,.6);border:1px solid rgba(148,163,184,.15);border-radius:12px 12px 0 0;color:#94a3b8;font-weight:600;font-size:16px;transition:all .3s cubic-bezier(.4,0,.2,1);backdrop-filter:blur(10px)}
.stTabs [data-baseweb="tab"]:hover{background:rgba(102,126,234,.15);border-color:rgba(102,126,234,.3);transform:translateY(-2px)}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%)!important;color:#fff!important;border-color:transparent!important;box-shadow:0 10px 40px rgba(102,126,234,.4),0 0 20px rgba(118,75,162,.3)}
.stButton>button{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;border:none;border-radius:12px;padding:16px 48px;font-weight:700;font-size:18px;letter-spacing:.5px;text-transform:uppercase;transition:all .3s cubic-bezier(.4,0,.2,1);box-shadow:0 10px 30px rgba(102,126,234,.4);animation:glow 3s infinite}
.stButton>button:hover{transform:translateY(-3px);box-shadow:0 15px 50px rgba(102,126,234,.6),0 0 30px rgba(118,75,162,.4)}
.stButton>button:active{transform:translateY(0)}
.stFileUploader{background:rgba(22,33,62,.5);border:2px dashed rgba(102,126,234,.3);border-radius:12px;padding:24px;transition:all .3s ease}
.stFileUploader:hover{border-color:rgba(102,126,234,.6);background:rgba(22,33,62,.7)}
.stTextArea textarea{background:rgba(22,33,62,.8)!important;border:1px solid rgba(148,163,184,.2)!important;border-radius:12px!important;color:#e2e8f0!important;font-size:15px!important;padding:16px!important;transition:all .3s ease!important}
.stTextArea textarea:focus{border-color:rgba(102,126,234,.5)!important;box-shadow:0 0 20px rgba(102,126,234,.2)!important}
.metric-card{background:linear-gradient(135deg,rgba(22,33,62,.8) 0%,rgba(22,33,62,.6) 100%);border:1px solid rgba(148,163,184,.2);border-radius:16px;padding:28px;transition:all .4s cubic-bezier(.4,0,.2,1);animation:slideInUp .6s ease;backdrop-filter:blur(20px)}
.metric-card:hover{border-color:rgba(102,126,234,.4);box-shadow:0 20px 60px rgba(102,126,234,.2);transform:translateY(-8px)}
.analysis-card{background:linear-gradient(135deg,rgba(22,33,62,.8) 0%,rgba(16,21,46,.6) 100%);border:1px solid rgba(148,163,184,.2);border-radius:16px;padding:32px;transition:all .4s cubic-bezier(.4,0,.2,1);backdrop-filter:blur(20px);animation:fadeIn .8s ease}
.analysis-card:hover{border-color:rgba(102,126,234,.5);box-shadow:0 30px 80px rgba(102,126,234,.3)}
.score-badge{display:inline-block;padding:20px 40px;border-radius:24px;font-weight:900;font-size:42px;text-align:center;letter-spacing:-1px;transition:all .3s ease;animation:glow 3s infinite}
.score-excellent{background:linear-gradient(135deg,#10b981 0%,#059669 100%);color:#fff;box-shadow:0 10px 40px rgba(16,185,129,.5)}
.score-good{background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%);color:#fff;box-shadow:0 10px 40px rgba(59,130,246,.5)}
.score-fair{background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);color:#fff;box-shadow:0 10px 40px rgba(245,158,11,.5)}
.score-poor{background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%);color:#fff;box-shadow:0 10px 40px rgba(239,68,68,.5)}
.skill-badge{display:inline-block;background:linear-gradient(135deg,rgba(102,126,234,.2),rgba(118,75,162,.2));border:2px solid rgba(102,126,234,.5);color:#818cf8;padding:10px 20px;border-radius:24px;margin:6px 4px;font-weight:600;font-size:14px;transition:all .3s ease;backdrop-filter:blur(10px)}
.skill-badge:hover{background:linear-gradient(135deg,rgba(102,126,234,.4),rgba(118,75,162,.4));border-color:#667eea;transform:translateY(-2px);box-shadow:0 8px 20px rgba(102,126,234,.3)}
.info-box{background:rgba(59,130,246,.12);border-left:4px solid #3b82f6;padding:20px;border-radius:12px;margin:16px 0;backdrop-filter:blur(10px)}
.success-box{background:rgba(16,185,129,.12);border-left:4px solid #10b981;padding:20px;border-radius:12px;margin:16px 0;backdrop-filter:blur(10px)}
.warning-box{background:rgba(245,158,11,.12);border-left:4px solid #f59e0b;padding:20px;border-radius:12px;margin:16px 0;backdrop-filter:blur(10px)}
.stProgress>div>div>div{background:linear-gradient(90deg,#667eea,#764ba2,#f093fb);border-radius:10px}
.streamlit-expanderHeader{background:rgba(22,33,62,.7)!important;border:1px solid rgba(148,163,184,.2)!important;border-radius:12px!important;padding:16px!important;transition:all .3s ease!important;backdrop-filter:blur(10px)!important}
.streamlit-expanderHeader:hover{background:rgba(102,126,234,.15)!important;border-color:rgba(102,126,234,.4)!important}
hr{border:none;height:2px;background:linear-gradient(90deg,transparent,rgba(148,163,184,.3),transparent);margin:32px 0}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:rgba(22,33,62,.5)}
::-webkit-scrollbar-thumb{background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px}
::-webkit-scrollbar-thumb:hover{background:linear-gradient(135deg,#764ba2,#667eea)}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

if 'models_loaded' not in st.session_state: st.session_state.models_loaded = False
if 'analysis_history' not in st.session_state: st.session_state.analysis_history = []
if 'uploads_history' not in st.session_state: st.session_state.uploads_history = []
if 'current_analysis' not in st.session_state: st.session_state.current_analysis = None

@st.cache_resource(show_spinner=False)
def load_models():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key: return None, None, None, False
    genai.configure(api_key=api_key)

    preferred = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
    fallbacks = [
        preferred,
        "gemini-2.5-pro",
        "gemini-2.5-pro-preview-06-05",
        "gemini-2.5-flash-preview-09-2025",
        "gemini-2.5-flash-lite",
        "gemini-2.0-pro-exp",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-002",
        "gemini-1.5-flash",
        "gemini-1.0-pro"
    ]
    try:
        available = {m.name.split('/')[-1] for m in genai.list_models() if getattr(m, "supported_generation_methods", []) and "generateContent" in m.supported_generation_methods}
    except Exception:
        available = set()

    model = None
    chosen_name = None
    for cand in fallbacks:
        if not cand: continue
        simple = cand.replace("models/", "")
        if available and simple not in available: # skip models we know are unavailable
            continue
        try:
            model = genai.GenerativeModel(simple)
            # light-touch health check so we fail fast on unsupported models
            model.count_tokens("health check")
            chosen_name = simple
            break
        except Exception:
            continue

    if not model:
        return None, None, None, False

    st.session_state["gemini_model_name"] = chosen_name

    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = spacy.blank("en")
        if "sentencizer" not in nlp.pipe_names: nlp.add_pipe("sentencizer")
    s_name = os.getenv("SENTENCE_MODEL_NAME", "all-MiniLM-L6-v2")
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
    except:
        return None, None, False

def norm_vecs(a):
    a = np.asarray(a, dtype=np.float32)
    n = np.linalg.norm(a, axis=1, keepdims=True) + 1e-12
    return a / n

def chunk_text(t, max_chars=1200, overlap=150):
    t = re.sub(r'\n{3,}', '\n\n', t)
    paras = [p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if len(buf)+len(p)+2 <= max_chars: buf = (buf+"\n\n"+p).strip()
        else:
            if buf: chunks.append(buf)
            if len(p) <= max_chars: buf = p
            else:
                s = 0
                step = max(max_chars - overlap, 1)
                while s < len(p):
                    e = min(s + max_chars, len(p))
                    piece = p[s:e]
                    chunks.append(piece.strip())
                    if e >= len(p):
                        break
                    s += step
                buf = ""
    if buf: chunks.append(buf)
    return chunks

def parse_contacts(txt):
    emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', txt)
    phones = re.findall(r'(\+?\d[\d\s().-]{8,}\d)', txt)
    return (emails[0] if emails else "Not found"), (phones[0] if phones else "Not found")

def extract_keyphrases(txt, nlp, top_n=30):
    words = re.findall(r'\b[a-z]{3,}\b', txt.lower())
    stop = set(['the','and','for','with','from','that','this','have','has','had','was','were','been','will','would','could','should','about','into','over','than','then','when','what','which','your','their','them','they','are','you','our','out','via','able','more','less'])
    freq = Counter([w for w in words if w not in stop])
    cands = [w for w,_ in freq.most_common(200)]
    doc = nlp(txt)
    noun_chunks = []
    if hasattr(doc, "noun_chunks"):
        for nc in doc.noun_chunks:
            s = re.sub(r'\s+',' ',nc.text.strip())
            if 3<=len(s)<=50: noun_chunks.append(s.lower())
    phrase_freq = Counter(noun_chunks)
    merged = {**dict(freq.most_common(top_n)), **dict(phrase_freq.most_common(top_n))}
    out = [k for k,_ in Counter(merged).most_common(top_n)]
    return out

def llm_json(model, prompt):
    resp = model.generate_content(prompt)
    text = resp.text or ""
    m = re.search(r"\{.*\}", text, re.S)
    s = m.group(0) if m else text
    try:
        return json.loads(s)
    except:
        s = s.replace("```json","").replace("```","").strip()
        try:
            return json.loads(s)
        except:
            return {}

def build_index(embedder, chunks):
    embs = embedder.encode(chunks, batch_size=32, convert_to_numpy=True, normalize_embeddings=True)
    dim = embs.shape[1]
    idx = faiss.IndexFlatIP(dim)
    idx.add(embs.astype(np.float32))
    return idx, embs

def retrieve(embedder, idx, queries, chunks, top_k=8):
    q_emb = embedder.encode(queries, convert_to_numpy=True, normalize_embeddings=True)
    if q_emb.ndim==1: q_emb = q_emb[None,:]
    D, I = idx.search(q_emb.astype(np.float32), top_k)
    results = []
    for qi,(ds,ids) in enumerate(zip(D,I)):
        pack=[]
        for d,i in zip(ds,ids):
            if i<0 or i>=len(chunks): continue
            pack.append({"chunk":chunks[i], "score":float(d), "index":int(i)})
        results.append({"query":queries[qi], "hits":pack})
    return results

def softmax(z):
    z = np.array(z, dtype=np.float64)
    z = z - z.max()
    e = np.exp(z)
    return e/(e.sum()+1e-12)

def dynamic_threshold(scores):
    s = np.array(scores, dtype=np.float64)
    mu, sd = s.mean(), s.std() if s.std()>1e-9 else 1.0
    th = float(mu + 0.25*sd)
    return th

def parse_resume_pdf(path, nlp, embedder):
    doc = fitz.open(path)
    text = "\n".join([p.get_text() for p in doc])
    doc.close()
    if not text.strip(): return None
    name = "Unknown"
    try:
        dn = nlp(text[:800])
        pers = [e.text for e in dn.ents if e.label_=="PERSON"]
        if pers: name = pers[0]
    except:
        pass
    email, phone = parse_contacts(text)
    chunks = chunk_text(text)
    idx, embs = build_index(embedder, chunks)
    ph = extract_keyphrases(text, nlp, top_n=30)
    return {"name":name,"email":email,"phone":phone,"text":text,"chunks":chunks,"faiss":idx,"embs":embs,"phrases":ph}

def jd_plan_prompt(jd, preview):
    return f"""
You are an expert hiring analyst. From the JOB DESCRIPTION and short RESUME PREVIEW, produce a JSON plan to guide a local RAG pipeline.
Return only valid JSON with keys: role_title, seniority, must_have, good_to_have, soft_skills, certifications, scoring_weights, red_flags, questions_to_ask, enrichment_cues.
Use concise phrases. Weights should be a dictionary with keys semantic, coverage, llm_fit summing to 1.0.
JOB DESCRIPTION:
{jd}

RESUME PREVIEW:
{preview}
"""

def analysis_prompt(jd, plan, evidence, global_sem, coverage_score, coverage_detail):
    return f"""
You are evaluating one candidate against one job. Use the PLAN and the retrieved EVIDENCE only. Produce a structured JSON assessment with fields:
cultural_fit, technical_strength, experience_relevance, top_strengths, improvement_areas, overall_comment, risk_flags, followup_questions, fit_score
fit_score must be a number from 0 to 10. Use nuanced reasoning and align with the plan's priorities.

JOB DESCRIPTION:
{jd}

PLAN:
{json.dumps(plan, ensure_ascii=False)}

GLOBAL_SEMANTIC_SIMILARITY:
{global_sem:.4f}

REQUIREMENT_COVERAGE_SCORE:
{coverage_score:.4f}

REQUIREMENT_COVERAGE_DETAIL:
{json.dumps(coverage_detail, ensure_ascii=False)}

EVIDENCE:
{json.dumps(evidence, ensure_ascii=False)}
"""

def compute_semantic(embedder, a, b):
    va = embedder.encode(a, convert_to_numpy=True, normalize_embeddings=True)
    vb = embedder.encode(b, convert_to_numpy=True, normalize_embeddings=True)
    return float(np.dot(va, vb))

def score_requirements(embedder, idx, chunks, reqs):
    out = []
    for r in reqs:
        rs = retrieve(embedder, idx, [r], chunks, top_k=5)[0]["hits"]
        best = max(rs, key=lambda x:x["score"]) if rs else {"score":0.0,"chunk":""}
        out.append({"requirement":r,"max_sim":best["score"],"evidence":best["chunk"]})
    sims = [x["max_sim"] for x in out] or [0.0]
    th = dynamic_threshold(sims)
    covered = [1.0 if s>=th else 0.0 for s in sims]
    coverage = float(np.mean(covered))
    return out, coverage, th

def compute_hybrid_score(semantic_s, coverage_s, llm_fit, weights):
    w_sem = float(weights.get("semantic",0.4))
    w_cov = float(weights.get("coverage",0.4))
    w_llm = float(weights.get("llm_fit",0.2))
    w = np.array([w_sem,w_cov,w_llm],dtype=np.float64)
    if w.sum()<=1e-9: w = np.array([0.4,0.4,0.2])
    w = w/w.sum()
    comp = np.array([semantic_s, coverage_s, llm_fit/10.0], dtype=np.float64)
    score = float(np.clip(np.dot(w, comp)*10.0,0,10))
    parts = {"semantic":float(semantic_s*10),"coverage":float(coverage_s*10),"llm_fit":float(llm_fit)}
    norm_parts = {"semantic":float(comp[0]*10),"coverage":float(comp[1]*10),"llm_fit":float(comp[2]*10)}
    return round(score,1), parts, norm_parts

def gauge(score):
    color = '#10b981' if score>=8 else '#3b82f6' if score>=6 else '#f59e0b' if score>=4 else '#ef4444'
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, domain={'x':[0,1],'y':[0,1]},
                                 title={'text':"Overall Match",'font':{'size':24,'color':'#e2e8f0'}},
                                 gauge={'axis':{'range':[0,10],'tickwidth':2,'tickcolor':'#475569'},
                                        'bar':{'color':color,'thickness':0.75},
                                        'bgcolor':'rgba(22,33,62,.3)','borderwidth':2,'bordercolor':'#334155',
                                        'steps':[{'range':[0,4],'color':'rgba(239,68,68,.15)'},
                                                 {'range':[4,6],'color':'rgba(245,158,11,.15)'},
                                                 {'range':[6,8],'color':'rgba(59,130,246,.15)'},
                                                 {'range':[8,10],'color':'rgba(16,185,129,.15)'}]}))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color':'#e2e8f0','family':'Inter'}, height=380, margin=dict(l=30,r=30,t=60,b=30))
    return fig

def radar(sem, cov, llm_fit):
    cats = ['Semantic','Coverage','LLM Fit']
    vals = [sem*10, cov*10, llm_fit]
    fig = go.Figure(data=go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]], fill='toself', line=dict(width=3)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,10], gridcolor='rgba(148,163,184,.2)', tickfont=dict(color='#94a3b8',size=12)),
                                 angularaxis=dict(gridcolor='rgba(148,163,184,.2)', tickfont=dict(color='#e2e8f0',size=14), rotation=90),
                                 bgcolor='rgba(22,33,62,.3)'),
                      paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter'), height=380, showlegend=False, margin=dict(l=40,r=40,t=40,b=40))
    return fig

def bar_coverage(detail, th):
    df = [{"Requirement":d["requirement"][:40]+"..." if len(d["requirement"])>43 else d["requirement"], "Similarity":d["max_sim"]} for d in detail]
    if not df: df=[{"Requirement":"None","Similarity":0.0}]
    fig = px.bar(df, x="Requirement", y="Similarity")
    fig.add_hline(y=th, line_dash="dash")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(l=40,r=40,t=40,b=80))
    return fig

def hist_distribution(sims):
    fig = px.histogram({"sim":sims}, x="sim", nbins=12)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320, margin=dict(l=40,r=40,t=40,b=40))
    return fig

def waterfall(parts):
    x = list(parts.keys())
    y = [parts[k] for k in x]
    base = 0
    measures = ["relative"]*len(x)
    fig = go.Figure(go.Waterfall(x=x, y=y, measure=measures))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=320, margin=dict(l=40,r=40,t=40,b=40))
    return fig

def save_to_db(resume_doc, jd, analysis, resumes_collection, analyses_collection, mongo_ok):
    rid = None
    try:
        if mongo_ok and resumes_collection:
            rdoc = {k:resume_doc[k] for k in ["name","email","phone"]}
            rdoc["file_name"] = resume_doc.get("file_name","unknown")
            rdoc["phrases"] = resume_doc.get("phrases",[])
            rdoc["timestamp"] = time.time()
            r = resumes_collection.insert_one(rdoc)
            rid = str(r.inserted_id)
        if mongo_ok and analyses_collection:
            adoc = {"resume_id":rid,"candidate":resume_doc.get("name","Unknown"),"email":resume_doc.get("email","N/A"),
                    "file_name":resume_doc.get("file_name","unknown"),"job_desc":jd,"analysis":analysis,"timestamp":time.time()}
            analyses_collection.insert_one(adoc)
    except:
        pass

def get_recent(analyses_collection, mongo_ok, limit=20):
    items = []
    try:
        if mongo_ok and analyses_collection:
            for x in analyses_collection.find({}, sort=[("timestamp",-1)]).limit(limit):
                items.append(x)
    except:
        pass
    return items

with st.spinner('Initializing models...'):
    model, nlp, embedder, models_ok = load_models()
    resumes_collection, analyses_collection, mongo_ok = init_mongodb()

if not models_ok:
    st.error("Gemini model unavailable. Verify GEMINI_API_KEY and set GEMINI_MODEL_NAME to a listed model (e.g., gemini-2.5-flash or gemini-pro-latest).")
    st.stop()

st.session_state.models_loaded = True

st.markdown("""
<div style="text-align:center;padding:40px 0 20px 0;animation:slideInDown .8s ease;">
<h1 style="font-size:56px;margin:0;background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-weight:900;letter-spacing:-2px;">🎯 Resume Screener Pro</h1>
<p style="font-size:20px;color:#94a3b8;margin-top:12px;font-weight:400;letter-spacing:1px;">RAG-Infused, LLM-Guided Resume Analysis</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.get("gemini_model_name"):
    st.caption(f"Using Gemini model: {st.session_state['gemini_model_name']}")

tab1, tab2 = st.tabs(["📄 Analyze", "🕒 Recent"])

with tab1:
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1,1], gap="large")
    with c1:
        st.markdown('<div class="analysis-card"><h3 style="margin-top:0;font-size:22px;color:#e2e8f0;">📤 Upload Resume (PDF)</h3></div>', unsafe_allow_html=True)
        up = st.file_uploader("pdf", type=['pdf'], label_visibility="collapsed")
    with c2:
        st.markdown('<div class="analysis-card"><h3 style="margin-top:0;font-size:22px;color:#e2e8f0;">📝 Job Description</h3></div>', unsafe_allow_html=True)
        jd = st.text_area("jd", height=220, label_visibility="collapsed", placeholder="Paste a detailed job description...")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
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
                prog.progress(0.15)
                stat.info("Parsing resume...")
                parsed = parse_resume_pdf(tmp_path, nlp, embedder)
                if not parsed:
                    st.error("No text parsed from the PDF.")
                    st.stop()
                parsed["file_name"] = up.name
                preview = "\n".join(parsed["chunks"][:2])[:1200]
                st.session_state.uploads_history.insert(0, {"file_name":up.name,"name":parsed["name"],"email":parsed["email"],"phone":parsed["phone"],"timestamp":time.time()})
                prog.progress(0.35)
                stat.info("Deriving dynamic analysis plan...")
                plan = llm_json(model, jd_plan_prompt(jd, preview))
                if not plan or not isinstance(plan, dict): plan = {"role_title":"","seniority":"","must_have":[],"good_to_have":[],"soft_skills":[],"certifications":[],"scoring_weights":{"semantic":0.45,"coverage":0.4,"llm_fit":0.15},"red_flags":[],"questions_to_ask":[],"enrichment_cues":[]}
                must = plan.get("must_have",[]) or []
                nice = plan.get("good_to_have",[]) or []
                queries = list(dict.fromkeys([*must, *nice, *parsed["phrases"][:10]]))
                prog.progress(0.55)
                stat.info("Retrieving evidence...")
                r = retrieve(embedder, parsed["faiss"], queries, parsed["chunks"], top_k=5)
                ev_hits = []
                for q in r:
                    hits = sorted(q["hits"], key=lambda x: -x["score"])[:2]
                    ev_hits.append({"query":q["query"], "hits":hits})
                prog.progress(0.7)
                stat.info("Scoring coverage and similarity...")
                must_detail, must_cov, th_m = score_requirements(embedder, parsed["faiss"], parsed["chunks"], must)
                nice_detail, nice_cov, th_g = score_requirements(embedder, parsed["faiss"], parsed["chunks"], nice)
                coverage_score = float(0.7*must_cov + 0.3*nice_cov) if (must or nice) else 0.0
                global_sem = compute_semantic(embedder, parsed["text"], jd)
                prog.progress(0.82)
                stat.info("LLM assessment and explanation...")
                llm_out = llm_json(model, analysis_prompt(jd, plan, ev_hits, global_sem, coverage_score, {"must_have":must_detail,"good_to_have":nice_detail}))
                fit_score = float(llm_out.get("fit_score", max(0.0, min(10.0, (global_sem*10)))))
                final_score, comp_parts, _ = compute_hybrid_score(global_sem, coverage_score, fit_score, plan.get("scoring_weights",{}))
                result = {
                    "score":final_score,
                    "semantic_score":round(global_sem*10,1),
                    "coverage_score":round(coverage_score*10,1),
                    "llm_fit_score":round(fit_score,1),
                    "thresholds":{"must_have":th_m,"good_to_have":th_g},
                    "matched_must":[d for d in must_detail if d["max_sim"]>=th_m],
                    "matched_good":[d for d in nice_detail if d["max_sim"]>=th_g],
                    "evidence":ev_hits,
                    "plan":plan,
                    "llm_analysis":{
                        "cultural_fit":llm_out.get("cultural_fit",""),
                        "technical_strength":llm_out.get("technical_strength",""),
                        "experience_relevance":llm_out.get("experience_relevance",""),
                        "top_strengths":llm_out.get("top_strengths",[]),
                        "improvement_areas":llm_out.get("improvement_areas",[]),
                        "overall_comment":llm_out.get("overall_comment",""),
                        "risk_flags":llm_out.get("risk_flags",[]),
                        "followup_questions":llm_out.get("followup_questions",[])
                    },
                    "components":comp_parts,
                    "raw_detail":{"must_have":must_detail,"good_to_have":nice_detail},
                    "resume_meta":{"name":parsed["name"],"email":parsed["email"],"phone":parsed["phone"],"file_name":parsed["file_name"]},
                    "timestamp":time.time()
                }
                save_to_db(parsed, jd, result, resumes_collection, analyses_collection, mongo_ok)
                st.session_state.analysis_history.insert(0, result)
                st.session_state.analysis_history = st.session_state.analysis_history[:100]
                st.session_state.current_analysis = (parsed, result)
                prog.progress(1.0)
                stat.success("Done")
                time.sleep(0.3)
                prog.empty(); stat.empty()
                st.rerun()
            finally:
                try: os.unlink(tmp_path)
                except: pass

    if st.session_state.current_analysis:
        resume, analysis = st.session_state.current_analysis
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns([2,1,1])
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin-top:0;color:#e2e8f0;font-size:24px;">👤 Candidate</h3>
                <p style="margin:8px 0;font-size:16px;"><strong>Name:</strong> {resume['name']}</p>
                <p style="margin:8px 0;font-size:16px;"><strong>Email:</strong> {resume['email']}</p>
                <p style="margin:8px 0;font-size:16px;"><strong>Phone:</strong> {resume['phone']}</p>
                <p style="margin:8px 0;font-size:16px;"><strong>File:</strong> {resume.get('file_name','')}</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin-top:0;color:#e2e8f0;font-size:24px;">📊 Metrics</h3>
                <p style="margin:8px 0;font-size:16px;"><strong>Semantic:</strong> {analysis['semantic_score']:.1f}/10</p>
                <p style="margin:8px 0;font-size:16px;"><strong>Coverage:</strong> {analysis['coverage_score']:.1f}/10</p>
                <p style="margin:8px 0;font-size:16px;"><strong>LLM Fit:</strong> {analysis['llm_fit_score']:.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            sc = analysis['score']
            cls = 'score-excellent' if sc>=8 else 'score-good' if sc>=6 else 'score-fair' if sc>=4 else 'score-poor'
            lab = '🌟 Excellent' if sc>=8 else '👍 Good' if sc>=6 else '⚠️ Fair' if sc>=4 else '❌ Poor'
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div class="score-badge {cls}">{sc}</div>
                <p style="margin-top:16px;font-size:18px;font-weight:700;">{lab}</p>
            </div>
            """, unsafe_allow_html=True)

        c4,c5 = st.columns(2, gap="large")
        with c4: st.plotly_chart(gauge(analysis['score']), use_container_width=True, config={'displayModeBar': False})
        with c5: st.plotly_chart(radar(analysis['semantic_score']/10.0, analysis['coverage_score']/10.0, analysis['llm_fit_score']), use_container_width=True, config={'displayModeBar': False})

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        c6,c7 = st.columns(2, gap="large")
        with c6:
            st.markdown('<div class="analysis-card"><h3 style="margin-top:0;color:#10b981;font-size:22px;">✅ Requirement Coverage</h3></div>', unsafe_allow_html=True)
            st.plotly_chart(bar_coverage(analysis['raw_detail']['must_have']+analysis['raw_detail']['good_to_have'], max(analysis['thresholds']['must_have'], analysis['thresholds']['good_to_have'])), use_container_width=True, config={'displayModeBar': False})
        with c7:
            sims = [d["max_sim"] for d in (analysis['raw_detail']['must_have']+analysis['raw_detail']['good_to_have'])]
            st.markdown('<div class="analysis-card"><h3 style="margin-top:0;color:#667eea;font-size:22px;">📈 Similarity Distribution</h3></div>', unsafe_allow_html=True)
            st.plotly_chart(hist_distribution(sims if sims else [0.0]), use_container_width=True, config={'displayModeBar': False})

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="analysis-card"><h3 style="margin-top:0;color:#e2e8f0;font-size:22px;">🔎 Evidence</h3></div>', unsafe_allow_html=True)
        for ev in analysis['evidence'][:8]:
            with st.expander(f"Query: {ev['query'][:80]}"):
                for h in ev['hits']:
                    st.markdown(f"**Similarity:** {h['score']:.3f}")
                    st.write(h['chunk'][:800]+"...")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        c8,c9 = st.columns(2, gap="large")
        with c8:
            llm = analysis['llm_analysis']
            st.markdown(f"""
            <div class="success-box">
                <h4 style="margin-top:0;color:#86efac;font-size:20px;">💪 Top Strengths</h4>
                {''.join([f'<p style="margin:8px 0;font-size:15px;">• {s}</p>' for s in llm.get('top_strengths',[])])}
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="warning-box">
                <h4 style="margin-top:0;color:#fcd34d;font-size:20px;">📈 Improvement Areas</h4>
                {''.join([f'<p style="margin:8px 0;font-size:15px;">• {a}</p>' for a in llm.get('improvement_areas',[])])}
            </div>
            """, unsafe_allow_html=True)
        with c9:
            st.markdown(f"""
            <div class="info-box">
                <h4 style="margin-top:0;color:#93c5fd;font-size:20px;">🤝 Cultural Fit</h4>
                <p style="font-size:15px;line-height:1.6;">{llm.get('cultural_fit','')}</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-box">
                <h4 style="margin-top:0;color:#93c5fd;font-size:20px;">⚙️ Technical Strength</h4>
                <p style="font-size:15px;line-height:1.6;">{llm.get('technical_strength','')}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="analysis-card" style="margin-top:20px;background:linear-gradient(135deg,rgba(102,126,234,.15),rgba(118,75,162,.15));border-color:rgba(102,126,234,.4);">
            <h4 style="margin-top:0;color:#e2e8f0;font-size:22px;">📋 Overall Assessment</h4>
            <p style="font-size:16px;line-height:1.7;">{analysis['llm_analysis'].get('overall_comment','')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="analysis-card"><h3 style="margin-top:0;color:#e2e8f0;font-size:22px;">🧮 Score Composition</h3></div>', unsafe_allow_html=True)
        st.plotly_chart(waterfall(analysis["components"]), use_container_width=True, config={'displayModeBar': False})

        payload = json.dumps(analysis, ensure_ascii=False, indent=2)
        st.download_button("⬇️ Download Analysis JSON", data=payload.encode('utf-8'), file_name=f"analysis_{int(time.time())}.json", use_container_width=True)

with tab2:
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="analysis-card"><h3 style="margin-top:0;font-size:22px;color:#e2e8f0;">Recent Uploads</h3></div>', unsafe_allow_html=True)
    if not st.session_state.uploads_history:
        st.info("No uploads yet.")
    else:
        for u in st.session_state.uploads_history[:12]:
            t = datetime.fromtimestamp(u["timestamp"]).strftime('%b %d, %Y • %I:%M %p')
            st.markdown(f"""
            <div class="metric-card">
                <p style="margin:6px 0;font-size:16px;"><strong>File:</strong> {u['file_name']}</p>
                <p style="margin:6px 0;font-size:16px;"><strong>Name:</strong> {u['name']} • <strong>Email:</strong> {u['email']} • <strong>Phone:</strong> {u['phone']}</p>
                <p style="margin:6px 0;font-size:14px;">{t}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="analysis-card"><h3 style="margin-top:0;font-size:22px;color:#e2e8f0;">Recent Analyses</h3></div>', unsafe_allow_html=True)
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
                    st.markdown(f"""<div style="text-align:center;"><div class="score-badge {cls}" style="font-size:36px;padding:16px 32px;">{sc}</div></div>""", unsafe_allow_html=True)
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
                    <p>{t}</p>
                </div>
                """, unsafe_allow_html=True)

