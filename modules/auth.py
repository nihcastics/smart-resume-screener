"""
Enterprise-Grade Authentication System
Secure user registration and login with individual user data isolation
"""
import hashlib
import secrets
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# Security configuration
PASSWORD_SALT_LENGTH = 32
MIN_PASSWORD_LENGTH = 8


def _hash_password(password, salt=None):
    """
    Securely hash password with salt using SHA-256.
    Returns (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(PASSWORD_SALT_LENGTH)
    
    # Combine password and salt
    salted = f"{password}{salt}".encode('utf-8')
    
    # Hash with SHA-256
    hashed = hashlib.sha256(salted).hexdigest()
    
    return hashed, salt


def init_auth_tables(conn):
    """
    Initialize authentication tables in database.
    Creates users table if not exists.
    """
    try:
        with conn.cursor() as cursor:
            # Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                password_salt VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
            
            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            
            -- Update resumes table to link to users
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='resumes' AND column_name='user_id'
                ) THEN
                    ALTER TABLE resumes ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
                    CREATE INDEX idx_resumes_user_id ON resumes(user_id);
                END IF;
            END $$;
            
            -- Update analyses table to link to users
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='analyses' AND column_name='user_id'
                ) THEN
                    ALTER TABLE analyses ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
                    CREATE INDEX idx_analyses_user_id ON analyses(user_id);
                END IF;
            END $$;
            """)
        
        conn.commit()
        logger.info("✅ Authentication tables initialized")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize auth tables: {e}")
        conn.rollback()
        return False


def register_user(conn, username, email, password, full_name=""):
    """
    Register a new user.
    Returns (success: bool, message: str, user_id: int or None)
    """
    # Input validation
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters", None
    
    if not email or '@' not in email:
        return False, "Invalid email address", None
    
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters", None
    
    # Sanitize inputs
    username = username.strip().lower()
    email = email.strip().lower()
    full_name = full_name.strip()
    
    try:
        # Check if username or email already exists
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT username, email FROM users 
                WHERE username = %s OR email = %s
            """, (username, email))
            
            existing = cursor.fetchone()
            if existing:
                if existing['username'] == username:
                    return False, "Username already taken", None
                else:
                    return False, "Email already registered", None
        
        # Hash password
        password_hash, salt = _hash_password(password)
        
        # Insert new user
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, password_salt, full_name)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (username, email, password_hash, salt, full_name))
            
            user_id = cursor.fetchone()[0]
        
        conn.commit()
        logger.info(f"✅ User registered: {username} (ID: {user_id})")
        return True, "Registration successful!", user_id
        
    except psycopg2.IntegrityError as e:
        conn.rollback()
        logger.error(f"Registration integrity error: {e}")
        return False, "Username or email already exists", None
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Registration failed: {e}")
        return False, f"Registration error: {str(e)[:100]}", None


def login_user(conn, username_or_email, password):
    """
    Authenticate user login.
    Returns (success: bool, message: str, user_data: dict or None)
    """
    if not username_or_email or not password:
        return False, "Please enter username/email and password", None
    
    username_or_email = username_or_email.strip().lower()
    
    try:
        # Fetch user
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, username, email, password_hash, password_salt, full_name, is_active
                FROM users
                WHERE username = %s OR email = %s
            """, (username_or_email, username_or_email))
            
            user = cursor.fetchone()
        
        if not user:
            return False, "Invalid username/email or password", None
        
        if not user['is_active']:
            return False, "Account is inactive. Contact support.", None
        
        # Verify password
        password_hash, _ = _hash_password(password, user['password_salt'])
        
        if password_hash != user['password_hash']:
            return False, "Invalid username/email or password", None
        
        # Update last login
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (user['id'],))
        
        conn.commit()
        
        # Return user data (without sensitive info)
        user_data = {
            'user_id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'] or user['username']
        }
        
        logger.info(f"✅ User logged in: {user['username']} (ID: {user['id']})")
        return True, "Login successful!", user_data
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False, f"Login error: {str(e)[:100]}", None


