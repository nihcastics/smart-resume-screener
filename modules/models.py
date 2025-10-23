"""
Model Loading and Initialization
"""
import os
import streamlit as st
import spacy
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

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

