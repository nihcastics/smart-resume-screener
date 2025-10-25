"""
Enhanced Database Operations (PostgreSQL with Supabase support)
Enterprise-grade with connection pooling, retry logic, and SQL injection protection
"""
import os
import json
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2 import pool
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ENTERPRISE CONFIGURATION
MAX_DB_RETRIES = 3
DB_RETRY_DELAY = 2  # seconds
CONNECTION_TIMEOUT = 15  # seconds
QUERY_TIMEOUT = 60  # seconds (increased for complex queries)
MIN_POOL_SIZE = 1
MAX_POOL_SIZE = 5

# Global connection pool
_connection_pool = None


def _get_connection_pool(db_url):
    """
    Get or create connection pool (singleton pattern).
    Returns connection pool or None.
    """
    global _connection_pool
    
    if _connection_pool is not None:
        try:
            # Test pool health
            conn = _connection_pool.getconn()
            conn.close()
            _connection_pool.putconn(conn)
            return _connection_pool
        except:
            logger.warning("Connection pool unhealthy, recreating...")
            _connection_pool = None
    
    # Create new pool
    try:
        import psycopg2.pool
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            MIN_POOL_SIZE,
            MAX_POOL_SIZE,
            db_url,
            connect_timeout=CONNECTION_TIMEOUT,
            options=f'-c statement_timeout={QUERY_TIMEOUT * 1000}'  # Convert to milliseconds
        )
        logger.info(f"✅ Connection pool created (size={MIN_POOL_SIZE}-{MAX_POOL_SIZE})")
        return _connection_pool
    except Exception as e:
        logger.error(f"Failed to create connection pool: {e}")
        return None


def _get_pooled_connection(db_url):
    """
    Get connection from pool with retry logic.
    Returns (conn, success_flag)
    """
    pool_obj = _get_connection_pool(db_url)
    
    if not pool_obj:
        return None, False
    
    for attempt in range(MAX_DB_RETRIES):
        try:
            conn = pool_obj.getconn()
            conn.autocommit = False  # Use transactions
            return conn, True
        except Exception as e:
            logger.warning(f"Pool getconn failed (attempt {attempt + 1}): {e}")
            if attempt < MAX_DB_RETRIES - 1:
                time.sleep(DB_RETRY_DELAY)
            continue
    
    return None, False


def _return_connection(conn):
    """Return connection to pool."""
    global _connection_pool
    if _connection_pool and conn:
        try:
            _connection_pool.putconn(conn)
        except:
            pass


