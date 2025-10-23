"""
Configuration and Constants
Contains CSS, environment setup, and application constants
"""
import os
import sys

# Environment setup
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['TORCH_CPP_LOG_LEVEL'] = 'ERROR'
os.environ['PYTORCH_JIT'] = '0'

# Suppress warnings
import warnings
import logging
import io

stderr_backup = sys.stderr
sys.stderr = io.StringIO()
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)

# Restore stderr after setup
sys.stderr = stderr_backup

# Gemini model fallback chain
GEMINI_MODELS = [
    "gemini-2.0-flash-exp",
    "gemini-exp-1206",
    "gemini-2.0-flash-thinking-exp-1219",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-1.0-pro"
]

# Block phrases for atom filtering
ATOM_BLOCK_PHRASES = {
    "as needed", "as required", "if any", "where applicable", "depending on", "based on",
    "bachelor degree", "master degree", "years experience", "strong understanding",
    "excellent communication", "good knowledge", "working knowledge", "team player",
    "self motivated", "attention detail", "problem solving", "time management",
    "etc", "and or", "including but not limited", "preferably", "preferred",
    "ability to", "able to", "capable of", "skills in", "experience in",
    "knowledge of", "familiarity with", "understanding of", "proficiency in",
    "expertise in", "competency in", "qualification in", "background in"
}

# Generic tokens to filter out
ATOM_GENERIC_TOKENS = {
    "experience", "skills", "knowledge", "understanding", "ability", "strong",
    "excellent", "good", "required", "preferred", "plus", "bonus", "nice",
    "must", "should", "will", "can", "may", "including", "such", "other",
    "related", "relevant", "similar", "equivalent", "additional", "minimum",
    "years", "year", "degree", "bachelor", "master", "phd", "certification"
}

# Scoring weights
DEFAULT_WEIGHTS = {
    'semantic': 0.35,
    'coverage': 0.50,
    'llm_fit': 0.15
}

# Fuzzy matching thresholds
SIMILARITY_THRESHOLDS = {
    'strict': 0.28,      # Full match (credit: 1.0)
    'partial': 0.18,     # Partial match (credit: 0.6)
    'weak': 0.13         # Weak match (credit: 0.3)
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ===== STUNNING MODERN DESIGN SYSTEM ===== */
:root {
    /* Beautiful Gradient Palette */
    --gradient-hero: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
    --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    --gradient-secondary: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
    --gradient-success: linear-gradient(135deg, #10b981 0%, #34d399 100%);
    --gradient-warning: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
    --gradient-info: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
    --gradient-soft: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
    
    /* Premium Backgrounds */
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-tertiary: #f3f4f6;
    --bg-glass: rgba(255, 255, 255, 0.7);
    
    /* Beautiful Text Colors */
    --text-primary: #111827;
    --text-secondary: #374151;
    --text-tertiary: #6b7280;
    --text-quaternary: #9ca3af;
    
    /* Elegant Borders */
    --border-color: #e5e7eb;
    --border-light: #f3f4f6;
    --border-focus: #6366f1;
    
    /* Professional Shadows */
    --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.3);
    --shadow-glow-pink: 0 0 40px rgba(236, 72, 153, 0.3);
    --shadow-glow-green: 0 0 40px rgba(16, 185, 129, 0.3);
    
    /* Smooth Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-smooth: 300ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* ===== CLEAN GLOBAL FOUNDATION ===== */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"], .main, .stApp {
    background: var(--bg-primary) !important;
    overflow-x: hidden;
    scroll-behavior: smooth;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* ===== BEAUTIFUL ANIMATED BACKGROUND ===== */
.stApp {
    position: relative;
    min-height: 100vh;
    background: 
        radial-gradient(ellipse at top, #f9fafb 0%, #ffffff 50%),
        linear-gradient(180deg, #ffffff 0%, #f9fafb 100%) !important;
}

.stApp::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.05) 0%, transparent 40%),
        radial-gradient(circle at 85% 80%, rgba(236, 72, 153, 0.05) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
    animation: gentleFloat 20s ease-in-out infinite;
}

@keyframes gentleFloat {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    50% { transform: translate(20px, 20px) rotate(1deg); }
}

/* ===== STUNNING TYPOGRAPHY ===== */
h1 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: clamp(2.5rem, 5vw, 4rem) !important;
    letter-spacing: -0.05em !important;
    line-height: 1.1 !important;
    background: var(--gradient-hero);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeSlideUp 0.8s cubic-bezier(0.23, 1, 0.32, 1) backwards;
}

h2 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: clamp(1.875rem, 4vw, 3rem) !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
    line-height: 1.2 !important;
    animation: fadeSlideUp 0.8s cubic-bezier(0.23, 1, 0.32, 1) 0.1s backwards;
}

