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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');

/* ===== PREMIUM DESIGN SYSTEM ===== */
:root {
    /* Vibrant Gradients - Inspired by Modern UI */
    --gradient-cosmic: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    --gradient-purple: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-pink: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --gradient-blue: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --gradient-green: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    --gradient-warm: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    
    /* Clean Backgrounds */
    --bg-main: #ffffff;
    --bg-soft: #fafbfc;
    --bg-muted: #f4f6f8;
    
    /* Premium Text */
    --text-primary: #0f1419;
    --text-secondary: #2d3748;
    --text-muted: #718096;
    --text-subtle: #a0aec0;
    
    /* Elegant Borders & Shadows */
    --border-subtle: rgba(226, 232, 240, 0.6);
    --border-light: rgba(203, 213, 225, 0.8);
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
    --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.16);
    --shadow-2xl: 0 24px 64px rgba(0, 0, 0, 0.20);
    --shadow-glow-purple: 0 8px 32px rgba(102, 126, 234, 0.35);
    --shadow-glow-pink: 0 8px 32px rgba(245, 87, 108, 0.35);
}

/* ===== GLOBAL FOUNDATION ===== */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"], .main, .stApp {
    background: var(--bg-main) !important;
    overflow-x: hidden;
    scroll-behavior: smooth;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ===== IMMERSIVE BACKGROUND WITH FLOATING ORBS ===== */
.stApp {
    position: relative;
    min-height: 100vh;
    background: linear-gradient(180deg, #ffffff 0%, #fafbfc 50%, #ffffff 100%) !important;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(245, 87, 108, 0.08) 0%, transparent 45%),
        radial-gradient(circle at 50% 50%, rgba(79, 172, 254, 0.06) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
    animation: floatOrbs 25s ease-in-out infinite;
}

@keyframes floatOrbs {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -30px) scale(1.05); }
    66% { transform: translate(-20px, 20px) scale(0.95); }
}

/* ===== GRADIENT GRID PATTERN ===== */
.stApp::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        linear-gradient(to right, rgba(128, 128, 128, 0.04) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(128, 128, 128, 0.04) 1px, transparent 1px);
    background-size: 64px 64px;
    mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, #000 70%, transparent 110%);
    -webkit-mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, #000 70%, transparent 110%);
    pointer-events: none;
    z-index: 0;
}

/* ===== PREMIUM TYPOGRAPHY ===== */
h1 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 800 !important;
    font-size: 3.5rem !important;
    letter-spacing: -0.04em !important;
    background: var(--gradient-purple);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1 !important;
    animation: fadeSlideDown 0.8s cubic-bezier(0.16, 1, 0.3, 1) backwards;
}

h2 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    font-size: 2.5rem !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
    line-height: 1.2 !important;
    animation: fadeSlideDown 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.1s backwards;
}

h3 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.875rem !important;
    color: var(--text-secondary) !important;
    letter-spacing: -0.02em !important;
}

h4, h5, h6 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
}

p, span, div, label {
    color: var(--text-muted) !important;
    line-height: 1.7 !important;
    font-size: 1rem !important;
}

/* ===== SLEEK TAB NAVIGATION ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
    background: rgba(255, 255, 255, 0.95);
    border: none !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    padding: 8px 20px;
    border-radius: 20px 20px 0 0;
    backdrop-filter: blur(20px) saturate(180%);
    box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 1);
    animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) backwards;
}

.stTabs [data-baseweb="tab"] {
    height: 48px;
    padding: 0 28px;
    background: transparent;
    border: none !important;
    border-radius: 14px;
    color: var(--text-muted);
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    font-size: 15px;
    letter-spacing: 0.2px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
}

.stTabs [data-baseweb="tab"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: var(--gradient-purple);
    opacity: 0.1;
    transition: left 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 14px;
}

.stTabs [data-baseweb="tab"]:hover::before {
    left: 100%;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(102, 126, 234, 0.08);
    color: var(--text-primary);
    transform: translateY(-2px) scale(1.02);
}

.stTabs [aria-selected="true"] {
    background: var(--gradient-purple) !important;
    color: #ffffff !important;
    box-shadow: var(--shadow-glow-purple) !important;
    transform: translateY(-2px) scale(1.02);
}

/* ===== MAGNETIC GRADIENT BUTTONS ===== */
.stButton > button {
    background: var(--gradient-purple);
    background-size: 200% 200%;
    color: #ffffff;
    border: none;
    border-radius: 14px;
    padding: 16px 40px;
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.3px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: var(--shadow-glow-purple), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
    cursor: pointer;
    animation: gradientSlide 3s ease infinite;
}