def init_postgresql():
    """
    Initialize PostgreSQL connection with Supabase-specific handling.
    Enterprise-grade with connection pooling, IPv6 fix, retry logic, and validation.
    """
    # Try environment variable for DATABASE_URL
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        logger.info("Using DATABASE_URL from environment variable")
    
    if not db_url or not db_url.strip():
        logger.warning("No DATABASE_URL found. Database features disabled.")
        return None, False
    
    # Validate DATABASE_URL format
    if not db_url.startswith(("postgresql://", "postgres://")):
        logger.error("Invalid DATABASE_URL format (must start with postgresql:// or postgres://)")
        return None, False

    # Retry logic for initialization
    for attempt in range(MAX_DB_RETRIES):
        try:
            # Supabase IPv6 compatibility fix (forces IPv4)
            import socket as _socket
            _original_getaddrinfo = _socket.getaddrinfo
            def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
                return _original_getaddrinfo(host, port, _socket.AF_INET, type, proto, flags)
            _socket.getaddrinfo = custom_getaddrinfo

            # Test connection with pooling
            logger.info(f"Connecting to Supabase PostgreSQL (attempt {attempt + 1}/{MAX_DB_RETRIES})...")
            
            conn, ok = _get_pooled_connection(db_url)
            if not ok or not conn:
                raise Exception("Could not get connection from pool")
            
            # Create tables with enhanced schema
            with conn.cursor() as cursor:
                logger.info("Creating/verifying database schema...")
                
                # Resumes table - stores candidate information
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS resumes (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    phone VARCHAR(100),
                    text TEXT NOT NULL,
                    chunks JSONB DEFAULT '[]'::jsonb,
                    entities JSONB DEFAULT '{}'::jsonb,
                    technical_skills JSONB DEFAULT '[]'::jsonb,
                    experience JSONB DEFAULT '[]'::jsonb,
                    projects JSONB DEFAULT '[]'::jsonb,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create indexes for better query performance
                CREATE INDEX IF NOT EXISTS idx_resumes_name ON resumes(name);
                CREATE INDEX IF NOT EXISTS idx_resumes_email ON resumes(email);
                CREATE INDEX IF NOT EXISTS idx_resumes_created_at ON resumes(created_at DESC);
                """)
                
                # Analyses table - stores matching results
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id SERIAL PRIMARY KEY,
                    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
                    jd_text TEXT NOT NULL,
                    plan JSONB DEFAULT '{}'::jsonb,
                    profile JSONB DEFAULT '{}'::jsonb,
                    coverage JSONB DEFAULT '{}'::jsonb,
                    cue_alignment JSONB DEFAULT '{}'::jsonb,
                    final_analysis JSONB DEFAULT '{}'::jsonb,
                    semantic_score REAL DEFAULT 0.0,
                    coverage_score REAL DEFAULT 0.0,
                    llm_fit_score REAL DEFAULT 0.0,
                    final_score REAL DEFAULT 0.0,
                    fit_score INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create indexes for analyses
                CREATE INDEX IF NOT EXISTS idx_analyses_resume_id ON analyses(resume_id);
                CREATE INDEX IF NOT EXISTS idx_analyses_final_score ON analyses(final_score DESC);
                CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_analyses_composite ON analyses(resume_id, created_at DESC);
                """)
            
            conn.commit()
            _return_connection(conn)
            
            logger.info("✅ Successfully connected to Supabase database and initialized schema")
            
            # Return a new connection for actual use (don't reuse initialization connection)
            conn, ok = _get_pooled_connection(db_url)
            return conn, ok
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            logger.error(f"❌ Database connection failed (attempt {attempt + 1}): {error_msg[:200]}")
            
            if attempt < MAX_DB_RETRIES - 1:
                wait_time = DB_RETRY_DELAY * (attempt + 1)  # Exponential backoff
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"❌ Database connection failed after {MAX_DB_RETRIES} attempts: {error_msg[:150]}")
                return None, False
                
        except Exception as e:
            logger.error(f"❌ Database initialization error: {str(e)[:200]}")
            if attempt < MAX_DB_RETRIES - 1:
                time.sleep(DB_RETRY_DELAY)
                continue
            else:
                logger.error(f"❌ Database initialization error: {str(e)[:150]}")
                return None, False
    
    return None, False


def _sanitize_for_postgres(data):
    """
    Sanitize data for PostgreSQL JSONB storage with validation.
    """
    if data is None:
        return None
    if isinstance(data, bool):  # Check bool before int (bool is subclass of int)
        return data
    if isinstance(data, (str, int, float)):
        return data
    if isinstance(data, (list, tuple)):
        return [_sanitize_for_postgres(item) for item in data]
    if isinstance(data, dict):
        return {k: _sanitize_for_postgres(v) for k, v in data.items() if k is not None}
    
    # Fallback: convert to string for unknown types
    try:
        return str(data)
    except:
        return None


def _validate_score(value, default=0.0):
    """Validate and normalize score value."""
    try:
        score = float(value)
        # Clamp to valid range
        return max(0.0, min(1.0, score))
    except (TypeError, ValueError):
        logger.warning(f"Invalid score value: {value}, using default {default}")
        return default


def _validate_integer(value, default=0, min_val=None, max_val=None):
    """Validate integer value with optional bounds."""
    try:
        val = int(value)
        if min_val is not None:
            val = max(min_val, val)
        if max_val is not None:
            val = min(max_val, val)
        return val
    except (TypeError, ValueError):
        return default


