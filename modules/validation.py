"""
Enterprise-Grade Data Validation Module
Prevents garbage data from entering the database with strict checks
"""
import re
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures"""
    pass


def validate_email(email: str) -> bool:
    """Validate email format with RFC 5322 compliance"""
    if not email or not isinstance(email, str):
        return False
    
    # Comprehensive email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """Validate phone number (flexible international format)"""
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-().]', '', phone)
    
    # Should be 10-15 digits, optionally starting with +
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def validate_text_quality(text: str, min_length: int = 100, max_length: int = 50000) -> Tuple[bool, Optional[str]]:
    """
    Validate text content quality
    Returns: (is_valid, error_message)
    """
    if not text or not isinstance(text, str):
        return False, "Text is empty or not a string"
    
    text_stripped = text.strip()
    
    # Length checks
    if len(text_stripped) < min_length:
        return False, f"Text too short ({len(text_stripped)} chars, minimum {min_length})"
    
    if len(text_stripped) > max_length:
        return False, f"Text too long ({len(text_stripped)} chars, maximum {max_length})"
    
    # Check for meaningful content (not just whitespace/symbols)
    words = text_stripped.split()
    if len(words) < 20:
        return False, f"Insufficient word count ({len(words)} words, minimum 20)"
    
    # Check character variety (not just repeated characters)
    unique_chars = len(set(text_stripped.replace(' ', '').replace('\n', '')))
    if unique_chars < 10:
        return False, f"Insufficient character variety ({unique_chars} unique chars)"
    
    # Check for readable text (should have some common English words)
    common_words = {'the', 'and', 'or', 'in', 'of', 'to', 'for', 'with', 'on', 'at', 'by', 'from'}
    text_lower = text_stripped.lower()
    common_found = sum(1 for word in common_words if f' {word} ' in f' {text_lower} ')
    if common_found < 3:
        return False, "Text appears to be gibberish (no common English words found)"
    
    return True, None


def validate_resume_data(resume_doc: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Comprehensive validation of parsed resume data before database insertion.
    Returns: (is_valid, list_of_issues)
    """
    issues = []
    
    if not resume_doc or not isinstance(resume_doc, dict):
        return False, ["Resume data is None or not a dictionary"]
    
    # 1. TEXT VALIDATION
    text = resume_doc.get('text', '')
    text_valid, text_error = validate_text_quality(text, min_length=100, max_length=50000)
    if not text_valid:
        issues.append(f"Invalid resume text: {text_error}")
    
    # 2. CONTACT VALIDATION
    email = resume_doc.get('email', 'Not found')
    phone = resume_doc.get('phone', 'Not found')
    
    # At least one contact method should be valid
    has_valid_email = email != 'Not found' and validate_email(email)
    has_valid_phone = phone != 'Not found' and validate_phone(phone)
    
    if not has_valid_email and not has_valid_phone:
        issues.append("No valid contact information (email or phone) found")
    
    # 3. SKILLS VALIDATION
    skills = resume_doc.get('technical_skills', [])
    if not isinstance(skills, list):
        issues.append("Technical skills must be a list")
    elif len(skills) == 0:
        issues.append("No technical skills extracted (resume likely malformed)")
    elif len(skills) > 200:
        issues.append(f"Too many skills ({len(skills)}), likely extraction error")
    
    # Check skill quality
    if skills:
        # Filter out empty/whitespace skills
        valid_skills = [s for s in skills if isinstance(s, str) and s.strip() and len(s.strip()) > 1]
        if len(valid_skills) < len(skills) * 0.5:
            issues.append(f"More than 50% of skills are invalid ({len(valid_skills)}/{len(skills)})")
    
    # 4. CHUNKS VALIDATION
    chunks = resume_doc.get('chunks', [])
    if not isinstance(chunks, list):
        issues.append("Chunks must be a list")
    elif len(chunks) == 0:
        issues.append("No text chunks created (parsing failed)")
    elif len(chunks) > 1000:
        issues.append(f"Too many chunks ({len(chunks)}), likely parsing error")
    
    # Check chunk quality
    if chunks:
        valid_chunks = [c for c in chunks if isinstance(c, str) and len(c.strip()) > 10]
        if len(valid_chunks) < len(chunks) * 0.8:
            issues.append(f"More than 20% of chunks are invalid ({len(valid_chunks)}/{len(chunks)})")
    
    # 5. NAME VALIDATION
    name = resume_doc.get('name', 'Unknown')
    if not name or name == 'Unknown' or not isinstance(name, str):
        issues.append("Candidate name not found or invalid")
    elif len(name) < 2 or len(name) > 100:
        issues.append(f"Name length suspicious ({len(name)} chars)")
    elif not re.search(r'[a-zA-Z]', name):
        issues.append("Name contains no letters")
    
    # 6. EMBEDDING/INDEX VALIDATION
    faiss_index = resume_doc.get('faiss')
    if faiss_index is None:
        issues.append("FAISS index not built (embedding failed)")
    
    # 7. EXPERIENCE VALIDATION
    experience = resume_doc.get('experience', [])
    if experience and isinstance(experience, list):
        for i, exp in enumerate(experience):
            if not isinstance(exp, dict):
                issues.append(f"Experience entry {i} is not a dict")
                continue
            
            if 'title' not in exp and 'company' not in exp:
                issues.append(f"Experience entry {i} missing title and company")
    
    # DETERMINE VALIDITY
    # Critical issues that MUST fail validation
    critical_keywords = [
        "Resume data is None",
        "not a dictionary",
        "Text too short",
        "gibberish",
        "No text chunks created",
        "FAISS index not built"
    ]
    
    has_critical_issue = any(
        any(keyword in issue for keyword in critical_keywords)
        for issue in issues
    )
    
    is_valid = not has_critical_issue and len(issues) < 5  # Max 4 non-critical issues allowed
    
    if not is_valid:
        logger.warning(f"Resume validation failed: {len(issues)} issues found")
        for issue in issues[:10]:  # Log first 10 issues
            logger.warning(f"  - {issue}")
    
    return is_valid, issues


