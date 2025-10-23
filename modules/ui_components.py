"""
UI Component Helpers
"""
import streamlit as st

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

