"""
LLM Operations and Prompt Engineering
Enterprise-grade with retry logic, input sanitization, and error handling
"""
import json
import time
import re
from modules.text_processing import normalize_text
from modules.prompt_enrichment import enrich_prompt_with_context
import logging

logger = logging.getLogger(__name__)

# ENTERPRISE CONFIGURATION
MAX_LLM_RETRIES = 3
LLM_RETRY_DELAY = 2  # seconds
MAX_PROMPT_LENGTH = 50000  # characters
MAX_RESUME_EXCERPT = 6000  # characters (increased for better context)

def sanitize_prompt_input(text, max_length=MAX_PROMPT_LENGTH):
    """
    Sanitize input text to prevent prompt injection and excessive token usage.
    Returns cleaned text.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potential prompt injection patterns
    text = text.replace("```", "")  # No code blocks in input
    text = text.replace("IGNORE PREVIOUS INSTRUCTIONS", "")
    text = text.replace("DISREGARD", "")
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate to max length
    if len(text) > max_length:
        logger.warning(f"Input truncated from {len(text)} to {max_length} chars")
        text = text[:max_length]
    
    return text


def llm_json(model, prompt, variables=None, max_retries=MAX_LLM_RETRIES):
    """
    Call LLM with JSON response mode and enterprise-grade error handling.
    Includes retry logic, timeout protection, and response validation.
    
    Args:
        model: The LLM model instance
        prompt: Either a string prompt or a callable that takes **variables
        variables: Dict of variables to pass to prompt function if prompt is callable
        max_retries: Maximum retry attempts
    """
    if not model:
        logger.error("llm_json called with no model")
        return {}
    
    # If prompt is callable, call it with variables
    if callable(prompt):
        if variables:
            prompt = prompt(**variables)
        else:
            prompt = prompt()
    elif variables:
        # If prompt is string and variables provided, format it
        try:
            prompt = prompt.format(**variables)
        except (KeyError, ValueError) as e:
            logger.warning(f"Failed to format prompt with variables: {e}")
    
    # Sanitize prompt
    prompt = sanitize_prompt_input(prompt)
    
    if not prompt:
        logger.error("Empty prompt after sanitization")
        return {}
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Try JSON mode first (preferred)
            try:
                resp = model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.15,
                        "top_p": 0.9
                    }
                )
                text = resp.text or ""
            except TypeError:
                # Fallback for models that don't support mime_type
                resp = model.generate_content(prompt)
                text = resp.text or ""
            
            # Validate response
            if not text or len(text.strip()) == 0:
                raise ValueError("Empty LLM response")
            
            # Extract JSON from response
            s = text.strip()
            
            # Find JSON object
            if not s.startswith("{"):
                m = re.search(r"\{.*\}", s, re.DOTALL)
                s = m.group(0) if m else s
            
            # Clean markdown artifacts
            s = s.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            try:
                result = json.loads(s)
                
                # Validate result is dict
                if not isinstance(result, dict):
                    raise ValueError(f"Expected dict, got {type(result)}")
                
                logger.debug(f"LLM JSON call successful (attempt {attempt + 1})")
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error (attempt {attempt + 1}): {str(e)[:100]}")
                logger.debug(f"Problematic JSON: {s[:500]}")
                last_error = e
                
                # Try to salvage partial JSON
                if "{" in s and "}" in s:
                    try:
                        # Extract first complete JSON object
                        start = s.index("{")
                        depth = 0
                        for i, char in enumerate(s[start:], start=start):
                            if char == "{":
                                depth += 1
                            elif char == "}":
                                depth -= 1
                                if depth == 0:
                                    partial = s[start:i+1]
                                    result = json.loads(partial)
                                    logger.warning("Recovered partial JSON")
                                    return result
                    except:
                        pass
                
                # Retry on parse error
                if attempt < max_retries - 1:
                    time.sleep(LLM_RETRY_DELAY)
                    continue
                else:
                    return {}
            
        except Exception as e:
            last_error = e
            logger.warning(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {str(e)[:150]}")
            
            # Exponential backoff for retries
            if attempt < max_retries - 1:
                delay = LLM_RETRY_DELAY * (2 ** attempt)
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
                continue
    
    # All retries exhausted
    logger.error(f"LLM call failed after {max_retries} attempts. Last error: {last_error}")
    return {}


def llm_verify_requirements_clean(model, requirements_payload, resume_text):
    """
    Clean LLM verification: Is each requirement present in the resume? Yes/No + Confidence + Evidence.
    Uses intelligent abbreviation matching and context-aware analysis.
    """
    if not requirements_payload or not model:
        return {}

    results = {}
    batch_size = 10  # Process 10 requirements at a time
    
    # Prepare resume excerpt (limit to avoid token overflow)
    resume_excerpt = resume_text[:4500] if len(resume_text) > 4500 else resume_text
    
    for i in range(0, len(requirements_payload), batch_size):
        batch = requirements_payload[i:i + batch_size]
        
        # Format batch for LLM
        formatted_reqs = []
        for item in batch:
            req_name = item.get("requirement", "")
            evidence_snippets = []
            for ev in (item.get("resume_evidence") or [])[:3]:
                evidence_snippets.append({
                    "text": ev.get("text", "")[:250],
                    "similarity": ev.get("similarity", 0.0),
                    "keyword_overlap": ev.get("keyword_overlap", 0.0)
                })
            
            formatted_reqs.append({
                "requirement": req_name,
                "type": item.get("req_type", ""),
                "evidence": evidence_snippets,
                "max_similarity": item.get("max_similarity", 0.0)
            })
        
        prompt = f"""You are an expert technical recruiter with deep knowledge of technology abbreviations and synonyms. Analyze each requirement INDEPENDENTLY with UNIQUE, SPECIFIC assessments.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 REQUIREMENTS TO VERIFY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{json.dumps(formatted_reqs, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 CANDIDATE'S RESUME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{resume_excerpt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 INTELLIGENT MATCHING RULES (CRITICAL!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ABBREVIATION AWARENESS:**
You MUST recognize common technical abbreviations as equivalent to their full forms:

✅ MATCH these automatically:
- "OS" ↔ "Operating Systems" ↔ "Operating System"
- "DBMS" ↔ "Database Management Systems" ↔ "Database Management System"  
- "CN" ↔ "Computer Networks" ↔ "Computer Networking"
- "OOP" ↔ "Object Oriented Programming" ↔ "OOPS"
- "JS" ↔ "JavaScript"
- "TS" ↔ "TypeScript"
- "Node.js" ↔ "Node" ↔ "NodeJS"
- "React.js" ↔ "React" ↔ "ReactJS"
- "Postgres" ↔ "PostgreSQL"
- "Mongo" ↔ "MongoDB"
- "K8s" ↔ "Kubernetes"
- "AWS" ↔ "Amazon Web Services"
- "GCP" ↔ "Google Cloud Platform"

**CONTEXT-AWARE MATCHING:**
- "Python" in requirement matches "Python 3", "Python 3.x", "Py" in resume
- "React" matches "React 18", "React.js", "ReactJS"
- "Database" concept satisfied by ANY specific DB (MySQL, PostgreSQL, etc.)
- "Cloud" satisfied by AWS, Azure, GCP mentions
- "Backend" satisfied by Django, Flask, Spring Boot, Node.js, etc.

**VERSION FLEXIBILITY:**
- Don't penalize for version differences unless explicitly required
- "Java" requirement satisfied by "Java 8", "Java 11", "Java 17"
- "Python" satisfied by any Python version unless JD specifies

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ASSESSMENT CRITERIA (BE SMART, NOT RIGID!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For EACH requirement, provide:

1. **present** (boolean): Is the skill/technology actually used?
   
   ✅ TRUE if ANY of these:
   - Exact match: "Python" requirement, resume has "Python"
   - Abbreviation match: "OS" requirement, resume has "Operating Systems"
   - Synonym match: "React" requirement, resume has "React.js" or "ReactJS"
   - Version match: "Java" requirement, resume has "Java 11"
   - Context match: "Database" requirement, resume shows MySQL/PostgreSQL usage
   - Mentioned in projects with proof of usage
   - In skills list AND evidence shows actual project usage
   
   ❌ FALSE if:
   - Completely different technology (MySQL ≠ MongoDB unless both mentioned)
   - No mention at all (including abbreviations/synonyms)
   - Only aspirational ("want to learn Python" ≠ has Python)

2. **confidence** (0.0 to 1.0): Certainty level - BE REASONABLE!
   
   HIGH CONFIDENCE (0.8-1.0):
   - Multiple projects with detailed usage + quantifiable results
   - Explicit mention with abbreviation/synonym match
   - Clear evidence with high semantic similarity (>0.7)
   
   MODERATE CONFIDENCE (0.6-0.7):
   - One solid project with good description
   - In skills list + some project context
   - Abbreviation match with supporting context
   
   LOW-MODERATE CONFIDENCE (0.4-0.5):
   - Skills list only + minimal evidence
   - Indirect evidence (e.g., "databases" for "PostgreSQL")
   - Low semantic similarity but keyword match
   
   LOW CONFIDENCE (0.2-0.3):
   - Weak/tangential mention
   - Uncertain abbreviation interpretation
   
   VERY LOW (0.0-0.1):
   - Not found at all (no abbreviations, no synonyms, no evidence)

3. **rationale** (15-30 words): SPECIFIC, UNIQUE explanation per requirement
   
   ⚠️ MANDATORY UNIQUENESS RULES:
   - MUST mention WHERE found: project name, section, context
   - If abbreviation match, STATE IT: "Resume has 'Operating Systems', matches 'OS' requirement"
   - If synonym match, STATE IT: "Resume shows 'React.js', equivalent to 'React'"
   - If missing, explain WHY or what's used INSTEAD
   - NO generic phrases ("demonstrated", "mentioned", "experience with")
   
   ✅ GOOD EXAMPLES:
   - "Resume has 'Operating Systems' in education, matches 'OS' requirement via abbreviation"
   - "Python 3.x used in E-commerce Platform project with Django and data pipelines"
   - "React.js (synonym of React) used in Healthcare Dashboard with hooks and Redux"
   - "No Docker found; deployment uses traditional VMs per infrastructure section"
   - "PostgreSQL mentioned as 'Postgres' in Database Admin project, direct match"
   
   ❌ BAD EXAMPLES (NEVER USE):
   - "Clearly demonstrated in projects" (too generic, no details)
   - "Mentioned in resume" (where? how?)
   - "Has experience with technology" (not specific)
   - "Good understanding shown" (vague)

4. **evidence** (20-50 words): Direct quote with PROJECT/SECTION context
   - Quote the SPECIFIC LINE proving usage
   - Include PROJECT NAME or COMPANY if available
   - If abbreviation/synonym match, include both forms
   - If not present, leave empty ("")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON (no markdown, no ```json):

{{
  "requirement_name": {{
    "present": true/false,
    "confidence": 0.0-1.0,
    "rationale": "Specific 15-30 word explanation with context (MUST BE UNIQUE!)",
    "evidence": "Quoted text with source context (or empty if absent)"
  }}
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ ANTI-REPETITION ENFORCEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Each rationale MUST be UNIQUE - NO copy-paste
2. MUST cite specific PROJECT/SECTION/CONTEXT
3. Abbreviation matches MUST state both forms explicitly
4. Synonym matches MUST explain equivalence
5. If absent, explain what alternative is present (if any)

**VERIFICATION STEP:** Before returning, ensure NO TWO rationales are similar!

BEGIN INTELLIGENT ANALYSIS:
"""

        try:
            raw = llm_json(model, prompt)
            if not isinstance(raw, dict):
                logger.warning(f"LLM returned non-dict: {type(raw)}")
                continue
            
            # Extract results for each requirement in batch
            for item in batch:
                req_name = item.get("requirement", "")
                if not req_name:
                    continue
                
                # Try exact match first
                verdict = raw.get(req_name)
                
                # Try normalized match if exact fails
                if verdict is None:
                    req_norm = normalize_text(req_name)
                    for key, value in raw.items():
                        if normalize_text(key) == req_norm:
                            verdict = value
                            break
                
                if isinstance(verdict, dict):
                    # Extract and validate fields
                    present = bool(verdict.get("present", False))
                    
                    confidence = verdict.get("confidence", 0.0)
                    try:
                        confidence = float(confidence)
                    except:
                        confidence = 0.0
                    confidence = max(0.0, min(1.0, confidence))
                    
                    rationale = str(verdict.get("rationale", "")).strip()
                    evidence = str(verdict.get("evidence", "")).strip()
                    
                    # Clean text: remove repetition, limit length
                    def clean_llm_text(text, max_words=30):
                        if not text:
                            return ""
                        # Remove markdown and code artifacts
                        text = re.sub(r'```\w*', '', text)
                        text = re.sub(r'[*_~`]', '', text)
                        # Remove repeated words (e.g., "Python Python Python")
                        text = re.sub(r'\b(\w+)(\s+\1\b){2,}', r'\1', text, flags=re.IGNORECASE)
                        # Remove repeated punctuation
                        text = re.sub(r'([.,!?])\1+', r'\1', text)
                        # Normalize whitespace
                        text = re.sub(r'\s+', ' ', text).strip()
                        # Truncate to word limit
                        words = text.split()
                        if len(words) > max_words:
                            text = ' '.join(words[:max_words])
                        return text
                    
                    rationale = clean_llm_text(rationale, max_words=30)
                    evidence = clean_llm_text(evidence, max_words=50)
                    
                    results[req_name] = {
                        "present": present,
                        "confidence": confidence,
                        "rationale": rationale,
                        "evidence": evidence
                    }
            
            logger.info(f"✅ LLM verified {len(results)} requirements in batch")
                    
        except Exception as e:
            logger.error(f"LLM verification batch failed: {e}")
            # Skip this batch on error, continue with next
            continue
    
    logger.info(f"✅ Total LLM verification complete: {len(results)} requirements processed")
    return results


def llm_verify_requirements(model, requirements_payload, resume_text, jd_text=""):
    """Legacy function - redirects to new clean implementation."""
    return llm_verify_requirements_clean(model, requirements_payload, resume_text)


def llm_extract_skills_comparison(model, jd_text, resume_text, jd_requirements=None):
    """
    Use LLM to intelligently extract and compare skills between JD and resume.
    This is more robust than keyword matching as LLM understands context and synonyms.
    
    Args:
        model: LLM model instance
        jd_text: Job description text
        resume_text: Resume text
        jd_requirements: Optional list of structured requirements from atomicize
    
    Returns:
        {
            "jd_skills": [list of skills from JD],
            "resume_skills": [list of skills from resume],
            "matched_skills": [skills present in both],
            "missing_skills": [JD skills missing from resume],
            "additional_skills": [resume skills not in JD],
            "match_rate": percentage,
            "analysis": detailed analysis text
        }
    """
    if not model:
        logger.warning("LLM not available for skill extraction")
        return {
            "jd_skills": [],
            "resume_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "additional_skills": [],
            "match_rate": 0.0,
            "analysis": "LLM not available"
        }
    
    # Prepare JD requirements list if provided
    jd_req_list = ""
    if jd_requirements and isinstance(jd_requirements, list):
        jd_req_list = "\n".join([f"- {req}" for req in jd_requirements[:30]])
    
    prompt = f"""You are an expert technical recruiter and skill matcher. Perform a comprehensive skill comparison between a job description and a candidate's resume.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 JOB DESCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{jd_text[:3000]}

{f'''
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 STRUCTURED REQUIREMENTS (from analysis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{jd_req_list}
''' if jd_req_list else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 CANDIDATE'S RESUME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{resume_text[:4000]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Extract and compare technical skills with INTELLIGENT MATCHING:

1. **JD Skills Extraction** (20-30 items):
   - Programming languages (Python, Java, JavaScript, etc.)
   - Frameworks & libraries (React, Django, Spring Boot, etc.)
   - Databases (MySQL, PostgreSQL, MongoDB, etc.)
   - Cloud platforms (AWS, Azure, GCP, specific services)
   - Tools & technologies (Docker, Kubernetes, Git, etc.)
   - CS Fundamentals (Data Structures, Algorithms, DBMS, OS, etc.)
   - Domain skills (Machine Learning, DevOps, etc.)

2. **Resume Skills Extraction** (20-40 items):
   - Extract ALL technical skills mentioned
   - Include skills from: Experience, Projects, Skills section, Education
   - Include both explicit and implicit skills (e.g., "built REST API" → has REST API skill)

3. **Intelligent Matching** (CRITICAL):
   - **Abbreviations**: "OS" = "Operating Systems", "DBMS" = "Database Management Systems"
   - **Synonyms**: "Node.js" = "Node" = "NodeJS", "React" = "React.js" = "ReactJS"
   - **Versions**: "Python 3" matches "Python", "Java 11" matches "Java"
   - **Implied skills**: If resume shows "Django", they have "Python"
   - **Framework→Language**: React → JavaScript, Spring Boot → Java
   - **Specifics→General**: PostgreSQL satisfies "SQL database", AWS Lambda satisfies "Serverless"
   
4. **Classification**:
   - **matched_skills**: JD skills PRESENT in resume (with intelligent matching)
   - **missing_skills**: JD skills NOT found in resume (critical gaps)
   - **additional_skills**: Resume skills NOT requested in JD (bonus capabilities)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL MATCHING RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**MATCH these as equivalent:**
- JD: "Operating Systems" + Resume: "OS" = ✅ MATCHED
- JD: "DBMS" + Resume: "Database Management Systems" = ✅ MATCHED
- JD: "React" + Resume: "React.js" or "ReactJS" = ✅ MATCHED
- JD: "Node.js" + Resume: "Node" or "NodeJS" = ✅ MATCHED
- JD: "Python" + Resume: "Python 3" or "Python 3.x" = ✅ MATCHED
- JD: "JavaScript" + Resume: "JS" = ✅ MATCHED
- JD: "Kubernetes" + Resume: "K8s" = ✅ MATCHED
- JD: "Database" + Resume: "MySQL" or "PostgreSQL" = ✅ MATCHED (specific satisfies general)
- JD: "Cloud" + Resume: "AWS" or "Azure" = ✅ MATCHED (specific satisfies general)

**DO NOT match these:**
- JD: "MySQL" + Resume: "PostgreSQL" = ❌ DIFFERENT (both are databases but not equivalent)
- JD: "React" + Resume: "Angular" = ❌ DIFFERENT (both are frontend but not equivalent)
- JD: "5 years Python" + Resume: "2 years Python" = ❌ EXPERIENCE MISMATCH

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT (Return ONLY valid JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{
  "jd_skills": [
    "Python", "Django", "PostgreSQL", "Docker", "AWS", "React", 
    "Operating Systems", "DBMS", "REST API", "Git"
  ],
  "resume_skills": [
    "Python 3.x", "Django REST Framework", "PostgreSQL", "MySQL",
    "Docker", "Kubernetes", "React.js", "Node.js", "OS", 
    "Database Management Systems", "JavaScript", "MongoDB"
  ],
  "matched_skills": [
    "Python",
    "Django", 
    "PostgreSQL",
    "Docker",
    "React",
    "Operating Systems",
    "DBMS"
  ],
  "missing_skills": [
    "AWS",
    "REST API",
    "Git"
  ],
  "additional_skills": [
    "MySQL",
    "Kubernetes",
    "Node.js",
    "JavaScript",
    "MongoDB"
  ],
  "match_rate": 70.0,
  "analysis": "Candidate has strong match with 7 out of 10 JD requirements (70%). Core skills like Python, Django, and PostgreSQL are present. Missing cloud experience (AWS) and version control (Git). Has valuable additional skills in Kubernetes and Node.js that weren't required but could be beneficial."
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ IMPORTANT NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Use YOUR KNOWLEDGE of technical abbreviations and synonyms
2. Be GENEROUS with matching - recognize equivalents intelligently  
3. Extract SPECIFIC technical skills, not generic terms like "programming" or "software"
4. Match rate = (matched_skills count / jd_skills count) * 100
5. Return ONLY valid JSON (no markdown, no explanations outside JSON)
6. Limit each list to most important/relevant items (quality > quantity)

BEGIN SKILL COMPARISON:
"""

    try:
        result = llm_json(model, prompt)
        
        if not isinstance(result, dict):
            logger.error(f"Invalid result type from LLM skill comparison: {type(result)}")
            return {
                "jd_skills": [],
                "resume_skills": [],
                "matched_skills": [],
                "missing_skills": [],
                "additional_skills": [],
                "match_rate": 0.0,
                "analysis": "Error: Invalid response format"
            }
        
        # Validate and clean results
        jd_skills = result.get("jd_skills", [])
        resume_skills = result.get("resume_skills", [])
        matched_skills = result.get("matched_skills", [])
        missing_skills = result.get("missing_skills", [])
        additional_skills = result.get("additional_skills", [])
        
        # Ensure all are lists
        if not isinstance(jd_skills, list):
            jd_skills = []
        if not isinstance(resume_skills, list):
            resume_skills = []
        if not isinstance(matched_skills, list):
            matched_skills = []
        if not isinstance(missing_skills, list):
            missing_skills = []
        if not isinstance(additional_skills, list):
            additional_skills = []
        
        # Calculate match rate
        match_rate = result.get("match_rate", 0.0)
        if not isinstance(match_rate, (int, float)):
            match_rate = (len(matched_skills) / max(len(jd_skills), 1)) * 100
        
        analysis = result.get("analysis", "")
        if not isinstance(analysis, str):
            analysis = ""
        
        logger.info(f"✅ LLM skill comparison: {len(matched_skills)} matched, {len(missing_skills)} missing, {len(additional_skills)} additional (match rate: {match_rate:.1f}%)")
        
        return {
            "jd_skills": jd_skills[:30],
            "resume_skills": resume_skills[:50],
            "matched_skills": matched_skills[:20],
            "missing_skills": missing_skills[:20],
            "additional_skills": additional_skills[:20],
            "match_rate": round(float(match_rate), 1),
            "analysis": analysis[:500]
        }
        
    except Exception as e:
        logger.error(f"LLM skill comparison failed: {e}")
        return {
            "jd_skills": [],
            "resume_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "additional_skills": [],
            "match_rate": 0.0,
            "analysis": f"Error: {str(e)[:200]}"
        }


def jd_plan_prompt(jd, preview):
    base_prompt = f"""
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
    
    # Apply dynamic enrichment
    try:
        enriched = enrich_prompt_with_context(base_prompt, jd, preview)
        logger.info("JD plan prompt enriched with dynamic context")
        return enriched
    except Exception as e:
        logger.warning(f"Dynamic enrichment failed for jd_plan_prompt: {e}, using base prompt")
        return base_prompt


def resume_profile_prompt(full_resume_text):
    base_prompt = f"""
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
    
    # Apply dynamic enrichment with resume context
    try:
        # For resume profile, we enrich with the resume itself to extract patterns
        enriched = enrich_prompt_with_context(base_prompt, full_resume_text[:3000], full_resume_text[:3000])
        logger.info("Resume profile prompt enriched with dynamic context")
        return enriched
    except Exception as e:
        logger.warning(f"Dynamic enrichment failed for resume_profile_prompt: {e}, using base prompt")
        return base_prompt


def atomicize_requirements_prompt(jd, resume_preview):
    return f"""You are an expert technical recruiter. Extract UNIQUE, SPECIFIC requirements from the job description. Avoid redundancy and be precise.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 EXTRACTION CATEGORIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Extract into 4 categories with MUST vs NICE classification:

1. **hard_skills**: Specific technologies, tools, frameworks (NO generic concepts)
   ✅ Extract: Python, React, PostgreSQL, Docker, AWS, Kubernetes, Django
   ❌ Skip: "programming languages", "databases", "cloud platforms" (too generic)

2. **fundamentals**: Core CS/IT concepts (ONLY if explicitly mentioned)
   ✅ Extract: DBMS, Operating Systems, Data Structures, Algorithms, OOP
   ❌ Skip: Generic phrases like "good foundation", "strong basics"

3. **experience**: Specific experience requirements (years + context)
   ✅ Extract: "5+ years Python", "3 years backend development"
   ❌ Skip: Vague like "experienced developer", "senior level" (no numbers)

4. **qualifications**: Degrees, certifications (specific only)
   ✅ Extract: "Bachelor's in Computer Science", "AWS Certified Solutions Architect"
   ❌ Skip: "Good education", "relevant degree" (too vague)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 CRITICAL ANTI-REDUNDANCY RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**RULE 1: One Form Per Concept**
- If JD says "Operating Systems" → Extract ONLY "Operating Systems"
- If JD says "OS" → Extract ONLY "OS"
- If JD says "DBMS" → Extract ONLY "DBMS" (not "Database Management Systems")
- NEVER extract both abbreviation AND full form for same concept

**RULE 2: No Synonym Duplicates**
- "Node" and "Node.js" → Pick ONE (whichever appears in JD)
- "React" and "React.js" → Pick ONE
- "Mongo" and "MongoDB" → Pick ONE
- Our system handles synonyms automatically

**RULE 3: No Version/Variant Redundancy**
- "Python" is enough, don't also add "Python 3", "Python 3.x"
- "React" covers "React 18", "React 17", etc.
- Extract base technology ONCE

**RULE 4: No Compound Splitting Unless Explicit**
- "Django/Flask" in JD → Extract as "Django" OR "Flask" (pick primary, or both if both explicitly mentioned separately elsewhere)
- "Frontend (React/Vue)" → Extract technologies mentioned, not the grouping phrase
- Don't invent items by splitting every "/" - use context

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PRIORITY CLASSIFICATION (MUST vs NICE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**MUST-HAVE indicators:** "required", "must", "essential", "mandatory", "minimum", "need"
**NICE-TO-HAVE indicators:** "preferred", "nice to have", "bonus", "plus", "desirable", "a plus"
**Default:** If unclear, classify core stack as MUST, others as NICE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 GOOD EXTRACTION EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Example 1:**
INPUT: "Required: 5+ years Python experience with Django or Flask. Strong PostgreSQL, Docker knowledge. Core IT fundamentals like DBMS, OS essential. Bachelor's in CS required. Preferred: AWS, Kubernetes, React."

OUTPUT:
{{
  "hard_skills": {{
    "must": ["Python", "Django", "PostgreSQL", "Docker"],
    "nice": ["AWS", "Kubernetes", "React"]
  }},
  "fundamentals": {{
    "must": ["DBMS", "OS"],
    "nice": []
  }},
  "experience": {{
    "must": ["5+ years Python experience"],
    "nice": []
  }},
  "qualifications": {{
    "must": ["Bachelor's in Computer Science"],
    "nice": []
  }}
}}

Note: 
- Only "DBMS", "OS" (as written in JD), NOT "Database Management Systems"
- "Django" extracted (primary in "Django or Flask"), not both unless both explicitly required
- "Flask" could be added to nice since it's an "or" option

**Example 2:**
INPUT: "Full Stack Developer needed. Must know: React, Node.js, MongoDB, REST APIs. Understanding of microservices architecture. AWS experience preferred. TypeScript, GraphQL are bonuses."

OUTPUT:
{{
  "hard_skills": {{
    "must": ["React", "Node.js", "MongoDB", "REST API", "Microservices"],
    "nice": ["AWS", "TypeScript", "GraphQL"]
  }},
  "fundamentals": {{
    "must": [],
    "nice": []
  }},
  "experience": {{
    "must": ["Full Stack development experience"],
    "nice": []
  }},
  "qualifications": {{
    "must": [],
    "nice": []
  }}
}}

Note:
- "Node.js" as written (not "Node" separately)
- "REST API" (not "REST" + "API" separately)
- "Microservices" is architecture concept, still a hard skill requirement

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 JOB DESCRIPTION TO ANALYZE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{jd[:6000]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ FINAL CHECKLIST BEFORE RETURNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ✓ No duplicate concepts (abbreviation + full form)
2. ✓ No synonym duplicates (React + React.js)
3. ✓ No version redundancy (Python + Python 3)
4. ✓ Only specific technologies (no "databases", "frameworks" generic terms)
5. ✓ Each item appears ONCE across all categories
6. ✓ Only items EXPLICITLY mentioned in JD
7. ✓ Correct must/nice classification

Return ONLY valid JSON, no markdown, no explanations:
"""


def analysis_prompt(jd, plan, profile, coverage_summary, cue_alignment, global_sem, cov_final):
    must_details = (coverage_summary.get("details") or {}).get("must", {})
    nice_details = (coverage_summary.get("details") or {}).get("nice", {})

    def _pick_atoms(source, threshold_low, threshold_high=None, limit=8):
        picked = []
        for atom, info in source.items():
            score = float(info.get("score", 0.0))
            if threshold_high is None:
                if score >= threshold_low:
                    picked.append(atom)
            else:
                if threshold_low <= score < threshold_high:
                    picked.append(atom)
        return picked[:limit]

    coverage_brief = {
        "must_coverage": round(coverage_summary.get("must", 0.0), 3),
        "nice_coverage": round(coverage_summary.get("nice", 1.0), 3),
        "overall": round(coverage_summary.get("overall", 0.0), 3),
        "must_found": _pick_atoms(must_details, 0.85),
        "must_partial": _pick_atoms(must_details, 0.50, 0.85),
        "must_missing": _pick_atoms(must_details, 0.0, 0.50),
        "nice_found": _pick_atoms(nice_details, 0.85),
        "nice_partial": _pick_atoms(nice_details, 0.50, 0.85),
        "nice_missing": _pick_atoms(nice_details, 0.0, 0.50)
    }

    cue_brief = {
        "average_similarity": round(cue_alignment.get("average_similarity", 0.0), 3),
        "strong_matches": (cue_alignment.get("strong_matches") or [])[:10],
        "weak_matches": (cue_alignment.get("weak_matches") or [])[:10],
        "sample_alignments": (cue_alignment.get("alignments") or [])[:6]
    }

    coverage_json = json.dumps(coverage_brief, indent=2)[:1200]
    cue_json = json.dumps(cue_brief, indent=2)[:1100]
    plan_json = json.dumps(plan, indent=2)[:800]
    profile_json = json.dumps(profile, indent=2)[:1200]

    return f"""You are an ELITE technical recruiter with 15+ years of experience. Conduct a rigorous, evidence-based assessment of this candidate against the job requirements.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 OUTPUT FORMAT (Return ONLY valid JSON)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required JSON keys:
- cultural_fit: string (40-60 words) - Work style, team fit, values alignment
- technical_strength: string (40-60 words) - Technical capability depth & breadth
- experience_relevance: string (40-60 words) - Direct role alignment & seniority
- top_strengths: array of 3-5 specific strengths with evidence
- improvement_areas: array of 2-4 gaps/concerns with specifics
- overall_comment: string (50-80 words) - Concise hiring recommendation
- risk_flags: array of 0-3 critical concerns (or empty if none)
- followup_questions: array of 3-5 targeted interview questions
- fit_score: integer 0-10 (based on framework below)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ SCORING FRAMEWORK (Strict Adherence Required)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Score 9-10 (Exceptional - Top 5%) ⭐⭐⭐⭐⭐:
  ✓ Must-have coverage ≥ 0.85 (85%+ critical requirements met)
  ✓ Semantic similarity ≥ 0.75 (exceptional contextual alignment)
  ✓ Demonstrates depth: multiple relevant projects, measurable impact, recent experience
  ✓ Exceeds requirements: bonus skills present, additional certifications
  ✓ Clear evidence of progression, leadership, or specialized expertise
  ✓ Quantifiable achievements directly relevant to role
  → HIRE: Top-tier candidate, move fast

Score 7-8 (Strong Fit - Top 20%) ⭐⭐⭐⭐:
  ✓ Must-have coverage ≥ 0.70 (70-85% critical requirements)
  ✓ Semantic similarity ≥ 0.60 (strong alignment)
  ✓ Core competencies solid, only minor gaps in secondary areas
  ✓ Relevant experience with some quantifiable achievements
  ✓ Can ramp up quickly with minimal training
  ✓ Good technical foundation with proven track record
  → STRONG CONSIDERATION: Solid candidate, likely to succeed

Score 5-6 (Moderate Fit - Borderline) ⭐⭐⭐:
  ~ Must-have coverage 0.55-0.69 (55-70% critical requirements)
  ~ Semantic similarity 0.50-0.59 (moderate alignment)
  ~ Has foundation but missing several key skills or lacking depth
  ~ May require moderate training/onboarding (2-3 months)
  ~ Experience somewhat relevant but not exact match
  ~ Could work in right circumstances (team support, training budget)
  → PROCEED WITH CAUTION: Interview carefully, assess learning ability

Score 3-4 (Weak Fit - High Risk) ⭐:
  ✗ Must-have coverage 0.40-0.54 (40-55% critical requirements)
  ✗ Semantic similarity 0.35-0.49 (weak alignment)
  ✗ Missing multiple core requirements (>45% gaps)
  ✗ Limited relevant experience or outdated/tangential skills
  ✗ Would require extensive retraining (4-6+ months)
  ✗ Significant risk of failure or slow productivity ramp
  → LIKELY REJECT: Only consider if desperate or unique circumstances

Score 0-2 (Not Viable - Reject) ❌:
  ✗ Must-have coverage < 0.40 (< 40% critical requirements)
  ✗ Semantic similarity < 0.35 (poor alignment)
  ✗ Fundamentally wrong profile for role
  ✗ Lacks basic qualifications (>60% gaps in must-haves)
  ✗ No clear path to success, would need 6+ months training
  ✗ Better fit for different role or seniority level
  → REJECT: Clear mismatch, don't proceed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 MANDATORY SCORE CAPS (Hard Limits - Override Upward)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply these HARD CAPS regardless of other positive factors:

• Must_coverage < 0.25 → MAXIMUM score = 3 (critical failure, >75% gaps)
• Must_coverage < 0.40 → MAXIMUM score = 4 (major gaps, >60% missing)
• Must_coverage < 0.55 → MAXIMUM score = 6 (significant gaps, >45% missing)
• Must_coverage < 0.70 → MAXIMUM score = 7 (noticeable gaps, >30% missing)

Additional Penalties (subtract from base score):
• Both must_coverage < 0.50 AND semantic < 0.50 → Subtract 1.0 point (compound weakness)
• Missing ≥3 critical core technologies (e.g., primary language, main framework, key tool) → Subtract 0.5-1.0 points
• Experience years < 50% of required (e.g., 2 years vs 5+ required) → Subtract 1.0 point
• No quantifiable achievements AND must_coverage < 0.60 → Maximum score = 6
• Semantic similarity < 0.35 (very poor contextual fit) → Subtract 0.8 points

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 EVALUATION DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUANTITATIVE METRICS:
• Semantic Similarity: {global_sem:.3f} (0.0-1.0 scale, higher = better contextual fit)
• Overall Coverage: {cov_final:.3f} (0.0-1.0 scale, weighted must+nice requirements)
• Must-Have Coverage: {coverage_brief['must_coverage']} (critical requirements only)
• Nice-To-Have Coverage: {coverage_brief['nice_coverage']} (bonus skills)

REQUIREMENT ANALYSIS:
• Must-Have Requirements: {coverage_brief.get('must_atoms_count', 0)} total
  - Found: {len(coverage_brief.get('must_found', []))} items
  - Partial: {len(coverage_brief.get('must_partial', []))} items  
  - Missing: {len(coverage_brief.get('must_missing', []))} items
• Nice-To-Have Requirements: {coverage_brief.get('nice_atoms_count', 0)} total
  - Found: {len(coverage_brief.get('nice_found', []))} items

DETAILED COVERAGE BREAKDOWN:
{coverage_json}

CUE ALIGNMENT (Work Style & Context Fit):
• Average Cue Similarity: {cue_brief['average_similarity']} (0.0-1.0 scale)
• Strong Matches: {len(cue_brief.get('strong_matches', []))} cues
• Weak Matches: {len(cue_brief.get('weak_matches', []))} cues
{cue_json}

JOB ANALYSIS PLAN:
{plan_json}

CANDIDATE PROFILE:
{profile_json}

JOB DESCRIPTION EXCERPT:
{jd[:1800]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 ASSESSMENT GUIDELINES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Be SPECIFIC in your analysis:
  • Cite actual technologies/skills found or missing
  • Reference quantifiable achievements from resume
  • Compare experience years against requirements
  • Note recency of technical experience (outdated = red flag)
  • Consider breadth vs depth trade-offs

Avoid VAGUE statements like:
  ❌ "Good technical background"
  ❌ "Seems like a decent fit"
  ❌ "Has some relevant experience"
  
Use CONCRETE statements like:
  ✅ "5 years Python + Django aligns with 3+ years requirement"
  ✅ "Missing Kubernetes and Docker (both required)"
  ✅ "Led 2 production deployments with 40% performance gain"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL REMINDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Output ONLY valid JSON (no markdown, no explanations)
2. Apply scoring framework strictly (don't inflate scores)
3. Ground all statements in provided evidence
4. Be honest about gaps (don't sugarcoat weaknesses)
5. Prioritize must-haves over nice-to-haves
6. Consider both technical skills AND experience relevance

BEGIN ASSESSMENT NOW:
"""
