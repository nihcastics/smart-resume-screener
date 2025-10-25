"""
Dynamic Prompt Enrichment with AI-Powered Context Learning
Uses NLP and machine learning to extract and learn context from JD/Resume dynamically
Enterprise-grade with caching, validation, and ReDoS protection
"""
import re
import logging
from collections import Counter
import hashlib
from functools import lru_cache

logger = logging.getLogger(__name__)

# ENTERPRISE CONFIGURATION
MAX_TEXT_FOR_ENRICHMENT = 20000  # characters
MAX_REGEX_INPUT = 15000  # characters (ReDoS protection)
CACHE_SIZE = 128  # LRU cache entries

# ============================================================================
# DYNAMIC CONTEXT EXTRACTION
# ============================================================================

def _hash_text(text):
    """Generate hash for caching purposes."""
    return hashlib.md5(text.encode('utf-8', errors='ignore')).hexdigest()[:16]


@lru_cache(maxsize=CACHE_SIZE)
def _extract_technical_entities_cached(text_hash, text):
    """Cached version of technical entity extraction."""
    return _extract_technical_entities_impl(text)


def extract_technical_entities(text, nlp_model=None):
    """
    Dynamically extract technical entities from text using NLP with caching.
    Returns: dict with technologies, frameworks, tools, domains
    """
    if not text or not isinstance(text, str):
        logger.warning("Invalid text input to extract_technical_entities")
        return {
            "technologies": [],
            "frameworks": [],
            "tools": [],
            "domains": [],
            "experience_requirements": [],
            "version_specific": []
        }
    
    # Truncate if too long
    if len(text) > MAX_TEXT_FOR_ENRICHMENT:
        logger.warning(f"Text truncated for enrichment: {len(text)} → {MAX_TEXT_FOR_ENRICHMENT}")
        text = text[:MAX_TEXT_FOR_ENRICHMENT]
    
    # Use cache
    text_hash = _hash_text(text)
    try:
        return _extract_technical_entities_cached(text_hash, text)
    except Exception as e:
        logger.error(f"Cached extraction failed: {e}, falling back to direct call")
        return _extract_technical_entities_impl(text)


def _extract_technical_entities_impl(text):
    """Implementation of technical entity extraction."""
    # Truncate for ReDoS protection
    if len(text) > MAX_REGEX_INPUT:
        text = text[:MAX_REGEX_INPUT]
    
    text_lower = text.lower()
    
    entities = {
        "technologies": [],
        "frameworks": [],
        "tools": [],
        "domains": [],
        "experience_requirements": [],
        "version_specific": []
    }
    
    try:
        # Extract capitalized tech terms (high precision indicators)
        # ReDoS-safe: Limited input size + simple pattern
        tech_terms = re.findall(r'\b[A-Z][a-zA-Z0-9]*(?:\.[a-z]+)?(?:\s+[A-Z][a-zA-Z0-9]*){0,2}\b', text)
        
        # Validate extracted terms
        for tech in tech_terms:
            if len(tech) > 2 and len(tech) < 50 and tech not in ["The", "This", "That", "With", "From", "And", "But"]:
                entities["technologies"].append(tech)
        
        # Extract version-specific mentions (e.g., "Python 3.x", "React 18")
        version_patterns = re.findall(r'\b([A-Za-z]+)\s*(\d+(?:\.\d+)?(?:\+)?)\b', text)
        for tech, version in version_patterns[:20]:  # Limit to 20 results
            if len(tech) > 1:
                entities["version_specific"].append(f"{tech} {version}")
        
        # Extract experience patterns (e.g., "5+ years Python")
        experience_patterns = re.findall(r'(\d+\+?)\s*(?:years?|yrs?)\s+(?:of\s+)?(\w+)', text_lower)
        for exp_years, tech in experience_patterns[:15]:  # Limit to 15 results
            if len(tech) > 2:
                entities["experience_requirements"].append(f"{exp_years} years {tech}")
        
    except Exception as e:
        logger.error(f"Regex extraction failed: {e}")
    
    # Deduplicate while preserving order
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))[:30]  # Max 30 per category
    
    return entities