def save_to_db(parsed_resume, jd_text, analysis, conn, db_ok, user_id=None):
    """
    Save resume and analysis to database with user isolation.
    Enhanced error handling and validation with user_id for privacy.
    """
    if not db_ok or not conn:
        logger.warning("Database not available, skipping save operation")
        return None, None
    
    resume_id = None
    analysis_id = None
    
    try:
        with conn.cursor() as cursor:
            # Start transaction
            logger.info("Saving resume to database...")
            
            # Insert resume with enhanced fields + user_id
            cursor.execute("""
            INSERT INTO resumes (
                name, email, phone, text, chunks, entities, technical_skills, experience, projects, user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (
                parsed_resume.get('name', 'Unknown'),
                parsed_resume.get('email', 'Not found'),
                parsed_resume.get('phone', 'Not found'),
                (parsed_resume.get('text', '') or '')[:10000],  # Limit to 10k chars
                Json(_sanitize_for_postgres(parsed_resume.get('chunks', []))),
                Json(_sanitize_for_postgres(parsed_resume.get('entities', {}))),
                Json(_sanitize_for_postgres(parsed_resume.get('technical_skills', []))),
                Json(_sanitize_for_postgres(parsed_resume.get('experience', []))),
                Json(_sanitize_for_postgres(parsed_resume.get('projects', []))),
                user_id  # Add user_id for data isolation
            ))
            resume_id = cursor.fetchone()[0]
            logger.info(f"Resume saved with ID: {resume_id} for user: {user_id}")
            
            # Insert analysis with computed scores + user_id
            logger.info("Saving analysis to database...")
            plan_payload = _sanitize_for_postgres(analysis.get('plan', {}))
            profile_payload = _sanitize_for_postgres(analysis.get('profile', analysis.get('resume_profile', {})))

            coverage_payload = analysis.get('coverage')
            if isinstance(coverage_payload, dict):
                coverage_payload = dict(coverage_payload)
                if analysis.get('coverage_summary') and 'summary_percent' not in coverage_payload:
                    coverage_payload['summary_percent'] = analysis.get('coverage_summary')
            sanitized_coverage = _sanitize_for_postgres(coverage_payload or {})

            cue_alignment_payload = _sanitize_for_postgres(analysis.get('cue_alignment', {}))

            final_analysis_payload = analysis.get('final_analysis', analysis.get('llm_analysis', {}))
            if isinstance(final_analysis_payload, dict):
                final_analysis_payload = dict(final_analysis_payload)
                if 'score_breakdown' not in final_analysis_payload and analysis.get('score_breakdown'):
                    final_analysis_payload['score_breakdown'] = analysis.get('score_breakdown')
                if 'score_tier' not in final_analysis_payload and analysis.get('score_tier'):
                    final_analysis_payload['score_tier'] = analysis.get('score_tier')
                if analysis.get('missing_requirements') and 'missing_requirements' not in final_analysis_payload:
                    final_analysis_payload['missing_requirements'] = analysis.get('missing_requirements')
            sanitized_final_analysis = _sanitize_for_postgres(final_analysis_payload or {})

            semantic_score = _validate_score(float(analysis.get('semantic_score', 0.0)))
            coverage_score = _validate_score(float(analysis.get('coverage_score', 0.0)))
            llm_fit_score = max(0.0, min(10.0, float(analysis.get('llm_fit_score', analysis.get('final_score', 0.0)))))
            final_score_value = max(0.0, min(10.0, float(analysis.get('final_score', analysis.get('score', 0.0)))))
            fit_score_value = _validate_integer(round(float(analysis.get('fit_score', llm_fit_score))), min_val=0, max_val=10)

            cursor.execute("""
            INSERT INTO analyses (
                resume_id, jd_text, plan, profile, coverage, cue_alignment,
                final_analysis, semantic_score, coverage_score, llm_fit_score,
                final_score, fit_score, user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (
                resume_id,
                (jd_text or '')[:5000],  # Limit to 5k chars
                Json(plan_payload),
                Json(profile_payload),
                Json(sanitized_coverage),
                Json(cue_alignment_payload),
                Json(sanitized_final_analysis),
                semantic_score,
                coverage_score,
                llm_fit_score,
                final_score_value,
                fit_score_value,
                user_id  # Add user_id for data isolation
            ))
            analysis_id = cursor.fetchone()[0]
            logger.info(f"Analysis saved with ID: {analysis_id}")
        
        # Commit transaction
        conn.commit()
        logger.info(f"✅ Saved resume (ID: {resume_id}) and analysis (ID: {analysis_id}) to database")
        return resume_id, analysis_id
        
    except psycopg2.Error as e:
        # Rollback on error
        if conn:
            conn.rollback()
        logger.error(f"❌ Database save failed: {str(e)}")
        return None, None
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Unexpected error during save: {str(e)}")
        return None, None


def get_recent(conn, db_ok, limit=20, offset=0):
    """
    Fetch recent analyses from database with enhanced filtering and pagination.
    Returns list of analysis records with candidate details and scores.
    """
    if not db_ok or not conn:
        logger.warning("Database not available, returning empty results")
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
            SELECT 
                a.id AS analysis_id,
                r.id AS resume_id,
                r.name AS candidate,
                r.email,
                r.phone,
                r.technical_skills,
                LEFT(a.jd_text, 200) AS jd_preview,
                a.semantic_score,
                a.coverage_score,
                a.llm_fit_score,
                a.final_score,
                a.fit_score,
                a.final_analysis,
                a.coverage,
                a.created_at
            FROM analyses a
            JOIN resumes r ON r.id = a.resume_id
            ORDER BY a.created_at DESC
            LIMIT %s OFFSET %s
            """, (limit, offset))
            
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            # Parse JSON fields safely
            def safe_json_parse(field):
                data = row.get(field)
                if isinstance(data, dict):
                    return data
                if isinstance(data, str):
                    try:
                        return json.loads(data)
                    except:
                        return {}
                return {}
            
            final_analysis = safe_json_parse('final_analysis')
            coverage = safe_json_parse('coverage')
            
            # Extract skills (may be JSONB or array)
            skills = row.get('technical_skills', [])
            if isinstance(skills, str):
                try:
                    skills = json.loads(skills)
                except:
                    skills = []
            if not isinstance(skills, list):
                skills = []
            
            # Build result record
            results.append({
                'analysis_id': row.get('analysis_id'),
                'resume_id': row.get('resume_id'),
                'candidate': row.get('candidate', 'Unknown'),
                'email': row.get('email', 'Not found'),
                'phone': row.get('phone', 'Not found'),
                'skills': skills[:15],  # Limit to first 15 skills
                'jd_preview': (row.get('jd_preview', '') or '') + '...',
                'final_score': float(row.get('final_score', 0.0)) * 100,  # Convert to percentage
                'semantic_score': float(row.get('semantic_score', 0.0)) * 100,
                'coverage_score': float(row.get('coverage_score', 0.0)) * 100,
                'llm_fit_score': float(row.get('llm_fit_score', 0.0)) * 100,
                'fit_score': row.get('fit_score', 0),
                'top_strengths': (final_analysis.get('top_strengths') or [])[:3],
                'improvement_areas': (final_analysis.get('improvement_areas') or [])[:2],
                'overall_comment': (final_analysis.get('overall_comment', ''))[:150] + '...' if final_analysis.get('overall_comment') else '',
                'must_coverage': float(coverage.get('must', 0.0)) * 100 if isinstance(coverage, dict) else 0.0,
                'created_at': row.get('created_at'),
                'timestamp': row.get('created_at').timestamp() if row.get('created_at') else 0
            })
        
        logger.info(f"Retrieved {len(results)} recent analyses from database")
        return results
        
    except psycopg2.Error as e:
        logger.error(f"❌ Database query failed: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error retrieving recent analyses: {str(e)}")
        return []


def get_analysis_by_id(conn, db_ok, analysis_id):
    """
    Retrieve full analysis details by ID for detailed view.
    """
    if not db_ok or not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
            SELECT 
                a.*,
                r.name AS candidate_name,
                r.email AS candidate_email,
                r.phone AS candidate_phone,
                r.text AS resume_text,
                r.technical_skills,
                r.entities,
                r.experience,
                r.projects
            FROM analyses a
            JOIN resumes r ON r.id = a.resume_id
            WHERE a.id = %s
            """, (analysis_id,))
            
            row = cursor.fetchone()
        
        if not row:
            return None
        
        # Parse JSON fields
        def safe_json_load(field):
            data = row.get(field)
            if isinstance(data, dict):
                return data
            if isinstance(data, str):
                try:
                    return json.loads(data)
                except:
                    return {}
            return {}
        
        return {
            'analysis_id': row.get('id'),
            'candidate': row.get('candidate_name'),
            'email': row.get('candidate_email'),
            'phone': row.get('candidate_phone'),
            'resume_text': row.get('resume_text'),
            'skills': row.get('technical_skills', []),
            'entities': safe_json_load('entities'),
            'experience': safe_json_load('experience'),
            'projects': safe_json_load('projects'),
            'jd_text': row.get('jd_text'),
            'plan': safe_json_load('plan'),
            'profile': safe_json_load('profile'),
            'coverage': safe_json_load('coverage'),
            'cue_alignment': safe_json_load('cue_alignment'),
            'final_analysis': safe_json_load('final_analysis'),
            'final_score': float(row.get('final_score', 0.0)) * 100,
            'semantic_score': float(row.get('semantic_score', 0.0)) * 100,
            'coverage_score': float(row.get('coverage_score', 0.0)) * 100,
            'created_at': row.get('created_at')
        }
        
    except Exception as e:
        logger.error(f"❌ Error retrieving analysis {analysis_id}: {str(e)}")
        return None