@keyframes gradientSlide {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.25), transparent 70%);
    transform: translate(-50%, -50%);
    transition: width 0.5s ease, height 0.5s ease;
}

.stButton > button:hover::before {
    width: 300px;
    height: 300px;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4), 0 0 60px rgba(102, 126, 234, 0.3);
}

.stButton > button:active {
    transform: translateY(-1px) scale(0.98);
}

/* ===== GLASSMORPHIC FILE UPLOADER ===== */
.stFileUploader {
    background: rgba(255, 255, 255, 0.9);
    border: 2px dashed rgba(102, 126, 234, 0.25);
    border-radius: 18px;
    padding: 36px;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    backdrop-filter: blur(20px) saturate(180%);
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}

.stFileUploader::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 18px;
    background: var(--gradient-purple);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
    z-index: -1;
}

.stFileUploader:hover::before {
    opacity: 0.04;
}

.stFileUploader:hover {
    border-color: rgba(102, 126, 234, 0.5);
    border-style: solid;
    transform: translateY(-4px) scale(1.005);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
}

.stFileUploader button,
.stFileUploader section,
.stFileUploader label,
.stFileUploader div[data-testid="stFileUploaderDropzone"] {
    pointer-events: auto !important;
}

/* ===== MODERN TEXT AREAS ===== */
.stTextArea textarea {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid var(--border-light) !important;
    border-radius: 14px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', monospace !important;
    font-size: 15px !important;
    padding: 18px !important;
    transition: all 0.3s ease !important;
    line-height: 1.7 !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stTextArea textarea:focus {
    border-color: rgba(102, 126, 234, 0.5) !important;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), var(--shadow-lg) !important;
    background: rgba(255, 255, 255, 1) !important;
    outline: none !important;
    transform: scale(1.005);
}

/* ===== PREMIUM GLASSMORPHIC CARDS ===== */
.metric-card, .analysis-card {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 28px;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    backdrop-filter: blur(20px) saturate(180%);
    box-shadow: var(--shadow-md);
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
    background: var(--gradient-purple);
    opacity: 0;
    transition: opacity 0.4s ease;
}

.metric-card::after, .analysis-card::after {
    content: '';
    position: absolute;
    inset: -100%;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.06), transparent 70%);
    opacity: 0;
    transition: opacity 0.4s ease, transform 0.4s ease;
    pointer-events: none;
}

.metric-card:hover::before, .analysis-card:hover::before {
    opacity: 1;
}

.metric-card:hover::after, .analysis-card:hover::after {
    opacity: 1;
    transform: scale(1.2);
}

.metric-card:hover, .analysis-card:hover {
    border-color: rgba(102, 126, 234, 0.3);
    transform: translateY(-6px) scale(1.01);
    box-shadow: var(--shadow-2xl), var(--shadow-glow-purple);
}

/* ===== VIBRANT SCORE BADGES ===== */
.score-badge {
    display: inline-block;
    padding: 20px 44px;
    border-radius: 24px;
    font-family: 'Poppins', sans-serif;
    font-weight: 900;
    font-size: 48px;
    box-shadow: var(--shadow-xl), inset 0 2px 0 rgba(255, 255, 255, 0.25);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    letter-spacing: -0.02em;
}

.score-badge::after {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 28px;
    opacity: 0;
    filter: blur(18px);
    transition: opacity 0.3s ease;
    z-index: -1;
}

.score-badge:hover {
    transform: scale(1.06) translateY(-4px);
}

.score-badge:hover::after {
    opacity: 0.75;
}

.score-excellent {
    background: var(--gradient-green);
    color: #ffffff;
}

.score-excellent::after {
    background: var(--gradient-green);
}

.score-good {
    background: var(--gradient-blue);
    color: #ffffff;
}

.score-good::after {
    background: var(--gradient-blue);
}

.score-fair {
    background: var(--gradient-warm);
    color: #ffffff;
}

