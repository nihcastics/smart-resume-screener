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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ===== CSS VARIABLES - MODERN PROFESSIONAL PALETTE ===== */
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    
    --bg-white: #ffffff;
    --bg-light: #f8f9fa;
    --bg-lighter: #fafbfc;
    
    --text-primary: #1a202c;
    --text-secondary: #4a5568;
    --text-tertiary: #718096;
    --text-light: #a0aec0;
    
    --border-light: rgba(226, 232, 240, 0.8);
    --border-medium: rgba(203, 213, 225, 0.9);
    
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --shadow-lg: 0 10px 30px rgba(0,0,0,0.12);
    --shadow-xl: 0 20px 60px rgba(0,0,0,0.15);
    
    --glow-purple: rgba(102, 126, 234, 0.4);
    --glow-pink: rgba(245, 87, 108, 0.4);
    --glow-blue: rgba(79, 172, 254, 0.4);
    --glow-green: rgba(56, 239, 125, 0.4);
}

/* ===== GLOBAL RESET & SMOOTH BASE ===== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

html, body, [class*="css"], .main, .stApp {
    background: var(--bg-white) !important;
    overflow-x: hidden;
    scroll-behavior: smooth;
}

/* ===== IMMERSIVE FLOATING GRADIENT BACKGROUND ===== */
.stApp {
    background: linear-gradient(180deg, 
        #ffffff 0%, 
        #f8f9fa 50%,
        #fafbfc 100%) !important;
    position: relative;
    min-height: 100vh;
}

.stApp::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background-image: 
        radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 80% 70%, rgba(245, 87, 108, 0.08) 0%, transparent 45%),
        radial-gradient(circle at 50% 50%, rgba(79, 172, 254, 0.06) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
    animation: floatGradient 30s ease-in-out infinite;
}

@keyframes floatGradient {
    0%, 100% {
        transform: translate(0, 0) rotate(0deg);
    }
    33% {
        transform: translate(30px, -30px) rotate(5deg);
    }
    66% {
        transform: translate(-20px, 20px) rotate(-5deg);
    }
}

/* ===== MODERN TYPOGRAPHY HIERARCHY ===== */
h1 {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 800 !important;
    font-size: 3.5rem !important;
    letter-spacing: -0.04em !important;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeInDown 0.8s ease-out backwards;
}

h2 {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 2.25rem !important;
    letter-spacing: -0.03em !important;
    animation: fadeInDown 0.8s ease-out 0.1s backwards;
}

h3 {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-secondary) !important;
    font-weight: 700 !important;
    font-size: 1.75rem !important;
    letter-spacing: -0.02em !important;
}

h4, h5, h6 {
    font-family: 'Sora', sans-serif !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
}

p, span, div {
    color: var(--text-tertiary) !important;
    line-height: 1.7 !important;
    font-size: 1rem !important;
}

/* ===== ULTRA-SMOOTH FLUID TABS ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 16px;
    background: rgba(255, 255, 255, 0.95);
    border-bottom: none;
    padding: 12px 24px;
    border-radius: 20px;
    backdrop-filter: blur(20px) saturate(180%);
    box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255, 255, 255, 1);
    border: 1px solid var(--border-light);
    animation: slideInUp 0.6s ease-out backwards;
}

.stTabs [data-baseweb="tab"] {
    height: 52px;
    padding: 0 32px;
    background: transparent;
    border: none;
    border-radius: 14px;
    color: var(--text-tertiary);
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 15px;
    letter-spacing: 0.3px;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
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
    background: var(--primary-gradient);
    opacity: 0.1;
    transition: left 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 14px;
}

.stTabs [data-baseweb="tab"]:hover::before {
    left: 100%;
}

.stTabs [data-baseweb="tab"]:hover {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.08));
    color: var(--text-primary);
    transform: translateY(-2px) scale(1.02);
}

.stTabs [aria-selected="true"] {
    background: var(--primary-gradient) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 24px var(--glow-purple), 0 0 40px var(--glow-purple) !important;
    transform: translateY(-2px) scale(1.02);
}

/* ===== MODERN MAGNETIC BUTTONS WITH GLOW ===== */
.stButton > button {
    background: var(--primary-gradient);
    background-size: 200% 200%;
    color: #ffffff;
    border: none;
    border-radius: 16px;
    padding: 18px 48px;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 0.5px;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: 0 8px 24px var(--glow-purple), inset 0 1px 0 rgba(255, 255, 255, 0.2);
    position: relative;
    overflow: hidden;
    animation: gradientFlow 3s ease infinite;
}

