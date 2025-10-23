"""
LLM Operations and Prompt Engineering
"""
import json
import time
import re
from modules.text_processing import normalize_text

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


def llm_verify_requirements_clean(model, requirements_payload, resume_text):
    """
    Clean LLM verification: Is each requirement present in the resume? Yes/No + Confidence + Evidence.
    No complexity, no gibberish, just accurate matching.
    """
    if not requirements_payload or not model:
        return {}

    results = {}
    batch_size = 10  # Process 10 requirements at a time
    
    # Prepare resume excerpt (limit to avoid token overflow)
    resume_excerpt = resume_text[:4000] if len(resume_text) > 4000 else resume_text
    
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
                    "similarity": ev.get("similarity", 0.0)
                })
            
            formatted_reqs.append({
                "requirement": req_name,
                "type": item.get("req_type", ""),
                "evidence": evidence_snippets
            })
        
        prompt = f"""You are an expert technical recruiter analyzing a candidate's resume for specific requirements. Your task is to provide UNIQUE, SPECIFIC assessments for each requirement.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 REQUIREMENTS TO VERIFY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{json.dumps(formatted_reqs, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 CANDIDATE'S RESUME
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{resume_excerpt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ASSESSMENT CRITERIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For EACH requirement, provide:

1. **present** (boolean): Is the skill/technology actually used?
   ✅ TRUE if: Mentioned in projects/experience + specific use cases described
   ❌ FALSE if: Not mentioned OR only in skills list without usage proof

2. **confidence** (0.0 to 1.0): Certainty level - BE STRICT!
   - 0.9-1.0: Used extensively in multiple projects with detailed, concrete descriptions
   - 0.7-0.8: Used in at least one substantial project with clear, specific description
   - 0.5-0.6: Mentioned with some context OR in skills list with light project usage
   - 0.3-0.4: Only in skills list without evidence OR weak/indirect mention
   - 0.0-0.2: Not found, vague reference, or only aspirational mention

3. **rationale** (15-25 words): SPECIFIC, UNIQUE explanation
   ⚠️ MUST BE UNIQUE PER REQUIREMENT - Don't use generic phrases!
   ✅ GOOD: "Used Python in E-commerce Platform project for backend APIs and data processing"
   ✅ GOOD: "No PostgreSQL mention; uses MySQL in Project X instead"
   ✅ GOOD: "React expertise shown in Healthcare Dashboard with Redux state management"
   ❌ BAD: "Clearly demonstrated in projects" (too generic)
   ❌ BAD: "Mentioned in resume" (too vague)
   ❌ BAD: "Experience with technology" (not specific)
   
   REQUIRED FORMAT:
   - If present=true: Mention the PROJECT NAME or CONTEXT where used
   - If present=false: State what's missing or what alternative is used instead

4. **evidence** (20-40 words): Direct quote with PROJECT CONTEXT
   - Include the PROJECT/COMPANY NAME if possible
   - Quote the SPECIFIC LINE that proves usage
   - If not present, leave empty ("")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ MATCHING RULES (CRITICAL - READ CAREFULLY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⚠️ ABBREVIATIONS = FULL FORMS (treat as SAME):**
- OS = Operating Systems = Operating System
- DBMS = Database Management Systems = Database Management System
- CN = Computer Networks = Computer Networking
- DS = Data Structures = Data Structure
- OOP = Object Oriented Programming = Object-Oriented
- AWS = Amazon Web Services
- K8s = Kubernetes
- JS = JavaScript
- TS = TypeScript
- PostgreSQL = Postgres
- MongoDB = Mongo

**✅ Accept as matches:**
- Exact/common names: Python=Python
- Abbreviations: If resume has "OS", requirement "Operating Systems" is MET
- Versions: React 18 satisfies "React"
- Specifics: Django REST satisfies "Django"
- Skills list + ANY project usage = PRESENT (confidence 0.5-0.6)
- Skills list + detailed project = PRESENT (confidence 0.7-0.9)

**❌ Reject as non-matches:**
- Wrong tech: MySQL ≠ PostgreSQL
- Vague: "databases" ≠ "MongoDB"
- Insufficient duration: "1 yr Python" ≠ "5+ yrs Python"
- List-only: Skill listed but zero project usage = LOW confidence (0.4-0.5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON (no markdown, no ```json):

{{
  "requirement_name": {{
    "present": true/false,
    "confidence": 0.0-1.0,
    "rationale": "Specific explanation mentioning project/context (15-25 words)",
    "evidence": "Quoted text with project name (if present, else empty)"
  }}
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL ANTI-REPETITION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Each rationale MUST be UNIQUE - no copy-paste explanations
2. MUST mention specific PROJECT NAMES or CONTEXTS from resume
3. NO generic phrases like "demonstrated", "mentioned", "experience with"
4. If skill is absent, explain WHY or what's used INSTEAD
5. Be forensic: cite actual project names, company names, or specific contexts

EXAMPLE OF GOOD (UNIQUE, SPECIFIC) RATIONALES:
- "Python used extensively in E-commerce Platform project for REST API development and data pipelines"
- "No Docker mentioned; deployment appears to be traditional VM-based per DevOps section"
- "Strong React skills evidenced in Healthcare Dashboard project using hooks and context API"
- "AWS mentioned in resume but only S3 storage; no Lambda or serverless experience shown"

BEGIN ANALYSIS:
"""

        try:
            raw = llm_json(model, prompt)
            if not isinstance(raw, dict):
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
                    def clean_llm_text(text, max_words=25):
                        if not text:
                            return ""
                        # Remove markdown and code artifacts
                        text = re.sub(r'```\w*', '', text)
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
                    
                    rationale = clean_llm_text(rationale, max_words=20)
                    evidence = clean_llm_text(evidence, max_words=30)
                    
                    results[req_name] = {
                        "present": present,
                        "confidence": confidence,
                        "rationale": rationale,
                        "evidence": evidence
                    }
                    
        except Exception as e:
            # Skip this batch on error, continue with next
            continue
    
    return results


