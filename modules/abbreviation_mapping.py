"""
Intelligent Abbreviation and Synonym Mapping for Resume Screening
Maps common technical abbreviations to their full forms and vice versa
"""
import re
from typing import Set, List, Dict

# Comprehensive abbreviation dictionary
ABBREVIATION_MAP = {
    # Computer Science Fundamentals
    "os": ["operating systems", "operating system"],
    "operating systems": ["os"],
    "operating system": ["os"],
    
    "dbms": ["database management systems", "database management system"],
    "database management systems": ["dbms"],
    "database management system": ["dbms"],
    
    "cn": ["computer networks", "computer networking"],
    "computer networks": ["cn"],
    "computer networking": ["cn"],
    
    "ds": ["data structures"],
    "data structures": ["ds"],
    
    "algo": ["algorithms"],
    "algorithms": ["algo"],
    
    "oops": ["object oriented programming", "oop"],
    "oop": ["object oriented programming", "oops"],
    "object oriented programming": ["oop", "oops"],
    
    # Programming Languages
    "js": ["javascript"],
    "javascript": ["js"],
    
    "ts": ["typescript"],
    "typescript": ["ts"],
    
    "py": ["python"],
    "python": ["py"],
    
    # Frameworks & Libraries
    "react.js": ["react", "reactjs"],
    "reactjs": ["react", "react.js"],
    "react": ["reactjs", "react.js"],
    
    "node.js": ["node", "nodejs"],
    "nodejs": ["node", "node.js"],
    "node": ["nodejs", "node.js"],
    
    "next.js": ["nextjs"],
    "nextjs": ["next.js"],
    
    "vue.js": ["vue", "vuejs"],
    "vuejs": ["vue", "vue.js"],
    "vue": ["vuejs", "vue.js"],
    
    # Databases
    "postgres": ["postgresql"],
    "postgresql": ["postgres"],
    
    "mongo": ["mongodb"],
    "mongodb": ["mongo"],
    
    "db": ["database"],
    "database": ["db"],
    
    "sql": ["structured query language"],
    "structured query language": ["sql"],
    
    "nosql": ["no-sql", "no sql"],
    
    # Cloud & DevOps
    "aws": ["amazon web services"],
    "amazon web services": ["aws"],
    
    "gcp": ["google cloud platform"],
    "google cloud platform": ["gcp"],
    
    "k8s": ["kubernetes"],
    "kubernetes": ["k8s"],
    
    "ci/cd": ["continuous integration continuous deployment", "ci cd", "cicd"],
    "cicd": ["ci/cd", "ci cd"],
    
    # Machine Learning & AI
    "ml": ["machine learning"],
    "machine learning": ["ml"],
    
    "ai": ["artificial intelligence"],
    "artificial intelligence": ["ai"],
    
    "dl": ["deep learning"],
    "deep learning": ["dl"],
    
    "nlp": ["natural language processing"],
    "natural language processing": ["nlp"],
    
    "cv": ["computer vision"],
    "computer vision": ["cv"],
    
    # API & Architecture
    "rest": ["restful", "rest api", "restful api"],
    "restful": ["rest", "rest api"],
    "rest api": ["rest", "restful"],
    
    "api": ["application programming interface"],
    "application programming interface": ["api"],
    
    # Testing
    "tdd": ["test driven development"],
    "test driven development": ["tdd"],
    
    "bdd": ["behavior driven development"],
    "behavior driven development": ["bdd"],
    
    # Version Control
    "vcs": ["version control system"],
    "version control system": ["vcs"],
    
    # Mobile
    "ios": ["iphone os"],
    "iphone os": ["ios"],
    
    # Web Technologies
    "html": ["hypertext markup language"],
    "hypertext markup language": ["html"],
    
    "css": ["cascading style sheets"],
    "cascading style sheets": ["css"],
    
    "http": ["hypertext transfer protocol"],
    "hypertext transfer protocol": ["http"],
    
    "https": ["hypertext transfer protocol secure"],
    "hypertext transfer protocol secure": ["https"],
}

# Skill synonyms and variations
SKILL_SYNONYMS = {
    "react": ["react.js", "reactjs", "react 18", "react 17", "react 16"],
    "node": ["node.js", "nodejs"],
    "python": ["python 3", "python 3.x", "python 2", "py"],
    "java": ["java 8", "java 11", "java 17", "jdk"],
    "docker": ["docker container", "docker compose"],
    "kubernetes": ["k8s", "k8s cluster"],
    "postgresql": ["postgres", "postgres db"],
    "mongodb": ["mongo", "mongo db"],
    "aws": ["amazon web services", "aws cloud"],
    "azure": ["microsoft azure", "azure cloud"],
    "spring": ["spring boot", "spring framework", "spring mvc"],
    "django": ["django rest", "django rest framework"],
    "flask": ["flask api"],
}


def normalize_term(term: str) -> str:
    """Normalize a term for comparison: lowercase, remove special chars, trim."""
    if not term:
        return ""
    term = term.lower().strip()
    # Remove version numbers for base comparison
    term = re.sub(r'\s*\d+(\.\d+)*\s*$', '', term)
    term = re.sub(r'[^\w\s+#.-]', ' ', term)
    term = ' '.join(term.split())
    return term