def validate_jd_data(jd_text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate job description text before processing.
    Returns: (is_valid, error_message)
    """
    if not jd_text or not isinstance(jd_text, str):
        return False, "Job description is empty or not a string"
    
    # Use text quality validation
    is_valid, error = validate_text_quality(jd_text, min_length=50, max_length=20000)
    if not is_valid:
        return False, f"Invalid JD: {error}"
    
    # JD-specific checks
    jd_lower = jd_text.lower()
    
    # Should mention common JD keywords
    jd_keywords = ['experience', 'skill', 'requirement', 'responsibility', 'qualification', 'role', 'position', 'job']
    keywords_found = sum(1 for kw in jd_keywords if kw in jd_lower)
    
    if keywords_found < 2:
        return False, "Text doesn't appear to be a job description (missing common JD keywords)"
    
    return True, None


def validate_analysis_results(results: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate analysis results before saving to database.
    Returns: (is_valid, list_of_issues)
    """
    issues = []
    
    if not results or not isinstance(results, dict):
        return False, ["Analysis results are None or not a dictionary"]
    
    # 1. SCORE VALIDATION
    final_score = results.get('final_score')
    if final_score is None:
        issues.append("Missing final_score")
    elif not isinstance(final_score, (int, float)):
        issues.append(f"final_score must be numeric, got {type(final_score)}")
    elif not (0 <= final_score <= 10):
        issues.append(f"final_score out of range: {final_score} (must be 0-10)")
    
    # 2. COVERAGE VALIDATION
    coverage_score = results.get('coverage_score')
    if coverage_score is None:
        issues.append("Missing coverage_score")
    elif not isinstance(coverage_score, (int, float)):
        issues.append(f"coverage_score must be numeric, got {type(coverage_score)}")
    elif not (0 <= coverage_score <= 1):
        issues.append(f"coverage_score out of range: {coverage_score} (must be 0-1)")
    
    semantic_score = results.get('semantic_score')
    if semantic_score is None:
        issues.append("Missing semantic_score")
    elif not isinstance(semantic_score, (int, float)):
        issues.append(f"semantic_score must be numeric, got {type(semantic_score)}")
    elif not (0 <= semantic_score <= 1):
        issues.append(f"semantic_score out of range: {semantic_score} (must be 0-1)")
    
    # 3. FINAL ANALYSIS VALIDATION
    final_analysis = results.get('final_analysis', {})
    if not isinstance(final_analysis, dict):
        issues.append("final_analysis must be a dictionary")
    else:
        required_keys = ['strengths', 'gaps', 'recommendation']
        for key in required_keys:
            if key not in final_analysis:
                issues.append(f"final_analysis missing required key: {key}")
        
        # Validate strengths and gaps are lists
        strengths = final_analysis.get('strengths', [])
        gaps = final_analysis.get('gaps', [])
        
        if not isinstance(strengths, list):
            issues.append("strengths must be a list")
        elif len(strengths) == 0:
            issues.append("No strengths identified (analysis likely failed)")
        
        if not isinstance(gaps, list):
            issues.append("gaps must be a list")
        
        # Validate recommendation is string
        recommendation = final_analysis.get('recommendation', '')
        if not isinstance(recommendation, str):
            issues.append("recommendation must be a string")
        elif len(recommendation) < 20:
            issues.append(f"recommendation too short ({len(recommendation)} chars, min 20)")
    
    # 4. REQUIREMENT DETAILS VALIDATION
    requirement_details = results.get('requirement_details', {})
    if requirement_details and isinstance(requirement_details, dict):
        must_details = requirement_details.get('must', {})
        if not isinstance(must_details, dict):
            issues.append("requirement_details.must must be a dict")
    
    is_valid = len(issues) == 0
    
    if not is_valid:
        logger.warning(f"Analysis validation failed: {len(issues)} issues")
        for issue in issues[:10]:
            logger.warning(f"  - {issue}")
    
    return is_valid, issues


def sanitize_resume_data(resume_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize resume data to ensure clean database insertion.
    Removes nulls, trims whitespace, enforces types.
    """
    sanitized = {}
    
    # Name - ensure string, trim
    name = resume_doc.get('name', 'Unknown')
    sanitized['name'] = str(name).strip()[:100] if name else 'Unknown'
    
    # Email - validate and clean
    email = resume_doc.get('email', 'Not found')
    if email and validate_email(email):
        sanitized['email'] = email.strip().lower()
    else:
        sanitized['email'] = 'Not found'
    
    # Phone - validate and clean
    phone = resume_doc.get('phone', 'Not found')
    if phone and validate_phone(phone):
        sanitized['phone'] = phone.strip()
    else:
        sanitized['phone'] = 'Not found'
    
    # Text - trim and limit length
    text = resume_doc.get('text', '')
    sanitized['text'] = str(text).strip()[:50000] if text else ''
    
    # Skills - ensure list, remove duplicates, trim
    skills = resume_doc.get('technical_skills', [])
    if isinstance(skills, list):
        cleaned_skills = []
        seen = set()
        for skill in skills:
            if isinstance(skill, str):
                skill_clean = skill.strip()
                skill_lower = skill_clean.lower()
                if skill_clean and skill_lower not in seen and len(skill_clean) <= 100:
                    cleaned_skills.append(skill_clean)
                    seen.add(skill_lower)
        sanitized['technical_skills'] = cleaned_skills[:200]  # Max 200 skills
    else:
        sanitized['technical_skills'] = []
    
    # Chunks - ensure list, clean
    chunks = resume_doc.get('chunks', [])
    if isinstance(chunks, list):
        cleaned_chunks = [str(c).strip() for c in chunks if c and isinstance(c, str)]
        sanitized['chunks'] = cleaned_chunks[:1000]  # Max 1000 chunks
    else:
        sanitized['chunks'] = []
    
    # Experience - sanitize list of dicts
    experience = resume_doc.get('experience', [])
    if isinstance(experience, list):
        cleaned_exp = []
        for exp in experience[:20]:  # Max 20 experience entries
            if isinstance(exp, dict):
                cleaned_exp.append({
                    'title': str(exp.get('title', '')).strip()[:200],
                    'company': str(exp.get('company', '')).strip()[:200],
                    'years': float(exp.get('years', 0)) if exp.get('years') else 0
                })
        sanitized['experience'] = cleaned_exp
    else:
        sanitized['experience'] = []
    
    # Education - sanitize
    education = resume_doc.get('education', [])
    if isinstance(education, list):
        cleaned_edu = []
        for edu in education[:10]:  # Max 10 education entries
            if isinstance(edu, dict):
                cleaned_edu.append({
                    'degree': str(edu.get('degree', '')).strip()[:200],
                    'institution': str(edu.get('institution', '')).strip()[:200],
                    'year': str(edu.get('year', '')).strip()[:20]
                })
        sanitized['education'] = cleaned_edu
    else:
        sanitized['education'] = []
    
    # Keep FAISS index as-is (complex object)
    sanitized['faiss'] = resume_doc.get('faiss')
    
    # Keep embeddings as-is
    sanitized['embeddings'] = resume_doc.get('embeddings')
    
    # Entities - keep but limit
    entities = resume_doc.get('entities', {})
    if isinstance(entities, dict):
        sanitized['entities'] = entities
    else:
        sanitized['entities'] = {}
    
    return sanitized


def sanitize_analysis_data(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize analysis data before database insertion.
    """
    def _safe_dict(value: Any) -> Dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _safe_list(value: Any) -> List[Any]:
        return value if isinstance(value, list) else []

    sanitized: Dict[str, Any] = {}

    # Scores - ensure numeric and in range
    final_score = max(0, min(10, float(analysis_data.get('final_score', 0))))
    sanitized['final_score'] = final_score
    sanitized['llm_fit_score'] = max(0, min(10, float(analysis_data.get('llm_fit_score', final_score))))
    sanitized['fit_score'] = max(0, min(10, float(analysis_data.get('fit_score', sanitized['llm_fit_score']))))

    sanitized['coverage_score'] = max(0, min(1, float(analysis_data.get('coverage_score', 0))))
    sanitized['semantic_score'] = max(0, min(1, float(analysis_data.get('semantic_score', 0))))

    # Persist structured analysis metadata
    sanitized['plan'] = _safe_dict(analysis_data.get('plan'))
    profile_dict = analysis_data.get('profile', analysis_data.get('resume_profile', {}))
    sanitized['profile'] = _safe_dict(profile_dict)
    sanitized['cue_alignment'] = _safe_dict(analysis_data.get('cue_alignment'))

    coverage_dict = _safe_dict(analysis_data.get('coverage'))
    sanitized['coverage'] = coverage_dict

    coverage_summary = analysis_data.get('coverage_summary')
    if not isinstance(coverage_summary, dict):
        coverage_summary = coverage_dict.get('summary') if isinstance(coverage_dict, dict) else {}
    sanitized['coverage_summary'] = _safe_dict(coverage_summary)

    # Track must/nice coverage ratios when available
    summary = sanitized['coverage_summary'] if isinstance(sanitized['coverage_summary'], dict) else {}

    def _ratio_from_summary(summary_dict: Dict[str, Any], ratio_key: str, percent_key: str, fallback: float) -> float:
        if not isinstance(summary_dict, dict):
            return fallback
        ratio_value = summary_dict.get(ratio_key)
        if ratio_value is not None:
            try:
                return float(ratio_value)
            except (TypeError, ValueError):
                return fallback
        percent_value = summary_dict.get(percent_key)
        if percent_value is not None:
            try:
                return float(percent_value) / 100.0
            except (TypeError, ValueError):
                return fallback
        return fallback

    must_ratio_source = coverage_dict.get('summary', {}).get('must_coverage') if coverage_dict else None
    nice_ratio_source = coverage_dict.get('summary', {}).get('nice_coverage') if coverage_dict else None

    must_ratio = must_ratio_source if must_ratio_source is not None else _ratio_from_summary(summary, 'must_coverage', 'must_percent', float(analysis_data.get('must_coverage', 0.0)))
    nice_ratio = nice_ratio_source if nice_ratio_source is not None else _ratio_from_summary(summary, 'nice_coverage', 'nice_percent', float(analysis_data.get('nice_coverage', 1.0)))

    sanitized['must_coverage'] = max(0.0, min(1.0, float(must_ratio)))
    sanitized['nice_coverage'] = max(0.0, min(1.0, float(nice_ratio)))

    sanitized['must_present_count'] = int(analysis_data.get('must_present_count', summary.get('must_present_count', 0) if isinstance(summary, dict) else 0))
    sanitized['must_total'] = int(analysis_data.get('must_total', summary.get('must_total', 0) if isinstance(summary, dict) else 0))

    # Missing requirement insights
    sanitized['missing_requirements'] = _safe_list(analysis_data.get('missing_requirements'))[:10]

    # Requirement details
    requirement_details = analysis_data.get('requirement_details')
    if not isinstance(requirement_details, dict) and isinstance(coverage_dict, dict):
        requirement_details = coverage_dict.get('details', {})
    sanitized['requirement_details'] = _safe_dict(requirement_details)

    # Final analysis - sanitize sub-dict with added score metadata
    final_analysis = analysis_data.get('final_analysis', analysis_data.get('llm_analysis', {}))
    if isinstance(final_analysis, dict):
        strengths = [str(s).strip()[:200] for s in final_analysis.get('strengths', [])[:50]]
        gaps = [str(g).strip()[:200] for g in final_analysis.get('gaps', [])[:50]]
        recommendation = str(final_analysis.get('recommendation', '')).strip()[:2000]
        red_flags = [str(f).strip()[:200] for f in final_analysis.get('red_flags', [])[:20]]
        score_tier = str(final_analysis.get('score_tier', analysis_data.get('score_tier', ''))).strip()
        score_breakdown_source = final_analysis.get('score_breakdown', analysis_data.get('score_breakdown', analysis_data.get('calibration', {})))
        if not isinstance(score_breakdown_source, dict):
            score_breakdown_source = {}
    else:
        strengths, gaps, red_flags = [], [], []
        recommendation = 'Analysis failed'
        score_tier = str(analysis_data.get('score_tier', '')).strip()
        score_breakdown_source = analysis_data.get('score_breakdown', analysis_data.get('calibration', {}))
        if not isinstance(score_breakdown_source, dict):
            score_breakdown_source = {}

    score_breakdown = {
        'tier': score_tier,
        'final_score_out_of_10': round(final_score, 2),
        'final_score_percent': round(final_score * 10, 1),
        'semantic_match_percent': round(sanitized['semantic_score'] * 100, 1),
        'requirement_coverage_percent': round(sanitized['coverage_score'] * 100, 1),
        'must_have_coverage_percent': round(sanitized['must_coverage'] * 100, 1),
        'nice_to_have_coverage_percent': round(sanitized['nice_coverage'] * 100, 1),
        'breakdown_points': score_breakdown_source
    }

    sanitized['score_breakdown'] = score_breakdown
    sanitized['score_tier'] = score_tier

    sanitized['final_analysis'] = {
        'strengths': strengths,
        'top_strengths': strengths,
        'gaps': gaps,
        'improvement_areas': gaps,
        'recommendation': recommendation,
        'overall_comment': recommendation,
        'red_flags': red_flags,
        'score_tier': score_tier,
        'score_breakdown': score_breakdown,
        'coverage_summary': sanitized['coverage_summary'],
        'missing_requirements': sanitized['missing_requirements']
    }

    return sanitized