def get_user_analyses(conn, user_id, limit=20, offset=0):
    """
    Get analyses for specific user (data isolation).
    Returns list of analysis records.
    """
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
            WHERE a.user_id = %s
            ORDER BY a.created_at DESC
            LIMIT %s OFFSET %s
            """, (user_id, limit, offset))
            
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            # Parse JSON fields
            def safe_json_parse(field):
                data = row.get(field)
                if isinstance(data, dict):
                    return data
                if isinstance(data, str):
                    try:
                        import json
                        return json.loads(data)
                    except:
                        return {}
                return {}
            
            final_analysis = safe_json_parse('final_analysis')
            coverage = safe_json_parse('coverage')
            
            skills = row.get('technical_skills', [])
            if isinstance(skills, str):
                try:
                    import json
                    skills = json.loads(skills)
                except:
                    skills = []
            if not isinstance(skills, list):
                skills = []
            
            final_score_raw = float(row.get('final_score', 0.0) or 0.0)
            semantic_raw = float(row.get('semantic_score', 0.0) or 0.0)
            coverage_raw = float(row.get('coverage_score', 0.0) or 0.0)
            llm_fit_raw = float(row.get('llm_fit_score', final_score_raw) or 0.0)

            has_score_breakdown = isinstance(final_analysis, dict) and isinstance(final_analysis.get('score_breakdown'), dict)
            legacy_scale = (
                not has_score_breakdown and
                final_score_raw <= 1.0 and
                llm_fit_raw <= 1.0 and
                coverage_raw <= 0.2 and
                semantic_raw <= 0.2
            )

            if legacy_scale:
                final_score_raw = min(final_score_raw * 100.0, 10.0)
                llm_fit_raw = min(llm_fit_raw * 100.0, 10.0)
                coverage_raw = min(coverage_raw * 100.0, 1.0)
                semantic_raw = min(semantic_raw * 100.0, 1.0)

            coverage_summary = {}
            if isinstance(coverage, dict):
                summary_block = coverage.get('summary') or coverage.get('summary_percent') or {}
                if isinstance(summary_block, dict):
                    coverage_summary = summary_block

            score_breakdown = final_analysis.get('score_breakdown') if isinstance(final_analysis, dict) else {}
            if not isinstance(score_breakdown, dict):
                score_breakdown = {}
            if not score_breakdown:
                score_breakdown = {}

            nice_cover_raw = None
            must_cover_raw = None
            if isinstance(coverage, dict):
                summary_section = coverage.get('summary', {})
                if isinstance(summary_section, dict):
                    must_cover_raw = summary_section.get('must_coverage')
                    nice_cover_raw = summary_section.get('nice_coverage')
            if must_cover_raw is None:
                must_percent_value = coverage_summary.get('must_percent') if isinstance(coverage_summary, dict) else None
                if must_percent_value is not None:
                    try:
                        must_cover_raw = float(must_percent_value) / 100.0
                    except (TypeError, ValueError):
                        must_cover_raw = None
            if nice_cover_raw is None:
                nice_percent_value = coverage_summary.get('nice_percent') if isinstance(coverage_summary, dict) else None
                if nice_percent_value is not None:
                    try:
                        nice_cover_raw = float(nice_percent_value) / 100.0
                    except (TypeError, ValueError):
                        nice_cover_raw = None

            must_cover_raw = float(must_cover_raw) if must_cover_raw is not None else coverage_raw
            nice_cover_raw = float(nice_cover_raw) if nice_cover_raw is not None else 1.0

            if isinstance(score_breakdown, dict):
                score_breakdown.setdefault('tier', final_analysis.get('score_tier') if isinstance(final_analysis, dict) else '')
                score_breakdown.setdefault('final_score_out_of_10', round(final_score_raw, 2))
                score_breakdown.setdefault('final_score_percent', round(final_score_raw * 10, 1))
                score_breakdown.setdefault('semantic_match_percent', round(semantic_raw * 100, 1))
                score_breakdown.setdefault('requirement_coverage_percent', round(coverage_raw * 100, 1))
                score_breakdown.setdefault('must_have_coverage_percent', round(must_cover_raw * 100, 1))
                score_breakdown.setdefault('nice_to_have_coverage_percent', round(nice_cover_raw * 100, 1))

            recommendation_text = ''
            if isinstance(final_analysis, dict):
                recommendation_text = final_analysis.get('overall_comment') or final_analysis.get('recommendation') or ''

            missing_reqs = []
            if isinstance(final_analysis, dict):
                fa_missing = final_analysis.get('missing_requirements')
                if isinstance(fa_missing, list):
                    missing_reqs = fa_missing[:5]
            if not missing_reqs and isinstance(coverage, dict):
                coverage_missing = coverage.get('missing_requirements')
                if isinstance(coverage_missing, list):
                    missing_reqs = coverage_missing[:5]

            short_comment = (recommendation_text[:150] + '...') if recommendation_text and len(recommendation_text) > 150 else recommendation_text

            results.append({
                'analysis_id': row.get('analysis_id'),
                'resume_id': row.get('resume_id'),
                'candidate': row.get('candidate', 'Unknown'),
                'email': row.get('email', 'Not found'),
                'phone': row.get('phone', 'Not found'),
                'skills': skills[:15],
                'jd_preview': (row.get('jd_preview', '') or '') + '...',
                'final_score': round(final_score_raw, 2),
                'final_score_percent': round(final_score_raw * 10, 1),
                'semantic_score': semantic_raw,
                'semantic_score_percent': round(semantic_raw * 100, 1),
                'coverage_score': coverage_raw,
                'coverage_score_percent': round(coverage_raw * 100, 1),
                'llm_fit_score': round(llm_fit_raw, 2),
                'llm_fit_score_percent': round(llm_fit_raw * 10, 1),
                'fit_score': row.get('fit_score', round(final_score_raw)),
                'score_tier': score_breakdown.get('tier') or final_analysis.get('score_tier') if isinstance(final_analysis, dict) else '',
                'score_breakdown': score_breakdown,
                'top_strengths': (final_analysis.get('top_strengths') or final_analysis.get('strengths') or [])[:3] if isinstance(final_analysis, dict) else [],
                'improvement_areas': (final_analysis.get('improvement_areas') or final_analysis.get('gaps') or [])[:2] if isinstance(final_analysis, dict) else [],
                'overall_comment': short_comment,
                'overall_comment_full': recommendation_text,
                'must_coverage_percent': round(must_cover_raw * 100, 1),
                'nice_coverage_percent': round(nice_cover_raw * 100, 1),
                'coverage_summary': coverage_summary,
                'missing_requirements': missing_reqs,
                'created_at': row.get('created_at'),
                'timestamp': row.get('created_at').timestamp() if row.get('created_at') else 0
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to get user analyses: {e}")
        return []


def count_user_analyses(conn, user_id):
    """Get total count of analyses for user."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM analyses WHERE user_id = %s", (user_id,))
            return cursor.fetchone()[0]
    except:
        return 0