.score-fair::after {
    background: var(--gradient-warm);
}

.score-poor {
    background: var(--gradient-pink);
    color: #ffffff;
}

.score-poor::after {
    background: var(--gradient-pink);
}

/* ===== SMOOTH ANIMATED CHIPS ===== */
.chip {
    display: inline-block;
    margin: 5px 7px 5px 0;
    padding: 8px 18px;
    border-radius: 20px;
    background: rgba(102, 126, 234, 0.08);
    border: 1px solid rgba(102, 126, 234, 0.2);
    font-size: 14px;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    color: var(--text-secondary);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}

.chip::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    background: var(--gradient-purple);
    opacity: 0;
    transition: opacity 0.25s ease;
}

.chip:hover::before {
    opacity: 0.12;
}

.chip:hover {
    background: rgba(102, 126, 234, 0.12);
    border-color: rgba(102, 126, 234, 0.4);
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.25);
    color: var(--text-primary);
}

/* ===== ELEGANT DIVIDERS ===== */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.25), transparent);
    margin: 28px 0;
    position: relative;
}

hr::before {
    content: '';
    position: absolute;
    top: -1.5px;
    left: 50%;
    transform: translateX(-50%);
    width: 64px;
    height: 3px;
    background: var(--gradient-purple);
    border-radius: 2px;
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
}

/* ===== SLEEK EXPANDERS ===== */
.stExpander {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    transition: all 0.25s ease !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stExpander:hover {
    border-color: rgba(102, 126, 234, 0.3) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-2px) !important;
}

.stExpander [data-testid="stExpanderToggleButton"] {
    color: var(--text-primary) !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* ===== ANIMATED PROGRESS BAR ===== */
.stProgress {
    margin: 18px 0;
    position: relative;
    height: 8px !important;
}

.stProgress > div {
    background: rgba(226, 232, 240, 0.5);
    border-radius: 8px !important;
    overflow: hidden !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06);
    height: 8px !important;
    border: 1px solid var(--border-subtle);
}

.stProgress > div > div {
    background: var(--gradient-purple);
    border-radius: 8px !important;
    box-shadow: 0 0 12px rgba(102, 126, 234, 0.5);
    position: relative !important;
    height: 8px !important;
    transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    overflow: hidden !important;
}

.stProgress > div > div::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
    animation: shimmer 1.8s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* ===== PREMIUM SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(226, 232, 240, 0.3);
    border-radius: 8px;
}

::-webkit-scrollbar-thumb {
    background: var(--gradient-purple);
    border-radius: 8px;
    border: 2px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 0 6px rgba(102, 126, 234, 0.4);
}

::-webkit-scrollbar-thumb:hover {
    box-shadow: 0 0 12px rgba(102, 126, 234, 0.6);
}

/* ===== SECTION HEADERS WITH GRADIENT ===== */
.section-header {
    font-size: 2.25rem;
    font-weight: 800;
    background: var(--gradient-purple);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 20px;
    letter-spacing: -0.02em;
    font-family: 'Poppins', sans-serif !important;
}

/* ===== FLUID ENTRANCE ANIMATIONS ===== */
@keyframes fadeSlideDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeSlideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes scaleIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

.metric-card {
    animation: scaleIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) backwards;
}

.analysis-card {
    animation: fadeSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) backwards;
}

.metric-card:nth-child(1) { animation-delay: 0.05s; }
.metric-card:nth-child(2) { animation-delay: 0.1s; }
.metric-card:nth-child(3) { animation-delay: 0.15s; }
.analysis-card:nth-child(1) { animation-delay: 0.08s; }
.analysis-card:nth-child(2) { animation-delay: 0.16s; }

/* ===== HIDE STREAMLIT DEFAULTS ===== */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ===== UTILITY CLASSES ===== */
.small {
    font-size: 13px;
    color: var(--text-subtle);
    letter-spacing: 0.2px;
    font-weight: 500;
}

.text-gradient {
    background: var(--gradient-purple);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.text-gradient-warm {
    background: var(--gradient-warm);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.glow-sm {
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
}

.glow-md {
    box-shadow: 0 0 30px rgba(102, 126, 234, 0.4);
}

.glow-primary {
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
}
</style>
"""