h3 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    font-size: clamp(1.5rem, 3vw, 2.25rem) !important;
    color: var(--text-secondary) !important;
    letter-spacing: -0.02em !important;
    line-height: 1.3 !important;
}

h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    letter-spacing: -0.01em !important;
}

p, span, div, label {
    color: var(--text-tertiary) !important;
    line-height: 1.6 !important;
    font-size: 1rem !important;
}

/* ===== MODERN TAB NAVIGATION ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: var(--bg-glass);
    border: none !important;
    border-bottom: 1px solid var(--border-color) !important;
    padding: 8px 16px;
    border-radius: 16px 16px 0 0;
    backdrop-filter: blur(12px) saturate(180%);
    box-shadow: var(--shadow-sm);
    animation: fadeSlideDown 0.6s cubic-bezier(0.23, 1, 0.32, 1) backwards;
}

.stTabs [data-baseweb="tab"] {
    height: 44px;
    padding: 0 24px;
    background: transparent;
    border: none !important;
    border-radius: 12px;
    color: var(--text-tertiary);
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0px;
    transition: all var(--transition-smooth);
    position: relative;
    overflow: hidden;
}

.stTabs [data-baseweb="tab"]::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--gradient-primary);
    opacity: 0;
    transition: opacity var(--transition-smooth);
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
}

.stTabs [aria-selected="true"] {
    color: #ffffff !important;
}

.stTabs [aria-selected="true"]::before {
    opacity: 1;
}

/* ===== BEAUTIFUL GRADIENT BUTTONS ===== */
.stButton > button {
    background: var(--gradient-primary);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 14px 32px;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.3px;
    transition: all var(--transition-smooth);
    box-shadow: var(--shadow-md), 0 0 0 0 rgba(99, 102, 241, 0.4);
    position: relative;
    overflow: hidden;
    cursor: pointer;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    transform: translate(-50%, -50%);
    transition: width var(--transition-slow), height var(--transition-slow);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl), var(--shadow-glow);
}

.stButton > button:hover::before {
    width: 300px;
    height: 300px;
}

.stButton > button:active {
    transform: translateY(0);
}

/* ===== PREMIUM FILE UPLOADER ===== */
.stFileUploader {
    background: var(--bg-glass);
    border: 2px dashed var(--border-color);
    border-radius: 16px;
    padding: 32px;
    transition: all var(--transition-smooth);
    backdrop-filter: blur(12px);
    box-shadow: var(--shadow-sm);
}

.stFileUploader:hover {
    border-color: var(--border-focus);
    border-style: solid;
    background: rgba(99, 102, 241, 0.02);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.stFileUploader button,
.stFileUploader section,
.stFileUploader label,
.stFileUploader div[data-testid="stFileUploaderDropzone"] {
    pointer-events: auto !important;
}

/* ===== CLEAN TEXT AREAS ===== */
.stTextArea textarea {
    background: var(--bg-primary) !important;
    border: 2px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', monospace !important;
    font-size: 14px !important;
    padding: 16px !important;
    transition: all var(--transition-smooth) !important;
    line-height: 1.6 !important;
    box-shadow: var(--shadow-xs) !important;
}

.stTextArea textarea:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1), var(--shadow-md) !important;
    outline: none !important;
}

/* ===== GLASSMORPHIC CARDS ===== */
.metric-card, .analysis-card {
    background: var(--bg-glass);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    transition: all var(--transition-smooth);
    backdrop-filter: blur(12px) saturate(180%);
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}

.metric-card::before, .analysis-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-primary);
    opacity: 0;
    transition: opacity var(--transition-smooth);
}

.metric-card::after, .analysis-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.05), transparent 60%);
    opacity: 0;
    transition: opacity var(--transition-smooth);
    pointer-events: none;
}

.metric-card:hover, .analysis-card:hover {
    border-color: rgba(99, 102, 241, 0.2);
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
}

.metric-card:hover::before, .analysis-card:hover::before {
    opacity: 1;
}

.metric-card:hover::after, .analysis-card:hover::after {
    opacity: 1;
}

