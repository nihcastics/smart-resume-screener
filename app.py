""""""import os, sys

Smart Resume Screener - Modular Version

"""Smart Resume Screener - Modular Versionos.environ['TOKENIZERS_PARALLELISM'] = 'false'

from modules.config import CSS

from dotenv import load_dotenvMain application file with imports from organized modulesos.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

load_dotenv()

"""os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import streamlit as st

import tempfileos.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import json

from datetime import datetime# Environment setup and configurationos.environ['TORCH_CPP_LOG_LEVEL'] = 'ERROR'



from modules.models import load_modelsfrom modules.config import CSSos.environ['PYTORCH_JIT'] = '0'

from modules.database import init_postgresql, save_to_db, get_recent

from modules.text_processing import (from dotenv import load_dotenv

    normalize_text, chunk_text, parse_contacts, build_index,

    extract_sections, token_set, contains_atom, extract_atoms_from_text,load_dotenv()import warnings, logging, io

    refine_atom_list, extract_structured_entities, extract_technical_skills

)stderr_backup = sys.stderr

from modules.llm_operations import (

    llm_json, jd_plan_prompt, resume_profile_prompt,# Core importssys.stderr = io.StringIO()

    atomicize_requirements_prompt, analysis_prompt, llm_verify_requirements_clean

)import streamlit as stwarnings.filterwarnings('ignore')

from modules.scoring import (

    compute_global_semantic, evaluate_requirement_coverage,import tempfilelogging.getLogger().setLevel(logging.ERROR)

    compute_cue_alignment, build_competency_catalog,

    compute_competency_scores, map_atoms_to_competenciesimport jsonlogging.getLogger('sentence_transformers').setLevel(logging.ERROR)

)

from modules.resume_parser import parse_resume_pdffrom datetime import datetimelogging.getLogger('transformers').setLevel(logging.ERROR)

from modules.ui_components import section



st.set_page_config(

    layout="wide",# Module importsimport streamlit as st

    page_title="Smart Resume Screener",

    page_icon="🎯",from modules.models import load_modelsimport fitz  # PyMuPDF

    initial_sidebar_state="collapsed"

)from modules.database import init_postgresql, save_to_db, get_recentimport spacy



st.markdown(CSS, unsafe_allow_html=True)from modules.text_processing import (from sentence_transformers import SentenceTransformer



if "models_loaded" not in st.session_state:    normalize_text, chunk_text, parse_contacts, build_index,import faiss

    with st.spinner("🔄 Loading AI models..."):

        model, nlp, embedder, models_ok = load_models()    extract_sections, token_set, contains_atom, extract_atoms_from_text,import numpy as np

        st.session_state["model"] = model

        st.session_state["nlp"] = nlp    refine_atom_list, extract_structured_entities, extract_technical_skillsimport google.generativeai as genai

        st.session_state["embedder"] = embedder

        st.session_state["models_loaded"] = models_ok)from dotenv import load_dotenv