@keyframes gradientFlow {
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
    background: radial-gradient(circle, rgba(255, 255, 255, 0.3), transparent 70%);
    transform: translate(-50%, -50%);
    transition: width 0.6s ease, height 0.6s ease;
}

.stButton > button:hover::before {
    width: 300px;
    height: 300px;
}

.stButton > button:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 16px 40px var(--glow-purple), 0 0 60px var(--glow-purple);
}

.stButton > button:active {
    transform: translateY(-2px) scale(0.98);
}

/* ===== PREMIUM FILE UPLOADER WITH GLASS EFFECT ===== */
.stFileUploader {
    background: rgba(255, 255, 255, 0.9);
    border: 2px dashed rgba(102, 126, 234, 0.3);
    border-radius: 20px;
    padding: 40px;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    backdrop-filter: blur(20px) saturate(180%);
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}

.stFileUploader::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    background: var(--primary-gradient);
    opacity: 0;
    transition: opacity 0.4s ease;
    pointer-events: none;
    z-index: -1;
}

.stFileUploader:hover::before {
    opacity: 0.05;
}

.stFileUploader:hover {
    border-color: rgba(102, 126, 234, 0.6);
    border-style: solid;
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 16px 40px var(--glow-purple);
}

.stFileUploader button,
.stFileUploader section,
.stFileUploader label,
.stFileUploader div[data-testid="stFileUploaderDropzone"] {
    pointer-events: auto !important;
}

/* ===== ELEGANT TEXT AREA ===== */
.stTextArea textarea {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 2px solid var(--border-medium) !important;
    border-radius: 16px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 15px !important;
    padding: 20px !important;
    transition: all 0.3s ease !important;
    line-height: 1.8 !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stTextArea textarea:focus {
    border-color: rgba(102, 126, 234, 0.6) !important;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), var(--shadow-lg) !important;
    background: rgba(255, 255, 255, 1) !important;
    outline: none !important;
}

/* ===== MODERN GLASSMORPHIC METRIC CARDS ===== */
.metric-card {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid var(--border-light);
    border-radius: 24px;
    padding: 32px;
    transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
    backdrop-filter: blur(20px) saturate(180%);
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--primary-gradient);
    opacity: 0;
    transition: opacity 0.5s ease;
}

.metric-card::after {
    content: '';
    position: absolute;
    inset: -100%;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.08), transparent 70%);
    opacity: 0;
    transition: opacity 0.5s ease, transform 0.5s ease;
    pointer-events: none;
}

.metric-card:hover::before {
    opacity: 1;
}

.metric-card:hover::after {
    opacity: 1;
    transform: scale(1.3);
}

.metric-card:hover {
    border-color: rgba(102, 126, 234, 0.3);
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 50px var(--glow-purple);
}

/* ===== SLEEK ANALYSIS CARDS ===== */
.analysis-card {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid var(--border-light);
    border-radius: 20px;
    padding: 28px;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    backdrop-filter: blur(20px) saturate(180%);
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}

.analysis-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    background: var(--primary-gradient);
    opacity: 0;
    transition: opacity 0.4s ease;
}

.analysis-card:hover::before {
    opacity: 0.03;
}

.analysis-card:hover {
    border-color: rgba(102, 126, 234, 0.3);
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 16px 40px var(--glow-purple);
}

/* ===== VIBRANT 3D SCORE BADGES ===== */
.score-badge {
    display: inline-block;
    padding: 24px 48px;
    border-radius: 28px;
    font-family: 'Sora', sans-serif;
    font-weight: 900;
    font-size: 52px;
    box-shadow: var(--shadow-xl), inset 0 2px 0 rgba(255, 255, 255, 0.3);
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
    letter-spacing: -0.02em;
}

