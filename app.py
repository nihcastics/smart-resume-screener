"""
Smart Resume Screener - Modular Version
"""
from modules.config import CSS
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import tempfile
import json
from datetime import datetime

from modules.models import load_models
from modules.database import init_postgresql, save_to_db, get_recent
from modules.text_processing import normalize_text, chunk_text, parse_contacts, build_index, extract_sections, token_set, contains_atom, extract_atoms_from_text, refine_atom_list, extract_structured_entities, extract_technical_skills
from modules.llm_operations import llm_json, jd_plan_prompt, resume_profile_prompt, atomicize_requirements_prompt, analysis_prompt, llm_verify_requirements_clean
from modules.scoring import compute_global_semantic, evaluate_requirement_coverage, compute_cue_alignment, build_competency_catalog, compute_competency_scores, map_atoms_to_competencies
from modules.resume_parser import parse_resume_pdf
from modules.ui_components import section

st.set_page_config(layout="wide", page_title="Smart Resume Screener", page_icon="🎯", initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

if "models_loaded" not in st.session_state:
    with st.spinner("🔄 Loading AI models..."):
        model, nlp, embedder, models_ok = load_models()
        st.session_state["model"] = model
        st.session_state["nlp"] = nlp
        st.session_state["embedder"] = embedder
        st.session_state["models_loaded"] = models_ok
else:
    model = st.session_state.get("model")
    nlp = st.session_state.get("nlp")
    embedder = st.session_state.get("embedder")
    models_ok = st.session_state.get("models_loaded", False)

if "db_initialized" not in st.session_state:
    db_conn, db_ok = init_postgresql()
    st.session_state["db_conn"] = db_conn
    st.session_state["db_ok"] = db_ok
    st.session_state["db_initialized"] = True
else:
    db_conn = st.session_state.get("db_conn")
    db_ok = st.session_state.get("db_ok", False)

st.markdown("""
<div style="text-align:center;padding:40px 0 60px 0;">
    <h1 style="font-size:4.5rem;font-weight:900;background:linear-gradient(135deg,#8b5cf6 0%,#ec4899 50%,#6366f1 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:20px;
        letter-spacing:-0.04em;text-shadow:0 8px 32px rgba(139,92,246,0.4);">🎯 Smart Resume Screener</h1>
    <p style="font-size:1.35rem;color:#a78bfa;font-weight:600;letter-spacing:1px;text-shadow:0 2px 8px rgba(139,92,246,0.3);">
        AI-Powered Candidate Evaluation System</p>
</div>
""", unsafe_allow_html=True)

if models_ok:
    model_name = st.session_state.get("gemini_model_name", "Unknown")
    st.success(f"✅ **AI Models Loaded Successfully!** Using Google Gemini: `{model_name}`")
else:
    st.error("❌ **AI Models Not Available** - Please check your GEMINI_API_KEY in `.env` file")
    st.info("💡 Get a FREE API key at: https://makersuite.google.com/app/apikey")
    st.stop()

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

tab1, tab2 = st.tabs(["📄 Analyze", "🕒 Recent"])

with tab1:
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    uploaded_file = st.session_state.get('uploaded_file', None)
    job_description = st.session_state.get('job_description', '')
    
    step_placeholder = st.empty()
    if not uploaded_file:
        step_placeholder.markdown("""
        <div style="background:linear-gradient(135deg,rgba(99,102,241,.18),rgba(139,92,246,.15));
            border:2px solid rgba(99,102,241,.4);border-radius:20px;padding:20px 32px;text-align:center;margin-bottom:24px;">
            <span style="font-size:32px;">👆</span>
            <span style="font-size:17px;font-weight:700;color:#c7d2fe;">Step 1: Upload a resume PDF file</span>
        </div>
        """, unsafe_allow_html=True)
    elif not job_description or len(job_description) < 50:
        step_placeholder.markdown("""
        <div style="background:linear-gradient(135deg,rgba(236,72,153,.18),rgba(139,92,246,.15));
            border:2px solid rgba(236,72,153,.4);border-radius:20px;padding:20px 32px;text-align:center;margin-bottom:24px;">
            <span style="font-size:32px;">👉</span>
            <span style="font-size:17px;font-weight:700;color:#fbbf24;">Step 2: Add job description (minimum 50 characters)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        step_placeholder.markdown("""
        <div style="background:linear-gradient(135deg,rgba(16,185,129,.18),rgba(5,150,105,.15));
            border:2px solid rgba(16,185,129,.5);border-radius:20px;padding:20px 32px;text-align:center;margin-bottom:24px;">
            <span style="font-size:32px;">✅</span>
            <span style="font-size:17px;font-weight:700;color:#6ee7b7;">Ready! Click button below to start analysis</span>
            <span style="font-size:32px;">🚀</span>
        </div>
        """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1,1], gap="large")
    with c1:
        st.markdown("### 📄 Resume Upload")
        uploaded_file = st.file_uploader("Choose PDF file", type=['pdf'], key='uploaded_file',
            help="Upload candidate's resume in PDF format (max 10MB)")
    with c2:
        st.markdown("### 💼 Job Description")
        job_description = st.text_area("Paste job requirements", height=200,
            placeholder="Enter job description, required skills, qualifications...",
            key='job_description', help="Provide detailed job description for better matching")
    
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        analyze_btn = st.button("🚀 Analyze Resume", use_container_width=True,
            disabled=not (uploaded_file and job_description and len(job_description) >= 50))
    
    if analyze_btn:
        with st.spinner("🔍 Analyzing resume..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                
                progress = st.progress(0.1)
                st.info("📄 Parsing PDF resume...")
                resume_doc = parse_resume_pdf(tmp_path, nlp, embedder)
                
                progress.progress(0.3)
                st.info("🔍 Extracting requirements...")
                atoms = extract_atoms_from_text(job_description, nlp)
                atoms_clean = refine_atom_list(atoms, nlp, limit=50)
                must_atoms = [a for a in atoms_clean if len(a.split()) <= 3]
                nice_atoms = [a for a in atoms_clean if len(a.split()) > 3]
                
                progress.progress(0.5)
                st.info("🧠 Computing semantic similarities...")
                chunks = resume_doc.get('chunks', [])
                if chunks:
                    faiss_index, resume_embs = build_index(embedder, chunks)
                else:
                    faiss_index, resume_embs = None, None
                
                semantic_score = compute_global_semantic(embedder, resume_embs, job_description)
                
                progress.progress(0.7)
                st.info("📊 Evaluating requirement coverage...")
                coverage_result = evaluate_requirement_coverage(
                    must_atoms, nice_atoms, resume_doc.get('text', ''),
                    chunks, embedder, model, faiss_index)
                
                progress.progress(0.9)
                st.info("🤖 Generating final assessment...")
                analysis_prompt_text = analysis_prompt(
                    job_description, {"requirements": must_atoms + nice_atoms},
                    {"summary": resume_doc.get('text', '')[:2000]},
                    coverage_result, {}, semantic_score, coverage_result.get('overall', 0.5))
                llm_result = llm_json(model, analysis_prompt_text)
                
                coverage_score = coverage_result.get('overall', 0.5)
                llm_fit = llm_result.get('technical_strength', 50) / 100.0
                final_score = (semantic_score * 0.35 + coverage_score * 0.50 + llm_fit * 0.15) * 100
                
                progress.progress(1.0)
                st.success("✅ Analysis complete!")
                
                analysis = {
                    'candidate_name': resume_doc.get('name', 'Unknown'),
                    'email': resume_doc.get('email', 'Not found'),
                    'timestamp': datetime.now().timestamp(),
                    'score': final_score,
                    'semantic_score': semantic_score * 100,
                    'coverage_score': coverage_score * 100,
                    'llm_fit_score': llm_fit * 100,
                    'requirements': {'must': must_atoms, 'nice': nice_atoms},
                    'coverage_details': coverage_result,
                    'llm_analysis': llm_result,
                    'jd_text': job_description
                }
                
                st.session_state.analysis_history.insert(0, analysis)
                st.session_state['current_analysis'] = analysis
                if db_ok and db_conn:
                    save_to_db(resume_doc, job_description, analysis, db_conn, db_ok)
                
                st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
                st.markdown("## 📊 Analysis Results")
                score_class = (
                    "score-excellent" if final_score >= 75 else
                    "score-good" if final_score >= 60 else
                    "score-fair" if final_score >= 45 else "score-poor")
                st.markdown(f"""
                <div style="text-align:center;margin:40px 0;">
                    <div class="score-badge {score_class}">{final_score:.1f}</div>
                    <p style="margin-top:20px;font-size:1.2rem;color:#94a3b8;">Overall Match Score</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Coverage", f"{coverage_score*100:.1f}%")
                with col2:
                    st.metric("🧠 Semantic", f"{semantic_score*100:.1f}%")
                with col3:
                    st.metric("⚡ LLM Fit", f"{llm_fit*100:.1f}%")
                
                with st.expander("📋 Detailed Analysis", expanded=True):
                    st.markdown("**Top Strengths:**")
                    for strength in llm_result.get('top_strengths', [])[:4]:
                        st.markdown(f"- {strength}")
                    st.markdown("\n**Cultural Fit:**")
                    st.write(llm_result.get('cultural_fit', 'N/A'))
                    st.markdown("\n**Overall Comment:**")
                    st.write(llm_result.get('overall_comment', 'N/A'))
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

with tab2:
    st.markdown("## 🕒 Recent Analyses")
    if db_ok and db_conn:
        recent_items = get_recent(db_conn, db_ok, limit=20)
        if recent_items:
            for item in recent_items:
                score = item.get('final_score', 0) * 10
                st.markdown(f"""
                <div class="analysis-card">
                    <h4>💾 {item.get('candidate', 'Unknown')}</h4>
                    <p><strong>Score:</strong> {score:.1f}/10</p>
                    <p><strong>Date:</strong> {item.get('created_at', 'Unknown')}</p>
                    <p><strong>Email:</strong> {item.get('email', 'Not found')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent analyses in database")
    
    if st.session_state.analysis_history:
        st.markdown("### ⚡ Session History")
        for idx, activity in enumerate(st.session_state.analysis_history[:10]):
            score = activity.get('score', 0)
            name = activity.get('candidate_name', 'Unknown')
            st.markdown(f"""
            <div class="analysis-card">
                <h4>⚡ {name}</h4>
                <p><strong>Score:</strong> {score:.1f}/100</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:60px 0 40px 0;margin-top:80px;border-top:2px solid rgba(139,92,246,0.2);">
    <p style="font-size:14px;color:#64748b;margin:0;">Built with ❤️ using Streamlit, Google Gemini, FAISS & spaCy</p>
    <p style="font-size:12px;color:#475569;margin-top:8px;">© 2025 Smart Resume Screener | Powered by AI</p>
</div>
""", unsafe_allow_html=True)
