"""
Database Operations (PostgreSQL)
"""
import os
import psycopg2
from psycopg2 import pool
import streamlit as st
import json
from datetime import datetime

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

