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
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ===== GLOBAL RESET & BASE ===== */
*{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif}
html,body,[class*="css"],.main,.stApp{background:#060812!important;overflow-x:hidden}

/* ===== IMMERSIVE ANIMATED GRADIENT BACKGROUND ===== */
.stApp{
    background:linear-gradient(-45deg,#0d0221,#0f0624,#1a0933,#150a2e,#0d0221)!important;
    background-size:600% 600%!important;
    animation:cosmicShift 20s ease-in-out infinite!important;
    position:relative;
    min-height:100vh;
}
@keyframes cosmicShift{
    0%{background-position:0% 50%}
    25%{background-position:50% 75%}
    50%{background-position:100% 50%}
    75%{background-position:50% 25%}
    100%{background-position:0% 50%}
}

/* ===== FLOATING GLOW PARTICLES ===== */
.stApp::before{
    content:'';
    position:fixed;
    top:0;
    left:0;
    width:100%;
    height:100%;
    background-image:radial-gradient(circle at 20% 30%,rgba(139,92,246,.12) 0%,transparent 40%),
                     radial-gradient(circle at 80% 70%,rgba(236,72,153,.10) 0%,transparent 45%),
                     radial-gradient(circle at 50% 50%,rgba(99,102,241,.08) 0%,transparent 50%),
                     radial-gradient(circle at 10% 80%,rgba(16,185,129,.06) 0%,transparent 40%);
    pointer-events:none;
    z-index:0;
    animation:glowPulse 25s ease-in-out infinite;
}
@keyframes glowPulse{
    0%,100%{opacity:1;transform:translate(0,0) scale(1)}
    25%{opacity:.85;transform:translate(40px,-40px) scale(1.15)}
    50%{opacity:.95;transform:translate(-30px,30px) scale(1.05)}
    75%{opacity:.9;transform:translate(30px,20px) scale(1.1)}
}

/* ===== MODERN TYPOGRAPHY WITH BETTER HIERARCHY ===== */
h1{font-family:'Space Grotesk',sans-serif!important;color:#f8fafc!important;font-weight:800!important;font-size:3.5rem!important;letter-spacing:-.04em!important;text-shadow:0 4px 20px rgba(139,92,246,.6),0 0 60px rgba(236,72,153,.3)}
h2{font-family:'Space Grotesk',sans-serif!important;color:#f1f5f9!important;font-weight:700!important;font-size:2.25rem!important;letter-spacing:-.03em!important;text-shadow:0 3px 15px rgba(99,102,241,.5)}
h3{font-family:'Space Grotesk',sans-serif!important;color:#e2e8f0!important;font-weight:700!important;font-size:1.75rem!important;letter-spacing:-.02em!important;text-shadow:0 2px 12px rgba(139,92,246,.4)}
h4,h5,h6{font-family:'Space Grotesk',sans-serif!important;color:#cbd5e1!important;font-weight:600!important;text-shadow:0 2px 8px rgba(99,102,241,.3)}
p,span,div{color:#94a3b8!important;line-height:1.8!important;font-size:1.05rem!important}

/* ===== ULTRA-MODERN FLUID TABS ===== */
.stTabs [data-baseweb="tab-list"]{
    gap:24px;
    background:linear-gradient(135deg,rgba(21,10,46,.75),rgba(13,2,33,.75));
    border-bottom:none;
    padding:16px 28px;
    border-radius:24px 24px 0 0;
    backdrop-filter:blur(30px) saturate(180%);
    box-shadow:0 -15px 50px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.05);
    border:1px solid rgba(139,92,246,.15);
}
.stTabs [data-baseweb="tab"]{
    height:64px;
    padding:0 42px;
    background:linear-gradient(135deg,rgba(139,92,246,.08),rgba(99,102,241,.08));
    border:2px solid rgba(139,92,246,.2);
    border-radius:18px;
    color:#a78bfa;
    font-family:'Space Grotesk',sans-serif;
    font-weight:700;
    font-size:16px;
    letter-spacing:.5px;
    transition:all .5s cubic-bezier(.34,1.56,.64,1);
    backdrop-filter:blur(15px);
    position:relative;
    overflow:hidden;
    box-shadow:0 4px 15px rgba(139,92,246,.15);
}
.stTabs [data-baseweb="tab"]::before{
    content:'';
    position:absolute;
    top:0;
    left:-100%;
    width:100%;
    height:100%;
    background:linear-gradient(90deg,transparent,rgba(139,92,246,.3),rgba(236,72,153,.3),transparent);
    transition:left .8s cubic-bezier(.4,0,.2,1);
}
.stTabs [data-baseweb="tab"]::after{
    content:'';
    position:absolute;
    inset:0;
    border-radius:18px;
    padding:2px;
    background:linear-gradient(135deg,rgba(139,92,246,.4),rgba(236,72,153,.4));
    -webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);
    -webkit-mask-composite:exclude;
    mask-composite:exclude;
    opacity:0;
    transition:opacity .5s ease;
}
.stTabs [data-baseweb="tab"]:hover::before{left:100%}
.stTabs [data-baseweb="tab"]:hover::after{opacity:1}
.stTabs [data-baseweb="tab"]:hover{
    background:linear-gradient(135deg,rgba(139,92,246,.18),rgba(236,72,153,.15));
    border-color:rgba(139,92,246,.5);
    transform:translateY(-6px) scale(1.03);
    box-shadow:0 15px 45px rgba(139,92,246,.35),0 0 50px rgba(236,72,153,.25);
    color:#e9d5ff;
}
.stTabs [aria-selected="true"]{
    background:linear-gradient(135deg,#8b5cf6 0%,#ec4899 100%)!important;
    color:#fff!important;
    border-color:rgba(139,92,246,.8)!important;
    box-shadow:0 20px 60px rgba(139,92,246,.6),0 0 80px rgba(236,72,153,.5),inset 0 2px 0 rgba(255,255,255,.3),inset 0 -2px 0 rgba(0,0,0,.2)!important;
    transform:translateY(-4px) scale(1.02);
}

/* ===== MAGNETIC GLOWING BUTTONS ===== */
.stButton>button{
    background:linear-gradient(135deg,#8b5cf6 0%,#6366f1 50%,#ec4899 100%);
    background-size:200% 200%;
    color:#fff;
    border:none;
    border-radius:20px;
    padding:22px 60px;
    font-family:'Space Grotesk',sans-serif;
    font-weight:800;
    font-size:17px;
    letter-spacing:1.5px;
    text-transform:uppercase;
    transition:all .5s cubic-bezier(.34,1.56,.64,1);
    box-shadow:0 15px 50px rgba(139,92,246,.5),0 0 60px rgba(236,72,153,.3),inset 0 2px 0 rgba(255,255,255,.3),inset 0 -2px 0 rgba(0,0,0,.2);
    position:relative;
    overflow:hidden;
    animation:gradientSlide 4s ease infinite;
}
@keyframes gradientSlide{
    0%,100%{background-position:0% 50%}
    50%{background-position:100% 50%}
}
.stButton>button::before{
    content:'';
    position:absolute;
    top:50%;
    left:50%;
    width:0;
    height:0;
    border-radius:50%;
    background:radial-gradient(circle,rgba(255,255,255,.4),transparent 70%);
    transform:translate(-50%,-50%);
    transition:width .7s cubic-bezier(.4,0,.2,1),height .7s cubic-bezier(.4,0,.2,1);
}
.stButton>button::after{
    content:'';
    position:absolute;
    inset:-2px;
    border-radius:22px;
    background:linear-gradient(45deg,#8b5cf6,#ec4899,#6366f1,#8b5cf6);
    background-size:400% 400%;
    opacity:0;
    filter:blur(20px);
    transition:opacity .5s ease;
    animation:rotateGradient 6s linear infinite;
    z-index:-1;
}
@keyframes rotateGradient{
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}
.stButton>button:hover::before{width:400px;height:400px}
.stButton>button:hover::after{opacity:.8}
.stButton>button:hover{
    transform:translateY(-6px) scale(1.05);
    box-shadow:0 25px 80px rgba(139,92,246,.7),0 0 90px rgba(236,72,153,.6),0 0 120px rgba(99,102,241,.4),inset 0 2px 0 rgba(255,255,255,.4);
}
.stButton>button:active{transform:translateY(-3px) scale(.98)}

/* ===== IMMERSIVE FILE UPLOADER ===== */
.stFileUploader{
    background:linear-gradient(135deg,rgba(139,92,246,.08),rgba(236,72,153,.08));
    border:3px dashed rgba(139,92,246,.5);
    border-radius:24px;
    padding:40px;
    transition:all .5s cubic-bezier(.34,1.56,.64,1);
    backdrop-filter:blur(25px) saturate(180%);
    position:relative;
    overflow:hidden;
}
.stFileUploader::before{
    content:'';
    position:absolute;
    inset:0;
    border-radius:24px;
    background:linear-gradient(45deg,rgba(139,92,246,.15),rgba(236,72,153,.15));
    opacity:0;
    transition:opacity .5s ease;
    pointer-events:none!important;
    z-index:-1;
}
.stFileUploader:hover::before{opacity:1}
.stFileUploader:hover{
    background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(236,72,153,.15));
    border-color:rgba(139,92,246,.8);
    border-style:solid;
    transform:scale(1.02) translateY(-4px);
    box-shadow:0 20px 60px rgba(139,92,246,.3),0 0 80px rgba(236,72,153,.2);
}
/* Ensure file uploader button is always clickable */
.stFileUploader button{
    pointer-events:auto!important;
    cursor:pointer!important;
    opacity:1!important;
}
.stFileUploader section{
    pointer-events:auto!important;
}
.stFileUploader label{
    pointer-events:auto!important;
}
.stFileUploader div[data-testid="stFileUploaderDropzone"]{
    pointer-events:auto!important;
}

/* ===== GLOWING TEXT AREA ===== */
.stTextArea textarea{
    background:linear-gradient(135deg,rgba(21,10,46,.9),rgba(13,2,33,.9))!important;
    border:2px solid rgba(139,92,246,.3)!important;
    border-radius:20px!important;
    color:#f1f5f9!important;
    font-family:'JetBrains Mono',monospace!important;
    font-size:16px!important;
    padding:24px!important;
    transition:all .4s cubic-bezier(.4,0,.2,1)!important;
    line-height:1.9!important;
    backdrop-filter:blur(20px)!important;
    box-shadow:inset 0 2px 8px rgba(0,0,0,.3)!important;
}
.stTextArea textarea:focus{
    border-color:rgba(139,92,246,.9)!important;
    box-shadow:0 0 0 5px rgba(139,92,246,.2),0 15px 50px rgba(139,92,246,.3),0 0 70px rgba(236,72,153,.2),inset 0 2px 8px rgba(0,0,0,.3)!important;
    background:linear-gradient(135deg,rgba(21,10,46,.98),rgba(13,2,33,.98))!important;
    transform:scale(1.01)!important;
}

/* ===== PREMIUM METRIC CARDS WITH GLOW ===== */
.metric-card{
    background:linear-gradient(135deg,rgba(21,10,46,.90),rgba(13,2,33,.88));
    border:2px solid rgba(139,92,246,.25);
    border-radius:28px;
    padding:36px;
    transition:all .6s cubic-bezier(.34,1.56,.64,1);
    backdrop-filter:blur(30px) saturate(200%);
    box-shadow:0 10px 40px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.05);
    position:relative;
    overflow:hidden;
}
.metric-card::before{
    content:'';
    position:absolute;
    top:0;
    left:0;
    right:0;
    height:4px;
    background:linear-gradient(90deg,transparent,rgba(139,92,246,.8),rgba(236,72,153,.8),transparent);
    opacity:0;
    transition:opacity .6s ease;
    box-shadow:0 0 20px rgba(139,92,246,.6);
}
.metric-card::after{
    content:'';
    position:absolute;
    inset:-100%;
    background:radial-gradient(circle,rgba(139,92,246,.15),transparent 70%);
    opacity:0;
    transition:opacity .6s ease,transform .6s ease;
    pointer-events:none;
}
.metric-card:hover::before{opacity:1}
.metric-card:hover::after{opacity:1;transform:scale(1.5)}
.metric-card:hover{
    border-color:rgba(139,92,246,.6);
    transform:translateY(-10px) scale(1.02) rotate(0.5deg);
    box-shadow:0 25px 70px rgba(139,92,246,.4),0 0 90px rgba(236,72,153,.3),inset 0 2px 0 rgba(255,255,255,.1);
}

/* ===== IMMERSIVE ANALYSIS CARDS ===== */
.analysis-card{
    background:linear-gradient(135deg,rgba(21,10,46,.92),rgba(13,2,33,.90));
    border:2px solid rgba(139,92,246,.3);
    border-radius:24px;
    padding:34px;
    transition:all .5s cubic-bezier(.34,1.56,.64,1);
    backdrop-filter:blur(25px) saturate(180%);
    box-shadow:0 12px 45px rgba(0,0,0,.4);
    position:relative;
    overflow:hidden;
}
.analysis-card::before{
    content:'';
    position:absolute;
    inset:0;
    border-radius:24px;
    background:linear-gradient(135deg,rgba(139,92,246,.1),rgba(236,72,153,.1));
    opacity:0;
    transition:opacity .5s ease;
}
.analysis-card:hover::before{opacity:1}
.analysis-card:hover{
    border-color:rgba(139,92,246,.6);
    transform:translateY(-8px) scale(1.01);
    box-shadow:0 20px 65px rgba(139,92,246,.35),0 0 80px rgba(236,72,153,.25);
}

/* ===== ULTRA 3D GLOWING SCORE BADGES ===== */
.score-badge{
    display:inline-block;
    padding:28px 52px;
    border-radius:32px;
    font-family:'Space Grotesk',sans-serif;
    font-weight:900;
    font-size:56px;
    box-shadow:0 20px 60px rgba(0,0,0,.6),inset 0 3px 0 rgba(255,255,255,.4),inset 0 -3px 0 rgba(0,0,0,.4);
    transition:all .5s cubic-bezier(.34,1.56,.64,1);
    position:relative;
    letter-spacing:-.02em;
}
.score-badge::after{
    content:'';
    position:absolute;
    inset:-4px;
    border-radius:36px;
    opacity:0;
    filter:blur(25px);
    transition:opacity .5s ease;
    z-index:-1;
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

/* ===== ELEGANT GLOWING PROGRESS BAR ===== */
.stProgress{
    margin:20px 0;
    position:relative;
}
.stProgress>div{
    background:linear-gradient(90deg,rgba(99,102,241,.12),rgba(139,92,246,.10));
    border-radius:16px!important;
    overflow:visible!important;
    box-shadow:inset 0 1px 4px rgba(0,0,0,.25),0 2px 15px rgba(99,102,241,.18);
    height:12px!important;
    border:1px solid rgba(99,102,241,.15);
}
.stProgress>div>div{
    background:linear-gradient(90deg,#6366f1,#8b5cf6,#a855f7,#8b5cf6,#6366f1);
    background-size:200% 100%;
    border-radius:16px!important;
    box-shadow:0 0 20px rgba(139,92,246,.7),
               0 0 40px rgba(99,102,241,.5),
               inset 0 1px 2px rgba(255,255,255,.3);
    position:relative!important;
    height:12px!important;
    transition:width 0.3s ease-out!important;
    animation:progressGlow 3s ease-in-out infinite;
}
@keyframes progressGlow{
    0%,100%{background-position:0% 50%;filter:brightness(1)}
    50%{background-position:100% 50%;filter:brightness(1.2)}
}
.stProgress>div>div::after{
    content:'';
    position:absolute;
    top:50%;
    right:-8px;
    transform:translateY(-50%);
    width:20px;
    height:20px;
    background:radial-gradient(circle at 35% 35%,
        rgba(255,255,255,1) 0%,
        rgba(236,72,153,.9) 25%,
        rgba(139,92,246,.7) 50%,
        rgba(99,102,241,.4) 75%,
        transparent 100%);
    border-radius:50%;
    box-shadow:0 0 20px rgba(236,72,153,.9),
               0 0 35px rgba(139,92,246,.6);
    animation:pulse 2s ease-in-out infinite;
    z-index:10;
}
@keyframes pulse{
    0%,100%{transform:translateY(-50%) scale(1);opacity:1}
    50%{transform:translateY(-50%) scale(1.15);opacity:0.9}
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

# --- Config (balanced weights for accurate scoring) ---
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
def init_mongodb():
    # Try Streamlit secrets first (for cloud deployment), then fall back to environment variables
    try:
        uri = st.secrets["MONGO_URI"]
    except (KeyError, AttributeError):
        uri = os.getenv("MONGO_URI", "")
    
    uri = uri.strip() if uri else ""
    if not uri: 
        print("⚠️ MongoDB URI not found - skipping database connection")
        return None, None, False
    
    try:
        # Increase timeouts for better reliability
        client = MongoClient(
            uri, 
            serverSelectionTimeoutMS=10000,  # Increased to 10 seconds
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            retryWrites=True,
            w='majority'
        )
        # Test connection
        client.admin.command('ping')
        db = client["resume_screener_db"]  # More descriptive database name
        print("✅ MongoDB connected successfully!")
        return db["resumes"], db["analyses"], True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
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
    """
    Optimized global semantic similarity with balanced scoring.
    Uses top-k averaging for robust similarity estimation without over-penalizing.
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
        
        # Use top-10 chunks for more comprehensive comparison
        k = min(10, sims.size)
        topk = np.sort(sims)[-k:]
        
        # Weighted average: emphasize top chunks but not too much
        if k > 1:
            weights = np.linspace(0.6, 1.0, k)  # Gentler weighting
            score = float(np.average(topk, weights=weights))
        else:
            score = float(np.mean(topk))
        
        # Minimal calibration: 0.98 factor (previously 0.94, too harsh)
        calibrated = score * 0.98
        
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

# --- Atom refinement helpers - SIGNIFICANTLY EXPANDED ---
ATOM_GENERIC_TOKENS = set([
    # Experience/skill descriptors
    "experience","experiences","experienced","skill","skills","skilled","tools","tool","technologies",
    "technology","knowledge","knowledgeable","projects","project","responsibilities","responsibility",
    "requirements","requirement","required","prefer","preferred","preferably",
    # Job roles (too generic)
    "engineer","engineering","developer","development","analyst","analysis","internship","intern",
    "fresher","graduate","undergraduate","candidate","candidates","professional","professionals",
    # Qualifiers
    "strong","stronger","strongest","good","better","best","excellent","exceptional","outstanding",
    "ability","abilities","able","capable","proficient","proficiency","competent","competency",
    "familiar","familiarity","comfortable","understanding","understands","comprehension",
    # Action verbs
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
    # Generic concepts
    "nice","have","having","foundation","foundations","basics","basic","understanding","concept",
    "concepts","process","processes","practice","practices","methodology","methodologies","principles",
    "principle","background","backgrounds","exposure","working","knowledge","competency","competencies",
    "capability","capabilities","qualification","qualifications","plus","bonus","ideal","ideally",
    # Time/measurement (when isolated)
    "year","years","month","months","level","levels","degree","minimum","maximum","at","least",
    # Connectors/prepositions (when standalone)
    "with","without","using","use","used","via","through","across","within","including","such","like",
    "related","relevant","appropriate","suitable","equivalent","similar","other","others","various",
    "multiple","several","any","all","some","both","either","neither","each","every","general"
])

ATOM_BLOCK_PHRASES = {
    # Soft skill phrases
    "nice to have","nice-to-have","nice to know","good to have","good-to-have","would be nice",
    "good knowledge","strong knowledge","strong foundation","solid foundation","deep understanding",
    "computer foundations","computer foundation","soft skills","strong communication","interpersonal skills",
    "good communication","excellent communication","communication skills","problem solving skills",
    "problem-solving skills","analytical skills","critical thinking","attention to detail",
    # Generic requirement phrases
    "experience with","experience in","knowledge of","understanding of","familiarity with",
    "exposure to","working knowledge","hands-on experience","practical experience","proven experience",
    "ability to","able to","capable of","proficiency in","proficient in","competency in","skilled in",
    "expertise in","background in","track record","demonstrated ability","strong understanding",
    # Job responsibilities (not skills)
    "responsible for","work with","collaborate with","partner with","interact with","communicate with",
    "develop and","design and","build and","create and","implement and","maintain and","support and",
    "work closely","team environment","fast-paced environment","dynamic environment","agile environment",
    # Vague qualifiers
    "preferred qualifications","nice to haves","bonus points","plus points","additional skills",
    "good understanding","solid grasp","thorough understanding","comprehensive knowledge",
    "general knowledge","basic understanding","foundational knowledge","core concepts"
}

ATOM_WEAK_SINGLE = {
    "foundation","foundations","knowledge","understanding","experience","skill","skills","skillset",
    "competency","competencies","capability","capabilities","background","exposure","proficiency",
    "familiarity","expertise","qualification","qualifications","certification","certifications",
    "training","education","degree","masters","bachelor","phd","diploma","course","courses"
}

ATOM_LEADING_ADJECTIVES = {
    "strong","good","excellent","basic","advanced","intermediate","solid","sound","robust",
    "deep","thorough","comprehensive","extensive","broad","general","specific","detailed",
    "proven","demonstrated","hands-on","practical","theoretical","applied","relevant","appropriate"
}

def _tokenize_atom(atom: str):
    return re.findall(r"[a-z0-9][a-z0-9+.#-]*", normalize_text(atom))

def _is_valid_atom(atom: str):
    """Strict validation to filter out gibberish and generic phrases."""
    s = normalize_text(atom)
    if len(s) < 2:
        return False
    
    # Block known bad phrases
    if any(phrase in s for phrase in ATOM_BLOCK_PHRASES):
        return False
    
    tokens = _tokenize_atom(s)
    if not tokens:
        return False
    
    # Check for meaningful content
    meaningful = [t for t in tokens if t not in ATOM_GENERIC_TOKENS]
    if not meaningful:
        return False
    
    # Single weak tokens are invalid
    if len(meaningful) == 1 and meaningful[0] in ATOM_WEAK_SINGLE:
        return False
    
    # Must have at least one technical indicator
    tech_indicators = {
        # Programming languages
        'python','java','javascript','typescript','c++','csharp','ruby','go','rust','php','swift','kotlin','scala','r','matlab','perl',
        # Frameworks
        'react','angular','vue','node','django','flask','spring','express','fastapi','rails','laravel','dotnet','asp',
        # Databases
        'sql','mysql','postgresql','mongodb','redis','cassandra','oracle','dynamodb','elasticsearch','neo4j','sqlite',
        # Cloud/DevOps
        'aws','azure','gcp','docker','kubernetes','jenkins','terraform','ansible','gitlab','circleci','github','git',
        'lambda','ec2','s3','rds','cloudformation','helm','prometheus','grafana','datadog','newrelic',
        # Data/ML/AI
        'tensorflow','pytorch','keras','scikit','pandas','numpy','spark','hadoop','kafka','airflow','mlflow',
        'tableau','powerbi','looker','dbt','snowflake','redshift','bigquery','machinelearning','deeplearning',
        'nlp','computervision','transformers','bert','gpt','llm','ai','ml','dl','cnn','rnn','lstm',
        # Tools/Tech
        'linux','unix','windows','bash','powershell','vim','vscode','intellij','eclipse','jira','confluence',
        'slack','teams','notion','figma','sketch','postman','swagger','graphql','rest','grpc','soap',
        # Web/Mobile
        'html','css','sass','less','webpack','babel','npm','yarn','ios','android','flutter','reactnative',
        'nextjs','gatsby','nuxt','svelte','tailwind','bootstrap','materialui','redux','mobx','graphql',
        # Concepts with numbers/versions
        'api','sdk','cli','gui','ui','ux','cicd','etl','crud','orm','mvc','mvvm','solid','agile','scrum'
    }
    
    # Check if any meaningful token is a tech indicator
    has_tech = any(token in tech_indicators for token in meaningful)
    
    # Allow if contains tech, version numbers, or is a multi-word technical phrase
    if has_tech:
        return True
    
    # Allow if contains version/year patterns
    if any(re.search(r'\d', token) for token in tokens):
        return True
    
    # Allow specific multi-word phrases (likely certifications or specialized terms)
    if len(tokens) >= 2 and len(meaningful) >= 2:
        # Check for certification patterns
        cert_keywords = {'certified','certification','certificate','associate','professional','architect','administrator','specialist','expert'}
        if any(kw in tokens for kw in cert_keywords):
            return True
        
        # Check for degree patterns  
        degree_keywords = {'bachelor','master','phd','doctorate','degree','bs','ms','mba','btech','mtech'}
        if any(kw in tokens for kw in degree_keywords):
            return True
        
        # Multi-word technical terms are likely valid
        if len(meaningful) >= 2:
            return True
    
    return False

def _canonical_atom(atom: str, nlp=None):
    s = normalize_text(atom)
    if not s:
        return ""
    if nlp is not None:
        try:
            doc = nlp(s)
            lemmas = [t.lemma_.lower() for t in doc if re.match(r"[a-z0-9][a-z0-9+.#-]*", t.lemma_.lower())]
            canned = " ".join(lemmas)
            if canned:
                return canned
        except Exception:
            pass
    tokens = _tokenize_atom(s)
    return " ".join(tokens)

def refine_atom_list(atoms, nlp=None, reserved_canonicals=None, limit=40):
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
                                   faiss_index=None, strict_threshold=0.55, partial_threshold=0.45):
    """
    Enhanced requirement coverage with optimized thresholds for better accuracy.
    Stricter thresholds (0.55/0.45) prevent false positives while maintaining recall.
    """
    tokens = token_set(resume_text)
    chunk_embs = None
    if resume_chunks and embedder:
        try:
            chunk_embs = embedder.encode(resume_chunks, convert_to_numpy=True, normalize_embeddings=True)
            if chunk_embs.ndim == 1:
                chunk_embs = chunk_embs.reshape(1, -1)
        except Exception:
            chunk_embs = None

    def assess(atoms, req_type):
        details = {}
        pending = []
        for atom in atoms:
            sim = 0.0
            token_hit = contains_atom(atom, tokens, resume_text)
            semantic_hit = False
            partial = False
            if chunk_embs is not None:
                try:
                    atom_emb = embedder.encode(atom, convert_to_numpy=True, normalize_embeddings=True)
                    if atom_emb.ndim > 1:
                        atom_emb = atom_emb[0]
                    sims = np.dot(chunk_embs, atom_emb)
                    sim = float(np.max(sims)) if sims.size > 0 else 0.0
                    semantic_hit = sim >= strict_threshold
                    if not semantic_hit and sim >= partial_threshold:
                        partial = True
                except Exception:
                    sim = 0.0

            # Enhanced scoring with clear differentiation
            if token_hit or semantic_hit:
                score = 1.0
            elif partial:
                score = 0.5  # Reduced from 0.55 for clearer distinction
            else:
                score = 0.0
                
            details[atom] = {
                "token_hit": bool(token_hit),
                "semantic_hit": bool(semantic_hit),
                "partial_semantic": bool(partial and score == 0.5),
                "similarity": sim,
                "llm_hit": False,
                "score": score
            }

            # Only use LLM for uncertain cases (partial matches only)
            if model and score == 0.5:
                pending.append(atom)

        # RAG-enhanced LLM verification for partial matches only
        if model and pending:
            llm_results = llm_verify_requirements(
                model, pending, resume_text, req_type, 
                faiss_index=faiss_index, chunks=resume_chunks, embedder=embedder
            )
            for atom in pending:
                if llm_results.get(atom):
                    details[atom]["llm_hit"] = True
                    details[atom]["score"] = 0.85  # Between partial and full for LLM-verified
        return details

    must_details = assess(must_atoms, "must-have")
    nice_details = assess(nice_atoms, "nice-to-have") if nice_atoms else {}

    must_scores = [d["score"] for d in must_details.values()]
    nice_scores = [d["score"] for d in nice_details.values()]

    must_cov = float(np.mean(must_scores)) if must_scores else 0.0
    nice_cov = float(np.mean(nice_scores)) if nice_scores else 0.0
    
    # Adjusted weighting: 75% must-have, 25% nice-to-have
    overall = 0.75 * must_cov + 0.25 * nice_cov if (must_scores or nice_scores) else 0.0

    return {
        "overall": overall,
        "must": must_cov,
        "nice": nice_cov,
        "details": {"must": must_details, "nice": nice_details}
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

def llm_verify_requirements(model, requirements, resume_text, req_type="must-have", faiss_index=None, chunks=None, embedder=None):
    """
    Enhanced LLM-assisted verification with RAG (Retrieval-Augmented Generation).
    Uses relevant resume chunks retrieved via FAISS for better accuracy.
    """
    if not requirements or not resume_text:
        return {}
    
    # RAG: Retrieve relevant context for each requirement
    relevant_contexts = {}
    if faiss_index and chunks and embedder:
        for req in requirements:
            contexts = retrieve_relevant_context(req, faiss_index, chunks, embedder, top_k=2)
            if contexts:
                relevant_contexts[req] = "\n".join([ctx[0] for ctx in contexts])
    
    req_list = "\n".join([f"{i+1}. {r}" for i, r in enumerate(requirements)])
    
    # Build context section with RAG if available
    context_section = ""
    if relevant_contexts:
        context_section = "\n**RELEVANT RESUME EXCERPTS** (most similar sections):\n"
        for req, ctx in list(relevant_contexts.items())[:5]:  # Limit to 5 for token efficiency
            context_section += f"\nFor '{req}':\n{ctx[:400]}\n"
    
    prompt = f"""You are an expert technical recruiter with deep knowledge of technology synonyms and variations.

**TASK**: For each requirement, determine if there's STRONG EVIDENCE in the resume.

**REQUIREMENTS TO VERIFY** ({req_type}):
{req_list}
{context_section}

**FULL RESUME** (if specific context not found above):
{resume_text[:4000]}

**MATCHING INTELLIGENCE**:
1. Technology Synonyms & Variations:
   - "AI" or "ML" matches: artificial intelligence, machine learning, AI/ML, ML models, deep learning, neural networks
   - "Cloud" matches: AWS, Azure, GCP, cloud computing, cloud platforms, serverless
   - Programming languages match if mentioned in: projects, skills, tools, "worked with X", "experience in X"
   - "React" matches: React, React.js, ReactJS, React Native
   - "Node" matches: Node.js, NodeJS, Node, Express
   - "PostgreSQL" matches: PostgreSQL, Postgres, psql
   - "CI/CD" matches: continuous integration, continuous deployment, Jenkins, GitLab CI, GitHub Actions
   
2. Experience Pattern Matching:
   - "5+ years Python" is satisfied by: "6 years Python", "Python developer since 2018", "Senior Python dev"
   - "3+ years experience" matches job titles with "Senior" or longer project durations
   
3. Education & Certifications:
   - "Bachelor degree" matches: BS, B.S., B.Tech, Bachelor of Science, Undergraduate degree
   - "AWS Certified" matches: AWS Solutions Architect, AWS Developer Associate, any AWS certification

4. Contextual Evidence:
   - If resume shows projects using a technology, count it as experience
   - If resume lists technology in skills section, it counts
   - If technology appears in job responsibilities, it counts

**SCORING RULES**:
- Return `true` if there's REASONABLE EVIDENCE (direct mention, synonym, related project)
- Return `false` if there's NO EVIDENCE or only vague mentions
- Be GENEROUS but ACCURATE - if there's valid evidence, mark true
- Consider the FULL CONTEXT, not just keyword matching

**OUTPUT FORMAT**:
Return ONLY valid JSON (no markdown, no explanations):
{{"requirement1_exact_text": true, "requirement2_exact_text": false, ...}}

Use the EXACT requirement text as keys.
"""
    
    try:
        result = llm_json(model, prompt)
        if not isinstance(result, dict):
            return {}
        
        # Normalize keys to match requirements
        normalized_result = {}
        for req in requirements:
            # Try exact match first
            if req in result:
                normalized_result[req] = result[req]
            else:
                # Try case-insensitive match
                for k, v in result.items():
                    if normalize_text(k) == normalize_text(req):
                        normalized_result[req] = v
                        break
        
        return normalized_result
    except Exception:
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
    return f"""
You are a technical requirement extraction expert. Extract ONLY CONCRETE TECHNICAL REQUIREMENTS.

Return ONLY JSON with:
- must_atoms: Array of 15-30 CRITICAL technical skills/requirements (2-5 words each)
- nice_atoms: Array of 8-20 BONUS/OPTIONAL technical skills (2-5 words each)

**CRITICAL EXTRACTION RULES**:
1. Extract ONLY: specific technologies, programming languages, frameworks, tools, platforms, databases, certifications
2. Include version numbers: "Python 3.9+", "Java 11+", "React 18", "Node.js 16+"
3. Include experience requirements with context: "5+ years Python", "3+ years AWS"
4. Keep CONCRETE and SHORT (2-5 words max)
5. **NEVER extract**: soft skills, responsibilities, qualifiers, generic terms
6. **IGNORE completely**: communication, teamwork, leadership, problem-solving, collaboration
7. **IGNORE qualifiers**: "strong", "excellent", "good knowledge of", "experience with", "ability to"
8. **IGNORE job responsibilities**: "design solutions", "work with team", "develop features"
9. Extract certifications: "AWS Solutions Architect", "PMP", "CKA", "CISSP"
10. Extract education ONLY if explicitly required: "Bachelor Computer Science", "Master degree"

**STRICT FILTERING** - DO NOT EXTRACT:
❌ "strong communication skills"
❌ "team player"
❌ "problem solving"
❌ "ability to work independently"
❌ "good knowledge of"
❌ "experience with databases" (too vague - need specific: PostgreSQL, MongoDB)
❌ "cloud platforms" (too vague - need specific: AWS, Azure, GCP)
❌ "programming languages" (too vague - need specific: Python, Java, JavaScript)
❌ "agile methodologies" (too vague - unless specific: Scrum, Kanban)
❌ "design and develop"
❌ "collaborate with stakeholders"

**CORRECT EXAMPLES**:

Example 1:
JD: "5+ years of Python development experience. Strong knowledge of Django and Flask. Proficiency in AWS (Lambda, S3, DynamoDB). Excellent problem-solving skills. Bachelor's degree in Computer Science required."

GOOD OUTPUT:
{{"must_atoms": ["5+ years python", "django", "flask", "aws lambda", "aws s3", "aws dynamodb", "bachelor computer science"], "nice_atoms": []}}

BAD OUTPUT (DO NOT DO THIS):
{{"must_atoms": ["strong knowledge", "python development experience", "excellent problem-solving", "proficiency in aws"], ...}}
❌ Why bad: Contains qualifiers and vague terms

Example 2:
JD: "Required: Java 11+, Spring Boot, Kubernetes, Docker, CI/CD. Nice to have: React, TypeScript, MongoDB. Must have excellent communication skills and work well in teams."

GOOD OUTPUT:
{{"must_atoms": ["java 11", "spring boot", "kubernetes", "docker", "ci/cd"], "nice_atoms": ["react", "typescript", "mongodb"]}}

BAD OUTPUT (DO NOT DO THIS):
{{"must_atoms": ["java development", "excellent communication skills", "work well in teams", "cloud native"], ...}}
❌ Why bad: Includes soft skills and vague terms

Example 3:
JD: "We need a machine learning engineer with expertise in TensorFlow, PyTorch, and scikit-learn. Experience deploying models to production using Docker and Kubernetes. Knowledge of MLOps tools like MLflow. Good understanding of deep learning and NLP. AWS or GCP experience is a plus."

GOOD OUTPUT:
{{"must_atoms": ["machine learning", "tensorflow", "pytorch", "scikit-learn", "docker", "kubernetes", "mlops", "mlflow", "deep learning", "nlp"], "nice_atoms": ["aws", "gcp"]}}

BAD OUTPUT (DO NOT DO THIS):
{{"must_atoms": ["expertise in ml", "good understanding", "knowledge of mlops", "experience deploying models"], ...}}
❌ Why bad: Contains qualifiers and vague phrases

**NOW EXTRACT FROM THIS JOB DESCRIPTION**:
{jd[:2500]}

**RESUME PREVIEW** (for context ONLY - do NOT extract from resume):
{resume_preview[:800]}

**FINAL REMINDERS**:
- Extract NOUNS (technologies, tools), NOT verbs or adjectives
- Be ULTRA SPECIFIC: "PostgreSQL 14" not "database experience"
- COMPLETELY IGNORE all soft skills
- Keep 2-5 words per atom maximum
- If a requirement is vague, skip it or make it specific

Return ONLY valid JSON. No markdown, no explanations.
"""

def analysis_prompt(jd, plan, profile, global_sem, cov_final, cov_parts):
    return f"""
You are a STRICT technical recruiter evaluating candidate fit. Be critical and demanding.

Return ONLY JSON with:
cultural_fit, technical_strength, experience_relevance (<=60 words each),
top_strengths (string[]),
improvement_areas (string[]),
overall_comment (<=80 words),
risk_flags (string[]),
followup_questions (string[]),
fit_score (0-10 integer).

**Scoring Guide** (be CRITICAL):
- 9-10: Exceptional, exceeds all requirements, rare talent
- 7-8: Strong fit, meets all must-haves + most nice-to-haves
- 5-6: Adequate, meets most must-haves, some gaps
- 3-4: Weak fit, missing key requirements
- 0-2: Poor fit, not recommended

**Key Factors**:
- Must-have coverage: {cov_parts.get('must_coverage', 0):.2f} ({cov_parts.get('must_atoms_count', 0)} requirements)
- Nice-to-have coverage: {cov_parts.get('nice_coverage', 0):.2f} ({cov_parts.get('nice_atoms_count', 0)} requirements)
- Semantic similarity: {global_sem:.3f}
- Overall requirement match: {cov_final:.3f}

**CRITICAL RULES**:
1. If must-have coverage < 0.5, fit_score MUST be ≤ 5
2. If must-have coverage < 0.3, fit_score MUST be ≤ 3
3. Missing critical skills → significant score penalty
4. Soft skills alone don't compensate for technical gaps
5. Years of experience must match seniority requirements

JOB_DESCRIPTION:
{jd[:1500]}

ANALYSIS_PLAN:
{json.dumps(plan, indent=2)[:800]}

RESUME_PROFILE:
{json.dumps(profile, indent=2)[:1200]}

Return ONLY valid JSON. Be brutally honest in assessment.
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
    if not mongo_ok:
        print("⚠️ MongoDB not connected - skipping database save")
        return
    
    rid = None
    try:
        # Save resume document
        if resumes_collection:
            rdoc = {
                "name": resume_doc.get("name", "Unknown"),
                "email": resume_doc.get("email", "N/A"),
                "phone": resume_doc.get("phone", "N/A"),
                "file_name": resume_doc.get("file_name", "unknown"),
                "timestamp": time.time()
            }
            r = resumes_collection.insert_one(rdoc)
            rid = str(r.inserted_id)
            print(f"✅ Resume saved to DB with ID: {rid}")
        
        # Save analysis document with correct field mapping
        if analyses_collection:
            adoc = {
                "resume_id": rid,
                "candidate": resume_doc.get("name", "Unknown"),
                "email": resume_doc.get("email", "N/A"),
                "file_name": resume_doc.get("file_name", "unknown"),
                "job_desc": jd[:500] if len(jd) > 500 else jd,
                "job_desc_full": jd,
                "analysis": _sanitize_for_mongo(analysis),
                "timestamp": time.time(),
                # Fix: Use correct field names from analysis dict
                "overall_score": analysis.get("score", 0),
                "coverage_pct": analysis.get("coverage_score", 0)
            }
            result = analyses_collection.insert_one(adoc)
            print(f"✅ Analysis saved to DB with ID: {result.inserted_id}")
            st.success(f"💾 Analysis saved to database successfully!")
    except Exception as exc:
        print(f"❌ MongoDB save error: {exc}")
        import traceback
        traceback.print_exc()
        st.warning(f"⚠️ Could not save to database: {str(exc)[:100]}")

def get_recent(analyses_collection, mongo_ok, limit=20):
    items = []
    if not mongo_ok or not analyses_collection:
        print("⚠️ MongoDB not available - cannot fetch recent analyses")
        return items
    
    try:
        cursor = analyses_collection.find({}).sort("timestamp", -1).limit(limit)
        for x in cursor:
            items.append(x)
        print(f"✅ Retrieved {len(items)} recent analyses from database")
    except Exception as e:
        print(f"❌ Error fetching recent analyses: {e}")
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
        resumes_collection, analyses_collection, mongo_ok = init_mongodb()
    except Exception as e:
        st.warning(f"⚠️ MongoDB connection failed: {str(e)[:100]}")
        resumes_collection, analyses_collection, mongo_ok = None, None, False

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

                # Helper function for beautiful status messages with fade
                def show_status(progress_val, emoji, message, color_start, color_end):
                    prog.progress(progress_val)
                    stat.markdown(f"""
                    <div style="
                        background:linear-gradient(135deg,{color_start},{color_end});
                        border-radius:12px;
                        padding:14px 24px;
                        margin:8px 0;
                        box-shadow:0 4px 16px {color_start}50,0 0 30px {color_end}40;
                        backdrop-filter:blur(20px);
                        animation:statusFade 1.2s ease-in-out;
                        border:none;
                        display:flex;
                        align-items:center;
                        gap:12px;
                    ">
                        <span style="font-size:24px;animation:bounce 1s ease-in-out infinite;flex-shrink:0;">{emoji}</span>
                        <span style="
                            font-size:15px;
                            font-weight:600;
                            color:#f1f5f9;
                            font-family:'Inter',sans-serif;
                            letter-spacing:0.2px;
                            flex:1;
                        ">{message}</span>
                    </div>
                    <style>
                        @keyframes statusFade {{
                            0% {{ opacity:0; transform:translateY(-8px); }}
                            10% {{ opacity:1; transform:translateY(0); }}
                            90% {{ opacity:1; transform:translateY(0); }}
                            100% {{ opacity:0.1; transform:translateY(-8px); }}
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                    time.sleep(0.08)

                # ---------- Parse resume ----------
                show_status(0.12, "📄", "Parsing resume...", "rgba(139,92,246,.15)", "rgba(99,102,241,.12)")
                parsed = parse_resume_pdf(tmp_path, nlp, embedder)
                if not parsed:
                    st.error("No text parsed from the PDF."); st.stop()
                parsed["file_name"] = up.name
                preview = "\n".join(parsed["chunks"][:2])[:1200]
                st.session_state.uploads_history.insert(0, {"file_name":up.name,"name":parsed["name"],"email":parsed["email"],"phone":parsed["phone"],"timestamp":time.time()})

                # ---------- Plan & profile ----------
                show_status(0.28, "🎯", "Deriving analysis plan...", "rgba(236,72,153,.15)", "rgba(219,39,119,.12)")
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

                show_status(0.36, "👤", "Parsing resume profile...", "rgba(99,102,241,.15)", "rgba(79,70,229,.12)")
                profile = llm_json(model, resume_profile_prompt(parsed["text"])) or {}
                parsed["llm_profile"] = profile

                # ---------- Atomic requirements (LLM + heuristic) ----------
                show_status(0.46, "🔍", "Extracting atomic requirements...", "rgba(139,92,246,.15)", "rgba(124,58,237,.12)")
                atoms_llm = llm_json(model, atomicize_requirements_prompt(jd, preview)) or {}
                jd_atoms_raw = extract_atoms_from_text(jd, nlp, max_atoms=60)

                must_candidates = (atoms_llm.get("must_atoms") or []) + jd_atoms_raw[:30]
                must_atoms, must_canon = refine_atom_list(must_candidates, nlp, limit=35)

                nice_candidates = (atoms_llm.get("nice_atoms") or []) + jd_atoms_raw[30:80]
                nice_atoms, _ = refine_atom_list(nice_candidates, nlp, reserved_canonicals=must_canon, limit=30)

                # ---------- Coverage (semantic similarity over chunks) ----------
                show_status(0.58, "📊", "Scoring requirement coverage...", "rgba(16,185,129,.15)", "rgba(5,150,105,.12)")
                coverage_summary = evaluate_requirement_coverage(
                    must_atoms, nice_atoms, parsed.get("text", ""), parsed.get("chunks", []), 
                    embedder, model, faiss_index=parsed.get("faiss")
                )
                cov_final = coverage_summary["overall"]
                must_cov = coverage_summary["must"]
                nice_cov = coverage_summary["nice"]

                # ---------- Global semantic ----------
                show_status(0.68, "🧠", "Computing semantic similarity...", "rgba(236,72,153,.15)", "rgba(219,39,119,.12)")
                global_sem = compute_global_semantic(embedder, parsed.get("embs"), jd)
                global_sem01 = (global_sem + 1.0) / 2.0  # map [-1,1] -> [0,1]

                # ---------- LLM narrative & fit ----------
                show_status(0.78, "✨", "LLM narrative assessment...", "rgba(99,102,241,.15)", "rgba(79,70,229,.12)")
                cov_parts = {
                    "must_coverage": round(must_cov,3),
                    "nice_coverage": round(nice_cov,3),
                    "must_atoms_count": len(must_atoms),
                    "nice_atoms_count": len(nice_atoms),
                    "overall": round(cov_final,3)
                }
                llm_out = llm_json(model, analysis_prompt(jd, plan, profile, global_sem01, cov_final, cov_parts))
                fit_score = llm_out.get("fit_score")
                if not isinstance(fit_score, (int, float)):
                    # Enhanced fallback: better balance between semantic and coverage
                    # Favor coverage more as it's more concrete
                    fit_score = round(10 * (0.35*global_sem01 + 0.65*cov_final), 1)
                fit_score = float(np.clip(fit_score, 0, 10))

                # ---------- Balanced Final Scoring with Smart Penalties ----------
                weights = plan.get("scoring_weights", DEFAULT_WEIGHTS)
                sem10, cov10 = round(10*global_sem01,1), round(10*cov_final,1)
                w_sem, w_cov, w_llm = float(weights["semantic"]), float(weights["coverage"]), float(weights["llm_fit"])
                W = w_sem + w_cov + w_llm
                if W <= 1e-9:
                    w_sem, w_cov, w_llm = DEFAULT_WEIGHTS["semantic"], DEFAULT_WEIGHTS["coverage"], DEFAULT_WEIGHTS["llm_fit"]
                    W = w_sem + w_cov + w_llm
                w_sem, w_cov, w_llm = w_sem/W, w_cov/W, w_llm/W
                
                # Base score calculation
                raw_score = float(np.clip(w_sem*sem10 + w_cov*cov10 + w_llm*fit_score, 0, 10))
                
                # Smart penalty system - only penalize truly poor matches
                penalty = 0.0
                penalty_reason = []
                
                if must_atoms and len(must_atoms) > 0:
                    # Only apply penalties for significantly low coverage
                    if must_cov < 0.30:  # Less than 30% is critical failure
                        penalty_amount = max(raw_score - 4.0, 0)
                        penalty = max(penalty, penalty_amount)
                        penalty_reason.append(f"Critical gaps (<30% must-haves)")
                    elif must_cov < 0.45:  # Less than 45% is major concern
                        penalty_amount = min(raw_score * 0.20, 1.5)
                        penalty = max(penalty, penalty_amount)
                        penalty_reason.append(f"Major gaps (<45% must-haves)")
                    
                    # Small penalty for low combined semantic + coverage
                    if global_sem01 < 0.40 and must_cov < 0.50:
                        additional_penalty = min(1.0, raw_score * 0.10)
                        penalty += additional_penalty
                        penalty_reason.append("Low overall alignment")
                
                # Apply penalty
                final_score = float(np.clip(raw_score - penalty, 0, 10))
                
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

                # Final success with beautiful fade
                prog.progress(1.0)
                stat.markdown("""
                <div style="
                    background:linear-gradient(135deg,rgba(16,185,129,.2),rgba(5,150,105,.15));
                    border:2px solid rgba(16,185,129,.5);
                    border-radius:16px;
                    padding:18px 32px;
                    margin:12px 0;
                    box-shadow:0 8px 32px rgba(16,185,129,.4),0 0 60px rgba(5,150,105,.3);
                    backdrop-filter:blur(20px);
                    animation:successFadeOut 1.5s ease-in-out forwards;
                ">
                    <div style="display:flex;align-items:center;justify-content:center;gap:16px;">
                        <span style="font-size:32px;animation:bounce 0.6s ease-in-out 3;">✅</span>
                        <span style="
                            font-size:18px;
                            font-weight:900;
                            color:#6ee7b7;
                            font-family:'Space Grotesk',sans-serif;
                            letter-spacing:0.5px;
                        ">Analysis Complete!</span>
                        <span style="font-size:32px;animation:bounce 0.6s ease-in-out 3;animation-delay:0.2s;">🚀</span>
                    </div>
                </div>
                <style>
                    @keyframes successFadeOut {
                        0% { opacity:0; transform:scale(0.9); }
                        15% { opacity:1; transform:scale(1); }
                        85% { opacity:1; transform:scale(1); }
                        100% { opacity:0; transform:scale(0.95); }
                    }
                </style>
                """, unsafe_allow_html=True)
                time.sleep(1.2)
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
                info.setdefault("token_hit", False)
                info.setdefault("semantic_hit", False)
                info.setdefault("partial_semantic", False)
                info.setdefault("llm_hit", False)
                info.setdefault("similarity", 0.0)
                detail_map[atom] = info
            return detail_map

        must_detail_map = build_detail_map(must_atoms, matches.get("must", {}))
        nice_detail_map = build_detail_map(nice_atoms, matches.get("nice", {}))

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
                        signals = []
                        if info.get("token_hit"):
                            signals.append("Token match")
                        if info.get("semantic_hit"):
                            signals.append("Semantic match")
                        if info.get("llm_hit"):
                            signals.append("LLM verified")
                        if not signals and info.get("similarity", 0.0) > 0:
                            signals.append(f"Sim {info['similarity']:.2f}")
                        signal_html = " • ".join(signals) if signals else "Signal not captured"
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                                    border:2px solid rgba(16,185,129,.4);border-left:5px solid #10b981;
                                    border-radius:16px;padding:20px 24px;display:flex;align-items:center;gap:16px;
                                    backdrop-filter:blur(20px);transition:all .4s cubic-bezier(.34,1.56,.64,1);
                                    box-shadow:0 6px 20px rgba(16,185,129,.2);position:relative;overflow:hidden;">
                            <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(16,185,129,.08),transparent);
                                        opacity:0;transition:opacity .4s ease;"></div>
                            <span style="flex-shrink:0;min-width:40px;height:40px;
                                         background:linear-gradient(135deg,rgba(16,185,129,.35),rgba(16,185,129,.25));
                                         color:#6ee7b7;border-radius:50%;display:flex;align-items:center;justify-content:center;
                                         font-size:20px;font-weight:900;border:2px solid rgba(16,185,129,.6);
                                         box-shadow:0 4px 15px rgba(16,185,129,.4);position:relative;z-index:1;">✓</span>
                            <div style="display:flex;flex-direction:column;gap:4px;position:relative;z-index:1;">
                                <span style="color:#f1f5f9;font-size:16px;font-weight:600;line-height:1.6;">{req}</span>
                                <span style="color:#94a3b8;font-size:12px;font-weight:500;">{signal_html}</span>
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
                        signals = []
                        if info.get("token_hit"):
                            signals.append("Token evidence")
                        if info.get("partial_semantic") or info.get("semantic_hit"):
                            signals.append(f"Semantic {info.get('similarity',0.0):.2f}")
                        if info.get("llm_hit"):
                            signals.append("LLM verified")
                        signal_html = " • ".join(signals) if signals else "Weak evidence"
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                                    border:2px solid rgba(251,191,36,.4);border-left:5px solid #fbbf24;
                                    border-radius:16px;padding:20px 24px;display:flex;align-items:center;gap:16px;
                                    backdrop-filter:blur(20px);transition:all .4s cubic-bezier(.34,1.56,.64,1);
                                    box-shadow:0 6px 20px rgba(251,191,36,.2);position:relative;overflow:hidden;">
                            <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(251,191,36,.08),transparent);
                                        opacity:0;transition:opacity .4s ease;"></div>
                            <span style="flex-shrink:0;min-width:40px;height:40px;
                                         background:linear-gradient(135deg,rgba(251,191,36,.35),rgba(251,191,36,.25));
                                         color:#fde68a;border-radius:50%;display:flex;align-items:center;justify-content:center;
                                         font-size:20px;font-weight:900;border:2px solid rgba(251,191,36,.6);
                                         box-shadow:0 4px 15px rgba(251,191,36,.4);position:relative;z-index:1;">△</span>
                            <div style="display:flex;flex-direction:column;gap:4px;position:relative;z-index:1;">
                                <span style="color:#f1f5f9;font-size:16px;font-weight:600;line-height:1.6;">{req}</span>
                                <span style="color:#94a3b8;font-size:12px;font-weight:500;">{signal_html}</span>
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
                        similarity_note = info.get("similarity", 0.0)
                        signals = []
                        if similarity_note > 0.05:
                            signals.append(f"Best sim {similarity_note:.2f}")
                        if info.get("token_hit"):
                            signals.append("tokens present")
                        signal_html = " • ".join(signals) if signals else "No supporting evidence"
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                                    border:2px solid rgba(239,68,68,.4);border-left:5px solid #ef4444;
                                    border-radius:16px;padding:20px 24px;display:flex;align-items:center;gap:16px;
                                    backdrop-filter:blur(20px);transition:all .4s cubic-bezier(.34,1.56,.64,1);
                                    box-shadow:0 6px 20px rgba(239,68,68,.2);position:relative;overflow:hidden;">
                            <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(239,68,68,.08),transparent);
                                        opacity:0;transition:opacity .4s ease;"></div>
                            <span style="flex-shrink:0;min-width:40px;height:40px;
                                         background:linear-gradient(135deg,rgba(239,68,68,.35),rgba(239,68,68,.25));
                                         color:#fca5a5;border-radius:50%;display:flex;align-items:center;justify-content:center;
                                         font-size:20px;font-weight:900;border:2px solid rgba(239,68,68,.6);
                                         box-shadow:0 4px 15px rgba(239,68,68,.4);position:relative;z-index:1;">✗</span>
                            <div style="display:flex;flex-direction:column;gap:4px;position:relative;z-index:1;">
                                <span style="color:#f1f5f9;font-size:16px;font-weight:600;line-height:1.6;">{req}</span>
                                <span style="color:#94a3b8;font-size:12px;font-weight:500;">{signal_html}</span>
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
                        signals = []
                        if info.get("token_hit"):
                            signals.append("Token match")
                        if info.get("semantic_hit"):
                            signals.append("Semantic match")
                        if info.get("llm_hit"):
                            signals.append("LLM verified")
                        if not signals and info.get("similarity", 0.0) > 0:
                            signals.append(f"Sim {info['similarity']:.2f}")
                        signal_html = " • ".join(signals) if signals else "Signal not captured"
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                                    border:2px solid rgba(139,92,246,.4);border-left:5px solid #8b5cf6;
                                    border-radius:16px;padding:20px 24px;display:flex;align-items:center;gap:16px;
                                    backdrop-filter:blur(20px);transition:all .4s cubic-bezier(.34,1.56,.64,1);
                                    box-shadow:0 6px 20px rgba(139,92,246,.2);position:relative;overflow:hidden;">
                            <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(139,92,246,.08),transparent);
                                        opacity:0;transition:opacity .4s ease;"></div>
                            <span style="flex-shrink:0;min-width:40px;height:40px;
                                         background:linear-gradient(135deg,rgba(139,92,246,.35),rgba(139,92,246,.25));
                                         color:#c7d2fe;border-radius:50%;display:flex;align-items:center;justify-content:center;
                                         font-size:20px;font-weight:900;border:2px solid rgba(139,92,246,.6);
                                         box-shadow:0 4px 15px rgba(139,92,246,.4);position:relative;z-index:1;">⭐</span>
                            <div style="display:flex;flex-direction:column;gap:4px;position:relative;z-index:1;">
                                <span style="color:#f1f5f9;font-size:16px;font-weight:600;line-height:1.6;">{req}</span>
                                <span style="color:#94a3b8;font-size:12px;font-weight:500;">{signal_html}</span>
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
                        signals = []
                        if info.get("token_hit"):
                            signals.append("Token evidence")
                        if info.get("partial_semantic") or info.get("semantic_hit"):
                            signals.append(f"Semantic {info.get('similarity',0.0):.2f}")
                        if info.get("llm_hit"):
                            signals.append("LLM verified")
                        signal_html = " • ".join(signals) if signals else "Weak evidence"
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                                    border:2px solid rgba(96,165,250,.4);border-left:5px solid #60a5fa;
                                    border-radius:16px;padding:20px 24px;display:flex;align-items:center;gap:16px;
                                    backdrop-filter:blur(20px);transition:all .4s cubic-bezier(.34,1.56,.64,1);
                                    box-shadow:0 6px 20px rgba(96,165,250,.2);position:relative;overflow:hidden;">
                            <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(96,165,250,.08),transparent);
                                        opacity:0;transition:opacity .4s ease;"></div>
                            <span style="flex-shrink:0;min-width:40px;height:40px;
                                         background:linear-gradient(135deg,rgba(96,165,250,.35),rgba(96,165,250,.25));
                                         color:#dbeafe;border-radius:50%;display:flex;align-items:center;justify-content:center;
                                         font-size:20px;font-weight:900;border:2px solid rgba(96,165,250,.6);
                                         box-shadow:0 4px 15px rgba(96,165,250,.4);position:relative;z-index:1;">△</span>
                            <div style="display:flex;flex-direction:column;gap:4px;position:relative;z-index:1;">
                                <span style="color:#f1f5f9;font-size:16px;font-weight:600;line-height:1.6;">{req}</span>
                                <span style="color:#94a3b8;font-size:12px;font-weight:500;">{signal_html}</span>
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
                        similarity_note = info.get("similarity", 0.0)
                        signals = []
                        if similarity_note > 0.05:
                            signals.append(f"Best sim {similarity_note:.2f}")
                        if info.get("token_hit"):
                            signals.append("tokens present")
                        signal_html = " • ".join(signals) if signals else "No supporting evidence"
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,rgba(21,10,46,.85),rgba(13,2,33,.85));
                                    border:2px solid rgba(99,102,241,.4);border-left:5px solid #6366f1;
                                    border-radius:16px;padding:20px 24px;display:flex;align-items:center;gap:16px;
                                    backdrop-filter:blur(20px);transition:all .4s cubic-bezier(.34,1.56,.64,1);
                                    box-shadow:0 6px 20px rgba(99,102,241,.2);position:relative;overflow:hidden;">
                            <div style="position:absolute;inset:0;background:linear-gradient(135deg,rgba(99,102,241,.08),transparent);
                                        opacity:0;transition:opacity .4s ease;"></div>
                            <span style="flex-shrink:0;min-width:40px;height:40px;
                                         background:linear-gradient(135deg,rgba(99,102,241,.35),rgba(99,102,241,.25));
                                         color:#93c5fd;border-radius:50%;display:flex;align-items:center;justify-content:center;
                                         font-size:20px;font-weight:900;border:2px solid rgba(99,102,241,.6);
                                         box-shadow:0 4px 15px rgba(99,102,241,.4);position:relative;z-index:1;">○</span>
                            <div style="display:flex;flex-direction:column;gap:4px;position:relative;z-index:1;">
                                <span style="color:#cbd5e1;font-size:16px;font-weight:600;line-height:1.6;">{req}</span>
                                <span style="color:#94a3b8;font-size:12px;font-weight:500;">{signal_html}</span>
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
            technical_strength = str(llm.get('technical_strength', 'N/A'))
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
                        {area}
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
        """ + str(llm.get('overall_comment', 'Pending analysis'))[:500] + """
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
    
    # Combine all recent activities
    recent_db = get_recent(analyses_collection, mongo_ok, limit=15)
    all_activities = []
    
    # Add uploads
    for u in st.session_state.uploads_history[:12]:
        all_activities.append({
            "type": "upload",
            "name": u.get("name", "Unknown"),
            "file": u.get("file_name", "Unknown"),
            "email": u.get("email", "N/A"),
            "phone": u.get("phone", "N/A"),
            "timestamp": u.get("timestamp", 0),
            "emoji": "📄"
        })
    
    # Add analyses
    for i, entry in enumerate(st.session_state.analysis_history[:10] if st.session_state.analysis_history else []):
        all_activities.append({
            "type": "analysis",
            "name": entry.get("resume_meta", {}).get("name", "Unknown"),
            "score": entry.get("score", 0),
            "semantic": entry.get("semantic_score", 0),
            "coverage": entry.get("coverage_score", 0),
            "fit": entry.get("llm_fit_score", 0),
            "email": entry.get("resume_meta", {}).get("email", ""),
            "file": entry.get("resume_meta", {}).get("file_name", ""),
            "timestamp": entry.get("timestamp", 0),
            "emoji": "✨"
        })
    
    # Sort by timestamp descending
    all_activities.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
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
            
            if activity["type"] == "analysis":
                score = activity.get("score", 0)
                color_class = "score-excellent" if score >= 8 else "score-good" if score >= 6 else "score-fair" if score >= 4 else "score-poor"
                
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
            else:  # upload
                st.markdown(f"""
                <div style="
                    background:linear-gradient(135deg,rgba(99,102,241,.08),rgba(139,92,246,.06));
                    border-left:4px solid rgba(99,102,241,.5);
                    border-radius:14px;
                    padding:18px 24px;
                    margin-bottom:16px;
                    box-shadow:0 4px 16px rgba(0,0,0,.15),0 0 30px rgba(99,102,241,.1);
                    backdrop-filter:blur(20px);
                    animation:fadeInRotate 0.5s ease-out;
                    animation-delay:{idx * 0.05}s;
                ">
                    <div style="display:flex;align-items:center;gap:14px;">
                        <span style="font-size:24px;">{activity['emoji']}</span>
                        <div style="flex:1;">
                            <div style="
                                font-size:15px;
                                font-weight:700;
                                color:#f1f5f9;
                                font-family:'Inter',sans-serif;
                                margin-bottom:6px;
                            ">{activity['name']} <span style="color:#94a3b8;font-weight:500;">• {activity['file']}</span></div>
                            <div style="
                                display:flex;
                                gap:20px;
                                font-size:12px;
                                color:#cbd5e1;
                                flex-wrap:wrap;
                            ">
                                <span><strong>Email:</strong> {activity['email']}</span>
                                <span><strong>Phone:</strong> {activity['phone']}</span>
                                <span style="color:#94a3b8;font-weight:500;margin-left:auto;">{t}</span>
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
