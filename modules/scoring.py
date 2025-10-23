"""
Scoring and Evaluation Logic
"""
import numpy as np
import re
import json
from modules.llm_operations import llm_verify_requirements_clean, llm_json
from modules.text_processing import retrieve_relevant_context, token_set, contains_atom, normalize_text

def compute_global_semantic(embedder, resume_embs, jd_text):
    """
    IMPROVED global semantic similarity: fair to good candidates.
    Uses top-k averaging without over-penalizing well-matched resumes.
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
        
        # Use top-8 chunks for balance (focused, not too generous)
        k = min(8, sims.size)
        topk = np.sort(sims)[-k:]
        
        # Weighted average: emphasize very top chunks
        if k > 1:
            weights = np.linspace(0.7, 1.0, k)  # Smoother weighting
            score = float(np.average(topk, weights=weights))
        else:
            score = float(np.mean(topk))
        
        # IMPROVED: Softer calibration (1.0 factor = no penalty)
        # This allows genuinely good semantic matches to score high
        calibrated = score * 1.0  # No harsh calibration factor
        
        return float(np.clip(calibrated, 0.0, 1.0))
    except Exception:
        return 0.0

def evaluate_requirement_coverage(must_atoms, nice_atoms, resume_text, resume_chunks, embedder, model=None,
                                   faiss_index=None, strict_threshold=0.85, partial_threshold=0.70,
                                   nlp=None, jd_text=""):
    """
    Clean, accurate requirement coverage analysis with VERY STRICT thresholds:
    1. Use semantic search to find relevant resume sections for each requirement
    2. LLM verifies if requirement is actually met based on evidence
    3. Score based on: presence (yes/no) + confidence (0-1) + evidence quality
    
    Thresholds (very strict for accurate differentiation):
    - Strict match: ≥0.85 (was 0.80) - Very high bar for full credit
    - Partial match: ≥0.70 (was 0.65) - High bar for partial credit
    - Weak match: ≥0.55 (was 0.50) - Minimum for any credit
    
    No random adjustments, no fingerprints, just accurate matching.
    """
    
    # Step 1: Encode resume chunks for semantic search
    chunk_embs = None
    if resume_chunks and embedder:
        try:
            chunk_embs = embedder.encode(resume_chunks, convert_to_numpy=True, normalize_embeddings=True)
            if chunk_embs.ndim == 1:
                chunk_embs = chunk_embs.reshape(1, -1)
        except Exception:
            chunk_embs = None

    def get_best_resume_evidence(requirement, top_k=5):
        """
        Find the most relevant resume sections for this requirement.
        Uses hybrid approach: semantic search + keyword matching for better accuracy.
        """
        if not requirement:
            return [], 0.0
        
        evidence = []
        similarities = []
        keyword_boost_applied = False
        
        # Helper: Check if requirement keywords exist in text
        def has_keyword_match(text, req):
            """Check for keyword/phrase match with variations."""
            text_lower = text.lower()
            req_lower = req.lower()
            
            # Direct match
            if req_lower in text_lower:
                return True
            
            # Check for abbreviation/full form matches
            abbrev_variants = {
                'operating system': ['operating system', 'os ', ' os', 'os,', 'os.', 'os)', 'os/'],
                'database management': ['dbms', 'database management', 'database systems'],
                'computer network': ['computer network', 'networking', ' cn ', 'cn,', 'cn.'],
                'data structure': ['data structure', 'ds ', ' ds,', 'ds.'],
                'object oriented': ['oop', 'object oriented', 'object-oriented'],
                'aws': ['aws', 'amazon web service'],
                'kubernetes': ['kubernetes', 'k8s'],
                'javascript': ['javascript', 'js ', ' js,', 'js.'],
                'typescript': ['typescript', 'ts '],
                'postgresql': ['postgresql', 'postgres'],
                'mongodb': ['mongodb', 'mongo'],
            }
            
            # Check variants
            for full_form, variants in abbrev_variants.items():
                if full_form in req_lower:
                    if any(v in text_lower for v in variants):
                        return True
            
            # Check individual important words (for compound requirements)
            req_words = [w for w in req_lower.split() if len(w) > 2]
            if len(req_words) >= 2:
                # For multi-word requirements, check if most words are present
                matches = sum(1 for w in req_words if w in text_lower)
                if matches >= len(req_words) * 0.6:  # 60% of words present
                    return True
            
            return False
        
        # Use FAISS if available (faster)
        if faiss_index is not None and resume_chunks and embedder:
            try:
                results = retrieve_relevant_context(requirement, faiss_index, resume_chunks, embedder, top_k=top_k)
                for text, sim in results:
                    sim = float(np.clip(sim, 0.0, 1.0))
                    
                    # Boost similarity if keyword match found
                    if has_keyword_match(text, requirement):
                        sim = min(0.95, sim + 0.30)  # +30% boost, cap at 0.95
                        keyword_boost_applied = True
                    
                    evidence.append({"text": text[:300], "similarity": round(sim, 3)})
                    similarities.append(sim)
            except Exception:
                pass
        
        # Fallback to direct embedding comparison
        elif chunk_embs is not None and embedder and resume_chunks:
            try:
                req_emb = embedder.encode(requirement, convert_to_numpy=True, normalize_embeddings=True)
                if req_emb.ndim > 1:
                    req_emb = req_emb[0]
                
                sims = np.dot(chunk_embs, req_emb)
                top_indices = np.argsort(sims)[-top_k:][::-1]
                
                for idx in top_indices:
                    if 0 <= idx < len(resume_chunks):
                        sim = float(np.clip(sims[idx], 0.0, 1.0))
                        
                        # Boost similarity if keyword match found
                        if has_keyword_match(resume_chunks[idx], requirement):
                            sim = min(0.95, sim + 0.30)  # +30% boost
                            keyword_boost_applied = True
                        
                        if sim > 0.3:  # Only include relevant matches
                            evidence.append({"text": resume_chunks[idx][:300], "similarity": round(sim, 3)})
                            similarities.append(sim)
            except Exception:
                pass
        
        # Additional keyword search if semantic search fails
        if not similarities or max(similarities) < 0.50:
            # Search entire resume text for keyword matches
            for chunk in (resume_chunks or []):
                if has_keyword_match(chunk, requirement):
                    # Found keyword match that semantic search missed
                    boosted_sim = 0.70  # Assign decent similarity for keyword match
                    if chunk[:300] not in [e["text"] for e in evidence]:
                        evidence.append({"text": chunk[:300], "similarity": round(boosted_sim, 3)})
                        similarities.append(boosted_sim)
                        keyword_boost_applied = True
                    if len(evidence) >= top_k:
                        break
        
        max_sim = max(similarities) if similarities else 0.0
        return evidence[:top_k], round(max_sim, 3)

    def calculate_initial_score(requirement, max_similarity):
        """Calculate preliminary score based on semantic similarity with VERY STRICT thresholds."""
        if max_similarity >= strict_threshold:  # ≥0.85
            return 0.85  # Strong match - very high bar
        elif max_similarity >= partial_threshold:  # ≥0.70
            return 0.60  # Partial match - high bar
        elif max_similarity >= 0.55:  # ≥0.55 (was 0.50)
            return 0.35  # Weak match - minimum threshold raised
        else:
            return 0.0  # No match

    # Step 2: Analyze each requirement
    def analyze_requirements(atoms, req_type):
        """Analyze a list of requirements (must-have or nice-to-have)."""
        details = {}
        llm_queue = []
        
        for atom in atoms:
            evidence, max_sim = get_best_resume_evidence(atom)
            initial_score = calculate_initial_score(atom, max_sim)
            
            detail = {
                "req_type": req_type,
                "similarity": max_sim,
                "max_similarity": max_sim,
                "resume_contexts": evidence,
                "jd_context": {"text": "", "similarity": 0.0},  # Simplified - focus on resume evidence
                "pre_llm_score": initial_score,
                "score": initial_score,
                "llm_present": False,
                "llm_confidence": 0.0,
                "llm_rationale": "",
                "llm_evidence": ""
            }
            details[atom] = detail
            
            # Queue for LLM verification if model available and evidence found
            if model and evidence:
                llm_queue.append({
                    "requirement": atom,
                    "req_type": req_type,
                    "resume_evidence": evidence,
                    "max_similarity": max_sim
                })
        
        return details, llm_queue

    must_details, must_queue = analyze_requirements(must_atoms, "must-have")
    nice_details, nice_queue = analyze_requirements(nice_atoms, "nice-to-have") if nice_atoms else ({}, [])

    # Step 3: LLM verification for accurate presence detection
    if model and (must_queue or nice_queue):
        all_queue = must_queue + nice_queue
        llm_results = llm_verify_requirements_clean(model, all_queue, resume_text)
        
        # Update details with LLM verdicts
        for atom, detail in {**must_details, **nice_details}.items():
            verdict = llm_results.get(atom)
            if not verdict:
                continue
            
            present = verdict.get("present", False)
            confidence = float(verdict.get("confidence", 0.0))
            confidence = max(0.0, min(1.0, confidence))
            
            detail["llm_present"] = present
            detail["llm_confidence"] = confidence
            detail["llm_rationale"] = verdict.get("rationale", "")
            detail["llm_evidence"] = verdict.get("evidence", "")
            
            # Calculate final score using STRICT algorithm
            if present:
                # Skill is present - score based on confidence and evidence quality
                # Range: 0.55 to 1.0 (stricter base)
                base_score = 0.55  # Lowered from 0.60
                confidence_bonus = 0.45 * confidence  # Increased range (was 0.40)
                detail["score"] = base_score + confidence_bonus
                
                # Boost for strong evidence (high semantic similarity) - stricter thresholds
                if detail["max_similarity"] >= 0.90:
                    detail["score"] = min(1.0, detail["score"] * 1.12)  # 12% boost for very strong
                elif detail["max_similarity"] >= 0.85:
                    detail["score"] = min(1.0, detail["score"] * 1.08)  # 8% boost (was 10%)
                elif detail["max_similarity"] >= 0.75:
                    detail["score"] = min(1.0, detail["score"] * 1.04)  # 4% boost (was 5%)
                    
            else:
                # Skill is absent - stricter penalties
                if confidence >= 0.85:  # Raised from 0.8
                    # Highly confident it's missing - zero points
                    detail["score"] = 0.0
                elif confidence >= 0.70:  # Raised from 0.6
                    # Likely missing - very small residual score
                    detail["score"] = 0.05  # Reduced from 0.10
                elif confidence >= 0.50:  # Raised from 0.4
                    # Uncertain - minimal benefit of doubt
                    detail["score"] = 0.20  # Reduced from 0.25
                else:
                    # Low confidence in absence - maybe present but unclear
                    # Use semantic similarity as tiebreaker (more conservative)
                    detail["score"] = min(0.35, detail["pre_llm_score"] * 0.7)  # Reduced from 0.40 and 0.8

    # Step 4: Calculate overall coverage with sophisticated weighting
    must_scores = [d["score"] for d in must_details.values()]
    nice_scores = [d["score"] for d in nice_details.values()]

    # Must-have coverage: strict average (all must be met)
    must_coverage = float(np.mean(must_scores)) if must_scores else 0.0
    
    # Nice-to-have coverage: more forgiving (bonus, not required)
    nice_coverage = float(np.mean(nice_scores)) if nice_scores else 1.0
    
    # Apply penalty if too many must-haves are missing
    must_present_count = sum(1 for d in must_details.values() if d.get("llm_present", False))
    must_total = len(must_details) if must_details else 1
    must_fulfillment_rate = must_present_count / must_total
    
    # Penalty factor: STRICT penalties for missing must-haves
    if must_fulfillment_rate < 0.4:  # Less than 40% must-haves present (was 50%)
        penalty_factor = 0.60  # 40% penalty (was 30%)
    elif must_fulfillment_rate < 0.6:  # 40-60% present (was 50-70%)
        penalty_factor = 0.75  # 25% penalty (was 15%)
    elif must_fulfillment_rate < 0.8:  # 60-80% present (new tier)
        penalty_factor = 0.90  # 10% penalty
    else:
        penalty_factor = 1.0  # No penalty only if 80%+ met
    
    # Calculate overall: 80% must-have, 20% nice-to-have (must-haves matter MUCH more)
    if must_scores:
        raw_overall = (0.80 * must_coverage + 0.20 * nice_coverage)  # Changed from 75/25
        overall_coverage = raw_overall * penalty_factor
    else:
        overall_coverage = nice_coverage

    return {
        "overall": round(overall_coverage, 3),
        "must": round(must_coverage, 3),
        "nice": round(nice_coverage, 3),
        "details": {"must": must_details, "nice": nice_details},
        "competencies": {"scores": {}, "evidence": {}}  # Removed complex competency logic
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

def compute_cue_alignment(plan, parsed_resume, profile, embedder, faiss_index=None):
    """Compute cosine-similarity alignment between JD enrichment cues and resume evidence."""
    jd_cues = [c.strip() for c in (plan.get("enrichment_cues") or []) if isinstance(c, str) and c.strip()]
    jd_cues = jd_cues[:25]

    def _collect_strings(values):
        collected = []
        if isinstance(values, list):
            for item in values:
                if isinstance(item, str) and item.strip():
                    collected.append(item.strip())
        return collected

    resume_cue_set = set()

    if isinstance(parsed_resume, dict):
        for skill in _collect_strings(parsed_resume.get("technical_skills")):
            resume_cue_set.add(skill)

    if isinstance(profile, dict):
        resume_cue_set.update(_collect_strings(profile.get("core_skills")))
        resume_cue_set.update(_collect_strings(profile.get("tools")))
        resume_cue_set.update(_collect_strings(profile.get("cloud_experience")))
        resume_cue_set.update(_collect_strings(profile.get("ml_ai_experience")))
        resume_cue_set.update(_collect_strings(profile.get("notable_metrics")))

        projects = profile.get("projects") or []
        if isinstance(projects, list):
            for proj in projects:
                if isinstance(proj, dict):
                    name = proj.get("name")
                    desc = proj.get("description")
                    if isinstance(name, str) and name.strip():
                        resume_cue_set.add(name.strip())
                    if isinstance(desc, str) and desc.strip():
                        resume_cue_set.add(desc.strip())

        summary = profile.get("summary")
        if isinstance(summary, str) and summary.strip():
            resume_cue_set.add(summary.strip())

    resume_cues = [c for c in resume_cue_set if len(c) > 2][:60]

    if not jd_cues or not resume_cues or embedder is None:
        return {
            "jd_cues": jd_cues,
            "resume_cues": resume_cues,
            "alignments": [],
            "average_similarity": 0.0,
            "strong_matches": [],
            "weak_matches": jd_cues
        }

    try:
        jd_embs = embedder.encode(jd_cues, convert_to_numpy=True, normalize_embeddings=True)
        if jd_embs.ndim == 1:
            jd_embs = jd_embs.reshape(1, -1)
        resume_embs = embedder.encode(resume_cues, convert_to_numpy=True, normalize_embeddings=True)
        if resume_embs.ndim == 1:
            resume_embs = resume_embs.reshape(1, -1)
    except Exception:
        return {
            "jd_cues": jd_cues,
            "resume_cues": resume_cues,
            "alignments": [],
            "average_similarity": 0.0,
            "strong_matches": [],
            "weak_matches": jd_cues
        }

    alignments = []
    strong, weak = [], []
    resume_chunks = parsed_resume.get("chunks") if isinstance(parsed_resume, dict) else None

    for idx, cue in enumerate(jd_cues):
        cue_emb = jd_embs[idx]
        sims = np.dot(resume_embs, cue_emb)
        best_idx = int(np.argmax(sims)) if sims.size > 0 else -1
        best_sim = float(np.clip(sims[best_idx], -1.0, 1.0)) if best_idx >= 0 else 0.0
        best_resume_cue = resume_cues[best_idx] if best_idx >= 0 else ""

        resume_context = ""
        if faiss_index is not None and resume_chunks and embedder and best_resume_cue:
            contexts = retrieve_relevant_context(best_resume_cue, faiss_index, resume_chunks, embedder, top_k=1)
            if contexts:
                snippet = re.sub(r'\s+', ' ', contexts[0][0]).strip()
                resume_context = snippet[:257].rstrip() + ("..." if len(snippet) > 260 else "")

        alignments.append({
            "jd_cue": cue,
            "matched_resume_cue": best_resume_cue,
            "similarity": best_sim,
            "resume_context": resume_context
        })

        if best_sim >= 0.70:
            strong.append(cue)
        elif best_sim < 0.40:
            weak.append(cue)

    average_similarity = float(np.mean([a["similarity"] for a in alignments])) if alignments else 0.0

    return {
        "jd_cues": jd_cues,
        "resume_cues": resume_cues,
        "alignments": alignments,
        "average_similarity": average_similarity,
        "strong_matches": strong,
        "weak_matches": weak
    }

def build_competency_catalog():
    """
    Define competency bundles that represent real-world capability beyond a single keyword.
    Each competency includes:
    - core: anchor terms (usually languages or role-defining tech)
    - frameworks/tools: ecosystem items that strengthen competency
    - project_verbs: verbs that indicate hands-on building
    - queries: suggested RAG queries
    """
    return {
        "java_ecosystem": {
            "core": ["java", "java 8", "java 11", "java 17"],
            "frameworks": [
                "spring", "spring boot", "spring cloud", "spring mvc",
                "hibernate", "jpa", "jakarta", "microservices", "rest api",
                "maven", "gradle", "junit", "mockito", "kafka"
            ],
            "project_verbs": ["built", "developed", "implemented", "designed", "maintained", "deployed"],
            "queries": ["java spring boot project", "java microservices", "spring hibernate"]
        },
        "python_backend": {
            "core": ["python", "python 3", "python 3.x"],
            "frameworks": [
                "django", "django rest framework", "flask", "fastapi",
                "pandas", "numpy", "celery", "sqlalchemy", "pytest"
            ],
            "project_verbs": ["built", "developed", "implemented", "designed", "maintained", "deployed"],
            "queries": ["python django api", "fastapi production", "flask project"]
        },
        "node_backend": {
            "core": ["node", "node.js", "nodejs"],
            "frameworks": ["express", "nest", "nestjs", "typescript", "prisma", "sequelize", "jest"],
            "project_verbs": ["built", "developed", "implemented", "designed", "maintained", "deployed"],
            "queries": ["node express api", "node microservices", "nestjs project"]
        },
        "frontend_js": {
            "core": ["javascript", "typescript"],
            "frameworks": ["react", "react 18", "nextjs", "next.js", "angular", "vue", "redux", "vite", "webpack"],
            "project_verbs": ["built", "developed", "implemented", "designed", "maintained", "deployed"],
            "queries": ["react project", "typescript react", "nextjs production"]
        },
        "devops_cloud": {
            "core": ["docker", "kubernetes", "k8s"],
            "frameworks": [
                "ci/cd", "jenkins", "github actions", "gitlab ci", "terraform", "ansible", "helm",
                "aws", "azure", "gcp", "prometheus", "grafana"
            ],
            "project_verbs": ["deployed", "automated", "scaled", "containerized", "orchestrated"],
            "queries": ["kubernetes deployment", "terraform ci/cd", "docker production"]
        },
        "data_ml": {
            "core": ["machine learning", "ml", "ai", "deep learning"],
            "frameworks": [
                "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras", "xgboost", "lightgbm",
                "mlflow", "airflow", "sagemaker", "vertex ai"
            ],
            "project_verbs": ["trained", "deployed", "optimized", "built", "developed"],
            "queries": ["ml production", "tensorflow deployment", "pytorch project"]
        }
    }

def compute_competency_scores(resume_text, chunks, embedder, nlp, model=None, faiss_index=None):
    """
    Compute a competency score per ecosystem using primarily local evidence, with LLM support for borderline cases.
    Scoring (0..1): core (0.3) + frameworks (up to 0.45) + projects evidence (0.15) + recency (0.1)
    Returns (scores, evidence) where evidence has keys: frameworks_found, project_contexts, recent
    """
    catalog = build_competency_catalog()
    tokens = token_set(resume_text)
    scores = {}
    evidences = {}

    for comp_id, spec in catalog.items():
        core = spec["core"]
        frameworks = spec["frameworks"]
        verbs = spec["project_verbs"]
        queries = spec["queries"]

        core_hits = _find_terms_in_text(core, tokens, resume_text)
        fw_hits = _find_terms_in_text(frameworks, tokens, resume_text)

        # RAG contexts to check project verbs & recency
        contexts = []
        if faiss_index and chunks and embedder:
            for q in queries[:2]:
                ctxs = retrieve_relevant_context(q, faiss_index, chunks, embedder, top_k=2)
                for t, s in ctxs:
                    contexts.append(t)
        # Deduplicate and trim
        contexts = list(dict.fromkeys(contexts))[:5]
        ctx_text = "\n".join(contexts)

        # Project verb evidence if appears near core/framework contexts
        project_evidence = 0
        if contexts:
            for c in contexts:
                if any(v in c.lower() for v in verbs):
                    project_evidence += 1
        recent = _recent_years_present(ctx_text) or _recent_years_present(resume_text)

        # Score aggregation
        score = 0.0
        if core_hits:
            score += 0.30
        # Frameworks: diminishing returns up to 0.45
        fw_count = len(fw_hits)
        if fw_count > 0:
            score += min(0.45, 0.20 + 0.12 * min(3, fw_count-1))
        # Projects
        if project_evidence > 0:
            score += min(0.15, 0.07 + 0.04 * min(2, project_evidence-1))
        # Recency
        if recent:
            score += 0.10

        # Optional LLM boost for borderline cases (supportive only)
        if model and 0.45 <= score < 0.75 and contexts:
            try:
                verdict = llm_json(model, f"""