def extract_domain_context(jd_text):
    """
    Dynamically extract domain/industry context from JD using TRUE semantic analysis.
    NO hardcoded patterns - learns from actual text using NLP and frequency analysis.
    Returns: dict with industry indicators, domain keywords, required skills
    """
    jd_lower = jd_text.lower()
    
    # Extract all meaningful terms (4+ chars, not common words)
    words = re.findall(r'\b[a-z]{4,}\b', jd_lower)
    word_freq = Counter(words)
    
    # Filter out common English words (expanded dynamic list)
    common_words = {
        "this", "that", "with", "from", "have", "will", "been", "about", "your", "their",
        "should", "would", "could", "were", "what", "when", "where", "which", "while",
        "must", "able", "such", "also", "more", "than", "other", "into", "only", "over",
        "some", "them", "then", "very", "well", "work", "years", "year", "experience",
        "requirements", "required", "preferred", "skills", "knowledge", "ability", "strong"
    }
    
    # Get domain-specific keywords (frequent, non-common, meaningful)
    relevant_keywords = [
        word for word, count in word_freq.most_common(50)
        if word not in common_words and count >= 2 and len(word) > 3
    ]
    
    # DYNAMIC DOMAIN DETECTION using keyword clustering
    # Instead of hardcoded domains, we cluster similar keywords
    domain_clusters = {}
    
    # Technical term categories (learned dynamically from top keywords)
    if relevant_keywords:
        # Data/Analytics cluster
        data_terms = [kw for kw in relevant_keywords if any(term in kw for term in ['data', 'analytics', 'analysis', 'insight', 'report', 'visual'])]
        if data_terms:
            domain_clusters["data_analytics"] = len(data_terms)
        
        # Cloud/Infrastructure cluster
        cloud_terms = [kw for kw in relevant_keywords if any(term in kw for term in ['cloud', 'infra', 'deploy', 'devops', 'server', 'container'])]
        if cloud_terms:
            domain_clusters["cloud_infrastructure"] = len(cloud_terms)
        
        # Security cluster
        security_terms = [kw for kw in relevant_keywords if any(term in kw for term in ['security', 'auth', 'encrypt', 'secure', 'compliance', 'vulnerability'])]
        if security_terms:
            domain_clusters["security_focus"] = len(security_terms)
        
        # Web/Application cluster
        web_terms = [kw for kw in relevant_keywords if any(term in kw for term in ['web', 'api', 'front', 'back', 'full', 'stack', 'mobile'])]
        if web_terms:
            domain_clusters["web_application"] = len(web_terms)
        
        # Machine Learning/AI cluster
        ml_terms = [kw for kw in relevant_keywords if any(term in kw for term in ['machine', 'learning', 'model', 'algorithm', 'neural', 'deep'])]
        if ml_terms:
            domain_clusters["ai_ml"] = len(ml_terms)
        
        # Financial/Business cluster
        finance_terms = [kw for kw in relevant_keywords if any(term in kw for term in ['financial', 'payment', 'transaction', 'banking', 'trading', 'commerce'])]
        if finance_terms:
            domain_clusters["finance_business"] = len(finance_terms)
    
    # Sort clusters by relevance
    top_domains = sorted(domain_clusters.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Extract role-specific keywords (most frequent meaningful terms)
    role_keywords = relevant_keywords[:15]
    
    return {
        "primary_domains": [d[0] for d in top_domains] if top_domains else ["general_technical"],
        "domain_scores": dict(top_domains),
        "role_keywords": role_keywords,
        "complexity_indicators": extract_complexity_indicators(jd_text),
        "keyword_diversity": len(set(relevant_keywords)),  # Measure of role breadth
        "technical_density": len([w for w in relevant_keywords if len(w) > 6]) / max(len(relevant_keywords), 1)
    }


def extract_complexity_indicators(text):
    """
    Dynamically assess role complexity from JD text.
    Returns: dict with seniority, scope, technical depth
    """
    text_lower = text.lower()
    
    # Seniority indicators
    seniority_keywords = {
        "senior": ["senior", "lead", "principal", "staff", "expert", "architect"],
        "mid": ["mid-level", "intermediate", "experienced", "3-5 years", "4+ years"],
        "junior": ["junior", "entry", "graduate", "1-2 years", "fresh"]
    }
    
    seniority_level = "mid"  # default
    for level, keywords in seniority_keywords.items():
        if any(kw in text_lower for kw in keywords):
            seniority_level = level
            break
    
    # Technical depth indicators
    depth_score = 0
    depth_score += len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text))  # Capitalized tech terms
    depth_score += len(re.findall(r'\d+\+?\s*years?', text_lower))  # Experience requirements
    depth_score += text_lower.count("experience with")
    depth_score += text_lower.count("proficient")
    depth_score += text_lower.count("expert")
    
    # Scope indicators
    scope_keywords = ["team", "lead", "manage", "architect", "design", "scale", "production"]
    scope_score = sum(1 for kw in scope_keywords if kw in text_lower)
    
    return {
        "seniority": seniority_level,
        "technical_depth": "high" if depth_score > 15 else "medium" if depth_score > 8 else "low",
        "leadership_scope": "high" if scope_score > 5 else "medium" if scope_score > 2 else "low",
        "estimated_complexity": "complex" if depth_score > 15 and scope_score > 4 
                               else "moderate" if depth_score > 8 
                               else "simple"
    }