def get_all_forms(term: str) -> Set[str]:
    """
    Get all equivalent forms of a term (abbreviations and full forms).
    Returns a set including the original term and all its mappings.
    """
    normalized = normalize_term(term)
    forms = {normalized, term.lower()}
    
    # Check abbreviation map
    if normalized in ABBREVIATION_MAP:
        forms.update([f.lower() for f in ABBREVIATION_MAP[normalized]])
    
    # Check skill synonyms
    for base_skill, variations in SKILL_SYNONYMS.items():
        if normalized == base_skill or normalized in [v.lower() for v in variations]:
            forms.add(base_skill)
            forms.update([v.lower() for v in variations])
    
    return forms


def terms_match(term1: str, term2: str) -> bool:
    """
    Check if two terms match, considering abbreviations and synonyms.
    Returns True if terms are equivalent.
    """
    if not term1 or not term2:
        return False
    
    # Direct match
    if normalize_term(term1) == normalize_term(term2):
        return True
    
    # Check if they share any equivalent forms
    forms1 = get_all_forms(term1)
    forms2 = get_all_forms(term2)
    
    return bool(forms1 & forms2)


def deduplicate_requirements(requirements: List[str]) -> List[str]:
    """
    Remove duplicate requirements considering abbreviations and synonyms.
    Keep the most specific/complete form.
    """
    if not requirements:
        return []
    
    unique = []
    seen_forms = set()
    
    for req in requirements:
        req_normalized = normalize_term(req)
        
        # Get all equivalent forms
        req_forms = get_all_forms(req)
        
        # Check if any form has been seen
        if any(form in seen_forms for form in req_forms):
            continue
        
        # Add to unique list
        unique.append(req)
        seen_forms.update(req_forms)
    
    return unique


def extract_skills_from_text(text: str, filter_generic: bool = True) -> List[str]:
    """
    Extract skill-like terms from text.
    Filters out generic words if filter_generic=True.
    """
    # Generic words to exclude
    GENERIC_WORDS = {
        "experience", "years", "knowledge", "understanding", "ability", "skills",
        "work", "working", "projects", "project", "development", "developer",
        "engineer", "engineering", "good", "strong", "excellent", "basic",
        "advanced", "proficient", "expert", "familiar", "familiarity",
        "required", "preferred", "must", "should", "nice", "have", "has",
        "using", "used", "use", "apply", "application", "implement", "implementation",
        "design", "develop", "create", "build", "maintain", "support",
        "team", "teams", "individual", "company", "organization",
        "role", "position", "job", "responsibilities", "duties",
        "bachelor", "master", "degree", "education", "certification",
        "plus", "bonus", "additional", "extra", "other", "various",
        "including", "such", "related", "relevant", "similar",
        "minimum", "maximum", "at least", "up to", "more than",
        "with", "without", "and", "or", "but", "the", "a", "an",
        "in", "on", "at", "for", "to", "from", "by", "of"
    }
    
    # Extract words that look like technical skills
    # Pattern: Words with 2+ chars, can include +, #, ., numbers
    words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#.]{1,}\b', text)
    
    skills = []
    for word in words:
        word_lower = word.lower()
        
        # Skip short words
        if len(word_lower) < 2:
            continue
        
        # Skip generic words if filtering enabled
        if filter_generic and word_lower in GENERIC_WORDS:
            continue
        
        # Skip pure numbers
        if word_lower.isdigit():
            continue
        
        skills.append(word_lower)
    
    # Deduplicate
    return list(dict.fromkeys(skills))


def match_requirements_to_resume(
    jd_requirements: List[str],
    resume_skills: List[str],
    resume_text: str = ""
) -> Dict[str, List[str]]:
    """
    Match job requirements against resume skills with intelligent mapping.
    
    Returns:
        {
            "matched": [list of matched skills],
            "missing": [list of missing requirements],
            "additional": [list of extra resume skills not in JD]
        }
    """
    matched = []
    missing = []
    
    # Normalize inputs
    jd_reqs_normalized = [normalize_term(r) for r in jd_requirements]
    resume_skills_normalized = [normalize_term(s) for s in resume_skills]
    
    # Build resume text for fuzzy matching
    resume_text_normalized = resume_text.lower() if resume_text else " ".join(resume_skills_normalized)
    
    # Match each JD requirement
    for jd_req in jd_requirements:
        jd_req_norm = normalize_term(jd_req)
        is_matched = False
        
        # Check direct match or abbreviation match
        for resume_skill in resume_skills:
            if terms_match(jd_req, resume_skill):
                matched.append(jd_req)
                is_matched = True
                break
        
        # If not matched, check in full resume text
        if not is_matched and resume_text:
            jd_forms = get_all_forms(jd_req)
            for form in jd_forms:
                if form in resume_text_normalized:
                    matched.append(jd_req)
                    is_matched = True
                    break
        
        if not is_matched:
            missing.append(jd_req)
    
    # Find additional skills in resume not in JD
    additional = []
    for resume_skill in resume_skills:
        is_in_jd = False
        for jd_req in jd_requirements:
            if terms_match(resume_skill, jd_req):
                is_in_jd = True
                break
        if not is_in_jd:
            additional.append(resume_skill)
    
    return {
        "matched": deduplicate_requirements(matched),
        "missing": deduplicate_requirements(missing),
        "additional": deduplicate_requirements(additional)
    }