.score-badge::after {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 32px;
    opacity: 0;
    filter: blur(20px);
    transition: opacity 0.4s ease;
    z-index: -1;
}

.score-badge:hover {
    transform: scale(1.08) translateY(-6px);
}

.score-badge:hover::after {
    opacity: 0.8;
}

.score-excellent {
    background: var(--success-gradient);
    color: #ffffff;
    box-shadow: 0 16px 50px var(--glow-green);
}

.score-excellent::after {
    background: var(--success-gradient);
}

.score-good {
    background: var(--accent-gradient);
    color: #ffffff;
    box-shadow: 0 16px 50px var(--glow-blue);
}

.score-good::after {
    background: var(--accent-gradient);
}

.score-fair {
    background: var(--warning-gradient);
    color: #ffffff;
    box-shadow: 0 16px 50px rgba(250, 112, 154, 0.4);
}

.score-fair::after {
    background: var(--warning-gradient);
}

.score-poor {
    background: var(--secondary-gradient);
    color: #ffffff;
    box-shadow: 0 16px 50px var(--glow-pink);
}

.score-poor::after {
    background: var(--secondary-gradient);
}

/* ===== SMOOTH ANIMATED CHIPS ===== */
.chip {
    display: inline-block;
    margin: 6px 8px 6px 0;
    padding: 10px 20px;
    border-radius: 24px;
    background: rgba(102, 126, 234, 0.08);
    border: 1px solid rgba(102, 126, 234, 0.2);
    font-size: 14px;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    color: var(--text-secondary);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}

.chip::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 24px;
    background: var(--primary-gradient);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.chip:hover::before {
    opacity: 0.15;
}

.chip:hover {
    background: rgba(102, 126, 234, 0.12);
    border-color: rgba(102, 126, 234, 0.4);
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 8px 20px var(--glow-purple);
    color: var(--text-primary);
}

/* ===== ELEGANT GRADIENT DIVIDERS ===== */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
    margin: 32px 0;
    position: relative;
}

hr::before {
    content: '';
    position: absolute;
    top: -1px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 4px;
    background: var(--primary-gradient);
    border-radius: 2px;
    box-shadow: 0 2px 12px var(--glow-purple);
}

/* ===== SMOOTH EXPANDERS ===== */
.stExpander {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid var(--border-light) !important;
    border-radius: 16px !important;
    transition: all 0.3s ease !important;
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
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* ===== SLEEK ANIMATED PROGRESS BAR ===== */
.stProgress {
    margin: 20px 0;
    position: relative;
    height: 10px !important;
}

.stProgress > div {
    background: rgba(226, 232, 240, 0.6);
    border-radius: 10px !important;
    overflow: hidden !important;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.08);
    height: 10px !important;
    border: 1px solid var(--border-light);
}

.stProgress > div > div {
    background: var(--primary-gradient);
    border-radius: 10px !important;
    box-shadow: 0 0 16px var(--glow-purple);
    position: relative !important;
    height: 10px !important;
    transition: width 0.3s ease !important;
    overflow: hidden !important;
}

.stProgress > div > div::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* ===== MODERN MINIMAL SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(226, 232, 240, 0.4);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--primary-gradient);
    border-radius: 10px;
    border: 2px solid rgba(255, 255, 255, 0.9);
    box-shadow: 0 0 8px var(--glow-purple);
}

::-webkit-scrollbar-thumb:hover {
    box-shadow: 0 0 16px var(--glow-purple);
}

/* ===== GRADIENT SECTION HEADERS ===== */
.section-header {
    font-size: 28px;
    font-weight: 800;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 24px;
    letter-spacing: -0.02em;
    font-family: 'Sora', sans-serif !important;
}

/* ===== FLUID ENTRANCE ANIMATIONS ===== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInUp {
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
    animation: scaleIn 0.6s ease-out backwards;
}

.analysis-card {
    animation: fadeInUp 0.6s ease-out backwards;
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
    color: var(--text-light);
    letter-spacing: 0.3px;
    font-weight: 500;
}

.glow-text {
    color: var(--text-primary) !important;
    text-shadow: 0 0 20px var(--glow-purple);
}
</style>
"""