def count_total_analyses(conn, db_ok):
    """Get total count of analyses for pagination."""
    if not db_ok or not conn:
        return 0
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM analyses")
            count = cursor.fetchone()[0]
        return count
    except:
        return 0


def search_analyses(conn, db_ok, search_term, limit=20):
    """
    Search analyses by candidate name, email, or skills.
    Enterprise-grade: SQL injection safe, input validated, limited results.
    """
    if not db_ok or not conn:
        return []
    
    # Input validation
    if not search_term or not isinstance(search_term, str):
        logger.warning("Invalid search term provided")
        return []
    
    # Sanitize search term (prevent SQL injection via LIKE patterns)
    search_term = search_term.strip()
    if len(search_term) == 0:
        return []
    
    # Limit search term length (DoS protection)
    if len(search_term) > 100:
        logger.warning(f"Search term too long ({len(search_term)} chars), truncating")
        search_term = search_term[:100]
    
    # Escape special LIKE characters
    search_term = search_term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    
    # Validate limit
    limit = _validate_integer(limit, default=20, min_val=1, max_val=100)
    
    try:
        # Safe parameterized query (NO string interpolation)
        search_pattern = f"%{search_term}%"
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Parameterized query - safe from SQL injection
            cursor.execute("""
            SELECT 
                a.id AS analysis_id,
                r.name AS candidate,
                r.email,
                a.final_score,
                a.created_at
            FROM analyses a
            JOIN resumes r ON r.id = a.resume_id
            WHERE 
                r.name ILIKE %s OR
                r.email ILIKE %s OR
                r.technical_skills::text ILIKE %s
            ORDER BY a.created_at DESC
            LIMIT %s
            """, (search_pattern, search_pattern, search_pattern, limit))
            
            results = cursor.fetchall()
            logger.info(f"Search for '{search_term}' returned {len(results)} results")
            return results
            
    except psycopg2.Error as e:
        logger.error(f"SQL search failed: {str(e)[:200]}")
        return []
    except Exception as e:
        logger.error(f"Search failed: {str(e)[:200]}")
        return []
        return []