/* ===== VIBRANT SCORE BADGES ===== */
.score-badge {
    display: inline-block;
    padding: 16px 40px;
    border-radius: 20px;
    font-family: 'Outfit', sans-serif;
    font-weight: 900;
    font-size: 44px;
    box-shadow: var(--shadow-lg);
    transition: all var(--transition-smooth);
    position: relative;
    letter-spacing: -0.02em;
}

.score-badge:hover {
    transform: scale(1.05) translateY(-4px);
    box-shadow: var(--shadow-2xl);
}

.score-excellent {
    background: var(--gradient-success);
    color: #ffffff;
    box-shadow: var(--shadow-lg), var(--shadow-glow-green);
}

.score-good {
    background: var(--gradient-info);
    color: #ffffff;
    box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.score-fair {
    background: var(--gradient-warning);
    color: #ffffff;
    box-shadow: var(--shadow-lg), 0 0 40px rgba(245, 158, 11, 0.3);
}

.score-poor {
    background: var(--gradient-secondary);
    color: #ffffff;
    box-shadow: var(--shadow-lg), var(--shadow-glow-pink);
}

/* ===== MODERN CHIPS ===== */
.chip {
    display: inline-block;
    margin: 4px 6px 4px 0;
    padding: 6px 16px;
    border-radius: 16px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    font-size: 13px;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    color: var(--text-secondary);
    transition: all var(--transition-base);
    box-shadow: var(--shadow-xs);
}

.chip:hover {
    background: var(--bg-primary);
    border-color: var(--border-focus);
    transform: translateY(-2px);
    box-shadow: var(--shadow-sm);
    color: var(--text-primary);
}

/* ===== ELEGANT DIVIDERS ===== */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    margin: 24px 0;
    position: relative;
}

hr::before {
    content: '';
    position: absolute;
    top: -1.5px;
    left: 50%;
    transform: translateX(-50%);
    width: 48px;
    height: 3px;
    background: var(--gradient-primary);
    border-radius: 2px;
}

/* ===== CLEAN EXPANDERS ===== */
.stExpander {
    background: var(--bg-glass) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    transition: all var(--transition-base) !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: var(--shadow-xs) !important;
}

.stExpander:hover {
    border-color: rgba(99, 102, 241, 0.2) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stExpander [data-testid="stExpanderToggleButton"] {
    color: var(--text-primary) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

/* ===== SMOOTH PROGRESS BAR ===== */
.stProgress {
    margin: 16px 0;
    height: 8px !important;
}

.stProgress > div {
    background: var(--bg-tertiary);
    border-radius: 8px !important;
    overflow: hidden !important;
    height: 8px !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
}

.stProgress > div > div {
    background: var(--gradient-primary);
    border-radius: 8px !important;
    height: 8px !important;
    transition: width var(--transition-smooth) !important;
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.4);
    position: relative;
    overflow: hidden;
}

.stProgress > div > div::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
    to { left: 100%; }
}

/* ===== MINIMAL SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-tertiary);
}

::-webkit-scrollbar-thumb {
    background: var(--gradient-primary);
    border-radius: 8px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #5558f1 0%, #7b4cf6 100%);
}

/* ===== GRADIENT TEXT UTILITY ===== */
.section-header {
    font-size: 2rem;
    font-weight: 800;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
    letter-spacing: -0.02em;
    font-family: 'Outfit', sans-serif !important;
}

/* ===== SMOOTH ANIMATIONS ===== */
@keyframes fadeSlideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeSlideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.96);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.metric-card {
    animation: scaleIn 0.5s cubic-bezier(0.23, 1, 0.32, 1) backwards;
}

.analysis-card {
    animation: fadeSlideUp 0.5s cubic-bezier(0.23, 1, 0.32, 1) backwards;
}

.metric-card:nth-child(1) { animation-delay: 0s; }
.metric-card:nth-child(2) { animation-delay: 0.05s; }
.metric-card:nth-child(3) { animation-delay: 0.1s; }
.analysis-card:nth-child(1) { animation-delay: 0.05s; }
.analysis-card:nth-child(2) { animation-delay: 0.1s; }

/* ===== HIDE STREAMLIT DEFAULTS ===== */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ===== UTILITY CLASSES ===== */
.small {
    font-size: 12px;
    color: var(--text-quaternary);
    font-weight: 500;
}

.text-gradient {
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
</style>
"""