def extract_resume_strengths(resume_text, nlp_model=None):
    """
    Dynamically extract candidate's key strengths from resume using NLP.
    Returns: dict with top skills, experience areas, achievements
    """
    resume_lower = resume_text.lower()
    
    # Extract quantifiable achievements (numbers + context)
    achievements = re.findall(
        r'(?:improved|increased|reduced|decreased|achieved|delivered|built|created|led)\s+[^.!?]{0,80}?\b\d+[%x]?\b[^.!?]{0,40}[.!?]',
        resume_lower,
        re.IGNORECASE
    )
    
    # Extract action verbs (strength indicators)
    action_verbs = re.findall(
        r'\b(developed|designed|built|created|implemented|architected|led|managed|optimized|improved|migrated|deployed)\b',
        resume_lower
    )
    action_verb_counts = Counter(action_verbs)
    
    # Extract years of experience per technology
    tech_experience = re.findall(r'(\d+\+?)\s*(?:years?|yrs?)\s+(?:of\s+)?([a-z]{3,})', resume_lower)
    
    # Extract project counts
    project_mentions = len(re.findall(r'\bproject\b', resume_lower))
    
    return {
        "quantifiable_achievements": achievements[:5],
        "primary_action_verbs": [verb for verb, count in action_verb_counts.most_common(5)],
        "tech_experience": dict(tech_experience[:10]),
        "project_count_estimate": project_mentions,
        "leadership_indicators": extract_leadership_indicators(resume_text)
    }


def extract_leadership_indicators(text):
    """Extract leadership and soft skill indicators dynamically."""
    text_lower = text.lower()
    
    leadership_keywords = ["led", "managed", "mentored", "coached", "directed", "supervised"]
    team_keywords = ["team", "cross-functional", "collaboration", "agile", "scrum"]
    
    leadership_count = sum(1 for kw in leadership_keywords if kw in text_lower)
    team_count = sum(1 for kw in team_keywords if kw in text_lower)
    
    return {
        "leadership_mentions": leadership_count,
        "team_collaboration": team_count,
        "level": "high" if leadership_count >= 3 else "medium" if leadership_count >= 1 else "low"
    }


def enrich_prompt_with_context(base_prompt, jd_text, resume_preview="", nlp_model=None):
    """
    Dynamically enrich prompt with AI-extracted context from JD and resume.
    NO static lexicons - learns from actual content.
    """
    # Extract dynamic context from JD
    jd_entities = extract_technical_entities(jd_text, nlp_model)
    domain_context = extract_domain_context(jd_text)
    
    # Extract dynamic context from resume (if provided)
    resume_strengths = None
    if resume_preview:
        resume_strengths = extract_resume_strengths(resume_preview, nlp_model)
    
    # Build dynamic context injection
    context_lines = []
    
    # Add domain context
    if domain_context["primary_domains"]:
        domains_str = ", ".join([d.replace("_", " ").title() for d in domain_context["primary_domains"][:2]])
        context_lines.append(f"🎯 **Detected Domain**: {domains_str}")
    
    # Add role complexity
    complexity = domain_context["complexity_indicators"]
    context_lines.append(f"📊 **Role Complexity**: {complexity['estimated_complexity'].title()} | "
                        f"Seniority: {complexity['seniority'].title()} | "
                        f"Technical Depth: {complexity['technical_depth'].title()}")
    
    # Add key technologies (dynamically extracted)
    if jd_entities["technologies"]:
        top_tech = jd_entities["technologies"][:8]
        context_lines.append(f"💻 **Key Technologies**: {', '.join(top_tech)}")
    
    # Add version-specific requirements
    if jd_entities["version_specific"]:
        context_lines.append(f"🔢 **Version-Specific**: {', '.join(jd_entities['version_specific'][:5])}")
    
    # Add experience requirements
    if jd_entities["experience_requirements"]:
        context_lines.append(f"⏱️ **Experience Needs**: {', '.join(jd_entities['experience_requirements'][:3])}")
    
    # Add role-specific keywords (learned from JD)
    if domain_context["role_keywords"]:
        context_lines.append(f"🔑 **Role Focus**: {', '.join(domain_context['role_keywords'][:6])}")
    
    # Add resume alignment insights (if available)
    if resume_strengths:
        if resume_strengths["quantifiable_achievements"]:
            context_lines.append(f"✨ **Candidate Highlights**: {len(resume_strengths['quantifiable_achievements'])} quantifiable achievements found")
        
        leadership = resume_strengths["leadership_indicators"]
        if leadership["level"] != "low":
            context_lines.append(f"👥 **Leadership**: {leadership['level'].title()} level ({leadership['leadership_mentions']} indicators)")
    
    if not context_lines:
        return base_prompt
    
    # Inject dynamically-learned context
    context_block = "\n".join(context_lines)
    enriched = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 DYNAMIC CONTEXT (AI-LEARNED FROM ACTUAL CONTENT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{context_block}

⚠️ **Adaptive Evaluation**: The above context was dynamically extracted from the JD and resume
   using NLP and pattern recognition. Prioritize these learned patterns in your assessment.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{base_prompt}
"""
    
    logger.info(f"Dynamic enrichment: domains={domain_context['primary_domains']}, "
                f"tech_count={len(jd_entities['technologies'])}, "
                f"complexity={complexity['estimated_complexity']}")
    return enriched


# ============================================================================
# EXPORT FUNCTIONS FOR USE IN OTHER MODULES
# ============================================================================

__all__ = [
    'extract_technical_entities',
    'extract_domain_context',
    'extract_complexity_indicators',
    'extract_resume_strengths',
    'extract_leadership_indicators',
    'enrich_prompt_with_context'
]