else:

    model = st.session_state.get("model")from modules.llm_operations import (import json, time, re, tempfile, html

    nlp = st.session_state.get("nlp")

    embedder = st.session_state.get("embedder")    llm_json, jd_plan_prompt, resume_profile_prompt,from datetime import datetime

    models_ok = st.session_state.get("models_loaded", False)

    atomicize_requirements_prompt, analysis_prompt, llm_verify_requirements_cleanfrom collections import Counter

if "db_initialized" not in st.session_state:

    db_conn, db_ok = init_postgresql())import psycopg2

    st.session_state["db_conn"] = db_conn

    st.session_state["db_ok"] = db_okfrom modules.scoring import (from psycopg2.extras import Json, RealDictCursor

    st.session_state["db_initialized"] = True

else:    compute_global_semantic, evaluate_requirement_coverage,import plotly.graph_objects as go

    db_conn = st.session_state.get("db_conn")

    db_ok = st.session_state.get("db_ok", False)    compute_cue_alignment, build_competency_catalog,import plotly.express as px



st.markdown("""    compute_competency_scores, map_atoms_to_competencies

<div style="text-align:center;padding:40px 0 60px 0;">

    <h1 style="font-size:4.5rem;font-weight:900;background:linear-gradient(135deg,#8b5cf6 0%,#ec4899 50%,#6366f1 100%);)sys.stderr = stderr_backup

        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:20px;

        letter-spacing:-0.04em;text-shadow:0 8px 32px rgba(139,92,246,0.4);">🎯 Smart Resume Screener</h1>from modules.resume_parser import parse_resume_pdfload_dotenv()

    <p style="font-size:1.35rem;color:#a78bfa;font-weight:600;letter-spacing:1px;text-shadow:0 2px 8px rgba(139,92,246,0.3);">

        AI-Powered Candidate Evaluation System</p>from modules.ui_components import section

</div>

""", unsafe_allow_html=True)import plotly.graph_objects as go# --- Streamlit page ---



if models_ok:import plotly.express as pxst.set_page_config(layout="wide", page_title="Smart Resume Screener", page_icon="🎯", initial_sidebar_state="collapsed")

    model_name = st.session_state.get("gemini_model_name", "Unknown")

    st.success(f"✅ **AI Models Loaded Successfully!** Using Google Gemini: `{model_name}`")

else:

    st.error("❌ **AI Models Not Available** - Please check your GEMINI_API_KEY in `.env` file")# Streamlit page configCSS = """

    st.info("💡 Get a FREE API key at: https://makersuite.google.com/app/apikey")

    st.stop()st.set_page_config(<style>



if 'analysis_history' not in st.session_state:    layout="wide",@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    st.session_state.analysis_history = []

    page_title="Smart Resume Screener",

tab1, tab2 = st.tabs(["📄 Analyze", "🕒 Recent"])

    page_icon="🎯",/* ===== GLOBAL RESET & BASE ===== */

with tab1:

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)    initial_sidebar_state="collapsed"*{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif}

    

    uploaded_file = st.session_state.get('uploaded_file', None))html,body,[class*="css"],.main,.stApp{background:#060812!important;overflow-x:hidden}

    job_description = st.session_state.get('job_description', '')

    

    step_placeholder = st.empty()

    if not uploaded_file:# Apply CSS/* ===== IMMERSIVE ANIMATED GRADIENT BACKGROUND ===== */

        step_placeholder.markdown("""

        <div style="background:linear-gradient(135deg,rgba(99,102,241,.18),rgba(139,92,246,.15));st.markdown(CSS, unsafe_allow_html=True).stApp{

            border:2px solid rgba(99,102,241,.4);border-radius:20px;padding:20px 32px;text-align:center;margin-bottom:24px;">

            <span style="font-size:32px;">👆</span>    background:linear-gradient(-45deg,#0d0221,#0f0624,#1a0933,#150a2e,#0d0221)!important;

            <span style="font-size:17px;font-weight:700;color:#c7d2fe;">Step 1: Upload a resume PDF file</span>

        </div># Initialize models and database    background-size:600% 600%!important;

        """, unsafe_allow_html=True)

    elif not job_description or len(job_description) < 50:if "models_loaded" not in st.session_state:    animation:cosmicShift 20s ease-in-out infinite!important;

        step_placeholder.markdown("""

        <div style="background:linear-gradient(135deg,rgba(236,72,153,.18),rgba(139,92,246,.15));    with st.spinner("🔄 Loading AI models..."):    position:relative;

            border:2px solid rgba(236,72,153,.4);border-radius:20px;padding:20px 32px;text-align:center;margin-bottom:24px;">

            <span style="font-size:32px;">👉</span>        model, nlp, embedder, models_ok = load_models()    min-height:100vh;

            <span style="font-size:17px;font-weight:700;color:#fbbf24;">Step 2: Add job description (minimum 50 characters)</span>

        </div>        st.session_state["model"] = model}

        """, unsafe_allow_html=True)

    else:        st.session_state["nlp"] = nlp@keyframes cosmicShift{

        step_placeholder.markdown("""

        <div style="background:linear-gradient(135deg,rgba(16,185,129,.18),rgba(5,150,105,.15));        st.session_state["embedder"] = embedder    0%{background-position:0% 50%}

            border:2px solid rgba(16,185,129,.5);border-radius:20px;padding:20px 32px;text-align:center;margin-bottom:24px;">

            <span style="font-size:32px;">✅</span>        st.session_state["models_loaded"] = models_ok    25%{background-position:50% 75%}

            <span style="font-size:17px;font-weight:700;color:#6ee7b7;">Ready! Click button below to start analysis</span>

            <span style="font-size:32px;">🚀</span>else:    50%{background-position:100% 50%}

        </div>

        """, unsafe_allow_html=True)    model = st.session_state.get("model")    75%{background-position:50% 25%}

    

    c1, c2 = st.columns([1,1], gap="large")    nlp = st.session_state.get("nlp")    100%{background-position:0% 50%}

    

    with c1:    embedder = st.session_state.get("embedder")}

        st.markdown("### 📄 Resume Upload")

        uploaded_file = st.file_uploader("Choose PDF file", type=['pdf'], key='uploaded_file',    models_ok = st.session_state.get("models_loaded", False)

            help="Upload candidate's resume in PDF format (max 10MB)")

    /* ===== FLOATING GLOW PARTICLES ===== */

    with c2:

        st.markdown("### 💼 Job Description")if "db_initialized" not in st.session_state:.stApp::before{

        job_description = st.text_area("Paste job requirements", height=200,

            placeholder="Enter job description, required skills, qualifications...",    db_conn, db_ok = init_postgresql()    content:'';

            key='job_description', help="Provide detailed job description for better matching")

        st.session_state["db_conn"] = db_conn    position:fixed;

    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

        st.session_state["db_ok"] = db_ok    top:0;

    col1, col2, col3 = st.columns([1,2,1])

    with col2:    st.session_state["db_initialized"] = True    left:0;

        analyze_btn = st.button("🚀 Analyze Resume", use_container_width=True,

            disabled=not (uploaded_file and job_description and len(job_description) >= 50))else:    width:100%;

    

    if analyze_btn:    db_conn = st.session_state.get("db_conn")    height:100%;

        with st.spinner("🔍 Analyzing resume..."):

            try:    db_ok = st.session_state.get("db_ok", False)    background-image:radial-gradient(circle at 20% 30%,rgba(139,92,246,.12) 0%,transparent 40%),

                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:

                    tmp.write(uploaded_file.read())                     radial-gradient(circle at 80% 70%,rgba(236,72,153,.10) 0%,transparent 45%),

                    tmp_path = tmp.name

                # Header                     radial-gradient(circle at 50% 50%,rgba(99,102,241,.08) 0%,transparent 50%),

                progress = st.progress(0.1)

                st.info("📄 Parsing PDF resume...")st.markdown("""                     radial-gradient(circle at 10% 80%,rgba(16,185,129,.06) 0%,transparent 40%);

                resume_doc = parse_resume_pdf(tmp_path, nlp, embedder)

                <div style="text-align:center;padding:40px 0 60px 0;">    pointer-events:none;

                progress.progress(0.3)

                st.info("🔍 Extracting requirements...")    <h1 style="    z-index:0;

                atoms = extract_atoms_from_text(job_description, nlp)

                atoms_clean = refine_atom_list(atoms, nlp, limit=50)        font-size:4.5rem;    animation:glowPulse 25s ease-in-out infinite;

                

                must_atoms = [a for a in atoms_clean if len(a.split()) <= 3]        font-weight:900;}

                nice_atoms = [a for a in atoms_clean if len(a.split()) > 3]

                        background:linear-gradient(135deg,#8b5cf6 0%,#ec4899 50%,#6366f1 100%);@keyframes glowPulse{

                progress.progress(0.5)

                st.info("🧠 Computing semantic similarities...")        -webkit-background-clip:text;    0%,100%{opacity:1;transform:translate(0,0) scale(1)}

                chunks = resume_doc.get('chunks', [])

                if chunks:        -webkit-text-fill-color:transparent;    25%{opacity:.85;transform:translate(40px,-40px) scale(1.15)}

                    faiss_index, resume_embs = build_index(embedder, chunks)

                else:        background-clip:text;    50%{opacity:.95;transform:translate(-30px,30px) scale(1.05)}

                    faiss_index, resume_embs = None, None

                        margin-bottom:20px;    75%{opacity:.9;transform:translate(30px,20px) scale(1.1)}

                semantic_score = compute_global_semantic(embedder, resume_embs, job_description)

                        letter-spacing:-0.04em;}

                progress.progress(0.7)

                st.info("📊 Evaluating requirement coverage...")        text-shadow:0 8px 32px rgba(139,92,246,0.4);

                coverage_result = evaluate_requirement_coverage(

                    must_atoms, nice_atoms, resume_doc.get('text', ''),    ">🎯 Smart Resume Screener</h1>/* ===== MODERN TYPOGRAPHY WITH BETTER HIERARCHY ===== */

                    chunks, embedder, model, faiss_index)

                    <p style="h1{font-family:'Space Grotesk',sans-serif!important;color:#f8fafc!important;font-weight:800!important;font-size:3.5rem!important;letter-spacing:-.04em!important;text-shadow:0 4px 20px rgba(139,92,246,.6),0 0 60px rgba(236,72,153,.3)}

                progress.progress(0.9)

                st.info("🤖 Generating final assessment...")        font-size:1.35rem;h2{font-family:'Space Grotesk',sans-serif!important;color:#f1f5f9!important;font-weight:700!important;font-size:2.25rem!important;letter-spacing:-.03em!important;text-shadow:0 3px 15px rgba(99,102,241,.5)}

                

                analysis_prompt_text = analysis_prompt(        color:#a78bfa;h3{font-family:'Space Grotesk',sans-serif!important;color:#e2e8f0!important;font-weight:700!important;font-size:1.75rem!important;letter-spacing:-.02em!important;text-shadow:0 2px 12px rgba(139,92,246,.4)}

                    job_description, {"requirements": must_atoms + nice_atoms},

                    {"summary": resume_doc.get('text', '')[:2000]},        font-weight:600;h4,h5,h6{font-family:'Space Grotesk',sans-serif!important;color:#cbd5e1!important;font-weight:600!important;text-shadow:0 2px 8px rgba(99,102,241,.3)}

                    coverage_result, {}, semantic_score, coverage_result.get('overall', 0.5))

                        letter-spacing:1px;p,span,div{color:#94a3b8!important;line-height:1.8!important;font-size:1.05rem!important}

                llm_result = llm_json(model, analysis_prompt_text)

                        text-shadow:0 2px 8px rgba(139,92,246,0.3);

                coverage_score = coverage_result.get('overall', 0.5)

                llm_fit = llm_result.get('technical_strength', 50) / 100.0    ">AI-Powered Candidate Evaluation System</p>/* ===== ULTRA-MODERN FLUID TABS ===== */

                

                final_score = (semantic_score * 0.35 + coverage_score * 0.50 + llm_fit * 0.15) * 100</div>.stTabs [data-baseweb="tab-list"]{

                

                progress.progress(1.0)""", unsafe_allow_html=True)    gap:24px;

                st.success("✅ Analysis complete!")

                    background:linear-gradient(135deg,rgba(21,10,46,.75),rgba(13,2,33,.75));

                analysis = {

                    'candidate_name': resume_doc.get('name', 'Unknown'),# Show model status    border-bottom:none;

                    'email': resume_doc.get('email', 'Not found'),

                    'timestamp': datetime.now().timestamp(),if models_ok:    padding:16px 28px;

                    'score': final_score,

                    'semantic_score': semantic_score * 100,    model_name = st.session_state.get("gemini_model_name", "Unknown")    border-radius:24px 24px 0 0;

                    'coverage_score': coverage_score * 100,

                    'llm_fit_score': llm_fit * 100,    st.success(f"✅ **AI Models Loaded Successfully!** Using Google Gemini: `{model_name}`")    backdrop-filter:blur(30px) saturate(180%);

                    'requirements': {'must': must_atoms, 'nice': nice_atoms},

                    'coverage_details': coverage_result,else:    box-shadow:0 -15px 50px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.05);

                    'llm_analysis': llm_result,

                    'jd_text': job_description    st.error("❌ **AI Models Not Available** - Please check your GEMINI_API_KEY in `.env` file")    border:1px solid rgba(139,92,246,.15);

                }

                    st.info("💡 Get a FREE API key at: https://makersuite.google.com/app/apikey")}

                st.session_state.analysis_history.insert(0, analysis)

                st.session_state['current_analysis'] = analysis    st.stop().stTabs [data-baseweb="tab"]{

                

                if db_ok and db_conn:    height:64px;

                    save_to_db(resume_doc, job_description, analysis, db_conn, db_ok)

                # Initialize session state    padding:0 42px;

                st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

                st.markdown("## 📊 Analysis Results")if 'analysis_history' not in st.session_state:    background:linear-gradient(135deg,rgba(139,92,246,.08),rgba(99,102,241,.08));

                

                score_class = (    st.session_state.analysis_history = []    border:2px solid rgba(139,92,246,.2);

                    "score-excellent" if final_score >= 75 else

                    "score-good" if final_score >= 60 else    border-radius:18px;

                    "score-fair" if final_score >= 45 else "score-poor")

                # Main tabs    color:#a78bfa;

                st.markdown(f"""

                <div style="text-align:center;margin:40px 0;">tab1, tab2 = st.tabs(["📄 Analyze", "🕒 Recent"])    font-family:'Space Grotesk',sans-serif;

                    <div class="score-badge {score_class}">{final_score:.1f}</div>

                    <p style="margin-top:20px;font-size:1.2rem;color:#94a3b8;">Overall Match Score</p>    font-weight:700;

                </div>

                """, unsafe_allow_html=True)# TAB 1: Analyze    font-size:16px;

                

                col1, col2, col3 = st.columns(3)with tab1:    letter-spacing:.5px;

                with col1:

                    st.metric("📊 Coverage", f"{coverage_score*100:.1f}%")    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)    transition:all .5s cubic-bezier(.34,1.56,.64,1);

                with col2:

                    st.metric("🧠 Semantic", f"{semantic_score*100:.1f}%")        backdrop-filter:blur(15px);

                with col3:

                    st.metric("⚡ LLM Fit", f"{llm_fit*100:.1f}%")    # Get current state    position:relative;

                

                with st.expander("📋 Detailed Analysis", expanded=True):    uploaded_file = st.session_state.get('uploaded_file', None)    overflow:hidden;

                    st.markdown("**Top Strengths:**")

                    for strength in llm_result.get('top_strengths', [])[:4]:    job_description = st.session_state.get('job_description', '')    box-shadow:0 4px 15px rgba(139,92,246,.15);

                        st.markdown(f"- {strength}")

                    st.markdown("\\n**Cultural Fit:**")    }

                    st.write(llm_result.get('cultural_fit', 'N/A'))

                    st.markdown("\\n**Overall Comment:**")    # Step indicator.stTabs [data-baseweb="tab"]::before{

                    st.write(llm_result.get('overall_comment', 'N/A'))

                    step_placeholder = st.empty()    content:'';

            except Exception as e:

                st.error(f"❌ Error during analysis: {str(e)}")    if not uploaded_file:    position:absolute;

                import traceback

                st.code(traceback.format_exc())        step_placeholder.markdown("""    top:0;



with tab2:        <div style="background:linear-gradient(135deg,rgba(99,102,241,.18),rgba(139,92,246,.15));    left:-100%;

    st.markdown("## 🕒 Recent Analyses")

                border:2px solid rgba(99,102,241,.4);border-radius:20px;padding:20px 32px;    width:100%;

    if db_ok and db_conn:

        recent_items = get_recent(db_conn, db_ok, limit=20)            text-align:center;margin-bottom:24px;">    height:100%;

        if recent_items:

            for item in recent_items:            <span style="font-size:32px;">👆</span>    background:linear-gradient(90deg,transparent,rgba(139,92,246,.3),rgba(236,72,153,.3),transparent);

                score = item.get('final_score', 0) * 10

                st.markdown(f"""            <span style="font-size:17px;font-weight:700;color:#c7d2fe;">    transition:left .8s cubic-bezier(.4,0,.2,1);

                <div class="analysis-card">

                    <h4>💾 {item.get('candidate', 'Unknown')}</h4>                Step 1: Upload a resume PDF file}

                    <p><strong>Score:</strong> {score:.1f}/10</p>

                    <p><strong>Date:</strong> {item.get('created_at', 'Unknown')}</p>            </span>.stTabs [data-baseweb="tab"]::after{

                    <p><strong>Email:</strong> {item.get('email', 'Not found')}</p>

                </div>        </div>    content:'';

                """, unsafe_allow_html=True)

        else:        """, unsafe_allow_html=True)    position:absolute;

            st.info("No recent analyses in database")

        elif not job_description or len(job_description) < 50:    inset:0;

    if st.session_state.analysis_history:

        st.markdown("### ⚡ Session History")        step_placeholder.markdown("""    border-radius:18px;

        for idx, activity in enumerate(st.session_state.analysis_history[:10]):

            score = activity.get('score', 0)        <div style="background:linear-gradient(135deg,rgba(236,72,153,.18),rgba(139,92,246,.15));    padding:2px;

            name = activity.get('candidate_name', 'Unknown')

            st.markdown(f"""            border:2px solid rgba(236,72,153,.4);border-radius:20px;padding:20px 32px;    background:linear-gradient(135deg,rgba(139,92,246,.4),rgba(236,72,153,.4));

            <div class="analysis-card">

                <h4>⚡ {name}</h4>            text-align:center;margin-bottom:24px;">    -webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);

                <p><strong>Score:</strong> {score:.1f}/100</p>

            </div>            <span style="font-size:32px;">👉</span>    -webkit-mask-composite:exclude;

            """, unsafe_allow_html=True)

            <span style="font-size:17px;font-weight:700;color:#fbbf24;">    mask-composite:exclude;

st.markdown("""

<div style="text-align:center;padding:60px 0 40px 0;margin-top:80px;border-top:2px solid rgba(139,92,246,0.2);">                Step 2: Add job description (minimum 50 characters)    opacity:0;

    <p style="font-size:14px;color:#64748b;margin:0;">Built with ❤️ using Streamlit, Google Gemini, FAISS & spaCy</p>

    <p style="font-size:12px;color:#475569;margin-top:8px;">© 2025 Smart Resume Screener | Powered by AI</p>            </span>    transition:opacity .5s ease;

</div>

""", unsafe_allow_html=True)        </div>}


        """, unsafe_allow_html=True).stTabs [data-baseweb="tab"]:hover::before{left:100%}

    else:.stTabs [data-baseweb="tab"]:hover::after{opacity:1}

        step_placeholder.markdown(""".stTabs [data-baseweb="tab"]:hover{

        <div style="background:linear-gradient(135deg,rgba(16,185,129,.18),rgba(5,150,105,.15));    background:linear-gradient(135deg,rgba(139,92,246,.18),rgba(236,72,153,.15));

            border:2px solid rgba(16,185,129,.5);border-radius:20px;padding:20px 32px;    border-color:rgba(139,92,246,.5);

            text-align:center;margin-bottom:24px;">    transform:translateY(-6px) scale(1.03);

            <span style="font-size:32px;">✅</span>    box-shadow:0 15px 45px rgba(139,92,246,.35),0 0 50px rgba(236,72,153,.25);

            <span style="font-size:17px;font-weight:700;color:#6ee7b7;">    color:#e9d5ff;

                Ready! Click button below to start analysis}

            </span>.stTabs [aria-selected="true"]{

            <span style="font-size:32px;">🚀</span>    background:linear-gradient(135deg,#8b5cf6 0%,#ec4899 100%)!important;

        </div>    color:#fff!important;

        """, unsafe_allow_html=True)    border-color:rgba(139,92,246,.8)!important;

        box-shadow:0 20px 60px rgba(139,92,246,.6),0 0 80px rgba(236,72,153,.5),inset 0 2px 0 rgba(255,255,255,.3),inset 0 -2px 0 rgba(0,0,0,.2)!important;

    # Two column layout    transform:translateY(-4px) scale(1.02);

    c1, c2 = st.columns([1,1], gap="large")}

    

    with c1:/* ===== MAGNETIC GLOWING BUTTONS ===== */

        st.markdown("### 📄 Resume Upload").stButton>button{

        uploaded_file = st.file_uploader(    background:linear-gradient(135deg,#8b5cf6 0%,#6366f1 50%,#ec4899 100%);

            "Choose PDF file",    background-size:200% 200%;

            type=['pdf'],    color:#fff;

            key='uploaded_file',    border:none;

            help="Upload candidate's resume in PDF format (max 10MB)"    border-radius:20px;

        )    padding:22px 60px;

        font-family:'Space Grotesk',sans-serif;

    with c2:    font-weight:800;

        st.markdown("### 💼 Job Description")    font-size:17px;

        job_description = st.text_area(    letter-spacing:1.5px;

            "Paste job requirements",    text-transform:uppercase;

            height=200,    transition:all .5s cubic-bezier(.34,1.56,.64,1);

            placeholder="Enter job description, required skills, qualifications...",    box-shadow:0 15px 50px rgba(139,92,246,.5),0 0 60px rgba(236,72,153,.3),inset 0 2px 0 rgba(255,255,255,.3),inset 0 -2px 0 rgba(0,0,0,.2);

            key='job_description',    position:relative;

            help="Provide detailed job description for better matching"    overflow:hidden;

        )    animation:gradientSlide 4s ease infinite;

    }

    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)@keyframes gradientSlide{

        0%,100%{background-position:0% 50%}

    # Analyze button    50%{background-position:100% 50%}

    col1, col2, col3 = st.columns([1,2,1])}

    with col2:.stButton>button::before{

        analyze_btn = st.button(    content:'';

            "🚀 Analyze Resume",    position:absolute;

            use_container_width=True,    top:50%;

            disabled=not (uploaded_file and job_description and len(job_description) >= 50)    left:50%;

        )    width:0;

        height:0;

    # Analysis logic    border-radius:50%;

    if analyze_btn:    background:radial-gradient(circle,rgba(255,255,255,.4),transparent 70%);

        with st.spinner("🔍 Analyzing resume..."):    transform:translate(-50%,-50%);

            try:    transition:width .7s cubic-bezier(.4,0,.2,1),height .7s cubic-bezier(.4,0,.2,1);

                # Save PDF temporarily}

                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:.stButton>button::after{

                    tmp.write(uploaded_file.read())    content:'';

                    tmp_path = tmp.name    position:absolute;

                    inset:-2px;

                # Parse resume    border-radius:22px;

                progress = st.progress(0.1)    background:linear-gradient(45deg,#8b5cf6,#ec4899,#6366f1,#8b5cf6);

                st.info("📄 Parsing PDF resume...")    background-size:400% 400%;

                resume_doc = parse_resume_pdf(tmp_path, nlp, embedder)    opacity:0;

                    filter:blur(20px);

                # Extract atoms from JD    transition:opacity .5s ease;

                progress.progress(0.3)    animation:rotateGradient 6s linear infinite;

                st.info("🔍 Extracting requirements...")    z-index:-1;

                atoms = extract_atoms_from_text(job_description, nlp)}

                atoms_clean = refine_atom_list(atoms, nlp, limit=50)@keyframes rotateGradient{

                    0%{background-position:0% 50%}

                # Separate must-have and nice-to-have    50%{background-position:100% 50%}

                must_atoms = [a for a in atoms_clean if len(a.split()) <= 3]    100%{background-position:0% 50%}

                nice_atoms = [a for a in atoms_clean if len(a.split()) > 3]}

                .stButton>button:hover::before{width:400px;height:400px}

                # Build FAISS index.stButton>button:hover::after{opacity:.8}

                progress.progress(0.5).stButton>button:hover{

                st.info("🧠 Computing semantic similarities...")    transform:translateY(-6px) scale(1.05);

                chunks = resume_doc.get('chunks', [])    box-shadow:0 25px 80px rgba(139,92,246,.7),0 0 90px rgba(236,72,153,.6),0 0 120px rgba(99,102,241,.4),inset 0 2px 0 rgba(255,255,255,.4);

                if chunks:}

                    faiss_index, resume_embs = build_index(embedder, chunks).stButton>button:active{transform:translateY(-3px) scale(.98)}

                else:

                    faiss_index, resume_embs = None, None/* ===== IMMERSIVE FILE UPLOADER ===== */

                .stFileUploader{

                # Compute semantic score    background:linear-gradient(135deg,rgba(139,92,246,.08),rgba(236,72,153,.08));

                semantic_score = compute_global_semantic(embedder, resume_embs, job_description)    border:3px dashed rgba(139,92,246,.5);

                    border-radius:24px;

                # Evaluate coverage    padding:40px;

                progress.progress(0.7)    transition:all .5s cubic-bezier(.34,1.56,.64,1);

                st.info("📊 Evaluating requirement coverage...")    backdrop-filter:blur(25px) saturate(180%);

                coverage_result = evaluate_requirement_coverage(    position:relative;

                    must_atoms, nice_atoms,    overflow:hidden;

                    resume_doc.get('text', ''),}

                    chunks, embedder, model,.stFileUploader::before{

                    faiss_index, resume_embs    content:'';

                )    position:absolute;

                    inset:0;

                # LLM holistic analysis    border-radius:24px;

                progress.progress(0.9)    background:linear-gradient(45deg,rgba(139,92,246,.15),rgba(236,72,153,.15));

                st.info("🤖 Generating final assessment...")    opacity:0;

                    transition:opacity .5s ease;

                analysis_prompt_text = analysis_prompt(    pointer-events:none!important;

                    job_description,    z-index:-1;

                    {"requirements": must_atoms + nice_atoms},}

                    {"summary": resume_doc.get('text', '')[:2000]},.stFileUploader:hover::before{opacity:1}

                    coverage_result,.stFileUploader:hover{

                    {},    background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(236,72,153,.15));

                    semantic_score,    border-color:rgba(139,92,246,.8);

                    coverage_result.get('coverage_score', 0.5)    border-style:solid;

                )    transform:scale(1.02) translateY(-4px);

                    box-shadow:0 20px 60px rgba(139,92,246,.3),0 0 80px rgba(236,72,153,.2);

                llm_result = llm_json(model, analysis_prompt_text)}

                /* Ensure file uploader button is always clickable */

                # Calculate final score.stFileUploader button{

                coverage_score = coverage_result.get('coverage_score', 0.5)    pointer-events:auto!important;

                llm_fit = llm_result.get('technical_strength', 50) / 100.0    cursor:pointer!important;

                    opacity:1!important;

                final_score = (}

                    semantic_score * 0.35 +.stFileUploader section{

                    coverage_score * 0.50 +    pointer-events:auto!important;

                    llm_fit * 0.15}

                ) * 100.stFileUploader label{

                    pointer-events:auto!important;

                progress.progress(1.0)}

                st.success("✅ Analysis complete!").stFileUploader div[data-testid="stFileUploaderDropzone"]{

                    pointer-events:auto!important;

                # Store result}

                analysis = {

                    'candidate_name': resume_doc.get('name', 'Unknown'),/* ===== GLOWING TEXT AREA ===== */

                    'email': resume_doc.get('email', 'Not found'),.stTextArea textarea{

                    'timestamp': datetime.now().timestamp(),    background:linear-gradient(135deg,rgba(21,10,46,.9),rgba(13,2,33,.9))!important;

                    'score': final_score,    border:2px solid rgba(139,92,246,.3)!important;

                    'semantic_score': semantic_score * 100,    border-radius:20px!important;

                    'coverage_score': coverage_score * 100,    color:#f1f5f9!important;

                    'llm_fit_score': llm_fit * 10,    font-family:'JetBrains Mono',monospace!important;

                    'requirements': {'must': must_atoms, 'nice': nice_atoms},    font-size:16px!important;

                    'coverage_details': coverage_result,    padding:24px!important;

                    'llm_analysis': llm_result,    transition:all .4s cubic-bezier(.4,0,.2,1)!important;

                    'jd_text': job_description    line-height:1.9!important;

                }    backdrop-filter:blur(20px)!important;

                    box-shadow:inset 0 2px 8px rgba(0,0,0,.3)!important;

                st.session_state.analysis_history.insert(0, analysis)}

                st.session_state['current_analysis'] = analysis.stTextArea textarea:focus{

                    border-color:rgba(139,92,246,.9)!important;

                # Save to database    box-shadow:0 0 0 5px rgba(139,92,246,.2),0 15px 50px rgba(139,92,246,.3),0 0 70px rgba(236,72,153,.2),inset 0 2px 8px rgba(0,0,0,.3)!important;

                if db_ok and db_conn:    background:linear-gradient(135deg,rgba(21,10,46,.98),rgba(13,2,33,.98))!important;

                    save_to_db(resume_doc, job_description, analysis, db_conn, db_ok)    transform:scale(1.01)!important;

                }

                # Display results

                st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)/* ===== PREMIUM METRIC CARDS WITH GLOW ===== */

                st.markdown("## 📊 Analysis Results").metric-card{

                    background:linear-gradient(135deg,rgba(21,10,46,.90),rgba(13,2,33,.88));

                # Score badge    border:2px solid rgba(139,92,246,.25);

                score_class = (    border-radius:28px;

                    "score-excellent" if final_score >= 75 else    padding:36px;

                    "score-good" if final_score >= 60 else    transition:all .6s cubic-bezier(.34,1.56,.64,1);

                    "score-fair" if final_score >= 45 else    backdrop-filter:blur(30px) saturate(200%);

                    "score-poor"    box-shadow:0 10px 40px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.05);

                )    position:relative;

                    overflow:hidden;

                st.markdown(f"""}

                <div style="text-align:center;margin:40px 0;">.metric-card::before{

                    <div class="score-badge {score_class}">{final_score:.1f}</div>    content:'';

                    <p style="margin-top:20px;font-size:1.2rem;color:#94a3b8;">    position:absolute;

                        Overall Match Score    top:0;

                    </p>    left:0;

                </div>    right:0;

                """, unsafe_allow_html=True)    height:4px;

                    background:linear-gradient(90deg,transparent,rgba(139,92,246,.8),rgba(236,72,153,.8),transparent);

                # Metrics    opacity:0;

                col1, col2, col3 = st.columns(3)    transition:opacity .6s ease;

                with col1:    box-shadow:0 0 20px rgba(139,92,246,.6);

                    st.metric("📊 Coverage", f"{coverage_score*100:.1f}%")}

                with col2:.metric-card::after{

                    st.metric("🧠 Semantic", f"{semantic_score*100:.1f}%")    content:'';

                with col3:    position:absolute;

                    st.metric("⚡ LLM Fit", f"{llm_fit*10:.1f}/10")    inset:-100%;

                    background:radial-gradient(circle,rgba(139,92,246,.15),transparent 70%);

                # Detailed analysis    opacity:0;

                with st.expander("📋 Detailed Analysis", expanded=True):    transition:opacity .6s ease,transform .6s ease;

                    st.markdown(f"**Top Strengths:**")    pointer-events:none;

                    for strength in llm_result.get('top_strengths', [])[:4]:}

                        st.markdown(f"- {strength}").metric-card:hover::before{opacity:1}

                    .metric-card:hover::after{opacity:1;transform:scale(1.5)}

                    st.markdown(f"\\n**Cultural Fit:**").metric-card:hover{

                    st.write(llm_result.get('cultural_fit', 'N/A'))    border-color:rgba(139,92,246,.6);

                        transform:translateY(-10px) scale(1.02) rotate(0.5deg);

                    st.markdown(f"\\n**Overall Comment:**")    box-shadow:0 25px 70px rgba(139,92,246,.4),0 0 90px rgba(236,72,153,.3),inset 0 2px 0 rgba(255,255,255,.1);

                    st.write(llm_result.get('overall_comment', 'N/A'))}

                

            except Exception as e:/* ===== IMMERSIVE ANALYSIS CARDS ===== */

                st.error(f"❌ Error during analysis: {str(e)}").analysis-card{

                import traceback    background:linear-gradient(135deg,rgba(21,10,46,.92),rgba(13,2,33,.90));

                st.code(traceback.format_exc())    border:2px solid rgba(139,92,246,.3);

    border-radius:24px;

# TAB 2: Recent    padding:34px;

with tab2:    transition:all .5s cubic-bezier(.34,1.56,.64,1);

    st.markdown("## 🕒 Recent Analyses")    backdrop-filter:blur(25px) saturate(180%);

        box-shadow:0 12px 45px rgba(0,0,0,.4);

    # Try to load from database    position:relative;

    if db_ok and db_conn:    overflow:hidden;

        recent_items = get_recent(db_conn, db_ok, limit=20)}

        if recent_items:.analysis-card::before{

            for item in recent_items:    content:'';

                score = item.get('final_score', 0) * 10  # Scale 0-1 to 0-10    position:absolute;

                st.markdown(f"""    inset:0;

                <div class="analysis-card">    border-radius:24px;

                    <h4>💾 {item.get('candidate', 'Unknown')}</h4>    background:linear-gradient(135deg,rgba(139,92,246,.1),rgba(236,72,153,.1));

                    <p><strong>Score:</strong> {score:.1f}/10</p>    opacity:0;

                    <p><strong>Date:</strong> {item.get('created_at', 'Unknown')}</p>    transition:opacity .5s ease;

                    <p><strong>Email:</strong> {item.get('email', 'Not found')}</p>}

                </div>.analysis-card:hover::before{opacity:1}

                """, unsafe_allow_html=True).analysis-card:hover{

        else:    border-color:rgba(139,92,246,.6);

            st.info("No recent analyses in database")    transform:translateY(-8px) scale(1.01);

        box-shadow:0 20px 65px rgba(139,92,246,.35),0 0 80px rgba(236,72,153,.25);

    # Show session analyses}

    if st.session_state.analysis_history:

        st.markdown("### ⚡ Session History")/* ===== ULTRA 3D GLOWING SCORE BADGES ===== */

        for idx, activity in enumerate(st.session_state.analysis_history[:10]):.score-badge{

            score = activity.get('score', 0)    display:inline-block;

            name = activity.get('candidate_name', 'Unknown')    padding:28px 52px;

            st.markdown(f"""    border-radius:32px;

            <div class="analysis-card">    font-family:'Space Grotesk',sans-serif;

                <h4>⚡ {name}</h4>    font-weight:900;

                <p><strong>Score:</strong> {score:.1f}/100</p>    font-size:56px;

            </div>    box-shadow:0 20px 60px rgba(0,0,0,.6),inset 0 3px 0 rgba(255,255,255,.4),inset 0 -3px 0 rgba(0,0,0,.4);

            """, unsafe_allow_html=True)    transition:all .5s cubic-bezier(.34,1.56,.64,1);

    position:relative;

# Footer    letter-spacing:-.02em;

st.markdown("""}

<div style="text-align:center;padding:60px 0 40px 0;margin-top:80px;border-top:2px solid rgba(139,92,246,0.2);">.score-badge::after{

    <p style="font-size:14px;color:#64748b;margin:0;">    content:'';

        Built with ❤️ using Streamlit, Google Gemini, FAISS & spaCy    position:absolute;

    </p>    inset:-4px;

    <p style="font-size:12px;color:#475569;margin-top:8px;">    border-radius:36px;

        © 2025 Smart Resume Screener | Powered by AI    opacity:0;

    </p>    filter:blur(25px);

</div>    transition:opacity .5s ease;

""", unsafe_allow_html=True)    z-index:-1;

}
.score-badge:hover{transform:scale(1.12) rotate(-3deg) translateY(-8px);box-shadow:0 30px 90px rgba(0,0,0,.7),inset 0 3px 0 rgba(255,255,255,.5)}
.score-badge:hover::after{opacity:.9}
.score-excellent{background:linear-gradient(135deg,#10b981 0%,#059669 50%,#047857 100%);color:#fff;box-shadow:0 20px 70px rgba(16,185,129,.7),0 0 90px rgba(16,185,129,.5)}
.score-excellent::after{background:linear-gradient(135deg,#10b981,#059669)}
.score-good{background:linear-gradient(135deg,#6366f1 0%,#4f46e5 50%,#4338ca 100%);color:#fff;box-shadow:0 20px 70px rgba(99,102,241,.7),0 0 90px rgba(99,102,241,.5)}
.score-good::after{background:linear-gradient(135deg,#6366f1,#4f46e5)}
.score-fair{background:linear-gradient(135deg,#f59e0b 0%,#d97706 50%,#b45309 100%);color:#fff;box-shadow:0 20px 70px rgba(245,158,11,.7),0 0 90px rgba(245,158,11,.5)}
.score-fair::after{background:linear-gradient(135deg,#f59e0b,#d97706)}
.score-poor{background:linear-gradient(135deg,#ef4444 0%,#dc2626 50%,#b91c1c 100%);color:#fff;box-shadow:0 20px 70px rgba(239,68,68,.7),0 0 90px rgba(239,68,68,.5)}
.score-poor::after{background:linear-gradient(135deg,#ef4444,#dc2626)}

/* ===== ANIMATED GLOW CHIPS ===== */
.chip{
    display:inline-block;
    margin:6px 10px 6px 0;
    padding:10px 20px;
    border-radius:28px;
    background:linear-gradient(135deg,rgba(139,92,246,.20),rgba(236,72,153,.18));
    border:2px solid rgba(139,92,246,.5);
    font-size:14px;
    font-family:'Space Grotesk',sans-serif;
    font-weight:700;
    color:#e9d5ff;
    transition:all .4s cubic-bezier(.34,1.56,.64,1);
    box-shadow:0 4px 12px rgba(139,92,246,.25),inset 0 1px 0 rgba(255,255,255,.1);
    position:relative;
    overflow:hidden;
}
.chip::before{
    content:'';
    position:absolute;
    inset:0;
    border-radius:28px;
    background:linear-gradient(135deg,rgba(139,92,246,.3),rgba(236,72,153,.3));
    opacity:0;
    transition:opacity .4s ease;
}
.chip:hover::before{opacity:1}
.chip:hover{
    background:linear-gradient(135deg,rgba(139,92,246,.35),rgba(236,72,153,.33));
    border-color:rgba(139,92,246,.8);
    transform:translateY(-4px) scale(1.05);
    box-shadow:0 10px 30px rgba(139,92,246,.45),0 0 40px rgba(236,72,153,.35),inset 0 1px 0 rgba(255,255,255,.2);
    color:#fff;
}

/* ===== GLOWING DIVIDERS ===== */
hr{
    border:none;
    height:3px;
    background:linear-gradient(90deg,transparent,rgba(139,92,246,.5),rgba(236,72,153,.5),transparent);
    margin:40px 0;
    position:relative;
    box-shadow:0 0 20px rgba(139,92,246,.3);
}
hr::before{
    content:'';
    position:absolute;
    top:-2px;
    left:50%;
    transform:translateX(-50%);
    width:120px;
    height:6px;
    background:linear-gradient(90deg,#8b5cf6,#ec4899,#6366f1);
    border-radius:3px;
    box-shadow:0 4px 20px rgba(139,92,246,.7),0 0 40px rgba(236,72,153,.5);
    animation:glowPulseSmall 3s ease-in-out infinite;
}
@keyframes glowPulseSmall{
    0%,100%{opacity:1;filter:brightness(1)}
    50%{opacity:.8;filter:brightness(1.3)}
}

/* ===== FLUID EXPANDERS ===== */
.stExpander{
    background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85))!important;
    border:2px solid rgba(139,92,246,.3)!important;
    border-radius:20px!important;
    transition:all .4s cubic-bezier(.4,0,.2,1)!important;
    backdrop-filter:blur(20px) saturate(180%)!important;
}
.stExpander:hover{
    border-color:rgba(139,92,246,.6)!important;
    box-shadow:0 12px 40px rgba(139,92,246,.25),0 0 50px rgba(236,72,153,.15)!important;
    transform:translateY(-2px)!important;
}
.stExpander [data-testid="stExpanderToggleButton"]{
    color:#f1f5f9!important;
    font-family:'Space Grotesk',sans-serif!important;
    font-weight:700!important;
    font-size:15px!important;
}

/* ===== SIMPLIFIED GLOWY PROGRESS BAR ===== */
.stProgress {
    margin: 24px 0;
    position: relative;
    height: 12px !important;
}

.stProgress > div {
    background: linear-gradient(135deg, rgba(30,41,59,0.6), rgba(15,23,42,0.8));
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 
        inset 0 1px 3px rgba(0,0,0,0.4),
        0 2px 8px rgba(99,102,241,0.2);
    height: 12px !important;
    border: 1px solid rgba(99,102,241,0.3);
    position: relative;
}

.stProgress > div > div {
    background: linear-gradient(90deg, 
        #6366f1 0%, 
        #8b5cf6 50%, 
        #ec4899 100%);
    border-radius: 12px !important;
    box-shadow: 
        0 0 20px rgba(139,92,246,0.8),
        0 0 40px rgba(99,102,241,0.4),
        inset 0 1px 2px rgba(255,255,255,0.3);
    position: relative !important;
    height: 12px !important;
    transition: width 0.3s ease !important;
    overflow: hidden !important;
}

/* Glowing shimmer effect */
.stProgress > div > div::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(255,255,255,0.4), 
        transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* ===== PREMIUM GLOWING SCROLLBAR ===== */
::-webkit-scrollbar{width:12px;height:12px}
::-webkit-scrollbar-track{background:rgba(13,2,33,.9);border-radius:12px;box-shadow:inset 0 0 10px rgba(0,0,0,.5)}
::-webkit-scrollbar-thumb{
    background:linear-gradient(135deg,#8b5cf6,#ec4899,#6366f1);
    background-size:200% 200%;
    border-radius:12px;
    border:2px solid rgba(13,2,33,.9);
    box-shadow:0 0 15px rgba(139,92,246,.6);
    animation:scrollGlow 4s ease infinite;
}
@keyframes scrollGlow{
    0%,100%{background-position:0% 50%}
    50%{background-position:100% 50%}
}
::-webkit-scrollbar-thumb:hover{
    background:linear-gradient(135deg,#ec4899,#8b5cf6,#6366f1);
    box-shadow:0 0 25px rgba(236,72,153,.8);
}

/* ===== GLOWING SECTION HEADERS ===== */
.section-header{
    font-size:32px;
    font-weight:900;
    color:#f8fafc!important;
    margin-bottom:28px;
    text-transform:uppercase;
    letter-spacing:2px;
    text-shadow:0 4px 20px rgba(139,92,246,.8),0 0 50px rgba(236,72,153,.6),0 0 80px rgba(99,102,241,.4);
    font-family:'Space Grotesk',sans-serif!important;
    animation:headerGlow 3s ease-in-out infinite;
}
@keyframes headerGlow{
    0%,100%{filter:brightness(1) drop-shadow(0 0 20px rgba(139,92,246,.6))}
    50%{filter:brightness(1.2) drop-shadow(0 0 40px rgba(236,72,153,.8))}
}

/* ===== FLUID ENTRANCE ANIMATIONS ===== */
@keyframes fadeInUp{
    from{opacity:0;transform:translateY(40px) scale(.95)}
    to{opacity:1;transform:translateY(0) scale(1)}
}
@keyframes fadeInRotate{
    from{opacity:0;transform:translateY(40px) rotate(-5deg) scale(.9)}
    to{opacity:1;transform:translateY(0) rotate(0deg) scale(1)}
}
.metric-card{animation:fadeInRotate .8s cubic-bezier(.34,1.56,.64,1) backwards}
.analysis-card{animation:fadeInUp .7s ease-out backwards}
.metric-card:nth-child(1){animation-delay:.05s}
.metric-card:nth-child(2){animation-delay:.15s}
.metric-card:nth-child(3){animation-delay:.25s}
.analysis-card:nth-child(1){animation-delay:.1s}
.analysis-card:nth-child(2){animation-delay:.2s}

/* ===== HIDE STREAMLIT DEFAULT ELEMENTS ===== */
#MainMenu{visibility:hidden}
footer{visibility:hidden}
header{visibility:hidden}
.stDeployButton{display:none}
[data-testid="stToolbar"]{display:none}

/* ===== UTILITIES WITH ENHANCED GLOWS ===== */
.small{font-size:13px;color:#a78bfa;letter-spacing:.5px;font-weight:500}
.glow-text{
    text-shadow:0 0 30px rgba(139,92,246,.9),0 0 60px rgba(236,72,153,.7),0 0 90px rgba(99,102,241,.5);
    animation:textGlow 3s ease-in-out infinite;
}
@keyframes textGlow{
    0%,100%{filter:brightness(1)}
    50%{filter:brightness(1.4)}
}
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

# --- Config (stricter scoring with balanced weights) ---
# Semantic: 40% (increased - contextual fit is important)
# Coverage: 35% (decreased - less priority to avoid over-reliance on keyword matching)
# STRICT WEIGHTS: Coverage matters most (concrete skill matching)
# Coverage: 45% (raised - most important: does resume have required skills?)
# Semantic: 35% (lowered - general alignment)
# LLM Fit: 20% (lowered - holistic assessment but can be subjective)
DEFAULT_WEIGHTS = {"semantic":0.35, "coverage":0.45, "llm_fit":0.20}

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
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("❌ spaCy model 'en_core_web_sm' not found. Attempting to download...")
        try:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model downloaded successfully!")
        except Exception as e:
            print(f"❌ Failed to download spaCy model: {e}")
            return None, None, None, False
    
    # Verify all required components are available
    if "parser" not in nlp.pipe_names:
        print("❌ spaCy parser component not available")
        return None, None, None, False
    if "tagger" not in nlp.pipe_names:
        print("❌ spaCy tagger component not available")
        return None, None, None, False

    # Stronger default embedder
    try:
        s_name = os.getenv("SENTENCE_MODEL_NAME", "all-mpnet-base-v2")
        embedder = SentenceTransformer(s_name, device='cpu')
        print(f"✅ Sentence transformer loaded: {s_name}")
    except Exception as e:
        print(f"❌ Failed to load sentence transformer: {e}")
        return None, None, None, False

    return model, nlp, embedder, True

@st.cache_resource(show_spinner=False)
def init_postgresql():
    """Initialize PostgreSQL connection and create tables if they don't exist."""
    # Try Streamlit secrets first (for cloud deployment), then fall back to environment variables
    try:
        db_url = st.secrets.get("DATABASE_URL", "")
        if db_url:
            print("🔑 Using DATABASE_URL from Streamlit secrets")
    except (KeyError, AttributeError, Exception):
        db_url = os.getenv("DATABASE_URL", "")
        if db_url:
            print("🔑 Using DATABASE_URL from environment variable")
    
    db_url = db_url.strip() if db_url else ""
    if not db_url: 
        print("⚠️ DATABASE_URL not found - skipping database connection")
        print("💡 To enable database: Set DATABASE_URL in .env or Streamlit secrets")
        print("   Free options: Supabase, Neon, Railway, ElephantSQL")
        st.warning("⚠️ Database not connected. Add DATABASE_URL to Streamlit secrets to enable data persistence.")
        return None, False
    
    try:
        print(f"🔌 Attempting PostgreSQL connection to: {db_url.split('@')[1] if '@' in db_url else 'hidden'}")
        
        # Fix for Supabase IPv6 issue: Force IPv4 by replacing hostname with pooler
        # Supabase IPv6 addresses often fail on certain networks
        if 'supabase.co' in db_url and 'db.' in db_url:
            # Replace db.xxx.supabase.co with aws-0-us-east-1.pooler.supabase.com or use IPv4 mode
            # Better approach: Add connect_timeout and options to force IPv4
            print("🔧 Using Supabase-optimized connection settings (IPv4 mode)")
            conn = psycopg2.connect(
                db_url,
                connect_timeout=10,
                options='-c statement_timeout=30000'
            )
        else:
            # Connect to PostgreSQL
            conn = psycopg2.connect(db_url)
        
        conn.autocommit = False  # Use transactions
        
        print("✅ PostgreSQL connection established!")
        
        # Create tables if they don't exist
        with conn.cursor() as cur:
            print("📋 Creating tables if not exist...")
            
            # Resumes table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    text TEXT,
                    chunks JSONB,
                    entities JSONB,
                    technical_skills JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Analyses table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id SERIAL PRIMARY KEY,
                    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
                    jd_text TEXT,
                    plan JSONB,
                    profile JSONB,
                    coverage JSONB,
                    cue_alignment JSONB,
                    final_analysis JSONB,
                    semantic_score REAL,
                    coverage_score REAL,
                    llm_fit_score REAL,
                    final_score REAL,
                    fit_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_resumes_email ON resumes(email);
                CREATE INDEX IF NOT EXISTS idx_resumes_created ON resumes(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_analyses_resume ON analyses(resume_id);
            """)
            
        conn.commit()
        print("✅ PostgreSQL connected successfully!")
        print("📊 Database ready with tables: resumes, analyses")
        
        # Beautiful fade-out success message
        st.markdown("""
        <style>
        @keyframes databaseFadeOut {
            0% { opacity: 0; transform: translateY(-20px); }
            10% { opacity: 1; transform: translateY(0); }
            85% { opacity: 1; transform: translateY(0); }
            100% { opacity: 0; transform: translateY(-10px); }
        }
        </style>
        <div style="
            position: fixed;
            top: 20px;
            right: 30px;
            z-index: 10000;
            background: linear-gradient(135deg, rgba(16,185,129,0.95), rgba(5,150,105,0.95));
            color: white;
            padding: 15px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(16,185,129,0.4), 0 0 50px rgba(16,185,129,0.25);
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            border: 2px solid rgba(255,255,255,0.3);
            backdrop-filter: blur(10px);
            animation: databaseFadeOut 4s ease-in-out forwards;
        ">
            <span style="font-size: 20px;">💾</span>
            <span>Database Connected!</span>
        </div>
        """, unsafe_allow_html=True)
        
        return conn, True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        st.error(f"❌ Database connection failed: {str(e)[:200]}")
        st.info("💡 Check your DATABASE_URL in Streamlit secrets. Format: `postgresql://user:password@host:port/dbname`")
        return None, False

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
    """
    IMPROVED global semantic similarity: fair to good candidates.
    Uses top-k averaging without over-penalizing well-matched resumes.
    """
    if resume_embs is None or len(resume_embs)==0: 
        return 0.0
    try:
        job_vec = embedder.encode(jd_text, convert_to_numpy=True, normalize_embeddings=True)
        if job_vec.ndim>1: 
            job_vec = job_vec[0]
        sims = np.dot(resume_embs, job_vec)
        if sims.size == 0: 
            return 0.0
        
        # Use top-8 chunks for balance (focused, not too generous)
        k = min(8, sims.size)
        topk = np.sort(sims)[-k:]
        
        # Weighted average: emphasize very top chunks
        if k > 1:
            weights = np.linspace(0.7, 1.0, k)  # Smoother weighting
            score = float(np.average(topk, weights=weights))
        else:
            score = float(np.mean(topk))
        
        # IMPROVED: Softer calibration (1.0 factor = no penalty)
        # This allows genuinely good semantic matches to score high
        calibrated = score * 1.0  # No harsh calibration factor
        
        return float(np.clip(calibrated, 0.0, 1.0))
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

def contains_atom(atom, text_tokens, full_text=""):
    """
    Robust detection with multiple strategies:
    1. Exact match in full text (case-insensitive)
    2. All tokens present (subset matching)
    3. Fuzzy match for compound terms (60% threshold)
    4. Common abbreviations and variations
    """
    a = normalize_text(atom)
    if len(a) < 2: return False
    
    # Strategy 1: Exact substring match in full text
    if full_text:
        normalized_full = normalize_text(full_text)
        if a in normalized_full:
            return True
    
    # Strategy 2: Extract requirement tokens
    a_tok = set(re.findall(r'[a-z0-9][a-z0-9+.#-]*', a))
    if not a_tok: return False
    
    # Strategy 3: All tokens present (strict match)
    if a_tok.issubset(text_tokens):
        return True
    
    # Strategy 4: Fuzzy match for compound terms (lowered to 60% for better recall)
    if len(a_tok) > 1:
        matched = sum(1 for t in a_tok if t in text_tokens)
        match_ratio = matched / len(a_tok)
        if match_ratio >= 0.6:  # 60% threshold
            return True
    
    # Strategy 5: Common tech abbreviations and variations
    # e.g., "ai" matches "artificial intelligence", "ml" matches "machine learning"
    tech_expansions = {
        'ai': ['artificial', 'intelligence'],
        'ml': ['machine', 'learning'],
        'dl': ['deep', 'learning'],
        'nlp': ['natural', 'language', 'processing'],
        'cv': ['computer', 'vision'],
        'db': ['database'],
        'api': ['application', 'programming', 'interface'],
        'ci': ['continuous', 'integration'],
        'cd': ['continuous', 'deployment'],
        'devops': ['development', 'operations'],
        'aws': ['amazon', 'web', 'services'],
        'gcp': ['google', 'cloud', 'platform'],
        'k8s': ['kubernetes'],
    }
    
    for token in a_tok:
        if token in tech_expansions:
            expansion_words = tech_expansions[token]
            if any(word in text_tokens for word in expansion_words):
                return True
    
    return False

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

    # STRICT filtering: Remove all useless/generic words and phrases
    generic = ATOM_GENERIC_TOKENS
    blocked_phrases = ATOM_BLOCK_PHRASES

    filtered = []
    for c in cands:
        if not c:
            continue
        if any(phrase in c for phrase in blocked_phrases):
            continue
        tokens = c.split()
        meaningful = [t for t in tokens if t not in generic]
        if not meaningful:
            continue
        if len(meaningful) == 1 and meaningful[0] in ATOM_WEAK_SINGLE:
            continue
        if tokens and tokens[0] in ATOM_LEADING_ADJECTIVES:
            continue
        filtered.append(c)
    
    freq = Counter(filtered)
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

# --- ULTRA-STRICT ATOM VALIDATION FILTERS ---
# These lists have been expanded and optimized to eliminate ALL gibberish

ATOM_GENERIC_TOKENS = set([
    # Experience/skill descriptors (CRITICAL - must be very inclusive)
    "experience","experiences","experienced","skill","skills","skilled","tools","tool","technologies",
    "technology","knowledge","knowledgeable","projects","project","responsibilities","responsibility",
    "requirements","requirement","required","prefer","preferred","preferably","requirements",
    # Job roles (too generic - EXPANDED)
    "engineer","engineering","developer","development","analyst","analysis","internship","intern",
    "fresher","graduate","undergraduate","candidate","candidates","professional","professionals",
    "programmer","programming","designer","designing","architect","architecting","lead","leader",
    "manager","management","supervisor","associate","junior","senior","executive","director",
    # Qualifiers (STRICT - added more)
    "strong","stronger","strongest","good","better","best","excellent","exceptional","outstanding",
    "ability","abilities","able","capable","proficient","proficiency","competent","competency",
    "familiar","familiarity","comfortable","understanding","understands","comprehension",
    "adequate","adequate","sufficient","necessary","basic","fundamental","keen","expert","novice",
    # Action verbs (COMPREHENSIVE)
    "work","working","worked","team","teams","teaming","communication","communicate","communicating",
    "problem","problems","solving","solve","solved","teamwork","leadership","lead","leading",
    "management","manage","managing","managed","collaborate","collaboration","collaborating",
    "develop","developing","developed","design","designing","designed","build","building","built",
    "create","creating","created","implement","implementing","implemented","maintain","maintaining",
    "support","supporting","supported","help","helping","helped","assist","assisting","assisted",
    "drive","driving","driven","track","tracking","tracked","monitor","monitoring","monitored",
    "report","reporting","reported","analyze","analyzing","analyzed","analyse","analysing","analysed",
    "evaluate","evaluating","evaluated","assess","assessing","assessed","review","reviewing","reviewed",
    "test","testing","tested","ensure","ensuring","ensured","provide","providing","provided",
    "handle","handling","manage","manage","coordinate","use","using","apply","applying","handle",
    # Generic concepts (EXPANDED - more noise terms)
    "nice","have","having","foundation","foundations","basics","basic","understanding","concept",
    "concepts","process","processes","practice","practices","methodology","methodologies","principles",
    "principle","background","backgrounds","exposure","working","knowledge","competency","competencies",
    "capability","capabilities","qualification","qualifications","plus","bonus","ideal","ideally",
    "requirement","requirement","desirable","useful","helpful","important","need","needs","necessary",
    # Time/measurement (STRICT isolation)
    "year","years","month","months","level","levels","degree","minimum","maximum","at","least",
    "circa","period","duration","time","date","range","window","around","approximately",
    # Connectors/prepositions (EXTENSIVE - all noise)
    "with","without","using","use","used","via","through","across","within","including","such","like",
    "related","relevant","appropriate","suitable","equivalent","similar","other","others","various",
    "multiple","several","any","all","some","both","either","neither","each","every","general",
    "and","or","but","nor","yet","so","in","on","at","by","to","from","for","during","before","after",
    "as","of","into","out","up","down","over","under","above","below","between","among","about",
    # Weak descriptors
    "thing","things","stuff","etc","etc","otherwise","example","examples","illustration",
    "instance","including","component","element","aspect","feature","characteristic","trait",
    # Negations/exclusions
    "not","no","neither","non","un","im","ir","dis","de"
])

ATOM_BLOCK_PHRASES = {
    # Soft skill phrases - EXHAUSTIVE
    "nice to have","nice-to-have","nice to know","good to have","good-to-have","would be nice",
    "good knowledge","strong knowledge","strong foundation","solid foundation","deep understanding",
    "computer foundations","computer foundation","soft skills","strong communication","interpersonal skills",
    "good communication","excellent communication","communication skills","problem solving skills",
    "problem-solving skills","analytical skills","critical thinking","attention to detail",
    "leadership skills","teamwork skills","collaborative","collaboration","team player",
    # Generic requirement phrases - EXHAUSTIVE
    "experience with","experience in","knowledge of","understanding of","familiarity with",
    "exposure to","working knowledge","hands-on experience","practical experience","proven experience",
    "ability to","able to","capable of","proficiency in","proficient in","competency in","skilled in",
    "expertise in","background in","track record","demonstrated ability","strong understanding",
    "some experience","basic knowledge","fundamental understanding","working familiarity",
    # Job responsibilities (not skills) - EXPANDED
    "responsible for","work with","collaborate with","partner with","interact with","communicate with",
    "develop and","design and","build and","create and","implement and","maintain and","support and",
    "work closely","team environment","fast-paced environment","dynamic environment","agile environment",
    "must be able to","should be able to","required to","expected to","responsible to",
    # Vague qualifiers - EXHAUSTIVE
    "preferred qualifications","nice to haves","bonus points","plus points","additional skills",
    "good understanding","solid grasp","thorough understanding","comprehensive knowledge",
    "general knowledge","basic understanding","foundational knowledge","core concepts",
    "advanced understanding","deep knowledge","extensive experience","broad background",
    # More generic phrases
    "familiar with","basic familiarity","general familiarity","some knowledge of",
    "working in","working on","experience in","background in","training in",
    "introduction to","exposure to","introduction","familiarity","minimum knowledge",
    "basic skill","intermediate skill","advanced skill","expert level","mastery of",
    "can demonstrate","able to demonstrate","proven ability to show",
    "will be required","is required","must have","should have","nice to have",
    "highly desirable","would be beneficial","helpful to have","beneficial to have",
    "key skill","key competency","core skill","primary skill","secondary skill",
    "important role","critical role","essential role","important function"
}

ATOM_WEAK_SINGLE = {
    # EXPANDED - ALL single weak tokens
    "foundation","foundations","knowledge","understanding","experience","skill","skills","skillset",
    "competency","competencies","capability","capabilities","background","exposure","proficiency",
    "familiarity","expertise","qualification","qualifications","certification","certifications",
    "training","education","degree","masters","bachelor","phd","diploma","course","courses",
    "tool","tools","technology","technologies","technique","techniques","method","methods",
    "ability","abilities","trait","traits","characteristic","characteristics","competency",
    "requirement","requirements","specification","specifications","attribute","attributes",
    "strength","strengths","weakness","weaknesses","advantage","disadvantages",
    "area","areas","domain","domains","field","fields","practice","practices",
    "role","roles","position","positions","level","levels","tier","tiers",
    "type","types","category","categories","class","classes","group","groups",
    "aspect","aspects","element","elements","component","components","feature","features",
    "skill","skills","duty","duties","function","functions","responsibility","responsibilities",
    "item","items","thing","things","stuff","matter","matters","subject","subjects"
}

ATOM_LEADING_ADJECTIVES = {
    # EXPANDED - ALL qualifying adjectives
    "strong","good","excellent","basic","advanced","intermediate","solid","sound","robust",
    "deep","thorough","comprehensive","extensive","broad","general","specific","detailed",
    "proven","demonstrated","hands-on","practical","theoretical","applied","relevant","appropriate",
    "preferred","ideal","perfect","optimal","suitable","fit","fitting","appropriate",
    "better","best","superior","inferior","poor","weak","weak","strong","powerful",
    "fundamental","core","central","primary","secondary","main","major","minor",
    "essential","critical","crucial","vital","important","necessary","optional","required",
    "new","old","modern","legacy","recent","current","latest","outdated",
    "simple","complex","complicated","easy","difficult","hard","straightforward",
    "effective","efficient","productive","reliable","stable","consistent",
    "relevant","irrelevant","applicable","inapplicable","suitable","unsuitable"
}

def _detect_gibberish(s: str) -> bool:
    """
    Multi-pass gibberish detector.
    Returns True if atom is gibberish, False if it's likely valid.
    """
    # Too short
    if len(s) < 2:
        return True
    
    # All numbers or special chars
    if not any(c.isalpha() for c in s):
        return True
    
    # Single letter repeated
    if len(set(s.replace(" ", ""))) <= 2:
        return True
    
    # Too many special chars
    special_count = sum(1 for c in s if not c.isalnum() and c != " ")
    if special_count > len(s) * 0.5:
        return True
    
    # Repeated words (noise like "and and")
    words = s.split()
    if len(words) > 1 and words[0] == words[-1]:
        return True
    
    return False

def _tokenize_atom(atom: str):
    return re.findall(r"[a-z0-9][a-z0-9+.#-]*", normalize_text(atom))

def _is_valid_atom(atom: str):
    """
    Balanced validation: Filter gibberish while preserving valid technical terms.
    Uses pattern matching and heuristics instead of hardcoded lists.
    """
    s = normalize_text(atom)
    
    # ===== BASIC SANITY CHECKS =====
    if len(s) < 2 or len(s) > 60:
        return False
    if _detect_gibberish(s):
        return False
    if any(phrase in s for phrase in ATOM_BLOCK_PHRASES):
        return False
    
    tokens = _tokenize_atom(s)
    if not tokens:
        return False
    
    # ===== MEANINGFUL TOKEN CHECK =====
    meaningful = [t for t in tokens if t not in ATOM_GENERIC_TOKENS]
    
    # Must have at least one non-generic token
    if not meaningful:
        return False
    
    # ===== TECHNICAL HEURISTICS (pattern-based, not list-based) =====
    
    # Single token validation
    if len(meaningful) == 1:
        token = meaningful[0]
        
        # Reject if in weak list
        if token in ATOM_WEAK_SINGLE:
            return False
        
        # Accept if has technical indicators (numbers, caps, common patterns)
        # Examples: python3, AWS, k8s, C++, .NET, Node.js
        if any([
            any(c.isdigit() for c in token),  # Has numbers (python3, angular17, java11)
            any(c.isupper() for c in atom),  # Has uppercase (AWS, GCP, REST, API, SQL)
            '+' in atom or '#' in atom or '.' in atom,  # C++, C#, Node.js
            token.endswith('js') or token.endswith('sql'),  # JavaScript, MySQL
            token in {'api', 'rest', 'graphql', 'sql', 'nosql', 'oop', 'tdd', 'ci', 'cd', 'ml', 'ai', 'nlp'},
            len(token) <= 4 and token.isalpha(),  # Short acronyms (AWS, GCP, git, npm)
        ]):
            return True
        
        # Accept if matches common tech patterns
        tech_patterns = [
            r'.*script$',  # JavaScript, TypeScript
            r'.*sql$',     # MySQL, PostgreSQL
            r'.*db$',      # MongoDB, DynamoDB
            r'.*py$',      # NumPy, SciPy
            r'^[a-z]+\d+$',  # python3, java11, react18
        ]
        if any(re.match(pattern, token) for pattern in tech_patterns):
            return True
        
        # Reject single generic tokens (unless matched above)
        return False
    
    # ===== MULTI-TOKEN VALIDATION =====
    # Multiple meaningful tokens - more lenient (likely compound skills)
    
    # For multi-token phrases, check if they're meaningful compound skills
    # Examples: "react native", "machine learning", "rest api", "data structures"
    
    # Accept if has experience/year qualifiers (e.g., "5+ years python")
    if any(re.search(r'\d+\s*(year|yr|month|mo)', s) for s in [atom, s]):
        return True
    
    # Accept if has technical suffixes/prefixes
    technical_patterns = [
        r'.*script$',      # javascript, typescript
        r'.*sql$',         # mysql, postgresql
        r'.*db$',          # mongodb, dynamodb  
        r'.*py$',          # numpy, scipy
        r'.*js$',          # reactjs, vuejs, nodejs
        r'.*\.net$',       # asp.net
        r'^micro.*',       # microservices
        r'^web.*',         # web development, websocket
        r'^data.*',        # data science, data structures
        r'^full.*stack$',  # full stack
        r'^front.*end$',   # front end
        r'^back.*end$',    # back end
    ]
    
    if any(re.match(pattern, s, re.IGNORECASE) for pattern in technical_patterns):
        return True
    
    # Accept if contains numbers (version numbers, year requirements)
    if any(c.isdigit() for c in s):
        return True
    
    # Accept if contains uppercase in original (AWS, REST, SQL, API, CI/CD)
    if any(c.isupper() for c in atom):
        return True
    
    # Accept if contains special chars indicating tech (C++, C#, .NET)
    if any(char in atom for char in ['+', '#', '.']):
        return True
    
    # Accept compound phrases with 2-4 meaningful tokens
    # These are likely legitimate compound skills
    if 2 <= len(meaningful) <= 4:
        # Reject if too many adjectives
        adj_count = sum(1 for t in tokens if t in ATOM_LEADING_ADJECTIVES)
        if adj_count / max(len(tokens), 1) > 0.5:
            return False
        return True
    
    # Accept single meaningful tokens that are short (likely acronyms)
    if len(meaningful) == 1 and len(meaningful[0]) <= 5:
        return True
    
    return True  # Default to accepting if passed all filters above

def _canonical_atom(atom: str, nlp=None):
    """
    Create canonical form for deduplication, merging abbreviations with full forms.
    Examples: 'OS' and 'Operating Systems' → same canonical
    """
    s = normalize_text(atom)
    if not s:
        return ""
    
    # Common tech abbreviation mappings (for deduplication)
    abbreviation_map = {
        # CS Fundamentals
        'os': 'operating system',
        'operating systems': 'operating system',
        'dbms': 'database management system',
        'database management systems': 'database management system',
        'cn': 'computer network',
        'computer networks': 'computer network',
        'ds': 'data structure',
        'data structures': 'data structure',
        'algo': 'algorithm',
        'algorithms': 'algorithm',
        'oop': 'object oriented programming',
        'oops': 'object oriented programming',
        'object oriented': 'object oriented programming',
        
        # Cloud & DevOps
        'aws': 'amazon web services',
        'amazon web services': 'amazon web services',
        'gcp': 'google cloud platform',
        'google cloud': 'google cloud platform',
        'k8s': 'kubernetes',
        'ci cd': 'continuous integration',
        'ci/cd': 'continuous integration',
        
        # Databases
        'postgres': 'postgresql',
        'postgresql': 'postgresql',
        'mongo': 'mongodb',
        'mongodb': 'mongodb',
        
        # Languages
        'js': 'javascript',
        'javascript': 'javascript',
        'ts': 'typescript',
        'typescript': 'typescript',
        'py': 'python',
        
        # Frameworks
        'reactjs': 'react',
        'react.js': 'react',
        'nodejs': 'node',
        'node.js': 'node',
        'vuejs': 'vue',
        'vue.js': 'vue',
        
        # APIs
        'rest api': 'rest',
        'restful': 'rest',
        'rest apis': 'rest',
        'graphql api': 'graphql',
        
        # ML/AI
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'nlp': 'natural language processing',
        'cv': 'computer vision',
    }
    
    # Check if atom maps to a canonical form
    if s in abbreviation_map:
        return abbreviation_map[s]
    
    # Use NLP lemmatization for other terms
    if nlp is not None:
        try:
            doc = nlp(s)
            lemmas = [t.lemma_.lower() for t in doc if re.match(r"[a-z0-9][a-z0-9+.#-]*", t.lemma_.lower())]
            canned = " ".join(lemmas)
            if canned and canned in abbreviation_map:
                return abbreviation_map[canned]
            if canned:
                return canned
        except Exception:
            pass
    
    tokens = _tokenize_atom(s)
    canonical = " ".join(tokens)
    
    # Final check if tokenized form maps to canonical
    if canonical in abbreviation_map:
        return abbreviation_map[canonical]
    
    return canonical

def refine_atom_list(atoms, nlp=None, reserved_canonicals=None, limit=50):
    """
    Refine and deduplicate atoms while preserving ALL valid requirements.
    Increased limit to avoid losing requirements.
    """
    reserved = set(reserved_canonicals or [])
    best = {}
    order = []
    for idx, atom in enumerate(atoms):
        if not isinstance(atom, str):
            continue
        atom = normalize_text(atom)
        if not _is_valid_atom(atom):
            continue
        canonical = _canonical_atom(atom, nlp)
        if not canonical or canonical in reserved:
            continue
        current = best.get(canonical)
        if current is None:
            best[canonical] = {"value": atom, "index": idx}
            order.append(canonical)
        elif len(atom) < len(current["value"]):
            current["value"] = atom
    refined = [best[key]["value"] for key in order[:limit]]
    reserved.update(order[:limit])
    return refined, reserved

def evaluate_requirement_coverage(must_atoms, nice_atoms, resume_text, resume_chunks, embedder, model=None,
                                   faiss_index=None, strict_threshold=0.85, partial_threshold=0.70,
                                   nlp=None, jd_text=""):
    """
    Clean, accurate requirement coverage analysis with VERY STRICT thresholds:
    1. Use semantic search to find relevant resume sections for each requirement
    2. LLM verifies if requirement is actually met based on evidence
    3. Score based on: presence (yes/no) + confidence (0-1) + evidence quality
    
    Thresholds (very strict for accurate differentiation):
    - Strict match: ≥0.85 (was 0.80) - Very high bar for full credit
    - Partial match: ≥0.70 (was 0.65) - High bar for partial credit
    - Weak match: ≥0.55 (was 0.50) - Minimum for any credit
    
    No random adjustments, no fingerprints, just accurate matching.
    """
    
    # Step 1: Encode resume chunks for semantic search
    chunk_embs = None
    if resume_chunks and embedder:
        try:
            chunk_embs = embedder.encode(resume_chunks, convert_to_numpy=True, normalize_embeddings=True)
            if chunk_embs.ndim == 1:
                chunk_embs = chunk_embs.reshape(1, -1)
        except Exception:
            chunk_embs = None

    def get_best_resume_evidence(requirement, top_k=5):
        """
        Find the most relevant resume sections for this requirement.
        Uses hybrid approach: semantic search + keyword matching for better accuracy.
        """
        if not requirement:
            return [], 0.0
        
        evidence = []
        similarities = []
        keyword_boost_applied = False
        
        # Helper: Check if requirement keywords exist in text
        def has_keyword_match(text, req):
            """Check for keyword/phrase match with variations."""
            text_lower = text.lower()
            req_lower = req.lower()
            
            # Direct match
            if req_lower in text_lower:
                return True
            
            # Check for abbreviation/full form matches
            abbrev_variants = {
                'operating system': ['operating system', 'os ', ' os', 'os,', 'os.', 'os)', 'os/'],
                'database management': ['dbms', 'database management', 'database systems'],
                'computer network': ['computer network', 'networking', ' cn ', 'cn,', 'cn.'],
                'data structure': ['data structure', 'ds ', ' ds,', 'ds.'],
                'object oriented': ['oop', 'object oriented', 'object-oriented'],
                'aws': ['aws', 'amazon web service'],
                'kubernetes': ['kubernetes', 'k8s'],
                'javascript': ['javascript', 'js ', ' js,', 'js.'],
                'typescript': ['typescript', 'ts '],
                'postgresql': ['postgresql', 'postgres'],
                'mongodb': ['mongodb', 'mongo'],
            }
            
            # Check variants
            for full_form, variants in abbrev_variants.items():
                if full_form in req_lower:
                    if any(v in text_lower for v in variants):
                        return True
            
            # Check individual important words (for compound requirements)
            req_words = [w for w in req_lower.split() if len(w) > 2]
            if len(req_words) >= 2:
                # For multi-word requirements, check if most words are present
                matches = sum(1 for w in req_words if w in text_lower)
                if matches >= len(req_words) * 0.6:  # 60% of words present
                    return True
            
            return False
        
        # Use FAISS if available (faster)
        if faiss_index is not None and resume_chunks and embedder:
            try:
                results = retrieve_relevant_context(requirement, faiss_index, resume_chunks, embedder, top_k=top_k)
                for text, sim in results:
                    sim = float(np.clip(sim, 0.0, 1.0))
                    
                    # Boost similarity if keyword match found
                    if has_keyword_match(text, requirement):
                        sim = min(0.95, sim + 0.30)  # +30% boost, cap at 0.95
                        keyword_boost_applied = True
                    
                    evidence.append({"text": text[:300], "similarity": round(sim, 3)})
                    similarities.append(sim)
            except Exception:
                pass
        
        # Fallback to direct embedding comparison
        elif chunk_embs is not None and embedder and resume_chunks:
            try:
                req_emb = embedder.encode(requirement, convert_to_numpy=True, normalize_embeddings=True)
                if req_emb.ndim > 1:
                    req_emb = req_emb[0]
                
                sims = np.dot(chunk_embs, req_emb)
                top_indices = np.argsort(sims)[-top_k:][::-1]
                
                for idx in top_indices:
                    if 0 <= idx < len(resume_chunks):
                        sim = float(np.clip(sims[idx], 0.0, 1.0))
                        
                        # Boost similarity if keyword match found
                        if has_keyword_match(resume_chunks[idx], requirement):
                            sim = min(0.95, sim + 0.30)  # +30% boost
                            keyword_boost_applied = True
                        
                        if sim > 0.3:  # Only include relevant matches
                            evidence.append({"text": resume_chunks[idx][:300], "similarity": round(sim, 3)})
                            similarities.append(sim)
            except Exception:
                pass
        
        # Additional keyword search if semantic search fails
        if not similarities or max(similarities) < 0.50:
            # Search entire resume text for keyword matches
            for chunk in (resume_chunks or []):
                if has_keyword_match(chunk, requirement):
                    # Found keyword match that semantic search missed
                    boosted_sim = 0.70  # Assign decent similarity for keyword match
                    if chunk[:300] not in [e["text"] for e in evidence]:
                        evidence.append({"text": chunk[:300], "similarity": round(boosted_sim, 3)})
                        similarities.append(boosted_sim)
                        keyword_boost_applied = True
                    if len(evidence) >= top_k:
                        break
        
        max_sim = max(similarities) if similarities else 0.0
        return evidence[:top_k], round(max_sim, 3)

    def calculate_initial_score(requirement, max_similarity):
        """Calculate preliminary score based on semantic similarity with VERY STRICT thresholds."""
        if max_similarity >= strict_threshold:  # ≥0.85
            return 0.85  # Strong match - very high bar
        elif max_similarity >= partial_threshold:  # ≥0.70
            return 0.60  # Partial match - high bar
        elif max_similarity >= 0.55:  # ≥0.55 (was 0.50)
            return 0.35  # Weak match - minimum threshold raised
        else:
            return 0.0  # No match

    # Step 2: Analyze each requirement
    def analyze_requirements(atoms, req_type):
        """Analyze a list of requirements (must-have or nice-to-have)."""
        details = {}
        llm_queue = []
        
        for atom in atoms:
            evidence, max_sim = get_best_resume_evidence(atom)
            initial_score = calculate_initial_score(atom, max_sim)
            
            detail = {
                "req_type": req_type,
                "similarity": max_sim,
                "max_similarity": max_sim,
                "resume_contexts": evidence,
                "jd_context": {"text": "", "similarity": 0.0},  # Simplified - focus on resume evidence
                "pre_llm_score": initial_score,
                "score": initial_score,
                "llm_present": False,
                "llm_confidence": 0.0,
                "llm_rationale": "",
                "llm_evidence": ""
            }
            details[atom] = detail
            
            # Queue for LLM verification if model available and evidence found
            if model and evidence:
                llm_queue.append({
                    "requirement": atom,
                    "req_type": req_type,
                    "resume_evidence": evidence,
                    "max_similarity": max_sim
                })
        
        return details, llm_queue

    must_details, must_queue = analyze_requirements(must_atoms, "must-have")
    nice_details, nice_queue = analyze_requirements(nice_atoms, "nice-to-have") if nice_atoms else ({}, [])

    # Step 3: LLM verification for accurate presence detection
    if model and (must_queue or nice_queue):
        all_queue = must_queue + nice_queue
        llm_results = llm_verify_requirements_clean(model, all_queue, resume_text)
        
        # Update details with LLM verdicts
        for atom, detail in {**must_details, **nice_details}.items():
            verdict = llm_results.get(atom)
            if not verdict:
                continue
            
            present = verdict.get("present", False)
            confidence = float(verdict.get("confidence", 0.0))
            confidence = max(0.0, min(1.0, confidence))
            
            detail["llm_present"] = present
            detail["llm_confidence"] = confidence
            detail["llm_rationale"] = verdict.get("rationale", "")
            detail["llm_evidence"] = verdict.get("evidence", "")
            
            # Calculate final score using STRICT algorithm
            if present:
                # Skill is present - score based on confidence and evidence quality
                # Range: 0.55 to 1.0 (stricter base)
                base_score = 0.55  # Lowered from 0.60
                confidence_bonus = 0.45 * confidence  # Increased range (was 0.40)
                detail["score"] = base_score + confidence_bonus
                
                # Boost for strong evidence (high semantic similarity) - stricter thresholds
                if detail["max_similarity"] >= 0.90:
                    detail["score"] = min(1.0, detail["score"] * 1.12)  # 12% boost for very strong
                elif detail["max_similarity"] >= 0.85:
                    detail["score"] = min(1.0, detail["score"] * 1.08)  # 8% boost (was 10%)
                elif detail["max_similarity"] >= 0.75:
                    detail["score"] = min(1.0, detail["score"] * 1.04)  # 4% boost (was 5%)
                    
            else:
                # Skill is absent - stricter penalties
                if confidence >= 0.85:  # Raised from 0.8
                    # Highly confident it's missing - zero points
                    detail["score"] = 0.0
                elif confidence >= 0.70:  # Raised from 0.6
                    # Likely missing - very small residual score
                    detail["score"] = 0.05  # Reduced from 0.10
                elif confidence >= 0.50:  # Raised from 0.4
                    # Uncertain - minimal benefit of doubt
                    detail["score"] = 0.20  # Reduced from 0.25
                else:
                    # Low confidence in absence - maybe present but unclear
                    # Use semantic similarity as tiebreaker (more conservative)
                    detail["score"] = min(0.35, detail["pre_llm_score"] * 0.7)  # Reduced from 0.40 and 0.8

    # Step 4: Calculate overall coverage with sophisticated weighting
    must_scores = [d["score"] for d in must_details.values()]
    nice_scores = [d["score"] for d in nice_details.values()]

    # Must-have coverage: strict average (all must be met)
    must_coverage = float(np.mean(must_scores)) if must_scores else 0.0
    
    # Nice-to-have coverage: more forgiving (bonus, not required)
    nice_coverage = float(np.mean(nice_scores)) if nice_scores else 1.0
    
    # Apply penalty if too many must-haves are missing
    must_present_count = sum(1 for d in must_details.values() if d.get("llm_present", False))
    must_total = len(must_details) if must_details else 1
    must_fulfillment_rate = must_present_count / must_total
    
    # Penalty factor: STRICT penalties for missing must-haves
    if must_fulfillment_rate < 0.4:  # Less than 40% must-haves present (was 50%)
        penalty_factor = 0.60  # 40% penalty (was 30%)
    elif must_fulfillment_rate < 0.6:  # 40-60% present (was 50-70%)
        penalty_factor = 0.75  # 25% penalty (was 15%)
    elif must_fulfillment_rate < 0.8:  # 60-80% present (new tier)
        penalty_factor = 0.90  # 10% penalty
    else:
        penalty_factor = 1.0  # No penalty only if 80%+ met
    
    # Calculate overall: 80% must-have, 20% nice-to-have (must-haves matter MUCH more)
    if must_scores:
        raw_overall = (0.80 * must_coverage + 0.20 * nice_coverage)  # Changed from 75/25
        overall_coverage = raw_overall * penalty_factor
    else:
        overall_coverage = nice_coverage

    return {
        "overall": round(overall_coverage, 3),
        "must": round(must_coverage, 3),
        "nice": round(nice_coverage, 3),
        "details": {"must": must_details, "nice": nice_details},
        "competencies": {"scores": {}, "evidence": {}}  # Removed complex competency logic
    }

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

def llm_verify_requirements_clean(model, requirements_payload, resume_text):
    """
    Clean LLM verification: Is each requirement present in the resume? Yes/No + Confidence + Evidence.
    No complexity, no gibberish, just accurate matching.
    """
    if not requirements_payload or not model:
        return {}

    results = {}
    batch_size = 10  # Process 10 requirements at a time
    
    # Prepare resume excerpt (limit to avoid token overflow)
    resume_excerpt = resume_text[:4000] if len(resume_text) > 4000 else resume_text
    
    for i in range(0, len(requirements_payload), batch_size):
        batch = requirements_payload[i:i + batch_size]
        
        # Format batch for LLM
        formatted_reqs = []
        for item in batch:
            req_name = item.get("requirement", "")
            evidence_snippets = []
            for ev in (item.get("resume_evidence") or [])[:3]:
                evidence_snippets.append({
                    "text": ev.get("text", "")[:250],
                    "similarity": ev.get("similarity", 0.0)
                })
            
            formatted_reqs.append({
                "requirement": req_name,
                "type": item.get("req_type", ""),
                "evidence": evidence_snippets
            })
        
        prompt = f"""You are an expert technical recruiter analyzing a candidate's resume for specific requirements. Your task is to provide UNIQUE, SPECIFIC assessments for each requirement.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 REQUIREMENTS TO VERIFY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{json.dumps(formatted_reqs, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 CANDIDATE'S RESUME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{resume_excerpt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ASSESSMENT CRITERIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For EACH requirement, provide:

1. **present** (boolean): Is the skill/technology actually used?
   ✅ TRUE if: Mentioned in projects/experience + specific use cases described
   ❌ FALSE if: Not mentioned OR only in skills list without usage proof

2. **confidence** (0.0 to 1.0): Certainty level - BE STRICT!
   - 0.9-1.0: Used extensively in multiple projects with detailed, concrete descriptions
   - 0.7-0.8: Used in at least one substantial project with clear, specific description
   - 0.5-0.6: Mentioned with some context OR in skills list with light project usage
   - 0.3-0.4: Only in skills list without evidence OR weak/indirect mention
   - 0.0-0.2: Not found, vague reference, or only aspirational mention

3. **rationale** (15-25 words): SPECIFIC, UNIQUE explanation
   ⚠️ MUST BE UNIQUE PER REQUIREMENT - Don't use generic phrases!
   ✅ GOOD: "Used Python in E-commerce Platform project for backend APIs and data processing"
   ✅ GOOD: "No PostgreSQL mention; uses MySQL in Project X instead"
   ✅ GOOD: "React expertise shown in Healthcare Dashboard with Redux state management"
   ❌ BAD: "Clearly demonstrated in projects" (too generic)
   ❌ BAD: "Mentioned in resume" (too vague)
   ❌ BAD: "Experience with technology" (not specific)
   
   REQUIRED FORMAT:
   - If present=true: Mention the PROJECT NAME or CONTEXT where used
   - If present=false: State what's missing or what alternative is used instead

4. **evidence** (20-40 words): Direct quote with PROJECT CONTEXT
   - Include the PROJECT/COMPANY NAME if possible
   - Quote the SPECIFIC LINE that proves usage
   - If not present, leave empty ("")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ MATCHING RULES (CRITICAL - READ CAREFULLY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⚠️ ABBREVIATIONS = FULL FORMS (treat as SAME):**
- OS = Operating Systems = Operating System
- DBMS = Database Management Systems = Database Management System
- CN = Computer Networks = Computer Networking
- DS = Data Structures = Data Structure
- OOP = Object Oriented Programming = Object-Oriented
- AWS = Amazon Web Services
- K8s = Kubernetes
- JS = JavaScript
- TS = TypeScript
- PostgreSQL = Postgres
- MongoDB = Mongo

**✅ Accept as matches:**
- Exact/common names: Python=Python
- Abbreviations: If resume has "OS", requirement "Operating Systems" is MET
- Versions: React 18 satisfies "React"
- Specifics: Django REST satisfies "Django"
- Skills list + ANY project usage = PRESENT (confidence 0.5-0.6)
- Skills list + detailed project = PRESENT (confidence 0.7-0.9)

**❌ Reject as non-matches:**
- Wrong tech: MySQL ≠ PostgreSQL
- Vague: "databases" ≠ "MongoDB"
- Insufficient duration: "1 yr Python" ≠ "5+ yrs Python"
- List-only: Skill listed but zero project usage = LOW confidence (0.4-0.5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON (no markdown, no ```json):

{{
  "requirement_name": {{
    "present": true/false,
    "confidence": 0.0-1.0,
    "rationale": "Specific explanation mentioning project/context (15-25 words)",
    "evidence": "Quoted text with project name (if present, else empty)"
  }}
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL ANTI-REPETITION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Each rationale MUST be UNIQUE - no copy-paste explanations
2. MUST mention specific PROJECT NAMES or CONTEXTS from resume
3. NO generic phrases like "demonstrated", "mentioned", "experience with"
4. If skill is absent, explain WHY or what's used INSTEAD
5. Be forensic: cite actual project names, company names, or specific contexts

EXAMPLE OF GOOD (UNIQUE, SPECIFIC) RATIONALES:
- "Python used extensively in E-commerce Platform project for REST API development and data pipelines"
- "No Docker mentioned; deployment appears to be traditional VM-based per DevOps section"
- "Strong React skills evidenced in Healthcare Dashboard project using hooks and context API"
- "AWS mentioned in resume but only S3 storage; no Lambda or serverless experience shown"

BEGIN ANALYSIS:
"""

        try:
            raw = llm_json(model, prompt)
            if not isinstance(raw, dict):
                continue
            
            # Extract results for each requirement in batch
            for item in batch:
                req_name = item.get("requirement", "")
                if not req_name:
                    continue
                
                # Try exact match first
                verdict = raw.get(req_name)
                
                # Try normalized match if exact fails
                if verdict is None:
                    req_norm = normalize_text(req_name)
                    for key, value in raw.items():
                        if normalize_text(key) == req_norm:
                            verdict = value
                            break
                
                if isinstance(verdict, dict):
                    # Extract and validate fields
                    present = bool(verdict.get("present", False))
                    
                    confidence = verdict.get("confidence", 0.0)
                    try:
                        confidence = float(confidence)
                    except:
                        confidence = 0.0
                    confidence = max(0.0, min(1.0, confidence))
                    
                    rationale = str(verdict.get("rationale", "")).strip()
                    evidence = str(verdict.get("evidence", "")).strip()
                    
                    # Clean text: remove repetition, limit length
                    def clean_llm_text(text, max_words=25):
                        if not text:
                            return ""
                        # Remove markdown and code artifacts
                        text = re.sub(r'```\w*', '', text)
                        # Remove repeated words (e.g., "Python Python Python")
                        text = re.sub(r'\b(\w+)(\s+\1\b){2,}', r'\1', text, flags=re.IGNORECASE)
                        # Remove repeated punctuation
                        text = re.sub(r'([.,!?])\1+', r'\1', text)
                        # Normalize whitespace
                        text = re.sub(r'\s+', ' ', text).strip()
                        # Truncate to word limit
                        words = text.split()
                        if len(words) > max_words:
                            text = ' '.join(words[:max_words])
                        return text
                    
                    rationale = clean_llm_text(rationale, max_words=20)
                    evidence = clean_llm_text(evidence, max_words=30)
                    
                    results[req_name] = {
                        "present": present,
                        "confidence": confidence,
                        "rationale": rationale,
                        "evidence": evidence
                    }
                    
        except Exception as e:
            # Skip this batch on error, continue with next
            continue
    
    return results

def llm_verify_requirements(model, requirements_payload, resume_text, jd_text=""):
    """Legacy function - redirects to new clean implementation."""
    return llm_verify_requirements_clean(model, requirements_payload, resume_text)

def llm_verify_requirements_old(model, requirements_payload, resume_text, jd_text=""):
    """
    Cross-verify requirement coverage using curated RAG evidence + JD context.
    Returns a mapping of requirement -> {present, confidence, rationale, evidence}.
    """
    if not requirements_payload:
        return {}

    def _shorten(text, limit=320):
        text = (text or "").strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > limit:
            text = text[:limit-3].rstrip() + "..."
        return text

    results = {}
    batch_size = 8
    resume_excerpt = _shorten(resume_text, 2000)
    jd_excerpt = _shorten(jd_text, 2000)

    for i in range(0, len(requirements_payload), batch_size):
        batch = requirements_payload[i:i + batch_size]
        formatted_batch = []
        for item in batch:
            ctxs = []
            for ctx in (item.get("resume_contexts") or [])[:3]:
                try:
                    sim_val = float(ctx.get("similarity", 0.0))
                except Exception:
                    sim_val = 0.0
                ctxs.append({
                    "similarity": round(sim_val, 3),
                    "text": _shorten(ctx.get("text", ""), 320)
                })

            jd_ctx = item.get("jd_context") or {}
            try:
                max_sim = float(item.get("max_similarity", 0.0))
            except Exception:
                max_sim = 0.0

            formatted_batch.append({
                "requirement": item.get("requirement", ""),
                "req_type": item.get("req_type", ""),
                "max_similarity": round(max_sim, 3),
                "job_description_focus": _shorten(jd_ctx.get("text", ""), 320),
                "resume_evidence": ctxs
            })

        prompt = f"""You are an expert technical recruiter. Your task: Verify if each requirement is satisfied by examining ACTUAL evidence from the candidate's resume.

**REQUIREMENTS TO VERIFY:**
{json.dumps(formatted_batch, indent=2)}

**CANDIDATE'S RESUME:**
{resume_excerpt}

**JOB DESCRIPTION (for context):**
{jd_excerpt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 VERIFICATION METHODOLOGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each requirement, determine:

1. **Is it present?** (true/false)
   - Search resume for EXACT skill/technology name or clear synonyms
   - Check if candidate has USED it in projects/work (not just listed)
   - Verify experience duration meets requirement (if years specified)

2. **How confident are you?** (0.0 to 1.0)
   - 0.9-1.0: Direct mention + concrete project usage + metrics
   - 0.7-0.9: Clear mention + described experience
   - 0.5-0.7: Mentioned but limited details or borderline match
   - 0.3-0.5: Weak/indirect evidence
   - 0.0-0.3: Not found or clearly insufficient

3. **What's the evidence?** (brief, factual)
   - Quote the SPECIFIC line from resume that proves it
   - If absent, state what's missing in 1 sentence
   - Keep rationale under 25 words

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ EXAMPLES OF GOOD VERIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Requirement: "Python"
Resume says: "Built REST APIs using Python and Django for 3 years"
→ present: true, confidence: 0.95, rationale: "3 years Python with Django APIs", evidence: "Built REST APIs using Python and Django"

Requirement: "5+ years AWS"  
Resume says: "2 years experience with AWS Lambda and S3"
→ present: false, confidence: 0.4, rationale: "Has AWS but only 2 years vs 5+ required", evidence: ""

Requirement: "Docker"
Resume says: "Technologies: Git, Jenkins, Kubernetes"
→ present: false, confidence: 0.2, rationale: "No Docker mentioned, only K8s", evidence: ""

Requirement: "React"
Resume says: "Frontend: React 18, TypeScript, Redux. Built 5 production apps"
→ present: true, confidence: 1.0, rationale: "React 18 with 5 production apps", evidence: "Frontend: React 18, TypeScript, Redux"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 MATCHING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Accept as matches:**
- Exact names: "PostgreSQL" matches "PostgreSQL"
- Common abbreviations: "K8s" = "Kubernetes", "JS" = "JavaScript"
- Version variants: "Python 3.11" satisfies "Python 3.9+"
- Framework variations: "Django REST" satisfies "Django"
- Cloud specifics: "AWS Lambda" satisfies both "AWS" and "Lambda"

**Reject as non-matches:**
- Different technologies: "MySQL" ≠ "PostgreSQL"
- Generic categories: "databases" ≠ "MongoDB" (too vague)
- Insufficient years: "2 years Python" ≠ "5+ years Python"
- Listed but not used: Skill in "Technologies" list with no project evidence

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON (no markdown, no explanations):

{{
  "requirement_name": {{
    "present": true or false,
    "confidence": number between 0.0 and 1.0,
    "rationale": "brief factual statement under 25 words",
    "evidence": "direct quote from resume if present=true, empty string if false"
  }}
}}

**CRITICAL:** 
- Base answers ONLY on resume content provided
- Do NOT invent or assume skills
- Do NOT add explanatory text outside JSON
- Keep rationale concise and factual

BEGIN VERIFICATION:
"""

        try:
            raw = llm_json(model, prompt)
        except Exception:
            raw = {}

        if not isinstance(raw, dict):
            continue

        for item in batch:
            req_text = item.get("requirement", "")
            if not req_text:
                continue

            verdict = raw.get(req_text)
            if verdict is None:
                for key, value in raw.items():
                    if normalize_text(key) == normalize_text(req_text):
                        verdict = value
                        break

            if isinstance(verdict, dict):
                present = bool(verdict.get("present"))
                confidence = verdict.get("confidence", verdict.get("confidence_score", 0.0))
                try:
                    confidence = float(confidence)
                except Exception:
                    confidence = 0.0
                confidence = max(0.0, min(1.0, confidence))

                rationale = str(verdict.get("rationale", verdict.get("reason", "")) or "").strip()
                evidence = str(verdict.get("evidence", "") or "").strip()
                
                # Clean gibberish: remove repetitive patterns and truncate long text
                def clean_text(text, max_words=30):
                    if not text:
                        return ""
                    # Remove code artifacts
                    text = text.replace("```", "").replace("json", "").replace("python", "")
                    # Remove common gibberish patterns
                    text = re.sub(r'(\b\w+\b)(\s+\1){3,}', r'\1', text)  # Remove word repetition
                    text = re.sub(r'([^\w\s])\1{2,}', r'\1', text)  # Remove symbol repetition
                    text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
                    # Truncate to reasonable length (keep first sentence if too long)
                    words = text.split()
                    if len(words) > max_words:
                        text = ' '.join(words[:max_words]) + "..."
                    return text
                
                rationale = clean_text(rationale, max_words=25)
                evidence = clean_text(evidence, max_words=30)

                results[req_text] = {
                    "present": present,
                    "confidence": confidence,
                    "rationale": rationale,
                    "evidence": evidence
                }
            elif isinstance(verdict, bool):
                results[req_text] = {
                    "present": bool(verdict),
                    "confidence": 0.5,
                    "rationale": "",
                    "evidence": ""
                }

    return results

def compute_cue_alignment(plan, parsed_resume, profile, embedder, faiss_index=None):
    """Compute cosine-similarity alignment between JD enrichment cues and resume evidence."""
    jd_cues = [c.strip() for c in (plan.get("enrichment_cues") or []) if isinstance(c, str) and c.strip()]
    jd_cues = jd_cues[:25]

    def _collect_strings(values):
        collected = []
        if isinstance(values, list):
            for item in values:
                if isinstance(item, str) and item.strip():
                    collected.append(item.strip())
        return collected

    resume_cue_set = set()

    if isinstance(parsed_resume, dict):
        for skill in _collect_strings(parsed_resume.get("technical_skills")):
            resume_cue_set.add(skill)

    if isinstance(profile, dict):
        resume_cue_set.update(_collect_strings(profile.get("core_skills")))
        resume_cue_set.update(_collect_strings(profile.get("tools")))
        resume_cue_set.update(_collect_strings(profile.get("cloud_experience")))
        resume_cue_set.update(_collect_strings(profile.get("ml_ai_experience")))
        resume_cue_set.update(_collect_strings(profile.get("notable_metrics")))

        projects = profile.get("projects") or []
        if isinstance(projects, list):
            for proj in projects:
                if isinstance(proj, dict):
                    name = proj.get("name")
                    desc = proj.get("description")
                    if isinstance(name, str) and name.strip():
                        resume_cue_set.add(name.strip())
                    if isinstance(desc, str) and desc.strip():
                        resume_cue_set.add(desc.strip())

        summary = profile.get("summary")
        if isinstance(summary, str) and summary.strip():
            resume_cue_set.add(summary.strip())

    resume_cues = [c for c in resume_cue_set if len(c) > 2][:60]

    if not jd_cues or not resume_cues or embedder is None:
        return {
            "jd_cues": jd_cues,
            "resume_cues": resume_cues,
            "alignments": [],
            "average_similarity": 0.0,
            "strong_matches": [],
            "weak_matches": jd_cues
        }

    try:
        jd_embs = embedder.encode(jd_cues, convert_to_numpy=True, normalize_embeddings=True)
        if jd_embs.ndim == 1:
            jd_embs = jd_embs.reshape(1, -1)
        resume_embs = embedder.encode(resume_cues, convert_to_numpy=True, normalize_embeddings=True)
        if resume_embs.ndim == 1:
            resume_embs = resume_embs.reshape(1, -1)
    except Exception:
        return {
            "jd_cues": jd_cues,
            "resume_cues": resume_cues,
            "alignments": [],
            "average_similarity": 0.0,
            "strong_matches": [],
            "weak_matches": jd_cues
        }

    alignments = []
    strong, weak = [], []
    resume_chunks = parsed_resume.get("chunks") if isinstance(parsed_resume, dict) else None

    for idx, cue in enumerate(jd_cues):
        cue_emb = jd_embs[idx]
        sims = np.dot(resume_embs, cue_emb)
        best_idx = int(np.argmax(sims)) if sims.size > 0 else -1
        best_sim = float(np.clip(sims[best_idx], -1.0, 1.0)) if best_idx >= 0 else 0.0
        best_resume_cue = resume_cues[best_idx] if best_idx >= 0 else ""

        resume_context = ""
        if faiss_index is not None and resume_chunks and embedder and best_resume_cue:
            contexts = retrieve_relevant_context(best_resume_cue, faiss_index, resume_chunks, embedder, top_k=1)
            if contexts:
                snippet = re.sub(r'\s+', ' ', contexts[0][0]).strip()
                resume_context = snippet[:257].rstrip() + ("..." if len(snippet) > 260 else "")

        alignments.append({
            "jd_cue": cue,
            "matched_resume_cue": best_resume_cue,
            "similarity": best_sim,
            "resume_context": resume_context
        })

        if best_sim >= 0.70:
            strong.append(cue)
        elif best_sim < 0.40:
            weak.append(cue)

    average_similarity = float(np.mean([a["similarity"] for a in alignments])) if alignments else 0.0

    return {
        "jd_cues": jd_cues,
        "resume_cues": resume_cues,
        "alignments": alignments,
        "average_similarity": average_similarity,
        "strong_matches": strong,
        "weak_matches": weak
    }

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
You are an expert resume analyzer. Extract FACTUAL information ONLY - do not invent or infer.

Return ONLY JSON with:
- summary: 25-35 word summary of candidate's core expertise
- core_skills: Array of 10-18 technical skills actually mentioned (be specific: "Python 3.x", not just "Python")
- projects: Array of objects with {{name, description (15-25 words), impact (metrics if available)}}
- cloud_experience: Array of cloud platforms/services mentioned (AWS Lambda, Azure Functions, etc.)
- ml_ai_experience: Array of ML/AI technologies/frameworks mentioned
- certifications: Array of actual certifications mentioned
- tools: Array of development tools mentioned (Git, Docker, Jenkins, etc.)
- notable_metrics: Array of quantifiable achievements ("increased performance by 40%", "managed team of 5", etc.)
- years_of_experience: Best estimate as integer (count from earliest job to latest)
- education: Array of degrees mentioned

**CRITICAL RULES**:
1. Extract ONLY what is explicitly stated - do NOT infer or add
2. For skills: Include version numbers when present ("React 18", "Java 11")
3. For projects: Focus on technical projects, include tech stack if mentioned
4. For metrics: Extract exact numbers and percentages as stated
5. Avoid generic phrases - be specific
6. If a field has no data, return empty array/null

**EXAMPLES OF GOOD EXTRACTION**:
✅ "Python 3.x, Django REST Framework" → core_skills: ["python 3.x", "django rest framework"]
✅ "Deployed microservices on AWS Lambda and DynamoDB" → cloud_experience: ["aws lambda", "dynamodb"]
✅ "Reduced latency by 35%" → notable_metrics: ["reduced latency by 35%"]

**EXAMPLES OF BAD EXTRACTION** (AVOID):
❌ Adding skills not explicitly mentioned
❌ "Programming" as a skill (too generic)
❌ Inferring years of experience from graduation date (use job history only)

RESUME TEXT:
{full_resume_text[:6000]}

Return ONLY valid JSON. No markdown, no explanations.
"""

def atomicize_requirements_prompt(jd, resume_preview):
    return f"""You are an expert technical recruiter analyzing a job description. Extract ALL requirements in a structured, comprehensive way.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 EXTRACTION CATEGORIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Extract requirements into 4 distinct categories:

1. **hard_skills**: Technical skills, technologies, tools, frameworks
   - Languages: Python, Java, JavaScript, C++, Go, Rust, etc.
   - Frameworks: React, Angular, Django, Flask, Spring Boot, etc.
   - Databases: PostgreSQL, MySQL, MongoDB, Redis, Cassandra, etc.
   - Cloud: AWS, Azure, GCP, specific services (Lambda, S3, EC2, etc.)
   - DevOps: Docker, Kubernetes, Jenkins, CI/CD, Terraform, etc.
   - Tools: Git, Postman, VS Code, JIRA, etc.
   - Concepts: REST API, GraphQL, Microservices, OOP, etc.

2. **fundamentals**: Core CS/IT concepts and foundations
   - DBMS, Operating Systems, Computer Networks, Data Structures
   - Algorithms, System Design, Software Architecture
   - Security principles, Design patterns, etc.

3. **experience**: Years of experience, seniority, specific domains
   - "5+ years Python", "3 years backend development"
   - "Senior level", "Mid-level", "Experience with fintech"
   - Industry experience requirements

4. **qualifications**: Education, certifications, degrees
   - "Bachelor's in CS", "Master's preferred"
   - "AWS Certified", "PMP Certification"
   - Specific degree requirements

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 EXTRACTION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **DO:**
- Extract EVERY specific technology/tool mentioned
- Include common abbreviations (AWS, K8s, JS, etc.)
- Extract version-specific mentions (Python 3.x, React 18, etc.)
- Include compound skills as separate items (Django/Flask → both)
- Keep original casing for proper nouns (React, MongoDB, AWS)
- Extract implicit requirements (mentions "Lambda" → add "AWS")

❌ **DON'T:**
- Include vague qualifiers ("good knowledge", "strong understanding")
- Extract generic words ("experience", "skills", "work")
- Include soft skills here (teamwork, communication) - skip these
- Add items not in the JD
- Be repetitive (don't list "Python" 10 times)

⚠️ **AVOID REDUNDANT ABBREVIATION/FULL FORM DUPLICATES:**
- If JD says "Operating Systems", extract ONLY "Operating Systems" (not both "OS" + "Operating Systems")
- If JD says "OS", extract ONLY "OS" (not both)
- If JD says "DBMS", extract ONLY "DBMS" (not "Database Management Systems" too)
- Exception: If JD explicitly uses BOTH forms, then include both
- Our system automatically maps abbreviations to full forms, so one is enough

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 PRIORITY CLASSIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each category, classify items as MUST-HAVE or NICE-TO-HAVE:

**must**: Required, mandatory, essential
- Keywords: "required", "must have", "essential", "mandatory"
- Core tech stack items
- Minimum experience requirements

**nice**: Preferred, bonus, optional
- Keywords: "preferred", "nice to have", "bonus", "plus"
- Secondary technologies
- "Good to have" items

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Example 1:**
INPUT: "Required: 5+ years Python, strong Django/Flask experience, PostgreSQL, Docker. Core IT fundamentals (DBMS/OS/CN) essential. Bachelor's in CS required. Preferred: AWS, Kubernetes, React."

OUTPUT:
{{
  "hard_skills": {{
    "must": ["Python", "Django", "Flask", "PostgreSQL", "Docker"],
    "nice": ["AWS", "Kubernetes", "React"]
  }},
  "fundamentals": {{
    "must": ["DBMS", "OS", "CN"],
    "nice": []
  }},
  "experience": {{
    "must": ["5+ years Python experience"],
    "nice": []
  }},
  "qualifications": {{
    "must": ["Bachelor's in Computer Science"],
    "nice": []
  }}
}}

Note: Only "DBMS", "OS", "CN" extracted (not full forms) because JD uses abbreviations. Our system handles the mapping automatically.

**Example 2:**
INPUT: "Looking for Full Stack Engineer with React, Node.js, MongoDB. Good understanding of REST APIs, microservices. Experience with AWS Lambda, S3. Agile methodology. Nice to have: TypeScript, GraphQL, Redis."

OUTPUT:
{{
  "hard_skills": {{
    "must": ["React", "Node.js", "Node", "MongoDB", "Mongo", "REST API", "REST", "Microservices", "AWS Lambda", "Lambda", "AWS S3", "S3", "AWS", "Agile"],
    "nice": ["TypeScript", "TS", "GraphQL", "Redis"]
  }},
  "fundamentals": {{
    "must": [],
    "nice": []
  }},
  "experience": {{
    "must": ["Full Stack development experience"],
    "nice": []
  }},
  "qualifications": {{
    "must": [],
    "nice": []
  }}
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 JOB DESCRIPTION TO ANALYZE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{jd[:6000]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL INSTRUCTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Read the ENTIRE job description above
2. Extract EVERY specific technical requirement
3. Be thorough - missing skills hurts accuracy
4. Return ONLY valid JSON (no markdown, no explanations)
5. Use the EXACT structure shown in examples

BEGIN EXTRACTION:
"""

def analysis_prompt(jd, plan, profile, coverage_summary, cue_alignment, global_sem, cov_final):
    must_details = (coverage_summary.get("details") or {}).get("must", {})
    nice_details = (coverage_summary.get("details") or {}).get("nice", {})

    def _pick_atoms(source, threshold_low, threshold_high=None, limit=8):
        picked = []
        for atom, info in source.items():
            score = float(info.get("score", 0.0))
            if threshold_high is None:
                if score >= threshold_low:
                    picked.append(atom)
            else:
                if threshold_low <= score < threshold_high:
                    picked.append(atom)
        return picked[:limit]

    coverage_brief = {
        "must_coverage": round(coverage_summary.get("must", 0.0), 3),
        "nice_coverage": round(coverage_summary.get("nice", 1.0), 3),
        "overall": round(coverage_summary.get("overall", 0.0), 3),
        "must_found": _pick_atoms(must_details, 0.85),
        "must_partial": _pick_atoms(must_details, 0.50, 0.85),
        "must_missing": _pick_atoms(must_details, 0.0, 0.50),
        "nice_found": _pick_atoms(nice_details, 0.85),
        "nice_partial": _pick_atoms(nice_details, 0.50, 0.85),
        "nice_missing": _pick_atoms(nice_details, 0.0, 0.50)
    }

    cue_brief = {
        "average_similarity": round(cue_alignment.get("average_similarity", 0.0), 3),
        "strong_matches": (cue_alignment.get("strong_matches") or [])[:10],
        "weak_matches": (cue_alignment.get("weak_matches") or [])[:10],
        "sample_alignments": (cue_alignment.get("alignments") or [])[:6]
    }

    coverage_json = json.dumps(coverage_brief, indent=2)[:1200]
    cue_json = json.dumps(cue_brief, indent=2)[:1100]
    plan_json = json.dumps(plan, indent=2)[:800]
    profile_json = json.dumps(profile, indent=2)[:1200]

    return f"""You are an ELITE technical recruiter with 15+ years of experience. Conduct a rigorous, evidence-based assessment of this candidate against the job requirements.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 OUTPUT FORMAT (Return ONLY valid JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required JSON keys:
- cultural_fit: string (40-60 words) - Work style, team fit, values alignment
- technical_strength: string (40-60 words) - Technical capability depth & breadth
- experience_relevance: string (40-60 words) - Direct role alignment & seniority
- top_strengths: array of 3-5 specific strengths with evidence
- improvement_areas: array of 2-4 gaps/concerns with specifics
- overall_comment: string (50-80 words) - Concise hiring recommendation
- risk_flags: array of 0-3 critical concerns (or empty if none)
- followup_questions: array of 3-5 targeted interview questions
- fit_score: integer 0-10 (based on framework below)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ SCORING FRAMEWORK (Strict Adherence Required)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Score 9-10 (Exceptional - Top 5%) ⭐⭐⭐⭐⭐:
  ✓ Must-have coverage ≥ 0.85 (85%+ critical requirements met)
  ✓ Semantic similarity ≥ 0.75 (exceptional contextual alignment)
  ✓ Demonstrates depth: multiple relevant projects, measurable impact, recent experience
  ✓ Exceeds requirements: bonus skills present, additional certifications
  ✓ Clear evidence of progression, leadership, or specialized expertise
  ✓ Quantifiable achievements directly relevant to role
  → HIRE: Top-tier candidate, move fast

Score 7-8 (Strong Fit - Top 20%) ⭐⭐⭐⭐:
  ✓ Must-have coverage ≥ 0.70 (70-85% critical requirements)
  ✓ Semantic similarity ≥ 0.60 (strong alignment)
  ✓ Core competencies solid, only minor gaps in secondary areas
  ✓ Relevant experience with some quantifiable achievements
  ✓ Can ramp up quickly with minimal training
  ✓ Good technical foundation with proven track record
  → STRONG CONSIDERATION: Solid candidate, likely to succeed

Score 5-6 (Moderate Fit - Borderline) ⭐⭐⭐:
  ~ Must-have coverage 0.55-0.69 (55-70% critical requirements)
  ~ Semantic similarity 0.50-0.59 (moderate alignment)
  ~ Has foundation but missing several key skills or lacking depth
  ~ May require moderate training/onboarding (2-3 months)
  ~ Experience somewhat relevant but not exact match
  ~ Could work in right circumstances (team support, training budget)
  → PROCEED WITH CAUTION: Interview carefully, assess learning ability

Score 3-4 (Weak Fit - High Risk) ⭐:
  ✗ Must-have coverage 0.40-0.54 (40-55% critical requirements)
  ✗ Semantic similarity 0.35-0.49 (weak alignment)
  ✗ Missing multiple core requirements (>45% gaps)
  ✗ Limited relevant experience or outdated/tangential skills
  ✗ Would require extensive retraining (4-6+ months)
  ✗ Significant risk of failure or slow productivity ramp
  → LIKELY REJECT: Only consider if desperate or unique circumstances

Score 0-2 (Not Viable - Reject) ❌:
  ✗ Must-have coverage < 0.40 (< 40% critical requirements)
  ✗ Semantic similarity < 0.35 (poor alignment)
  ✗ Fundamentally wrong profile for role
  ✗ Lacks basic qualifications (>60% gaps in must-haves)
  ✗ No clear path to success, would need 6+ months training
  ✗ Better fit for different role or seniority level
  → REJECT: Clear mismatch, don't proceed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 MANDATORY SCORE CAPS (Hard Limits - Override Upward)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply these HARD CAPS regardless of other positive factors:

• Must_coverage < 0.25 → MAXIMUM score = 3 (critical failure, >75% gaps)
• Must_coverage < 0.40 → MAXIMUM score = 4 (major gaps, >60% missing)
• Must_coverage < 0.55 → MAXIMUM score = 6 (significant gaps, >45% missing)
• Must_coverage < 0.70 → MAXIMUM score = 7 (noticeable gaps, >30% missing)

Additional Penalties (subtract from base score):
• Both must_coverage < 0.50 AND semantic < 0.50 → Subtract 1.0 point (compound weakness)
• Missing ≥3 critical core technologies (e.g., primary language, main framework, key tool) → Subtract 0.5-1.0 points
• Experience years < 50% of required (e.g., 2 years vs 5+ required) → Subtract 1.0 point
• No quantifiable achievements AND must_coverage < 0.60 → Maximum score = 6
• Semantic similarity < 0.35 (very poor contextual fit) → Subtract 0.8 points

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 EVALUATION DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUANTITATIVE METRICS:
• Semantic Similarity: {global_sem:.3f} (0.0-1.0 scale, higher = better contextual fit)
• Overall Coverage: {cov_final:.3f} (0.0-1.0 scale, weighted must+nice requirements)
• Must-Have Coverage: {coverage_brief['must_coverage']} (critical requirements only)
• Nice-To-Have Coverage: {coverage_brief['nice_coverage']} (bonus skills)

REQUIREMENT ANALYSIS:
• Must-Have Requirements: {coverage_brief.get('must_atoms_count', 0)} total
  - Found: {len(coverage_brief.get('must_found', []))} items
  - Partial: {len(coverage_brief.get('must_partial', []))} items  
  - Missing: {len(coverage_brief.get('must_missing', []))} items
• Nice-To-Have Requirements: {coverage_brief.get('nice_atoms_count', 0)} total
  - Found: {len(coverage_brief.get('nice_found', []))} items

DETAILED COVERAGE BREAKDOWN:
{coverage_json}

CUE ALIGNMENT (Work Style & Context Fit):
• Average Cue Similarity: {cue_brief['average_similarity']} (0.0-1.0 scale)
• Strong Matches: {len(cue_brief.get('strong_matches', []))} cues
• Weak Matches: {len(cue_brief.get('weak_matches', []))} cues
{cue_json}

JOB ANALYSIS PLAN:
{plan_json}

CANDIDATE PROFILE:
{profile_json}

JOB DESCRIPTION EXCERPT:
{jd[:1800]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 ASSESSMENT GUIDELINES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Be SPECIFIC in your analysis:
  • Cite actual technologies/skills found or missing
  • Reference quantifiable achievements from resume
  • Compare experience years against requirements
  • Note recency of technical experience (outdated = red flag)
  • Consider breadth vs depth trade-offs

Avoid VAGUE statements like:
  ❌ "Good technical background"
  ❌ "Seems like a decent fit"
  ❌ "Has some relevant experience"
  
Use CONCRETE statements like:
  ✅ "5 years Python + Django aligns with 3+ years requirement"
  ✅ "Missing Kubernetes and Docker (both required)"
  ✅ "Led 2 production deployments with 40% performance gain"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL REMINDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Output ONLY valid JSON (no markdown, no explanations)
2. Apply scoring framework strictly (don't inflate scores)
3. Ground all statements in provided evidence
4. Be honest about gaps (don't sugarcoat weaknesses)
5. Prioritize must-haves over nice-to-haves
6. Consider both technical skills AND experience relevance

BEGIN ASSESSMENT NOW:
"""

def extract_structured_entities(text, nlp):
    """
    Extract structured entities from resume using spaCy NER and custom patterns.
    Returns: dict with organizations, dates, skills, education, certifications
    """
    doc = nlp(text[:5000])  # Limit to first 5000 chars for efficiency
    
    entities = {
        "organizations": [],
        "dates": [],
        "skills": [],
        "education": [],
        "certifications": [],
        "technologies": []
    }
    
    # Extract named entities
    for ent in doc.ents:
        if ent.label_ == "ORG":
            org = ent.text.strip()
            if len(org) > 2 and org not in entities["organizations"]:
                entities["organizations"].append(org)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text.strip())
    
    # Extract education patterns
    education_patterns = [
        r'\b(bachelor|master|phd|doctorate|b\.?s\.?|m\.?s\.?|m\.?tech|b\.?tech|mba|ph\.?d\.?)\b.*?(?:in|of)\s+([a-z\s]+)',
        r'\b(undergraduate|graduate)\s+(?:degree|program)\s+in\s+([a-z\s]+)',
    ]
    for pattern in education_patterns:
        for match in re.finditer(pattern, text.lower()):
            degree = match.group(0).strip()
            if degree and len(degree) < 100:
                entities["education"].append(degree)
    
    # Extract certification patterns
    cert_keywords = ['certified', 'certification', 'certificate', 'credential']
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in cert_keywords):
            cert = line.strip()
            if 10 < len(cert) < 150:
                entities["certifications"].append(cert)
    
    # Extract technology mentions using dependency parsing
    tech_patterns = [
        r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|kotlin|swift|scala)\b',
        r'\b(react|angular|vue|node\.?js|django|flask|spring|express)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|jenkins|terraform|ansible)\b',
        r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch|cassandra)\b',
        r'\b(machine learning|deep learning|nlp|computer vision|ai|ml|dl)\b',
        r'\b(git|github|gitlab|bitbucket|jira|confluence)\b'
    ]
    
    for pattern in tech_patterns:
        for match in re.finditer(pattern, text.lower()):
            tech = match.group(0).strip()
            if tech and tech not in entities["technologies"]:
                entities["technologies"].append(tech)
    
    # Limit results
    entities["organizations"] = entities["organizations"][:15]
    entities["education"] = list(set(entities["education"]))[:5]
    entities["certifications"] = list(set(entities["certifications"]))[:10]
    entities["technologies"] = list(set(entities["technologies"]))[:30]
    
    return entities

def extract_technical_skills(text, nlp):
    """
    Extract technical skills using advanced NLP: noun chunks + dependency parsing + pattern matching.
    Returns: list of technical skills/tools/frameworks
    """
    doc = nlp(text[:8000])
    skills = set()
    
    # Method 1: Noun phrases that are likely technical skills
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower().strip()
        # Filter for technical-looking noun chunks
        if (2 <= len(chunk_text) <= 40 and 
            not chunk_text.startswith(('the ', 'a ', 'an ')) and
            any(char.isalnum() for char in chunk_text)):
            # Check if contains technical indicators
            tech_indicators = ['system', 'software', 'framework', 'library', 'tool', 'platform', 
                             'language', 'database', 'service', 'api', 'sdk', 'development']
            if any(ind in chunk_text for ind in tech_indicators):
                skills.add(chunk_text)
    
    # Method 2: Extract from "Skills" section if present
    skills_section_pattern = r'(?:skills?|technologies?|tools?|technical\s+skills?)[:\s]+([^\n]+(?:\n[^\n]+){0,15})'
    for match in re.finditer(skills_section_pattern, text.lower()):
        section_text = match.group(1)
        # Split by common delimiters
        skill_items = re.split(r'[,;•|/\n]', section_text)
        for item in skill_items:
            item = item.strip()
            if 2 <= len(item) <= 50 and not item.startswith(('the ', 'a ', 'an ')):
                skills.add(item)
    
    # Method 3: Common technical patterns
    version_pattern = r'\b([a-z]+(?:\s+[a-z]+)?)\s+\d+(?:\.\d+)*\b'
    for match in re.finditer(version_pattern, text.lower()):
        tech_with_version = match.group(0).strip()
        if len(tech_with_version) < 30:
            skills.add(tech_with_version)
    
    # Clean and filter
    filtered_skills = []
    generic_words = {'experience', 'knowledge', 'skill', 'ability', 'working', 'using', 'with'}
    
    for skill in skills:
        # Remove generic prefixes/suffixes
        skill = re.sub(r'^(experience with|knowledge of|using|working with|proficient in)\s+', '', skill)
        skill = skill.strip()
        
        # Filter out pure generic terms
        if skill and len(skill) >= 2 and skill not in generic_words:
            filtered_skills.append(skill)
    
    return list(set(filtered_skills))[:50]  # Limit to top 50

def semantic_chunk_text(text, nlp, embedder, max_chars=800, overlap=200):
    """
    Advanced semantic chunking: splits text intelligently using sentence boundaries
    and semantic coherence for better RAG retrieval.
    """
    # First pass: sentence-based splitting
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    # Ensure sentencizer is available
    if "sentencizer" not in nlp.pipe_names:
        try:
            nlp.add_pipe("sentencizer")
        except:
            pass
    
    doc = nlp(text)
    sentences = [s.text.strip() for s in getattr(doc, "sents", []) if s.text.strip()]
    
    if not sentences:
        # Fallback: split by paragraphs
        sentences = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Build chunks with semantic awareness
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sent in sentences:
        sent_length = len(sent)
        
        # If adding this sentence exceeds max_chars, finalize current chunk
        if current_length + sent_length > max_chars and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
            
            # Keep last few sentences for overlap (semantic continuity)
            if overlap > 0:
                overlap_sents = []
                overlap_len = 0
                for s in reversed(current_chunk):
                    if overlap_len + len(s) <= overlap:
                        overlap_sents.insert(0, s)
                        overlap_len += len(s)
                    else:
                        break
                current_chunk = overlap_sents
                current_length = overlap_len
            else:
                current_chunk = []
                current_length = 0
        
        current_chunk.append(sent)
        current_length += sent_length
    
    # Add final chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    # If no chunks created, return whole text
    if not chunks:
        chunks = [text]
    
    return chunks

def retrieve_relevant_context(query, faiss_index, chunks, embedder, top_k=3):
    """
    RAG: Retrieve most relevant resume chunks for a given query using FAISS.
    Returns: list of (chunk_text, similarity_score) tuples
    """
    if not chunks or faiss_index is None:
        return []
    
    try:
        # Encode query
        query_emb = embedder.encode(query, convert_to_numpy=True, normalize_embeddings=True)
        if query_emb.ndim > 1:
            query_emb = query_emb[0]
        
        # Search FAISS index
        query_emb = query_emb.reshape(1, -1).astype(np.float32)
        similarities, indices = faiss_index.search(query_emb, min(top_k, len(chunks)))
        
        # Build results
        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if 0 <= idx < len(chunks):
                results.append((chunks[idx], float(sim)))
        
        return results
    except Exception:
        return []

def build_competency_catalog():
    """
    Define competency bundles that represent real-world capability beyond a single keyword.
    Each competency includes:
    - core: anchor terms (usually languages or role-defining tech)
    - frameworks/tools: ecosystem items that strengthen competency
    - project_verbs: verbs that indicate hands-on building
    - queries: suggested RAG queries
    """
    return {
        "java_ecosystem": {
            "core": ["java", "java 8", "java 11", "java 17"],
            "frameworks": [
                "spring", "spring boot", "spring cloud", "spring mvc",
                "hibernate", "jpa", "jakarta", "microservices", "rest api",
                "maven", "gradle", "junit", "mockito", "kafka"
            ],
            "project_verbs": ["built", "developed", "implemented", "designed", "maintained", "deployed"],
            "queries": ["java spring boot project", "java microservices", "spring hibernate"]
        },
        "python_backend": {
            "core": ["python", "python 3", "python 3.x"],
            "frameworks": [
                "django", "django rest framework", "flask", "fastapi",
                "pandas", "numpy", "celery", "sqlalchemy", "pytest"
            ],
            "project_verbs": ["built", "developed", "implemented", "designed", "maintained", "deployed"],
            "queries": ["python django api", "fastapi production", "flask project"]
        },
        "node_backend": {
            "core": ["node", "node.js", "nodejs"],
            "frameworks": ["express", "nest", "nestjs", "typescript", "prisma", "sequelize", "jest"],
            "project_verbs": ["built", "developed", "implemented", "designed", "maintained", "deployed"],
            "queries": ["node express api", "node microservices", "nestjs project"]
        },
        "frontend_js": {
            "core": ["javascript", "typescript"],
            "frameworks": ["react", "react 18", "nextjs", "next.js", "angular", "vue", "redux", "vite", "webpack"],
            "project_verbs": ["built", "developed", "implemented", "designed", "maintained", "deployed"],
            "queries": ["react project", "typescript react", "nextjs production"]
        },
        "devops_cloud": {
            "core": ["docker", "kubernetes", "k8s"],
            "frameworks": [
                "ci/cd", "jenkins", "github actions", "gitlab ci", "terraform", "ansible", "helm",
                "aws", "azure", "gcp", "prometheus", "grafana"
            ],
            "project_verbs": ["deployed", "automated", "scaled", "containerized", "orchestrated"],
            "queries": ["kubernetes deployment", "terraform ci/cd", "docker production"]
        },
        "data_ml": {
            "core": ["machine learning", "ml", "ai", "deep learning"],
            "frameworks": [
                "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras", "xgboost", "lightgbm",
                "mlflow", "airflow", "sagemaker", "vertex ai"
            ],
            "project_verbs": ["trained", "deployed", "optimized", "built", "developed"],
            "queries": ["ml production", "tensorflow deployment", "pytorch project"]
        }
    }

def _find_terms_in_text(terms, tokens, full_text):
    hits = set()
    for t in terms:
        if contains_atom(t, tokens, full_text):
            hits.add(normalize_text(t))
    return hits

def _recent_years_present(text, window=4):
    try:
        from datetime import datetime as _dt
        year_now = _dt.now().year
    except Exception:
        year_now = 2025
    yrs = {str(y) for y in range(year_now-window+1, year_now+1)}
    return any(y in text for y in yrs)

def compute_competency_scores(resume_text, chunks, embedder, nlp, model=None, faiss_index=None):
    """
    Compute a competency score per ecosystem using primarily local evidence, with LLM support for borderline cases.
    Scoring (0..1): core (0.3) + frameworks (up to 0.45) + projects evidence (0.15) + recency (0.1)
    Returns (scores, evidence) where evidence has keys: frameworks_found, project_contexts, recent
    """
    catalog = build_competency_catalog()
    tokens = token_set(resume_text)
    scores = {}
    evidences = {}

    for comp_id, spec in catalog.items():
        core = spec["core"]
        frameworks = spec["frameworks"]
        verbs = spec["project_verbs"]
        queries = spec["queries"]

        core_hits = _find_terms_in_text(core, tokens, resume_text)
        fw_hits = _find_terms_in_text(frameworks, tokens, resume_text)

        # RAG contexts to check project verbs & recency
        contexts = []
        if faiss_index and chunks and embedder:
            for q in queries[:2]:
                ctxs = retrieve_relevant_context(q, faiss_index, chunks, embedder, top_k=2)
                for t, s in ctxs:
                    contexts.append(t)
        # Deduplicate and trim
        contexts = list(dict.fromkeys(contexts))[:5]
        ctx_text = "\n".join(contexts)

        # Project verb evidence if appears near core/framework contexts
        project_evidence = 0
        if contexts:
            for c in contexts:
                if any(v in c.lower() for v in verbs):
                    project_evidence += 1
        recent = _recent_years_present(ctx_text) or _recent_years_present(resume_text)

        # Score aggregation
        score = 0.0
        if core_hits:
            score += 0.30
        # Frameworks: diminishing returns up to 0.45
        fw_count = len(fw_hits)
        if fw_count > 0:
            score += min(0.45, 0.20 + 0.12 * min(3, fw_count-1))
        # Projects
        if project_evidence > 0:
            score += min(0.15, 0.07 + 0.04 * min(2, project_evidence-1))
        # Recency
        if recent:
            score += 0.10

        # Optional LLM boost for borderline cases (supportive only)
        if model and 0.45 <= score < 0.75 and contexts:
            try:
                verdict = llm_json(model, f"""
Return ONLY JSON: {{"substantial": true|false}}
You are validating if the resume shows SUBSTANTIAL, PRACTICAL experience in the competency: {comp_id}.
Consider these resume excerpts:
{ctx_text[:1200]}
Criteria: multiple ecosystem frameworks, projects built, deployments, or tests. Answer conservatively.
                """)
                if isinstance(verdict, dict) and bool(verdict.get("substantial")):
                    score = min(0.80, score + 0.12)
            except Exception:
                pass

        scores[comp_id] = float(np.clip(score, 0.0, 1.0))
        evidences[comp_id] = {
            "frameworks_found": sorted(list(fw_hits))[:10],
            "core_found": sorted(list(core_hits))[:5],
            "project_contexts": contexts,
            "recent": bool(recent),
            "frameworks_count": int(fw_count)
        }

    return scores, evidences

def map_atoms_to_competencies(atoms, catalog):
    """
    Map requirement atoms to competency IDs with kind: core/framework/tool.
    Returns: (atom_to_comp, atom_kind)
    """
    atom_to_comp = {}
    atom_kind = {}
    for a in atoms:
        a_norm = normalize_text(a)
        for comp_id, spec in catalog.items():
            # core match
            if any(t in a_norm for t in spec["core"]):
                atom_to_comp[a_norm] = comp_id
                atom_kind[a_norm] = "core"
                break
            # framework match
            if any(t in a_norm for t in spec["frameworks"]):
                atom_to_comp[a_norm] = comp_id
                atom_kind[a_norm] = "framework"
                break
        # If not matched, leave unmapped
    return atom_to_comp, atom_kind

def parse_resume_pdf(path, nlp, embedder):
    """
    Enhanced resume parser with multi-level NLP extraction.
    Extracts structured entities, skills, experience, education using spaCy NER + custom patterns.
    """
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
    
    # Enhanced: Extract structured entities using spaCy NER
    structured_entities = extract_structured_entities(text, nlp)
    
    # Enhanced: Semantic chunking with better overlap and sentence awareness
    chunks = semantic_chunk_text(text, nlp, embedder, max_chars=800, overlap=200)
    
    # Build vector index for RAG
    idx, embs = build_index(embedder, chunks)
    
    # Enhanced: Extract technical skills with pattern matching
    technical_skills = extract_technical_skills(text, nlp)
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "text": text,
        "chunks": chunks,
        "faiss": idx,
        "embs": embs,
        "entities": structured_entities,
        "technical_skills": technical_skills
    }

# ---- PostgreSQL helpers ----
def _sanitize_for_postgres(value):
    """Convert Python types to PostgreSQL-compatible JSON types."""
    import numpy as _np
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (_np.integer,)): return int(value)
    if isinstance(value, (_np.floating,)): return float(value)
    if isinstance(value, _np.ndarray): return value.tolist()
    if isinstance(value, (list, tuple)): return [_sanitize_for_postgres(v) for v in value]
    if isinstance(value, dict): return {str(k): _sanitize_for_postgres(v) for k,v in value.items()}
    return str(value)

def save_to_db(resume_doc, jd, analysis, db_conn, db_ok):
    """Save resume and analysis to PostgreSQL database."""
    if not db_ok or not db_conn:
        print("⚠️ PostgreSQL not connected - skipping database save")
        st.warning("⚠️ Database not available - analysis not saved to database")
        return None, None
    
    print(f"💾 Attempting to save to database...")
    print(f"   Resume: {resume_doc.get('name', 'Unknown')} ({resume_doc.get('email', 'N/A')})")
    
    resume_id = None
    analysis_id = None
    try:
        with db_conn.cursor() as cur:
            # Save resume document
            print("   → Inserting resume...")
            cur.execute("""
                INSERT INTO resumes (name, email, phone, text, chunks, entities, technical_skills)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                resume_doc.get("name", "Unknown"),
                resume_doc.get("email", "N/A"),
                resume_doc.get("phone", "N/A"),
                resume_doc.get("text", "")[:10000],  # Limit text size
                Json(_sanitize_for_postgres(resume_doc.get("chunks", []))),
                Json(_sanitize_for_postgres(resume_doc.get("entities", {}))),
                Json(_sanitize_for_postgres(resume_doc.get("technical_skills", [])))
            ))
            resume_id = cur.fetchone()[0]
            print(f"   ✅ Resume saved with ID: {resume_id}")
            
            # Save analysis document
            print("   → Inserting analysis...")
            cur.execute("""
                INSERT INTO analyses (
                    resume_id, jd_text, plan, profile, coverage, cue_alignment,
                    final_analysis, semantic_score, coverage_score, llm_fit_score,
                    final_score, fit_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                resume_id,
                jd[:5000],  # Limit JD text size
                Json(_sanitize_for_postgres(analysis.get("plan", {}))),
                Json(_sanitize_for_postgres(analysis.get("resume_profile", {}))),
                Json(_sanitize_for_postgres(analysis.get("coverage_summary", {}))),
                Json(_sanitize_for_postgres(analysis.get("cue_alignment", {}))),
                Json(_sanitize_for_postgres(analysis.get("llm_analysis", {}))),
                float(analysis.get("semantic_score", 0.0)) / 10.0,  # Scale 0-10 to 0-1 for DB
                float(analysis.get("coverage_score", 0.0)) / 10.0,  # Scale 0-10 to 0-1 for DB
                float(analysis.get("llm_fit_score", 0.0)) / 10.0,   # Scale 0-10 to 0-1 for DB
                float(analysis.get("score", 0.0)) / 10.0,           # Scale 0-10 to 0-1 for DB
                int(analysis.get("llm_fit_score", 0))               # Store as 0-10 integer
            ))
            analysis_id = cur.fetchone()[0]
            print(f"   ✅ Analysis saved with ID: {analysis_id}")
            
        db_conn.commit()
        print(f"✅ Transaction committed successfully!")
        st.success(f"💾 Saved to database! (Resume ID: {resume_id}, Analysis ID: {analysis_id})")
        return resume_id, analysis_id
    except Exception as exc:
        db_conn.rollback()
        print(f"❌ PostgreSQL save error: {type(exc).__name__}: {exc}")
        import traceback
        traceback.print_exc()
        st.error(f"❌ Database save failed: {str(exc)[:200]}")
        return None, None

def get_recent(db_conn, db_ok, limit=20):
    """Fetch recent analyses from PostgreSQL."""
    items = []
    if not db_ok or not db_conn:
        print("⚠️ PostgreSQL not available - cannot fetch recent analyses")
        return items
    
    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    a.id,
                    a.created_at,
                    r.name as candidate,
                    r.email,
                    a.final_score,
                    a.fit_score,
                    a.semantic_score,
                    a.coverage_score,
                    LEFT(a.jd_text, 200) as job_desc_preview
                FROM analyses a
                JOIN resumes r ON a.resume_id = r.id
                ORDER BY a.created_at DESC
                LIMIT %s
            """, (limit,))
            items = cur.fetchall()
            # Convert datetime to timestamp for compatibility
            for item in items:
                if 'created_at' in item and item['created_at']:
                    item['timestamp'] = item['created_at'].timestamp()
        print(f"✅ Retrieved {len(items)} recent analyses from database")
    except Exception as e:
        print(f"❌ Error fetching recent analyses: {e}")
        import traceback
        traceback.print_exc()
    return items

# =======================
# =======  UI  ==========
# =======================

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    dbg = st.toggle("Show debug details", value=False)
    st.caption("Tip: Turn on for atoms/coverage internals.")

with st.spinner('🔄 Initializing AI models and database...'):
    try:
        model, nlp, embedder, models_ok = load_models()
    except Exception as e:
        st.error(f"❌ **Model Loading Error**: {str(e)[:200]}")
        model, nlp, embedder, models_ok = None, None, None, False
    
    try:
        db_conn, db_ok = init_postgresql()
    except Exception as e:
        st.warning(f"⚠️ PostgreSQL connection failed: {str(e)[:100]}")
        db_conn, db_ok = None, False

# Show status but don't stop the app
if not models_ok:
    st.error("❌ **AI Models Not Available - Setup Required**")
    with st.expander("📋 Click here for setup instructions", expanded=True):
        st.markdown("""
        ### Quick Setup Steps:
        
        **1. Check your `.env` file** (in the project root):
        ```env
        GEMINI_API_KEY=your_api_key_here
        ```
        
        **2. Install spaCy model**:
        ```bash
        python -m spacy download en_core_web_sm
        ```
        
        **3. Restart the application**:
        ```bash
        streamlit run app.py
        ```
        
        **Need an API key?** Get one free at: https://makersuite.google.com/app/apikey
        """)
    st.warning("⚠️ File upload is available below, but analysis requires model setup.")
else:
    # Beautiful animated success message that fades out
    st.markdown("""
    <div class="success-banner" style="
        background:linear-gradient(135deg,rgba(16,185,129,.25),rgba(5,150,105,.20));
        border:3px solid rgba(16,185,129,.6);
        border-radius:24px;
        padding:24px 40px;
        text-align:center;
        box-shadow:0 12px 45px rgba(16,185,129,.35),0 0 70px rgba(16,185,129,.25);
        margin-bottom:24px;
        animation:fadeInOut 4s ease-in-out forwards;
        backdrop-filter:blur(20px);
    ">
        <div style="display:flex;align-items:center;justify-content:center;gap:16px;">
            <span style="font-size:36px;animation:bounce 1s ease-in-out infinite;">🎉</span>
            <span style="
                font-size:22px;
                font-weight:900;
                color:#6ee7b7;
                font-family:'Space Grotesk',sans-serif;
                text-shadow:0 2px 15px rgba(16,185,129,.8);
                letter-spacing:1px;
            ">✅ AI MODELS LOADED SUCCESSFULLY!</span>
            <span style="font-size:36px;animation:bounce 1s ease-in-out infinite;animation-delay:0.2s;">🚀</span>
        </div>
    </div>
    <style>
        @keyframes fadeInOut {
            0% { opacity:0; transform:translateY(-20px); }
            15% { opacity:1; transform:translateY(0); }
            85% { opacity:1; transform:translateY(0); }
            100% { opacity:0; transform:translateY(-20px); display:none; }
        }
        @keyframes bounce {
            0%, 100% { transform:translateY(0); }
            50% { transform:translateY(-10px); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Small delay to show the animation
    import time
    time.sleep(0.1)

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
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    
    # Initialize variables first to check state
    up = st.session_state.get('uploaded_file', None)
    jd = st.session_state.get('job_description', '')
    
    # Beautiful step indicator that fades out after showing
    step_placeholder = st.empty()
    if not models_ok:
        step_placeholder.warning("⚠️ **AI models not loaded** - Please check setup instructions above")
    elif not up:
        step_placeholder.markdown("""
        <div class="step-indicator" style="
            background:linear-gradient(135deg,rgba(99,102,241,.18),rgba(139,92,246,.15));
            border:2px solid rgba(99,102,241,.4);
            border-radius:20px;
            padding:20px 32px;
            text-align:center;
            box-shadow:0 8px 32px rgba(99,102,241,.25),0 0 60px rgba(139,92,246,.15);
            backdrop-filter:blur(20px);
            animation:fadeInOut 5s ease-in-out forwards;
            margin-bottom:24px;
        ">
            <div style="display:flex;align-items:center;justify-content:center;gap:14px;">
                <span style="font-size:32px;animation:bounce 1.5s ease-in-out infinite;">👆</span>
                <span style="
                    font-size:17px;
                    font-weight:700;
                    color:#c7d2fe;
                    font-family:'Space Grotesk',sans-serif;
                    letter-spacing:0.5px;
                ">Step 1: Upload a resume PDF file using the button below</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif not jd or len(jd) < 50:
        step_placeholder.markdown("""
        <div class="step-indicator" style="
            background:linear-gradient(135deg,rgba(236,72,153,.18),rgba(139,92,246,.15));
            border:2px solid rgba(236,72,153,.4);
            border-radius:20px;
            padding:20px 32px;
            text-align:center;
            box-shadow:0 8px 32px rgba(236,72,153,.25),0 0 60px rgba(139,92,246,.15);
            backdrop-filter:blur(20px);
            animation:fadeInOut 5s ease-in-out forwards;
            margin-bottom:24px;
        ">
            <div style="display:flex;align-items:center;justify-content:center;gap:14px;">
                <span style="font-size:32px;animation:bounce 1.5s ease-in-out infinite;">👉</span>
                <span style="
                    font-size:17px;
                    font-weight:700;
                    color:#fbbf24;
                    font-family:'Space Grotesk',sans-serif;
                    letter-spacing:0.5px;
                ">Step 2: Add a detailed job description (minimum 50 characters)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        step_placeholder.markdown("""
        <div class="step-indicator" style="
            background:linear-gradient(135deg,rgba(16,185,129,.18),rgba(5,150,105,.15));
            border:2px solid rgba(16,185,129,.5);
            border-radius:20px;
            padding:20px 32px;
            text-align:center;
            box-shadow:0 8px 32px rgba(16,185,129,.3),0 0 60px rgba(5,150,105,.2);
            backdrop-filter:blur(20px);
            animation:fadeInOut 5s ease-in-out forwards;
            margin-bottom:24px;
        ">
            <div style="display:flex;align-items:center;justify-content:center;gap:14px;">
                <span style="font-size:32px;animation:bounce 1.5s ease-in-out infinite;">✅</span>
                <span style="
                    font-size:17px;
                    font-weight:700;
                    color:#6ee7b7;
                    font-family:'Space Grotesk',sans-serif;
                    letter-spacing:0.5px;
                ">Ready! Click the button below to start analysis</span>
                <span style="font-size:32px;animation:bounce 1.5s ease-in-out infinite;animation-delay:0.3s;">🚀</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    c1,c2 = st.columns([1,1], gap="large")
    
    with c1:
        # Enhanced section with icon
        st.markdown("""
        <div style="margin-bottom:24px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
                <div style="
                    width:52px;
                    height:52px;
                    background:linear-gradient(135deg,rgba(139,92,246,.25),rgba(99,102,241,.20));
                    border-radius:16px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:26px;
                    box-shadow:0 6px 20px rgba(139,92,246,.3),0 0 40px rgba(99,102,241,.2);
                    animation:glowPulseSmall 3s ease-in-out infinite;
                ">📤</div>
                <h3 style="
                    margin:0;
                    font-size:1.75rem;
                    font-weight:800;
                    color:#e2e8f0;
                    font-family:'Space Grotesk',sans-serif;
                    text-shadow:0 2px 12px rgba(139,92,246,.5);
                ">Upload Resume (PDF)</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader - update session state
        uploaded = st.file_uploader(
            "Upload Resume PDF", 
            type=['pdf'], 
            label_visibility="collapsed",
            accept_multiple_files=False
        )
        if uploaded:
            st.session_state['uploaded_file'] = uploaded
            up = uploaded
        
        # Success message when file is uploaded
        if up:
            st.markdown(f"""
            <div style="
                margin-top:20px;
                padding:18px 26px;
                background:linear-gradient(135deg,rgba(16,185,129,.15),rgba(5,150,105,.12));
                border:2px solid rgba(16,185,129,.5);
                border-radius:18px;
                box-shadow:0 6px 24px rgba(16,185,129,.25),0 0 45px rgba(5,150,105,.15);
                backdrop-filter:blur(20px);
                animation:fadeInRotate 0.6s ease-out;
            ">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:28px;">✓</span>
                    <div style="flex:1;">
                        <p style="margin:0;color:#6ee7b7;font-size:16px;font-weight:700;font-family:'Space Grotesk',sans-serif;">
                            File Loaded Successfully
                        </p>
                        <p style="margin:4px 0 0 0;color:#a7f3d0;font-size:14px;font-weight:500;">
                            {up.name} • {len(up.getvalue())//1024} KB
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with c2:
        # Enhanced section with icon
        st.markdown("""
        <div style="margin-bottom:24px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
                <div style="
                    width:52px;
                    height:52px;
                    background:linear-gradient(135deg,rgba(236,72,153,.25),rgba(219,39,119,.20));
                    border-radius:16px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:26px;
                    box-shadow:0 6px 20px rgba(236,72,153,.3),0 0 40px rgba(219,39,119,.2);
                    animation:glowPulseSmall 3s ease-in-out infinite;
                    animation-delay:0.5s;
                ">📝</div>
                <h3 style="
                    margin:0;
                    font-size:1.75rem;
                    font-weight:800;
                    color:#e2e8f0;
                    font-family:'Space Grotesk',sans-serif;
                    text-shadow:0 2px 12px rgba(236,72,153,.5);
                ">Job Description</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        jd = st.text_area(
            "Job Description", 
            height=220, 
            label_visibility="collapsed", 
            placeholder="Paste a detailed job description here...\n\nInclude:\n• Required skills and experience\n• Technologies and tools\n• Education requirements\n• Responsibilities",
            key="job_description"
        )

    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    
    # Show button status with clear messages
    can_analyze = models_ok and up is not None and jd and len(jd) >= 50
    
    # Button without disabled attribute (let user click anytime)
    go_analyze = st.button(
        "🚀 Analyze Resume", 
        use_container_width=True,
        type="primary"
    )

    if go_analyze:
        if not models_ok:
            st.error("❌ Cannot analyze - AI models not loaded. Please complete setup first.")
        elif not up:
            st.error("❌ Upload a resume PDF.")
        elif not jd or len(jd)<50:
            st.error("❌ Enter a detailed job description (min 50 chars).")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(up.getvalue())
                tmp_path = tmp.name
            try:
                prog = st.empty()
                stat = st.empty()

                # Immersive status display with modern design
                def show_status(progress_val, emoji, message, theme="purple"):
                    """Display beautiful animated status messages during processing"""
                    prog.progress(progress_val)
                    
                    # Theme color palettes
                    themes = {
                        "purple": {
                            "bg_start": "rgba(99,102,241,.18)",
                            "bg_end": "rgba(139,92,246,.15)",
                            "border": "rgba(139,92,246,.4)",
                            "shadow_main": "rgba(139,92,246,.35)",
                            "shadow_glow": "rgba(99,102,241,.2)",
                            "text": "#c7d2fe"
                        },
                        "pink": {
                            "bg_start": "rgba(236,72,153,.18)",
                            "bg_end": "rgba(219,39,119,.15)",
                            "border": "rgba(236,72,153,.4)",
                            "shadow_main": "rgba(236,72,153,.35)",
                            "shadow_glow": "rgba(219,39,119,.2)",
                            "text": "#fbcfe8"
                        },
                        "blue": {
                            "bg_start": "rgba(59,130,246,.18)",
                            "bg_end": "rgba(37,99,235,.15)",
                            "border": "rgba(59,130,246,.4)",
                            "shadow_main": "rgba(59,130,246,.35)",
                            "shadow_glow": "rgba(37,99,235,.2)",
                            "text": "#bfdbfe"
                        },
                        "green": {
                            "bg_start": "rgba(16,185,129,.18)",
                            "bg_end": "rgba(5,150,105,.15)",
                            "border": "rgba(16,185,129,.4)",
                            "shadow_main": "rgba(16,185,129,.35)",
                            "shadow_glow": "rgba(5,150,105,.2)",
                            "text": "#a7f3d0"
                        },
                        "amber": {
                            "bg_start": "rgba(245,158,11,.18)",
                            "bg_end": "rgba(217,119,6,.15)",
                            "border": "rgba(245,158,11,.4)",
                            "shadow_main": "rgba(245,158,11,.35)",
                            "shadow_glow": "rgba(217,119,6,.2)",
                            "text": "#fde68a"
                        }
                    }
                    
                    colors = themes.get(theme, themes["purple"])
                    
                    stat.markdown(f"""
                    <div style="
                        background:linear-gradient(135deg,{colors['bg_start']},{colors['bg_end']});
                        border:2px solid {colors['border']};
                        border-radius:20px;
                        padding:20px 32px;
                        margin:16px 0;
                        box-shadow:
                            0 8px 32px {colors['shadow_main']},
                            0 0 60px {colors['shadow_glow']},
                            inset 0 1px 0 rgba(255,255,255,.1),
                            inset 0 -1px 0 rgba(0,0,0,.2);
                        backdrop-filter:blur(24px);
                        animation:statusSlideIn 0.6s cubic-bezier(0.34,1.56,0.64,1);
                        position:relative;
                        overflow:hidden;
                    ">
                        <div style="
                            position:absolute;
                            top:-50%;left:-50%;
                            width:200%;height:200%;
                            background:radial-gradient(circle at 50% 50%,rgba(255,255,255,.08) 0%,transparent 70%);
                            animation:orbitalGlow 8s linear infinite;
                        "></div>
                        <div style="
                            display:flex;
                            align-items:center;
                            gap:20px;
                            position:relative;
                            z-index:1;
                        ">
                            <span style="
                                font-size:36px;
                                animation:emojiFloat 2s ease-in-out infinite;
                                filter:drop-shadow(0 4px 12px rgba(0,0,0,.4));
                                flex-shrink:0;
                            ">{emoji}</span>
                            <div style="flex:1;">
                                <div style="
                                    font-size:17px;
                                    font-weight:700;
                                    color:{colors['text']};
                                    font-family:'Inter','Segoe UI',sans-serif;
                                    letter-spacing:0.3px;
                                    text-shadow:0 2px 8px rgba(0,0,0,.3);
                                    line-height:1.4;
                                ">{message}</div>
                                <div style="
                                    margin-top:8px;
                                    height:2px;
                                    background:linear-gradient(90deg,
                                        transparent 0%,
                                        {colors['border']} 20%,
                                        {colors['border']} 80%,
                                        transparent 100%);
                                    background-size:200% 100%;
                                    animation:progressShimmer 2s linear infinite;
                                    border-radius:4px;
                                "></div>
                            </div>
                        </div>
                    </div>
                    <style>
                        @keyframes statusSlideIn {{
                            0% {{ opacity:0; transform:translateY(-20px) scale(0.95); }}
                            100% {{ opacity:1; transform:translateY(0) scale(1); }}
                        }}
                        @keyframes emojiFloat {{
                            0%, 100% {{ transform:translateY(0) rotate(0deg); }}
                            25% {{ transform:translateY(-6px) rotate(-5deg); }}
                            75% {{ transform:translateY(6px) rotate(5deg); }}
                        }}
                        @keyframes orbitalGlow {{
                            0% {{ transform:rotate(0deg); }}
                            100% {{ transform:rotate(360deg); }}
                        }}
                        @keyframes progressShimmer {{
                            0% {{ background-position:200% 0; }}
                            100% {{ background-position:-200% 0; }}
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                    time.sleep(0.05)

                # ---------- Parse resume ----------
                show_status(0.12, "📄", "Parsing resume and extracting text...", "purple")
                parsed = parse_resume_pdf(tmp_path, nlp, embedder)
                if not parsed:
                    st.error("No text parsed from the PDF."); st.stop()
                parsed["file_name"] = up.name
                preview = "\n".join(parsed["chunks"][:2])[:1200]
                st.session_state.uploads_history.insert(0, {"file_name":up.name,"name":parsed["name"],"email":parsed["email"],"phone":parsed["phone"],"timestamp":time.time()})

                # ---------- Plan & profile ----------
                show_status(0.28, "🎯", "Deriving intelligent analysis plan...", "pink")
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

                show_status(0.36, "👤", "Building candidate profile...", "blue")
                profile = llm_json(model, resume_profile_prompt(parsed["text"])) or {}
                parsed["llm_profile"] = profile

                # ---------- Atomic requirements (LLM + heuristic) ----------
                show_status(0.46, "🔍", "Extracting atomic requirements with NLP...", "purple")
                atoms_llm = llm_json(model, atomicize_requirements_prompt(jd, preview)) or {}
                jd_atoms_raw = extract_atoms_from_text(jd, nlp, max_atoms=100)

                # Extract from new structured format
                must_candidates = []
                nice_candidates = []
                
                # Add hard skills (most important)
                hard_skills = atoms_llm.get("hard_skills", {})
                must_candidates.extend(hard_skills.get("must", []))
                nice_candidates.extend(hard_skills.get("nice", []))
                
                # Add fundamentals
                fundamentals = atoms_llm.get("fundamentals", {})
                must_candidates.extend(fundamentals.get("must", []))
                nice_candidates.extend(fundamentals.get("nice", []))
                
                # Add experience requirements
                experience = atoms_llm.get("experience", {})
                must_candidates.extend(experience.get("must", []))
                nice_candidates.extend(experience.get("nice", []))
                
                # Add qualifications
                quals = atoms_llm.get("qualifications", {})
                must_candidates.extend(quals.get("must", []))
                nice_candidates.extend(quals.get("nice", []))
                
                # Fallback: try old format for backward compatibility
                if not must_candidates and not nice_candidates:
                    must_candidates = atoms_llm.get("must_atoms", [])
                    nice_candidates = atoms_llm.get("nice_atoms", [])
                
                # Add heuristic extractions as supplements
                must_candidates.extend(jd_atoms_raw[:50])
                nice_candidates.extend(jd_atoms_raw[50:120])
                
                # Refine and deduplicate with higher limits
                must_atoms, must_canon = refine_atom_list(must_candidates, nlp, limit=60)
                nice_atoms, _ = refine_atom_list(nice_candidates, nlp, reserved_canonicals=must_canon, limit=40)

                # ---------- Coverage (semantic similarity over chunks) ----------
                show_status(0.58, "📊", "Computing requirement coverage with RAG...", "green")
                coverage_summary = evaluate_requirement_coverage(
                    must_atoms, nice_atoms, parsed.get("text", ""), parsed.get("chunks", []),
                    embedder, model, faiss_index=parsed.get("faiss"), nlp=nlp, jd_text=jd
                )
                cov_final = coverage_summary["overall"]
                must_cov = coverage_summary["must"]
                nice_cov = coverage_summary["nice"]

                # ---------- Global semantic ----------
                show_status(0.68, "🧠", "Analyzing semantic similarity...", "purple")
                global_sem = compute_global_semantic(embedder, parsed.get("embs"), jd)
                global_sem01 = (global_sem + 1.0) / 2.0  # map [-1,1] -> [0,1]

                # ---------- LLM narrative & fit ----------
                show_status(0.78, "✨", "Generating LLM narrative assessment...", "pink")
                cue_alignment = compute_cue_alignment(plan, parsed, profile, embedder, parsed.get("faiss"))
                cov_parts = {
                    "must_coverage": round(must_cov, 3),
                    "nice_coverage": round(nice_cov, 3),
                    "overall": round(cov_final, 3),
                    "must_atoms_count": len(must_atoms),
                    "nice_atoms_count": len(nice_atoms),
                    "cue_average_similarity": round(cue_alignment.get("average_similarity", 0.0), 3)
                }
                llm_out = llm_json(
                    model,
                    analysis_prompt(jd, plan, profile, coverage_summary, cue_alignment, global_sem01, cov_final)
                )
                fit_score = llm_out.get("fit_score")
                if not isinstance(fit_score, (int, float)):
                    # Enhanced fallback: better balance between semantic and coverage
                    # Favor coverage more as it's more concrete
                    fit_score = round(10 * (0.35*global_sem01 + 0.65*cov_final), 1)
                fit_score = float(np.clip(fit_score, 0, 10))

                # ---------- ACCURATE & REALISTIC Scoring System ----------
                weights = plan.get("scoring_weights", DEFAULT_WEIGHTS)
                sem10, cov10 = round(10*global_sem01,1), round(10*cov_final,1)
                w_sem, w_cov, w_llm = float(weights["semantic"]), float(weights["coverage"]), float(weights["llm_fit"])
                W = w_sem + w_cov + w_llm
                if W <= 1e-9:
                    w_sem, w_cov, w_llm = DEFAULT_WEIGHTS["semantic"], DEFAULT_WEIGHTS["coverage"], DEFAULT_WEIGHTS["llm_fit"]
                    W = w_sem + w_cov + w_llm
                w_sem, w_cov, w_llm = w_sem/W, w_cov/W, w_llm/W
                
                # Base score: weighted combination aligned with actual performance
                # Coverage is most important (concrete skills), then semantic (context fit), then LLM (qualitative)
                raw_score = float(np.clip(w_sem*sem10 + w_cov*cov10 + w_llm*fit_score, 0, 10))
                
                # REALISTIC PENALTIES based on must-have coverage (most critical factor)
                penalty = 0.0
                penalty_reason = []
                
                if must_atoms and len(must_atoms) > 0:
                    # Align scoring with actual must-have performance
                    # Coverage thresholds define score caps
                    if must_cov < 0.25:  # < 25% = Critical failure
                        # Cap score at 3.0, apply harsh penalty
                        max_allowed = 3.0
                        if raw_score > max_allowed:
                            penalty = raw_score - max_allowed
                            penalty_reason.append(f"Critical gaps (<25% must-haves) → capped at {max_allowed}")
                    elif must_cov < 0.40:  # 25-40% = Major concerns
                        # Cap score at 4.5, apply significant penalty
                        max_allowed = 4.5
                        if raw_score > max_allowed:
                            penalty = raw_score - max_allowed
                            penalty_reason.append(f"Major gaps (<40% must-haves) → capped at {max_allowed}")
                    elif must_cov < 0.55:  # 40-55% = Moderate concerns
                        # Cap score at 6.0
                        max_allowed = 6.0
                        if raw_score > max_allowed:
                            penalty = raw_score - max_allowed
                            penalty_reason.append(f"Moderate gaps (<55% must-haves) → capped at {max_allowed}")
                    elif must_cov < 0.70:  # 55-70% = Minor gaps
                        # Cap score at 7.5
                        max_allowed = 7.5
                        if raw_score > max_allowed:
                            penalty = raw_score - max_allowed
                            penalty_reason.append(f"Minor gaps (<70% must-haves) → capped at {max_allowed}")
                    
                    # Additional penalty for BOTH weak coverage AND weak semantic alignment
                    if must_cov < 0.50 and global_sem01 < 0.50:
                        # Both dimensions weak = compound problem
                        combo_penalty = 1.0
                        penalty += combo_penalty
                        penalty_reason.append("Weak skills + context misalignment")
                    
                    # Penalty for very low semantic score even with decent coverage
                    # (Has skills on paper but context doesn't match role)
                    if global_sem01 < 0.35 and must_cov >= 0.55:
                        semantic_penalty = 0.8
                        penalty += semantic_penalty
                        penalty_reason.append("Poor contextual fit for role")
                
                # Apply penalty with floor at 0
                final_score = float(np.clip(raw_score - penalty, 0, 10))
                
                # Final calibration: compress very high scores (>8.5) to be more realistic
                # Most candidates shouldn't score 9-10 unless truly exceptional
                if final_score >= 8.5:
                    final_score = 8.0 + (final_score - 8.5) * 0.5  # 8.5-10 → 8.0-8.75
                
                # Build component breakdown
                components = {
                    "Semantic": round(w_sem*sem10,1),
                    "Coverage": round(w_cov*cov10,1),
                    "LLM Fit": round(w_llm*fit_score,1)
                }
                if penalty > 0.0:
                    components["Penalty"] = -round(penalty,1)
                    components["Penalty_Reason"] = "; ".join(penalty_reason)

                # ---------- Package result ----------
                result = {
                    "score": round(final_score,1),
                    "semantic_score": round(sem10,1),
                    "coverage_score": round(cov10,1),
                    "llm_fit_score": round(fit_score,1),
                    "coverage_parts": cov_parts,
                    "coverage_summary": coverage_summary,
                    "atom_matches": coverage_summary.get("details", {}),
                    "cue_alignment": cue_alignment,
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

                save_to_db(parsed, jd, result, db_conn, db_ok)
                st.session_state.analysis_history.insert(0, result)
                st.session_state.analysis_history = st.session_state.analysis_history[:100]
                st.session_state.current_analysis = (parsed, result)

                # Final success with immersive celebration
                prog.progress(1.0)
                stat.markdown("""
                <div style="
                    background:linear-gradient(135deg,
                        rgba(16,185,129,.25) 0%,
                        rgba(5,150,105,.20) 50%,
                        rgba(16,185,129,.25) 100%);
                    border:3px solid rgba(16,185,129,.6);
                    border-radius:24px;
                    padding:32px 48px;
                    margin:20px 0;
                    box-shadow:
                        0 10px 50px rgba(16,185,129,.5),
                        0 0 100px rgba(5,150,105,.3),
                        inset 0 2px 0 rgba(255,255,255,.2),
                        inset 0 -2px 0 rgba(0,0,0,.2);
                    backdrop-filter:blur(30px);
                    animation:successZoomIn 1s cubic-bezier(0.34,1.56,0.64,1) forwards;
                    position:relative;
                    overflow:hidden;
                ">
                    <div style="
                        position:absolute;
                        top:50%;left:50%;
                        transform:translate(-50%,-50%);
                        width:300px;height:300px;
                        background:radial-gradient(circle,rgba(16,185,129,.3) 0%,transparent 70%);
                        animation:successPulse 2s ease-in-out infinite;
                    "></div>
                    <div style="
                        position:absolute;
                        top:0;left:0;right:0;bottom:0;
                        background:linear-gradient(45deg,
                            transparent 25%,
                            rgba(255,255,255,.05) 25%,
                            rgba(255,255,255,.05) 50%,
                            transparent 50%,
                            transparent 75%,
                            rgba(255,255,255,.05) 75%,
                            rgba(255,255,255,.05));
                        background-size:40px 40px;
                        animation:patternMove 20s linear infinite;
                        opacity:0.3;
                    "></div>
                    <div style="
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        gap:24px;
                        position:relative;
                        z-index:1;
                    ">
                        <span style="
                            font-size:56px;
                            animation:successBounce 1s ease-in-out 3;
                            filter:drop-shadow(0 8px 16px rgba(0,0,0,.4));
                        ">✅</span>
                        <div style="text-align:center;">
                            <div style="
                                font-size:28px;
                                font-weight:900;
                                color:#6ee7b7;
                                font-family:'Space Grotesk','Poppins',sans-serif;
                                letter-spacing:1px;
                                text-shadow:0 2px 12px rgba(0,0,0,.4);
                                margin-bottom:8px;
                            ">Analysis Complete!</div>
                            <div style="
                                font-size:14px;
                                font-weight:600;
                                color:#a7f3d0;
                                opacity:0.9;
                                letter-spacing:0.5px;
                            ">Resume successfully evaluated</div>
                        </div>
                        <span style="
                            font-size:56px;
                            animation:successBounce 1s ease-in-out 3;
                            animation-delay:0.15s;
                            filter:drop-shadow(0 8px 16px rgba(0,0,0,.4));
                        ">🚀</span>
                    </div>
                </div>
                <style>
                    @keyframes successZoomIn {
                        0% { opacity:0; transform:scale(0.85) rotateX(10deg); }
                        100% { opacity:1; transform:scale(1) rotateX(0deg); }
                    }
                    @keyframes successBounce {
                        0%, 100% { transform:translateY(0) scale(1); }
                        25% { transform:translateY(-20px) scale(1.15); }
                        50% { transform:translateY(0) scale(1); }
                        75% { transform:translateY(-10px) scale(1.08); }
                    }
                    @keyframes successPulse {
                        0%, 100% { transform:translate(-50%,-50%) scale(1); opacity:0.5; }
                        50% { transform:translate(-50%,-50%) scale(1.3); opacity:0.8; }
                    }
                    @keyframes patternMove {
                        0% { background-position:0 0; }
                        100% { background-position:40px 40px; }
                    }
                </style>
                """, unsafe_allow_html=True)
                time.sleep(1.5)
                prog.empty()
                stat.empty()
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
        <div style="text-align:center;margin:40px 0 24px 0;">
            <h3 class="section-header" style="display:inline-block;padding:14px 36px;
                       background:linear-gradient(135deg,rgba(16,185,129,.12),rgba(5,150,105,.08));
                       border-radius:16px;border:2px solid rgba(16,185,129,.35);
                       box-shadow:0 4px 16px rgba(16,185,129,.2);">
                ✅ Requirement Coverage Analysis
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Get requirement details
        matches = analysis.get("atom_matches", {})
        must_atoms = analysis["atoms"]["must"]
        nice_atoms = analysis["atoms"]["nice"]

        def build_detail_map(atoms, source):
            detail_map = {}
            for atom in atoms:
                info = dict(source.get(atom, {}))
                info.setdefault("score", 0.0)
                info.setdefault("similarity", 0.0)
                info.setdefault("max_similarity", info.get("similarity", 0.0))
                info.setdefault("resume_contexts", [])
                info.setdefault("jd_context", {"text": "", "similarity": 0.0})
                info.setdefault("pre_llm_score", 0.0)
                info.setdefault("llm_present", False)
                info.setdefault("llm_confidence", 0.0)
                info.setdefault("llm_rationale", "")
                info.setdefault("req_type", "")
                detail_map[atom] = info
            return detail_map

        must_detail_map = build_detail_map(must_atoms, matches.get("must", {}))
        nice_detail_map = build_detail_map(nice_atoms, matches.get("nice", {}))

        def _snippet_html(text, empty_label="No evidence", max_length=180):
            """Clean, truncated snippet for UI display"""
            if not text:
                return f"<span style=\"color:#64748b;font-style:italic;font-size:12px;\">{empty_label}</span>"
            safe = html.escape(text.strip())
            # Truncate long text
            if len(safe) > max_length:
                safe = safe[:max_length].rstrip() + "..."
            return f"<span style=\"font-size:12px;line-height:1.6;\">{safe}</span>"

        def _clean_rationale(text):
            """Clean up LLM-generated rationales to remove gibberish/noise"""
            if not text:
                return ""
            text = text.strip()
            # Remove common noise patterns
            text = re.sub(r'\[.*?\]', '', text)  # Remove [bracketed] content
            text = re.sub(r'\(.*?\)', '', text)  # Remove (parenthetical) content
            text = re.sub(r'\{.*?\}', '', text)  # Remove {braced} content
            text = re.sub(r'<.*?>', '', text)    # Remove <tags>
            text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
            text = text.replace('...', ' ')
            text = text.replace('..', ' ')
            # Remove fragments shorter than 10 chars (likely noise)
            if len(text) < 10:
                return ""
            # Limit to 150 chars for cleaner display
            if len(text) > 150:
                text = text[:147].rstrip() + "..."
            return text.strip()
        
        def _resume_snippet(info):
            """Get first resume context snippet"""
            contexts = info.get("resume_contexts") or []
            if contexts:
                return _snippet_html(contexts[0].get("text", ""), "Not found")
            return _snippet_html("", "Not found")

        def _jd_snippet(info):
            """Get JD context snippet"""
            jd_ctx = info.get("jd_context") or {}
            return _snippet_html(jd_ctx.get("text", ""), "No context")

        def split_status(detail_map):
            full, partial, missing = [], [], []
            for atom, info in detail_map.items():
                score = float(info.get("score", 0.0))
                if score >= 0.85:  # Full or LLM-verified
                    full.append((atom, info))
                elif score >= 0.5:  # Partial match
                    partial.append((atom, info))
                else:
                    missing.append((atom, info))
            return full, partial, missing

        must_full, must_partial, must_missing = split_status(must_detail_map)
        nice_full, nice_partial, nice_missing = split_status(nice_detail_map)

        must_score_total = sum(float(info.get("score", 0.0)) for info in must_detail_map.values())
        nice_score_total = sum(float(info.get("score", 0.0)) for info in nice_detail_map.values())

        total_atoms = len(must_atoms) + len(nice_atoms)
        total_score = must_score_total + nice_score_total
        coverage_pct = int(round((total_score / total_atoms) * 100)) if total_atoms else 0
        must_coverage_pct = int(round((must_score_total / len(must_atoms)) * 100)) if must_atoms else 0
        nice_pct = int(round((nice_score_total / len(nice_atoms)) * 100)) if nice_atoms else 0

        full_total = len(must_full) + len(nice_full)
        partial_total = len(must_partial) + len(nice_partial)
        
        # Coverage Overview Cards
        col1, col2, col3 = st.columns([1,1,1])
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(16,185,129,.15),rgba(5,150,105,.1));
                        border:2px solid rgba(16,185,129,.4);border-radius:16px;padding:24px;text-align:center;">
                <div style="display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:12px;">
                    <div style="width:48px;height:48px;background:#10b981;border-radius:12px;
                                display:flex;align-items:center;justify-content:center;font-size:24px;">✓</div>
                    <div style="text-align:left;">
                        <p style="margin:0;font-size:11px;color:#6ee7b7;text-transform:uppercase;font-weight:700;">Coverage</p>
                        <h3 style="margin:4px 0 0 0;font-size:32px;color:#10b981;font-weight:900;">{coverage_pct}%</h3>
                    </div>
                </div>
                <div style="height:6px;background:rgba(16,185,129,.2);border-radius:10px;overflow:hidden;">
                    <div style="width:{coverage_pct}%;height:100%;background:#10b981;border-radius:10px;
                                transition:width 1s ease;box-shadow:0 0 10px #10b98180;"></div>
                </div>
                <p style="margin:12px 0 0 0;font-size:13px;color:#94a3b8;">
                    <strong style="color:#10b981;">{full_total}</strong> full • <strong style="color:#fbbf24;">{partial_total}</strong> partial · <strong>{total_atoms}</strong> total
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(239,68,68,.15),rgba(220,38,38,.1));
                        border:2px solid rgba(239,68,68,.4);border-radius:16px;padding:24px;text-align:center;">
                <div style="display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:12px;">
                    <div style="width:48px;height:48px;background:#ef4444;border-radius:12px;
                                display:flex;align-items:center;justify-content:center;font-size:24px;">🔴</div>
                    <div style="text-align:left;">
                        <p style="margin:0;font-size:11px;color:#fca5a5;text-transform:uppercase;font-weight:700;">Must-Have</p>
                        <h3 style="margin:4px 0 0 0;font-size:32px;color:#ef4444;font-weight:900;">{must_coverage_pct}%</h3>
                    </div>
                </div>
                <div style="height:6px;background:rgba(239,68,68,.2);border-radius:10px;overflow:hidden;">
                    <div style="width:{must_coverage_pct}%;height:100%;background:#ef4444;border-radius:10px;
                                transition:width 1s ease;box-shadow:0 0 10px #ef444480;"></div>
                </div>
                <p style="margin:12px 0 0 0;font-size:13px;color:#94a3b8;">
                    <strong style="color:#10b981;">{len(must_full)}</strong> full · <strong style="color:#fbbf24;">{len(must_partial)}</strong> partial · <strong style="color:#ef4444;">{len(must_missing)}</strong> missing
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(59,130,246,.15),rgba(37,99,235,.1));
                        border:2px solid rgba(59,130,246,.4);border-radius:16px;padding:24px;text-align:center;">
                <div style="display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:12px;">
                    <div style="width:48px;height:48px;background:#3b82f6;border-radius:12px;
                                display:flex;align-items:center;justify-content:center;font-size:24px;">⭐</div>
                    <div style="text-align:left;">
                        <p style="margin:0;font-size:11px;color:#93c5fd;text-transform:uppercase;font-weight:700;">Nice-to-Have</p>
                        <h3 style="margin:4px 0 0 0;font-size:32px;color:#3b82f6;font-weight:900;">{nice_pct}%</h3>
                    </div>
                </div>
                <div style="height:6px;background:rgba(59,130,246,.2);border-radius:10px;overflow:hidden;">
                    <div style="width:{nice_pct}%;height:100%;background:#3b82f6;border-radius:10px;
                                transition:width 1s ease;box-shadow:0 0 10px #3b82f680;"></div>
                </div>
                <p style="margin:12px 0 0 0;font-size:13px;color:#94a3b8;">
                    {f'<strong style="color:#10b981;">{len(nice_full)}</strong> full · <strong style="color:#fbbf24;">{len(nice_partial)}</strong> partial · <strong style="color:#3b82f6;">{len(nice_missing)}</strong> missing' if len(nice_atoms) > 0 else '<span style="font-style:italic;">No nice-to-have specified</span>'}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # IMMERSIVE Requirements Breakdown
        st.markdown("""
        <div style="margin-top:48px;"></div>
        """, unsafe_allow_html=True)
        
        # Premium Tabbed view for requirements
        req_tab1, req_tab2 = st.tabs(["🔴 Must-Have Requirements", "⭐ Nice-to-Have"])
        
        with req_tab1:
            if len(must_atoms) > 0:
                if must_full:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:28px;background:linear-gradient(135deg,rgba(16,185,129,.20),rgba(5,150,105,.18));
                                border:3px solid rgba(16,185,129,.6);border-radius:24px;padding:28px;
                                box-shadow:0 12px 45px rgba(16,185,129,.35),0 0 70px rgba(16,185,129,.25),inset 0 2px 0 rgba(255,255,255,.1);">
                        <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
                            <div style="width:52px;height:52px;background:linear-gradient(135deg,#10b981,#059669);
                                        border-radius:16px;display:flex;align-items:center;justify-content:center;
                                        font-size:28px;box-shadow:0 8px 25px rgba(16,185,129,.5);animation:glowPulseSmall 3s ease-in-out infinite;">
                                ✓
                            </div>
                            <h4 style="margin:0;color:#6ee7b7;font-size:24px;font-weight:900;
                                       font-family:'Space Grotesk',sans-serif;text-transform:uppercase;
                        letter-spacing:1.5px;text-shadow:0 3px 15px rgba(16,185,129,.7);">
                    FOUND ({len(must_full)})
                            </h4>
                        </div>
                        <div style="display:grid;gap:14px;">
                    """, unsafe_allow_html=True)
                    
                    for idx, (req, info) in enumerate(must_full, 1):
                        conf_pct = int(round(info.get("llm_confidence", 0.0) * 100))
                        sim_val = info.get("similarity", 0.0)
                        signals = f"✓ {conf_pct}% · Sim {sim_val:.2f}" if info.get("llm_present") else f"Sim {sim_val:.2f}"
                        
                        resume_html = _resume_snippet(info)
                        raw_rationale = (info.get("llm_rationale") or "").strip()
                        rationale = _clean_rationale(raw_rationale)
                        
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(16,185,129,.08),rgba(5,150,105,.05));
                                    border:2px solid rgba(16,185,129,.35);border-left:5px solid #10b981;
                                    border-radius:16px;padding:24px 28px;margin-bottom:16px;
                                    box-shadow:0 4px 20px rgba(16,185,129,.18),0 8px 32px rgba(16,185,129,.12);
                                    transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
                                    position:relative;overflow:hidden;cursor:pointer;">
                            <div style="position:absolute;top:0;right:0;width:140px;height:140px;
                                        background:radial-gradient(circle,rgba(16,185,129,.18),transparent 70%);
                                        pointer-events:none;"></div>
                            <div style="display:flex;align-items:flex-start;gap:18px;position:relative;">
                                <div style="width:48px;height:48px;min-width:48px;
                                            background:linear-gradient(135deg,#10b981,#059669);
                                            border-radius:14px;display:flex;align-items:center;justify-content:center;
                                            font-size:24px;box-shadow:0 4px 16px rgba(16,185,129,.45),0 0 24px rgba(16,185,129,.25);">
                                    ✓
                                </div>
                                <div style="flex:1;">
                                    <div style="color:#f8fafc;font-size:17px;font-weight:700;margin-bottom:10px;
                                               line-height:1.5;font-family:'Inter',sans-serif;letter-spacing:-0.01em;">
                                        {html.escape(req)}
                                    </div>
                                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;">
                                        <span style="background:linear-gradient(135deg,rgba(16,185,129,.25),rgba(16,185,129,.15));
                                                     color:#6ee7b7;padding:5px 14px;border-radius:10px;
                                                     font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace;
                                                     border:1px solid rgba(16,185,129,.3);
                                                     box-shadow:0 2px 8px rgba(16,185,129,.2);">
                                            {signals}
                                        </span>
                                    </div>
                                    {f'<div style="color:#a7f3d0;font-size:14px;margin-bottom:12px;line-height:1.7;font-style:italic;padding-left:12px;border-left:3px solid rgba(16,185,129,.4);font-family:\'Inter\',sans-serif;">{html.escape(rationale)}</div>' if rationale else ''}
                                    <div style="background:linear-gradient(135deg,rgba(15,23,42,.8),rgba(15,23,42,.6));
                                               border-radius:12px;padding:14px 18px;
                                               border:1px solid rgba(16,185,129,.25);
                                               box-shadow:inset 0 2px 8px rgba(0,0,0,.3);">
                                        <div style="color:#94a3b8;font-size:10px;font-weight:700;margin-bottom:6px;
                                                   text-transform:uppercase;letter-spacing:1px;font-family:'Inter',sans-serif;">
                                            📄 Evidence from Resume
                                        </div>
                                        <div style="color:#e2e8f0;font-size:13px;line-height:1.7;font-family:'Inter',sans-serif;">
                                            {resume_html}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)

                if must_partial:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-top:20px;margin-bottom:28px;background:linear-gradient(135deg,rgba(250,204,21,.22),rgba(251,191,36,.18));
                                border:3px solid rgba(251,191,36,.6);border-radius:24px;padding:28px;
                                box-shadow:0 12px 45px rgba(251,191,36,.35),0 0 70px rgba(251,191,36,.25),inset 0 2px 0 rgba(255,255,255,.1);">
                        <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
                            <div style="width:52px;height:52px;background:linear-gradient(135deg,#facc15,#fbbf24);
                                        border-radius:16px;display:flex;align-items:center;justify-content:center;
                                        font-size:28px;box-shadow:0 8px 25px rgba(251,191,36,.5);animation:glowPulseSmall 3s ease-in-out infinite;">
                                △
                            </div>
                            <h4 style="margin:0;color:#fde68a;font-size:24px;font-weight:900;
                                       font-family:'Space Grotesk',sans-serif;text-transform:uppercase;
                                       letter-spacing:1.5px;text-shadow:0 3px 15px rgba(251,191,36,.7);">
                                PARTIAL SIGNALS ({len(must_partial)})
                            </h4>
                        </div>
                        <div style="display:grid;gap:14px;">
                    """, unsafe_allow_html=True)

                    for idx, (req, info) in enumerate(must_partial, 1):
                        conf_pct = int(round(info.get("llm_confidence", 0.0) * 100))
                        sim_val = info.get("similarity", 0.0)
                        signals = f"~{conf_pct}% · Sim {sim_val:.2f}" if conf_pct > 0 else f"Sim {sim_val:.2f}"
                        
                        resume_html = _resume_snippet(info)
                        raw_rationale = (info.get("llm_rationale") or "").strip()
                        rationale = _clean_rationale(raw_rationale)
                        
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(251,191,36,.08),rgba(250,204,21,.05));
                                    border:2px solid rgba(251,191,36,.35);border-left:5px solid #fbbf24;
                                    border-radius:16px;padding:24px 28px;margin-bottom:16px;
                                    box-shadow:0 4px 20px rgba(251,191,36,.18),0 8px 32px rgba(251,191,36,.12);
                                    transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
                                    position:relative;overflow:hidden;cursor:pointer;">
                            <div style="position:absolute;top:0;right:0;width:140px;height:140px;
                                        background:radial-gradient(circle,rgba(251,191,36,.18),transparent 70%);
                                        pointer-events:none;"></div>
                            <div style="display:flex;align-items:flex-start;gap:18px;position:relative;">
                                <div style="width:48px;height:48px;min-width:48px;
                                            background:linear-gradient(135deg,#fbbf24,#facc15);
                                            border-radius:14px;display:flex;align-items:center;justify-content:center;
                                            font-size:24px;box-shadow:0 4px 16px rgba(251,191,36,.45),0 0 24px rgba(251,191,36,.25);">
                                    △
                                </div>
                                <div style="flex:1;">
                                    <div style="color:#f8fafc;font-size:17px;font-weight:700;margin-bottom:10px;
                                               line-height:1.5;font-family:'Inter',sans-serif;letter-spacing:-0.01em;">
                                        {html.escape(req)}
                                    </div>
                                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;">
                                        <span style="background:linear-gradient(135deg,rgba(251,191,36,.25),rgba(251,191,36,.15));
                                                     color:#fde68a;padding:5px 14px;border-radius:10px;
                                                     font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace;
                                                     border:1px solid rgba(251,191,36,.3);
                                                     box-shadow:0 2px 8px rgba(251,191,36,.2);">
                                            {signals}
                                        </span>
                                    </div>
                                    {f'<div style="color:#fef3c7;font-size:14px;margin-bottom:12px;line-height:1.7;font-style:italic;padding-left:12px;border-left:3px solid rgba(251,191,36,.4);font-family:\'Inter\',sans-serif;">{html.escape(rationale)}</div>' if rationale else ''}
                                    <div style="background:linear-gradient(135deg,rgba(15,23,42,.8),rgba(15,23,42,.6));
                                               border-radius:12px;padding:14px 18px;
                                               border:1px solid rgba(251,191,36,.25);
                                               box-shadow:inset 0 2px 8px rgba(0,0,0,.3);">
                                        <div style="color:#94a3b8;font-size:10px;font-weight:700;margin-bottom:6px;
                                                   text-transform:uppercase;letter-spacing:1px;font-family:'Inter',sans-serif;">
                                            📄 Evidence from Resume
                                        </div>
                                        <div style="color:#e2e8f0;font-size:13px;line-height:1.7;font-family:'Inter',sans-serif;">
                                            {resume_html}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div></div>", unsafe_allow_html=True)

                if must_missing:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-top:28px;background:linear-gradient(135deg,rgba(239,68,68,.20),rgba(220,38,38,.18));
                                border:3px solid rgba(239,68,68,.6);border-radius:24px;padding:28px;
                                box-shadow:0 12px 45px rgba(239,68,68,.35),0 0 70px rgba(239,68,68,.25),inset 0 2px 0 rgba(255,255,255,.1);">
                        <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
                            <div style="width:52px;height:52px;background:linear-gradient(135deg,#ef4444,#dc2626);
                                        border-radius:16px;display:flex;align-items:center;justify-content:center;
                                        font-size:28px;box-shadow:0 8px 25px rgba(239,68,68,.5);animation:glowPulseSmall 3s ease-in-out infinite;">
                                ✗
                            </div>
                            <h4 style="margin:0;color:#fca5a5;font-size:24px;font-weight:900;
                                       font-family:'Space Grotesk',sans-serif;text-transform:uppercase;
                        letter-spacing:1.5px;text-shadow:0 3px 15px rgba(239,68,68,.7);">
                    MISSING ({len(must_missing)})
                            </h4>
                        </div>
                        <div style="display:grid;gap:14px;">
                    """, unsafe_allow_html=True)
                    
                    for idx, (req, info) in enumerate(must_missing, 1):
                        sim_val = info.get("similarity", 0.0)
                        conf_pct = int(round(info.get("llm_confidence", 0.0) * 100))
                        signals = f"✗ {conf_pct}% · Sim {sim_val:.2f}" if conf_pct > 0 else f"Sim {sim_val:.2f}"
                        
                        raw_rationale = (info.get("llm_rationale") or "No evidence found").strip()
                        rationale = _clean_rationale(raw_rationale) or "No evidence found"
                        
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(239,68,68,.08),rgba(220,38,38,.05));
                                    border:2px solid rgba(239,68,68,.35);border-left:5px solid #ef4444;
                                    border-radius:16px;padding:24px 28px;margin-bottom:16px;
                                    box-shadow:0 4px 20px rgba(239,68,68,.18),0 8px 32px rgba(239,68,68,.12);
                                    transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
                                    position:relative;overflow:hidden;cursor:pointer;">
                            <div style="position:absolute;top:0;right:0;width:140px;height:140px;
                                        background:radial-gradient(circle,rgba(239,68,68,.18),transparent 70%);
                                        pointer-events:none;"></div>
                            <div style="display:flex;align-items:flex-start;gap:18px;position:relative;">
                                <div style="width:48px;height:48px;min-width:48px;
                                            background:linear-gradient(135deg,#ef4444,#dc2626);
                                            border-radius:14px;display:flex;align-items:center;justify-content:center;
                                            font-size:24px;box-shadow:0 4px 16px rgba(239,68,68,.45),0 0 24px rgba(239,68,68,.25);">
                                    ✗
                                </div>
                                <div style="flex:1;">
                                    <div style="color:#f8fafc;font-size:17px;font-weight:700;margin-bottom:10px;
                                               line-height:1.5;font-family:'Inter',sans-serif;letter-spacing:-0.01em;">
                                        {html.escape(req)}
                                    </div>
                                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;">
                                        <span style="background:linear-gradient(135deg,rgba(239,68,68,.25),rgba(239,68,68,.15));
                                                     color:#fca5a5;padding:5px 14px;border-radius:10px;
                                                     font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace;
                                                     border:1px solid rgba(239,68,68,.3);
                                                     box-shadow:0 2px 8px rgba(239,68,68,.2);">
                                            {signals}
                                        </span>
                                    </div>
                                    <div style="color:#fecaca;font-size:14px;line-height:1.7;font-style:italic;
                                               padding:14px 18px;background:linear-gradient(135deg,rgba(239,68,68,.12),rgba(239,68,68,.08));
                                               border-radius:12px;border-left:3px solid rgba(239,68,68,.5);
                                               font-family:'Inter',sans-serif;
                                               box-shadow:inset 0 2px 8px rgba(0,0,0,.2);">
                                        ⚠️ {html.escape(rationale)}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
            else:
                st.info("No must-have requirements identified from job description.")
        
        with req_tab2:
            if len(nice_atoms) > 0:
                if nice_full:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:28px;background:linear-gradient(135deg,rgba(139,92,246,.20),rgba(99,102,241,.18));
                                border:3px solid rgba(139,92,246,.6);border-radius:24px;padding:28px;
                                box-shadow:0 12px 45px rgba(139,92,246,.35),0 0 70px rgba(139,92,246,.25),inset 0 2px 0 rgba(255,255,255,.1);">
                        <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
                            <div style="width:52px;height:52px;background:linear-gradient(135deg,#8b5cf6,#6366f1);
                                        border-radius:16px;display:flex;align-items:center;justify-content:center;
                                        font-size:28px;box-shadow:0 8px 25px rgba(139,92,246,.5);animation:glowPulseSmall 3s ease-in-out infinite;">
                                ⭐
                            </div>
                            <h4 style="margin:0;color:#c7d2fe;font-size:24px;font-weight:900;
                                       font-family:'Space Grotesk',sans-serif;text-transform:uppercase;
                        letter-spacing:1.5px;text-shadow:0 3px 15px rgba(139,92,246,.7);">
                    FOUND ({len(nice_full)})
                            </h4>
                        </div>
                        <div style="display:grid;gap:14px;">
                    """, unsafe_allow_html=True)
                    
                    for idx, (req, info) in enumerate(nice_full, 1):
                        conf_pct = int(round(info.get("llm_confidence", 0.0) * 100))
                        sim_val = info.get("similarity", 0.0)
                        signals = f"⭐ {conf_pct}% · Sim {sim_val:.2f}" if info.get("llm_present") else f"Sim {sim_val:.2f}"
                        
                        resume_html = _resume_snippet(info)
                        raw_rationale = (info.get("llm_rationale") or "").strip()
                        rationale = _clean_rationale(raw_rationale)
                        
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(139,92,246,.08),rgba(99,102,241,.05));
                                    border:2px solid rgba(139,92,246,.35);border-left:5px solid #8b5cf6;
                                    border-radius:16px;padding:24px 28px;margin-bottom:16px;
                                    box-shadow:0 4px 20px rgba(139,92,246,.18),0 8px 32px rgba(139,92,246,.12);
                                    transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
                                    position:relative;overflow:hidden;cursor:pointer;">
                            <div style="position:absolute;top:0;right:0;width:140px;height:140px;
                                        background:radial-gradient(circle,rgba(139,92,246,.18),transparent 70%);
                                        pointer-events:none;"></div>
                            <div style="display:flex;align-items:flex-start;gap:18px;position:relative;">
                                <div style="width:48px;height:48px;min-width:48px;
                                            background:linear-gradient(135deg,#8b5cf6,#6366f1);
                                            border-radius:14px;display:flex;align-items:center;justify-content:center;
                                            font-size:24px;box-shadow:0 4px 16px rgba(139,92,246,.45),0 0 24px rgba(139,92,246,.25);">
                                    ⭐
                                </div>
                                <div style="flex:1;">
                                    <div style="color:#f8fafc;font-size:17px;font-weight:700;margin-bottom:10px;
                                               line-height:1.5;font-family:'Inter',sans-serif;letter-spacing:-0.01em;">
                                        {html.escape(req)}
                                    </div>
                                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;">
                                        <span style="background:linear-gradient(135deg,rgba(139,92,246,.25),rgba(139,92,246,.15));
                                                     color:#c7d2fe;padding:5px 14px;border-radius:10px;
                                                     font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace;
                                                     border:1px solid rgba(139,92,246,.3);
                                                     box-shadow:0 2px 8px rgba(139,92,246,.2);">
                                            {signals}
                                        </span>
                                    </div>
                                    {f'<div style="color:#ddd6fe;font-size:14px;margin-bottom:12px;line-height:1.7;font-style:italic;padding-left:12px;border-left:3px solid rgba(139,92,246,.4);font-family:\'Inter\',sans-serif;">{html.escape(rationale)}</div>' if rationale else ''}
                                    <div style="background:linear-gradient(135deg,rgba(15,23,42,.8),rgba(15,23,42,.6));
                                               border-radius:12px;padding:14px 18px;
                                               border:1px solid rgba(139,92,246,.25);
                                               box-shadow:inset 0 2px 8px rgba(0,0,0,.3);">
                                        <div style="color:#94a3b8;font-size:10px;font-weight:700;margin-bottom:6px;
                                                   text-transform:uppercase;letter-spacing:1px;font-family:'Inter',sans-serif;">
                                            📄 Evidence from Resume
                                        </div>
                                        <div style="color:#e2e8f0;font-size:13px;line-height:1.7;font-family:'Inter',sans-serif;">
                                            {resume_html}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)

                if nice_partial:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-top:20px;margin-bottom:28px;background:linear-gradient(135deg,rgba(96,165,250,.22),rgba(59,130,246,.18));
                                border:3px solid rgba(59,130,246,.6);border-radius:24px;padding:28px;
                                box-shadow:0 12px 45px rgba(59,130,246,.35),0 0 70px rgba(59,130,246,.25),inset 0 2px 0 rgba(255,255,255,.1);">
                        <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
                            <div style="width:52px;height:52px;background:linear-gradient(135deg,#3b82f6,#60a5fa);
                                        border-radius:16px;display:flex;align-items:center;justify-content:center;
                                        font-size:28px;box-shadow:0 8px 25px rgba(59,130,246,.5);animation:glowPulseSmall 3s ease-in-out infinite;">
                                △
                            </div>
                            <h4 style="margin:0;color:#dbeafe;font-size:24px;font-weight:900;
                                       font-family:'Space Grotesk',sans-serif;text-transform:uppercase;
                                       letter-spacing:1.5px;text-shadow:0 3px 15px rgba(59,130,246,.7);">
                                PARTIAL SIGNALS ({len(nice_partial)})
                            </h4>
                        </div>
                        <div style="display:grid;gap:14px;">
                    """, unsafe_allow_html=True)

                    for idx, (req, info) in enumerate(nice_partial, 1):
                        conf_pct = int(round(info.get("llm_confidence", 0.0) * 100))
                        sim_val = info.get("similarity", 0.0)
                        signals = f"~{conf_pct}% · Sim {sim_val:.2f}" if conf_pct > 0 else f"Sim {sim_val:.2f}"
                        
                        resume_html = _resume_snippet(info)
                        raw_rationale = (info.get("llm_rationale") or "").strip()
                        rationale = _clean_rationale(raw_rationale)
                        
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(59,130,246,.08),rgba(96,165,250,.05));
                                    border:2px solid rgba(59,130,246,.35);border-left:5px solid #3b82f6;
                                    border-radius:16px;padding:24px 28px;margin-bottom:16px;
                                    box-shadow:0 4px 20px rgba(59,130,246,.18),0 8px 32px rgba(59,130,246,.12);
                                    transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
                                    position:relative;overflow:hidden;cursor:pointer;">
                            <div style="position:absolute;top:0;right:0;width:140px;height:140px;
                                        background:radial-gradient(circle,rgba(59,130,246,.18),transparent 70%);
                                        pointer-events:none;"></div>
                            <div style="display:flex;align-items:flex-start;gap:18px;position:relative;">
                                <div style="width:48px;height:48px;min-width:48px;
                                            background:linear-gradient(135deg,#3b82f6,#60a5fa);
                                            border-radius:14px;display:flex;align-items:center;justify-content:center;
                                            font-size:24px;box-shadow:0 4px 16px rgba(59,130,246,.45),0 0 24px rgba(59,130,246,.25);">
                                    △
                                </div>
                                <div style="flex:1;">
                                    <div style="color:#f8fafc;font-size:17px;font-weight:700;margin-bottom:10px;
                                               line-height:1.5;font-family:'Inter',sans-serif;letter-spacing:-0.01em;">
                                        {html.escape(req)}
                                    </div>
                                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;">
                                        <span style="background:linear-gradient(135deg,rgba(59,130,246,.25),rgba(59,130,246,.15));
                                                     color:#dbeafe;padding:5px 14px;border-radius:10px;
                                                     font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace;
                                                     border:1px solid rgba(59,130,246,.3);
                                                     box-shadow:0 2px 8px rgba(59,130,246,.2);">
                                            {signals}
                                        </span>
                                    </div>
                                    {f'<div style="color:#bfdbfe;font-size:14px;margin-bottom:12px;line-height:1.7;font-style:italic;padding-left:12px;border-left:3px solid rgba(59,130,246,.4);font-family:\'Inter\',sans-serif;">{html.escape(rationale)}</div>' if rationale else ''}
                                    <div style="background:linear-gradient(135deg,rgba(15,23,42,.8),rgba(15,23,42,.6));
                                               border-radius:12px;padding:14px 18px;
                                               border:1px solid rgba(59,130,246,.25);
                                               box-shadow:inset 0 2px 8px rgba(0,0,0,.3);">
                                        <div style="color:#94a3b8;font-size:10px;font-weight:700;margin-bottom:6px;
                                                   text-transform:uppercase;letter-spacing:1px;font-family:'Inter',sans-serif;">
                                            📄 Evidence from Resume
                                        </div>
                                        <div style="color:#e2e8f0;font-size:13px;line-height:1.7;font-family:'Inter',sans-serif;">
                                            {resume_html}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div></div>", unsafe_allow_html=True)

                if nice_missing:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-top:28px;background:linear-gradient(135deg,rgba(99,102,241,.18),rgba(79,70,229,.16));
                                border:3px solid rgba(99,102,241,.5);border-radius:24px;padding:28px;
                                box-shadow:0 12px 45px rgba(99,102,241,.3),0 0 70px rgba(99,102,241,.2),inset 0 2px 0 rgba(255,255,255,.1);">
                        <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
                            <div style="width:52px;height:52px;background:linear-gradient(135deg,#6366f1,#4f46e5);
                                        border-radius:16px;display:flex;align-items:center;justify-content:center;
                                        font-size:28px;box-shadow:0 8px 25px rgba(99,102,241,.5);animation:glowPulseSmall 3s ease-in-out infinite;">
                                ○
                            </div>
                            <h4 style="margin:0;color:#93c5fd;font-size:24px;font-weight:900;
                                       font-family:'Space Grotesk',sans-serif;text-transform:uppercase;
                        letter-spacing:1.5px;text-shadow:0 3px 15px rgba(99,102,241,.7);">
                    NOT FOUND ({len(nice_missing)})
                            </h4>
                        </div>
                        <div style="display:grid;gap:14px;">
                    """, unsafe_allow_html=True)
                    
                    for idx, (req, info) in enumerate(nice_missing, 1):
                        sim_val = info.get("similarity", 0.0)
                        conf_pct = int(round(info.get("llm_confidence", 0.0) * 100))
                        signals = f"○ {conf_pct}% · Sim {sim_val:.2f}" if conf_pct > 0 else f"Sim {sim_val:.2f}"
                        
                        raw_rationale = (info.get("llm_rationale") or "Optional - not found").strip()
                        rationale = _clean_rationale(raw_rationale) or "Optional - not found"
                        
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(99,102,241,.06),rgba(79,70,229,.04));
                                    border:2px solid rgba(99,102,241,.28);border-left:5px solid #6366f1;
                                    border-radius:16px;padding:24px 28px;margin-bottom:16px;
                                    box-shadow:0 4px 20px rgba(99,102,241,.12),0 8px 32px rgba(99,102,241,.08);
                                    transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
                                    position:relative;overflow:hidden;cursor:pointer;opacity:0.88;">
                            <div style="position:absolute;top:0;right:0;width:140px;height:140px;
                                        background:radial-gradient(circle,rgba(99,102,241,.14),transparent 70%);
                                        pointer-events:none;"></div>
                            <div style="display:flex;align-items:flex-start;gap:18px;position:relative;">
                                <div style="width:48px;height:48px;min-width:48px;
                                            background:linear-gradient(135deg,#6366f1,#4f46e5);
                                            border-radius:14px;display:flex;align-items:center;justify-content:center;
                                            font-size:24px;box-shadow:0 4px 16px rgba(99,102,241,.35),0 0 24px rgba(99,102,241,.2);">
                                    ○
                                </div>
                                <div style="flex:1;">
                                    <div style="color:#cbd5e1;font-size:17px;font-weight:700;margin-bottom:10px;
                                               line-height:1.5;font-family:'Inter',sans-serif;letter-spacing:-0.01em;">
                                        {html.escape(req)}
                                    </div>
                                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;">
                                        <span style="background:linear-gradient(135deg,rgba(99,102,241,.2),rgba(99,102,241,.12));
                                                     color:#a5b4fc;padding:5px 14px;border-radius:10px;
                                                     font-size:12px;font-weight:700;font-family:'JetBrains Mono',monospace;
                                                     border:1px solid rgba(99,102,241,.25);
                                                     box-shadow:0 2px 8px rgba(99,102,241,.15);">
                                            {signals}
                                        </span>
                                    </div>
                                    <div style="color:#a5b4fc;font-size:14px;line-height:1.7;font-style:italic;
                                               padding:14px 18px;background:linear-gradient(135deg,rgba(99,102,241,.1),rgba(99,102,241,.06));
                                               border-radius:12px;border-left:3px solid rgba(99,102,241,.3);
                                               font-family:'Inter',sans-serif;
                                               box-shadow:inset 0 2px 8px rgba(0,0,0,.2);">
                                        ℹ️ {html.escape(rationale)}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
            else:
                st.info("⭐ No nice-to-have requirements specified for this position.")
        
        # ===== IMMERSIVE CANDIDATE ASSESSMENT =====
        st.markdown("""
        <div style="text-align:center;margin:56px 0 40px 0;position:relative;">
            <h3 class="section-header" style="display:inline-block;padding:24px 56px;
                       background:linear-gradient(135deg,rgba(139,92,246,.25),rgba(236,72,153,.22));
                       border-radius:28px;border:3px solid rgba(139,92,246,.6);
                       box-shadow:0 15px 60px rgba(139,92,246,.5),0 0 80px rgba(236,72,153,.4),inset 0 2px 0 rgba(255,255,255,.15);
                       backdrop-filter:blur(20px);font-size:36px;letter-spacing:3px;animation:headerGlow 3s ease-in-out infinite;">
                🎯 CANDIDATE ASSESSMENT
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        llm = analysis['llm_analysis']
        
        # Helper function to clean and format text
        def format_text(value):
            """Clean text from lists/dicts and format nicely."""
            if isinstance(value, list):
                # If it's a list, join with newlines or commas
                if value and isinstance(value[0], str):
                    return '<br>• '.join(str(v) for v in value if v)
                return str(value[0]) if value else 'N/A'
            elif isinstance(value, dict):
                # If it's a dict, extract relevant text
                if 'text' in value:
                    return str(value['text'])
                elif 'content' in value:
                    return str(value['content'])
                # Otherwise join values
                return ' '.join(str(v) for v in value.values() if v)
            elif isinstance(value, str):
                return value
            else:
                return str(value) if value else 'N/A'
        
        # Top Strengths Section - Ultra Immersive
        strengths = llm.get('top_strengths', [])[:4]
        if strengths:
            st.markdown("""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(16,185,129,.22),rgba(5,150,105,.20));
                        border:3px solid rgba(16,185,129,.6);border-radius:32px;padding:40px;
                        box-shadow:0 20px 70px rgba(16,185,129,.45),0 0 100px rgba(16,185,129,.35),inset 0 2px 0 rgba(255,255,255,.1);
                        margin-bottom:32px;position:relative;overflow:hidden;">
                <div style="position:absolute;inset:0;background:radial-gradient(circle at top left,rgba(16,185,129,.15),transparent 60%);
                            pointer-events:none;"></div>
                <div style="display:flex;align-items:center;gap:20px;margin-bottom:28px;position:relative;z-index:1;">
                    <div style="width:72px;height:72px;background:linear-gradient(135deg,#10b981,#059669,#047857);
                                border-radius:20px;display:flex;align-items:center;justify-content:center;
                                font-size:36px;box-shadow:0 12px 40px rgba(16,185,129,.6),0 0 60px rgba(16,185,129,.4);
                                animation:glowPulseSmall 3s ease-in-out infinite;">
                        💪
                    </div>
                    <h3 style="margin:0;color:#6ee7b7;font-size:30px;font-weight:900;font-family:'Space Grotesk',sans-serif;
                               text-transform:uppercase;letter-spacing:2px;text-shadow:0 4px 20px rgba(16,185,129,.8);">
                        Top Strengths
                    </h3>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-top:24px;position:relative;z-index:1;">
            """, unsafe_allow_html=True)
            
            for idx, s in enumerate(strengths, 1):
                # Format the strength text
                strength_text = format_text(s)
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                            padding:26px;border-radius:20px;border-left:5px solid #10b981;
                            backdrop-filter:blur(25px);transition:all .4s cubic-bezier(.34,1.56,.64,1);
                            position:relative;overflow:hidden;border:2px solid rgba(16,185,129,.3);
                            box-shadow:0 8px 25px rgba(16,185,129,.2);">
                    <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(16,185,129,.08),transparent);
                                opacity:0;transition:opacity .4s ease;"></div>
                    <div style="position:absolute;top:14px;right:14px;width:40px;height:40px;
                                background:linear-gradient(135deg,rgba(16,185,129,.35),rgba(16,185,129,.25));
                                border-radius:50%;display:flex;align-items:center;justify-content:center;
                                font-size:16px;font-weight:900;color:#6ee7b7;
                                border:2px solid rgba(16,185,129,.6);box-shadow:0 4px 15px rgba(16,185,129,.4);">
                        {idx}
                    </div>
                    <p style="margin:0;color:#f1f5f9;font-size:16px;line-height:1.9;padding-right:50px;font-weight:600;">
                        ✓ {strength_text}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Grid Layout for Cultural & Technical Fit
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            cultural_fit = format_text(llm.get('cultural_fit', 'N/A'))
            st.markdown(f"""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(99,102,241,.22),rgba(139,92,246,.20));
                        border:3px solid rgba(99,102,241,.6);border-radius:28px;padding:38px;
                        box-shadow:0 18px 65px rgba(99,102,241,.4),0 0 90px rgba(139,92,246,.3),inset 0 2px 0 rgba(255,255,255,.1);
                        height:100%;position:relative;overflow:hidden;">
                <div style="position:absolute;inset:0;background:radial-gradient(circle at bottom right,rgba(99,102,241,.15),transparent 60%);
                            pointer-events:none;"></div>
                <div style="display:flex;align-items:center;gap:20px;margin-bottom:24px;position:relative;z-index:1;">
                    <div style="width:72px;height:72px;background:linear-gradient(135deg,#6366f1,#8b5cf6,#4f46e5);
                                border-radius:20px;display:flex;align-items:center;justify-content:center;
                                font-size:36px;box-shadow:0 12px 40px rgba(99,102,241,.6),0 0 60px rgba(139,92,246,.4);
                                animation:glowPulseSmall 3s ease-in-out infinite;">
                        🤝
                    </div>
                    <h3 style="margin:0;color:#c7d2fe;font-size:26px;font-weight:900;font-family:'Space Grotesk',sans-serif;
                               text-transform:uppercase;letter-spacing:2px;text-shadow:0 4px 20px rgba(99,102,241,.8);">
                        Cultural Fit
                    </h3>
                </div>
                <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                            padding:28px;border-radius:20px;border-left:5px solid #6366f1;
                            backdrop-filter:blur(25px);border:2px solid rgba(99,102,241,.3);
                            box-shadow:0 8px 25px rgba(99,102,241,.2);position:relative;z-index:1;">
                    <p style="margin:0;color:#f1f5f9;font-size:16px;line-height:1.9;font-weight:500;">
                        {cultural_fit}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            technical_strength = format_text(llm.get('technical_strength', 'N/A'))
            st.markdown(f"""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(236,72,153,.22),rgba(139,92,246,.20));
                        border:3px solid rgba(236,72,153,.6);border-radius:28px;padding:38px;
                        box-shadow:0 18px 65px rgba(236,72,153,.4),0 0 90px rgba(139,92,246,.3),inset 0 2px 0 rgba(255,255,255,.1);
                        height:100%;position:relative;overflow:hidden;">
                <div style="position:absolute;inset:0;background:radial-gradient(circle at bottom left,rgba(236,72,153,.15),transparent 60%);
                            pointer-events:none;"></div>
                <div style="display:flex;align-items:center;gap:20px;margin-bottom:24px;position:relative;z-index:1;">
                    <div style="width:72px;height:72px;background:linear-gradient(135deg,#ec4899,#8b5cf6,#d946ef);
                                border-radius:20px;display:flex;align-items:center;justify-content:center;
                                font-size:36px;box-shadow:0 12px 40px rgba(236,72,153,.6),0 0 60px rgba(139,92,246,.4);
                                animation:glowPulseSmall 3s ease-in-out infinite;">
                        ⚙️
                    </div>
                    <h3 style="margin:0;color:#fbcfe8;font-size:26px;font-weight:900;font-family:'Space Grotesk',sans-serif;
                               text-transform:uppercase;letter-spacing:2px;text-shadow:0 4px 20px rgba(236,72,153,.8);">
                        Technical Fit
                    </h3>
                </div>
                <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                            padding:28px;border-radius:20px;border-left:5px solid #ec4899;
                            backdrop-filter:blur(25px);border:2px solid rgba(236,72,153,.3);
                            box-shadow:0 8px 25px rgba(236,72,153,.2);position:relative;z-index:1;">
                    <p style="margin:0;color:#f1f5f9;font-size:16px;line-height:1.9;font-weight:500;">
                        {technical_strength}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Development Areas Section - Enhanced
        st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
        dev_areas = llm.get('improvement_areas', [])[:3]
        if dev_areas:
            st.markdown("""
            <div class="metric-card" style="background:linear-gradient(135deg,rgba(245,158,11,.22),rgba(217,119,6,.20));
                        border:3px solid rgba(245,158,11,.6);border-radius:32px;padding:40px;
                        box-shadow:0 20px 70px rgba(245,158,11,.45),0 0 100px rgba(245,158,11,.35),inset 0 2px 0 rgba(255,255,255,.1);
                        position:relative;overflow:hidden;">
                <div style="position:absolute;inset:0;background:radial-gradient(circle at top right,rgba(245,158,11,.15),transparent 60%);
                            pointer-events:none;"></div>
                <div style="display:flex;align-items:center;gap:20px;margin-bottom:28px;position:relative;z-index:1;">
                    <div style="width:72px;height:72px;background:linear-gradient(135deg,#f59e0b,#d97706,#b45309);
                                border-radius:20px;display:flex;align-items:center;justify-content:center;
                                font-size:36px;box-shadow:0 12px 40px rgba(245,158,11,.6),0 0 60px rgba(245,158,11,.4);
                                animation:glowPulseSmall 3s ease-in-out infinite;">
                        📈
                    </div>
                    <h3 style="margin:0;color:#fcd34d;font-size:30px;font-weight:900;font-family:'Space Grotesk',sans-serif;
                               text-transform:uppercase;letter-spacing:2px;text-shadow:0 4px 20px rgba(245,158,11,.8);">
                        Development Areas
                    </h3>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:24px;position:relative;z-index:1;">
            """, unsafe_allow_html=True)
            
            for idx, area in enumerate(dev_areas, 1):
                area_text = format_text(area)
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                            padding:26px;border-radius:20px;border-left:5px solid #f59e0b;
                            backdrop-filter:blur(25px);display:flex;align-items:start;gap:16px;
                            transition:all .4s cubic-bezier(.34,1.56,.64,1);border:2px solid rgba(245,158,11,.3);
                            box-shadow:0 8px 25px rgba(245,158,11,.2);position:relative;overflow:hidden;">
                    <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(245,158,11,.08),transparent);
                                opacity:0;transition:opacity .4s ease;"></div>
                    <span style="flex-shrink:0;width:42px;height:42px;
                                background:linear-gradient(135deg,rgba(245,158,11,.35),rgba(245,158,11,.25));
                                border-radius:50%;display:flex;align-items:center;justify-content:center;
                                font-size:18px;font-weight:900;color:#fcd34d;
                                border:2px solid rgba(245,158,11,.6);box-shadow:0 4px 15px rgba(245,158,11,.4);
                                position:relative;z-index:1;">
                        {idx}
                    </span>
                    <p style="margin:0;color:#f1f5f9;font-size:16px;line-height:1.9;font-weight:600;position:relative;z-index:1;">
                        {area_text}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
        
        # ===== Final Recommendation - Immersive =====
        st.markdown("""
        <div class="metric-card" style="margin-top:32px;background:linear-gradient(135deg,rgba(99,102,241,.22),rgba(236,72,153,.20));
                    border:3px solid rgba(99,102,241,.6);border-radius:28px;padding:36px;
                    box-shadow:0 18px 65px rgba(99,102,241,.4),0 0 90px rgba(236,72,153,.3),inset 0 2px 0 rgba(255,255,255,.1);
                    position:relative;overflow:hidden;">
            <div style="position:absolute;inset:0;background:radial-gradient(circle at center,rgba(99,102,241,.12),transparent 70%);
                        pointer-events:none;"></div>
            <div style="display:flex;align-items:center;gap:18px;margin-bottom:20px;position:relative;z-index:1;">
                <div style="font-size:34px;">📋</div>
                <h3 style="margin:0;color:#c7d2fe;font-size:26px;font-weight:900;text-transform:uppercase;
                           font-family:'Space Grotesk',sans-serif;letter-spacing:2px;
                           text-shadow:0 4px 20px rgba(99,102,241,.8);">Final Recommendation</h3>
            </div>
            <p style="margin:0;font-size:16px;line-height:1.9;color:#f1f5f9;font-weight:500;position:relative;z-index:1;">
        """ + format_text(llm.get('overall_comment', 'Pending analysis'))[:500] + """
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ===== Download Results =====
        st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
        payload = json.dumps(analysis, ensure_ascii=False, indent=2)
        
        # Immersive download section with animations
        st.markdown("""
        <div style="
            background:linear-gradient(135deg,rgba(99,102,241,.12),rgba(139,92,246,.1),rgba(236,72,153,.08));
            border-radius:20px;
            padding:32px 28px;
            text-align:center;
            box-shadow:0 6px 30px rgba(99,102,241,.2),0 0 50px rgba(139,92,246,.1);
            backdrop-filter:blur(25px) saturate(180%);
            margin-top:40px;
            margin-bottom:24px;
            animation:fadeInRotate 0.6s ease-out;
        ">
            <div style="display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:8px;">
                <span style="
                    font-size:36px;
                    animation:bounce 1.2s ease-in-out infinite;
                ">📥</span>
                <span style="
                    font-size:22px;
                    font-weight:800;
                    background:linear-gradient(135deg,#c7d2fe,#ec4899);
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                    background-clip:text;
                    font-family:'Space Grotesk',sans-serif;
                    letter-spacing:0.5px;
                ">Export Analysis Report</span>
            </div>
            <p style="
                margin:8px 0 0 0;
                color:#cbd5e1;
                font-size:14px;
                font-weight:500;
                font-family:'Inter',sans-serif;
            ">
                Download comprehensive JSON with all metrics, scoring details & insights
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced download button styling
        st.markdown("""
        <style>
        /* Premium Download Button Styling */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #ec4899 100%) !important;
            background-size: 200% 200% !important;
            color: #ffffff !important;
            border: 2px solid rgba(139, 92, 246, 0.6) !important;
            border-radius: 22px !important;
            padding: 18px 48px !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 800 !important;
            font-size: 15px !important;
            letter-spacing: 1.2px !important;
            text-transform: uppercase !important;
            transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
            box-shadow: 0 15px 50px rgba(139, 92, 246, 0.5), 0 0 60px rgba(236, 72, 153, 0.3), inset 0 2px 0 rgba(255, 255, 255, 0.3), inset 0 -2px 0 rgba(0, 0, 0, 0.2) !important;
            position: relative !important;
            overflow: hidden !important;
            animation: gradientSlide 4s ease infinite !important;
            width: 100% !important;
            height: auto !important;
            min-height: 56px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        .stDownloadButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.4), transparent 70%);
            transform: translate(-50%, -50%);
            transition: width 0.7s cubic-bezier(0.4, 0, 0.2, 1), height 0.7s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
        }
        
        .stDownloadButton > button:hover {
            transform: translateY(-6px) scale(1.05) !important;
            box-shadow: 0 25px 80px rgba(139, 92, 246, 0.7), 0 0 90px rgba(236, 72, 153, 0.6), 0 0 120px rgba(99, 102, 241, 0.4), inset 0 2px 0 rgba(255, 255, 255, 0.4) !important;
            border-color: rgba(139, 92, 246, 0.9) !important;
        }
        
        .stDownloadButton > button:hover::before {
            width: 400px;
            height: 400px;
        }
        
        .stDownloadButton > button:active {
            transform: translateY(-3px) scale(0.98) !important;
        }
        
        @keyframes gradientSlide {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.download_button(
            "📥 Download Full Analysis (JSON)",
            data=payload.encode('utf-8'),
            file_name=f"analysis_{resume['name'].replace(' ','_')}_{int(time.time())}.json",
            use_container_width=True,
            type="primary"
        )

# --- Recent tab ---
with tab2:
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    
    # Get recent analyses from database only
    recent_db = get_recent(db_conn, db_ok, limit=20)
    all_activities = []
    
    # Add database records (persistent analyses only)
    for db_record in recent_db:
        all_activities.append({
            "type": "analysis",
            "name": db_record.get("candidate", "Unknown"),
            "score": float(db_record.get("final_score", 0)) * 10,  # Scale 0-1 to 0-10
            "semantic": float(db_record.get("semantic_score", 0)) * 10,  # Scale 0-1 to 0-10
            "coverage": float(db_record.get("coverage_score", 0)) * 10,  # Scale 0-1 to 0-10
            "fit": float(db_record.get("fit_score", 0)),  # Already stored as 0-10 integer
            "email": db_record.get("email", "N/A"),
            "file": "Resume",
            "timestamp": db_record.get("timestamp", 0),
            "emoji": "✨",
            "source": "database"
        })
    
    if not all_activities:
        st.markdown("""
        <div style="
            background:linear-gradient(135deg,rgba(99,102,241,.1),rgba(139,92,246,.08));
            border-radius:16px;
            padding:48px 32px;
            text-align:center;
            backdrop-filter:blur(20px);
        ">
            <p style="
                margin:0;
                color:#94a3b8;
                font-size:16px;
                font-weight:600;
                font-family:'Inter',sans-serif;
            ">📭 No screening history yet</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px;">
            <span style="font-size:28px;">🕒</span>
            <span style="
                font-size:20px;
                font-weight:800;
                color:#e2e8f0;
                font-family:'Space Grotesk',sans-serif;
            ">Screening History</span>
            <span style="
                background:linear-gradient(135deg,#8b5cf6,#ec4899);
                color:#fff;
                padding:4px 14px;
                border-radius:12px;
                font-size:13px;
                font-weight:700;
                margin-left:auto;
            ">{}</span>
        </div>
        """.format(len(all_activities)), unsafe_allow_html=True)
        
        for idx, activity in enumerate(all_activities):
            t = datetime.fromtimestamp(activity["timestamp"]).strftime('%b %d, %Y • %I:%M %p')
            score = activity.get("score", 0)
            color_class = "score-excellent" if score >= 8 else "score-good" if score >= 6 else "score-fair" if score >= 4 else "score-poor"
            source_badge = "💾"
            source_tooltip = "Saved to database"
            
            st.markdown(f"""
            <div style="
                background:linear-gradient(135deg,rgba(236,72,153,.08),rgba(139,92,246,.06));
                border-left:4px solid rgba(236,72,153,.5);
                border-radius:14px;
                padding:20px 24px;
                margin-bottom:16px;
                box-shadow:0 4px 16px rgba(0,0,0,.15),0 0 30px rgba(236,72,153,.1);
                backdrop-filter:blur(20px);
                animation:fadeInRotate 0.5s ease-out;
                animation-delay:{idx * 0.05}s;
            ">
                <div style="display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;">
                    <div>
                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                            <span style="font-size:24px;">{activity['emoji']}</span>
                            <span style="
                                font-size:17px;
                                font-weight:800;
                                color:#f1f5f9;
                                font-family:'Space Grotesk',sans-serif;
                            ">{activity['name']}</span>
                            <span title="{source_tooltip}" style="
                                font-size:14px;
                                opacity:0.7;
                            ">{source_badge}</span>
                        </div>
                        <div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:8px;">
                            <span style="color:#cbd5e1;font-size:13px;"><strong>Email:</strong> {activity['email']}</span>
                            <span style="color:#cbd5e1;font-size:13px;"><strong>File:</strong> {activity['file']}</span>
                        </div>
                        <div style="color:#94a3b8;font-size:12px;margin-top:8px;font-weight:500;">{t}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="
                            font-size:32px;
                            font-weight:900;
                            background:linear-gradient(135deg,#6ee7b7 0%,#10b981 100%);
                            -webkit-background-clip:text;
                            -webkit-text-fill-color:transparent;
                            background-clip:text;
                            line-height:1;
                            margin-bottom:8px;
                        ">{score:.1f}</div>
                        <div style="
                            font-size:11px;
                            color:#cbd5e1;
                            font-weight:600;
                            font-family:'Inter',sans-serif;
                        ">Overall Score</div>
                        <div style="
                            display:grid;
                            grid-template-columns:1fr 1fr 1fr;
                            gap:8px;
                            margin-top:10px;
                            font-size:11px;
                        ">
                            <div style="color:#94a3b8;"><strong>📊</strong> {activity['coverage']:.1f}</div>
                            <div style="color:#94a3b8;"><strong>🧠</strong> {activity['semantic']:.1f}</div>
                            <div style="color:#94a3b8;"><strong>⚡</strong> {activity['fit']:.1f}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ===== IMMERSIVE FOOTER =====
st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="
    text-align:center;
    padding:40px 0;
    position:relative;
">
    <div style="
        position:absolute;
        top:0;
        left:50%;
        transform:translateX(-50%);
        width:120px;
        height:2px;
        background:linear-gradient(90deg,transparent,rgba(139,92,246,.5),transparent);
        margin-bottom:40px;
    "></div>
    <p style="
        margin:32px 0 0 0;
        font-size:14px;
        font-weight:600;
        background:linear-gradient(135deg,#8b5cf6,#ec4899);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        background-clip:text;
        font-family:'Space Grotesk',sans-serif;
        letter-spacing:0.5px;
    ">
        Created by <span style="font-weight:900;">Sachin S</span> from <span style="font-weight:900;">VIT Chennai</span>
    </p>
</div>
""", unsafe_allow_html=True)