Return ONLY JSON: {{"substantial": true|false}}
You are validating if the resume shows SUBSTANTIAL, PRACTICAL experience in the competency: {comp_id}.
Consider these resume excerpts:
{ctx_text[:1200]}
Criteria: multiple ecosystem frameworks, projects built, deployments, or tests. Answer conservatively.
                """)
                if isinstance(verdict, dict) and bool(verdict.get("substantial")):
                    score = min(0.80, score + 0.12)
            except Exception:
                pass

        scores[comp_id] = float(np.clip(score, 0.0, 1.0))
        evidences[comp_id] = {
            "frameworks_found": sorted(list(fw_hits))[:10],
            "core_found": sorted(list(core_hits))[:5],
            "project_contexts": contexts,
            "recent": bool(recent),
            "frameworks_count": int(fw_count)
        }

    return scores, evidences

def map_atoms_to_competencies(atoms, catalog):
    """
    Map requirement atoms to competency IDs with kind: core/framework/tool.
    Returns: (atom_to_comp, atom_kind)
    """
    atom_to_comp = {}
    atom_kind = {}
    for a in atoms:
        a_norm = normalize_text(a)
        for comp_id, spec in catalog.items():
            # core match
            if any(t in a_norm for t in spec["core"]):
                atom_to_comp[a_norm] = comp_id
                atom_kind[a_norm] = "core"
                break
            # framework match
            if any(t in a_norm for t in spec["frameworks"]):
                atom_to_comp[a_norm] = comp_id
                atom_kind[a_norm] = "framework"
                break
        # If not matched, leave unmapped
    return atom_to_comp, atom_kind

def _find_terms_in_text(terms, tokens, full_text):
    hits = set()
    for t in terms:
        if contains_atom(t, tokens, full_text):
            hits.add(normalize_text(t))
    return hits

def _recent_years_present(text, window=4):
    try:
        from datetime import datetime as _dt
        year_now = _dt.now().year
    except Exception:
        year_now = 2025
    yrs = {str(y) for y in range(year_now-window+1, year_now+1)}
    return any(y in text for y in yrs)