def llm_verify_requirements(model, requirements_payload, resume_text, jd_text=""):
    """Legacy function - redirects to new clean implementation."""
    return llm_verify_requirements_clean(model, requirements_payload, resume_text)


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
    return f"""You are an expert technical recruiter analyzing a job description. Extract ALL requirements in a structured, comprehensive way.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 EXTRACTION CATEGORIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Extract requirements into 4 distinct categories:

1. **hard_skills**: Technical skills, technologies, tools, frameworks
   - Languages: Python, Java, JavaScript, C++, Go, Rust, etc.
   - Frameworks: React, Angular, Django, Flask, Spring Boot, etc.
   - Databases: PostgreSQL, MySQL, MongoDB, Redis, Cassandra, etc.
   - Cloud: AWS, Azure, GCP, specific services (Lambda, S3, EC2, etc.)
   - DevOps: Docker, Kubernetes, Jenkins, CI/CD, Terraform, etc.
   - Tools: Git, Postman, VS Code, JIRA, etc.
   - Concepts: REST API, GraphQL, Microservices, OOP, etc.

2. **fundamentals**: Core CS/IT concepts and foundations
   - DBMS, Operating Systems, Computer Networks, Data Structures
   - Algorithms, System Design, Software Architecture
   - Security principles, Design patterns, etc.

3. **experience**: Years of experience, seniority, specific domains
   - "5+ years Python", "3 years backend development"
   - "Senior level", "Mid-level", "Experience with fintech"
   - Industry experience requirements

4. **qualifications**: Education, certifications, degrees
   - "Bachelor's in CS", "Master's preferred"
   - "AWS Certified", "PMP Certification"
   - Specific degree requirements

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 EXTRACTION RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **DO:**
- Extract EVERY specific technology/tool mentioned
- Include common abbreviations (AWS, K8s, JS, etc.)
- Extract version-specific mentions (Python 3.x, React 18, etc.)
- Include compound skills as separate items (Django/Flask → both)
- Keep original casing for proper nouns (React, MongoDB, AWS)
- Extract implicit requirements (mentions "Lambda" → add "AWS")

❌ **DON'T:**
- Include vague qualifiers ("good knowledge", "strong understanding")
- Extract generic words ("experience", "skills", "work")
- Include soft skills here (teamwork, communication) - skip these
- Add items not in the JD
- Be repetitive (don't list "Python" 10 times)

⚠️ **AVOID REDUNDANT ABBREVIATION/FULL FORM DUPLICATES:**
- If JD says "Operating Systems", extract ONLY "Operating Systems" (not both "OS" + "Operating Systems")
- If JD says "OS", extract ONLY "OS" (not both)
- If JD says "DBMS", extract ONLY "DBMS" (not "Database Management Systems" too)
- Exception: If JD explicitly uses BOTH forms, then include both
- Our system automatically maps abbreviations to full forms, so one is enough

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 PRIORITY CLASSIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each category, classify items as MUST-HAVE or NICE-TO-HAVE:

**must**: Required, mandatory, essential
- Keywords: "required", "must have", "essential", "mandatory"
- Core tech stack items
- Minimum experience requirements

**nice**: Preferred, bonus, optional
- Keywords: "preferred", "nice to have", "bonus", "plus"
- Secondary technologies
- "Good to have" items

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Example 1:**
INPUT: "Required: 5+ years Python, strong Django/Flask experience, PostgreSQL, Docker. Core IT fundamentals (DBMS/OS/CN) essential. Bachelor's in CS required. Preferred: AWS, Kubernetes, React."

OUTPUT:
{{
  "hard_skills": {{
    "must": ["Python", "Django", "Flask", "PostgreSQL", "Docker"],
    "nice": ["AWS", "Kubernetes", "React"]
  }},
  "fundamentals": {{
    "must": ["DBMS", "OS", "CN"],
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

Note: Only "DBMS", "OS", "CN" extracted (not full forms) because JD uses abbreviations. Our system handles the mapping automatically.

**Example 2:**
INPUT: "Looking for Full Stack Engineer with React, Node.js, MongoDB. Good understanding of REST APIs, microservices. Experience with AWS Lambda, S3. Agile methodology. Nice to have: TypeScript, GraphQL, Redis."

OUTPUT:
{{
  "hard_skills": {{
    "must": ["React", "Node.js", "Node", "MongoDB", "Mongo", "REST API", "REST", "Microservices", "AWS Lambda", "Lambda", "AWS S3", "S3", "AWS", "Agile"],
    "nice": ["TypeScript", "TS", "GraphQL", "Redis"]
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 JOB DESCRIPTION TO ANALYZE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{jd[:6000]}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL INSTRUCTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Read the ENTIRE job description above
2. Extract EVERY specific technical requirement
3. Be thorough - missing skills hurts accuracy
4. Return ONLY valid JSON (no markdown, no explanations)
5. Use the EXACT structure shown in examples

BEGIN EXTRACTION:
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
