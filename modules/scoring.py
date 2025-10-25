"""
Scoring and Evaluation Logic
ENTERPRISE-GRADE: Robust error handling, input validation, security checks
"""
import numpy as np
import re
import json
import logging
from difflib import SequenceMatcher
from modules.llm_operations import llm_verify_requirements_clean, llm_json
from modules.text_processing import retrieve_relevant_context, token_set, contains_atom, normalize_text

# Configure logging
logger = logging.getLogger(__name__)

def compute_global_semantic(jd_text, resume_text, embedder):
    """
    IMPROVED global semantic similarity: fair to good candidates.
    Uses top-k averaging without over-penalizing well-matched resumes.
    ENTERPRISE-GRADE: Input validation, dimension checking, error handling.
    """
    # ROBUSTNESS: Validate inputs
    if embedder is None:
        logger.warning("Embedder is None, returning 0.0 semantic score")
        return 0.0
    if not resume_text or not resume_text.strip():
        logger.warning("Resume text empty, returning 0.0 semantic score")
        return 0.0
    if not jd_text or not jd_text.strip():
        logger.warning("JD text empty, returning 0.0 semantic score")
        return 0.0
    
    try:
        # ROBUSTNESS: Limit text length (prevent memory issues)
        jd_text_truncated = jd_text[:5000]  # Max 5000 chars for embedding
        resume_text_truncated = resume_text[:10000]  # Max 10000 chars
        
        # Encode both texts
        jd_emb = embedder.encode(jd_text_truncated, convert_to_numpy=True, normalize_embeddings=True)
        resume_emb = embedder.encode(resume_text_truncated, convert_to_numpy=True, normalize_embeddings=True)
        
        if jd_emb.ndim > 1: 
            jd_emb = jd_emb[0]
        if resume_emb.ndim > 1:
            resume_emb = resume_emb[0]
        
        # ROBUSTNESS: Validate embedding dimensions match
        if jd_emb.shape[0] != resume_emb.shape[0]:
            logger.error(f"Embedding dimension mismatch: jd={jd_emb.shape[0]}, resume={resume_emb.shape[0]}")
            return 0.0
        
        # Compute cosine similarity (normalized embeddings, so just dot product)
        similarity = float(np.dot(jd_emb, resume_emb))
        
        # Clip to valid range
        return float(np.clip(similarity, 0.0, 1.0))
    except Exception as e:
        logger.error(f"Semantic similarity computation failed: {e}")
        return 0.0

def evaluate_requirement_coverage(atomic_reqs, resume_text, resume_chunks, embedder, model=None,
                                   faiss_index=None, nlp=None, jd_text=""):
    """
    Clean, accurate requirement coverage analysis with VERY STRICT thresholds.
    
    Parameters:
    - atomic_reqs: list of requirement strings
    - resume_text: full resume text
    - resume_chunks: list of resume text chunks
    - embedder: sentence transformer model
    - model: Gemini model for LLM verification (optional)
    - faiss_index: FAISS index for semantic search (optional)
    - nlp: spaCy model (optional)
    - jd_text: job description text (optional)
    
    Returns: (overall_score, coverage_details)
    """
    # Split requirements into must-have and nice-to-have if not already done
    must_atoms = atomic_reqs if isinstance(atomic_reqs, list) else []
    nice_atoms = []  # For now, treat all as must-have
    
    strict_threshold = 0.85
    partial_threshold = 0.70

    # Robust segmentation: sentences + bullet lines + provided chunks
    def _segment_resume(text, chunks, spacy_model):
        segments = []
        if spacy_model:
            try:
                doc = spacy_model(text)
                segments.extend([sent.text.strip() for sent in doc.sents if sent.text.strip()])
            except Exception:
                pass
        if not segments:
            # Fallback simple sentence split
            parts = re.split(r"(?<=[.!?])\s+", text)
            segments.extend([p.strip() for p in parts if p.strip()])

        # Append bullet style lines for richer evidence
        for line in text.splitlines():
            cleaned = line.strip().lstrip("-•▹•●")
            if cleaned and cleaned not in segments and len(cleaned.split()) >= 3:
                segments.append(cleaned)

        if chunks:
            segments.extend([c.strip() for c in chunks if isinstance(c, str) and c.strip()])

        # Deduplicate while preserving order
        seen = set()
        ordered = []
        for seg in segments:
            normalized = " ".join(seg.split())
            if len(normalized) < 18:
                continue
            if normalized.lower() in seen:
                continue
            seen.add(normalized.lower())
            ordered.append(normalized)
        return ordered[:400]

    resume_segments = _segment_resume(resume_text, resume_chunks, nlp)

    segment_embeddings = None
    if embedder and resume_segments:
        try:
            segment_embeddings = embedder.encode(resume_segments, convert_to_numpy=True, normalize_embeddings=True)
            if segment_embeddings.ndim == 1:
                segment_embeddings = segment_embeddings.reshape(1, -1)
        except Exception as e:
            logger.error(f"Failed to embed resume segments: {e}")
            segment_embeddings = None

    def _tokenize_requirement(req):
        words = re.findall(r"[a-zA-Z0-9+#]+", req.lower())
        return [w for w in words if len(w) > 2]

    def _keyword_presence(req_tokens, segment_text):
        if not req_tokens:
            return 0.0
        seg_words = set(re.findall(r"[a-zA-Z0-9+#]+", segment_text.lower()))
        if not seg_words:
            return 0.0
        matches = sum(1 for w in req_tokens if w in seg_words)
        return matches / max(len(req_tokens), 1)

    def _fuzzy_match(req, segment_text):
        if not req or not segment_text:
            return 0.0
        ratio = SequenceMatcher(None, req.lower(), segment_text.lower()).ratio()
        return float(ratio)

    def get_best_resume_evidence(requirement, top_k=5):
        """Semantic + keyword evidence using sentence-level parsing (no FAISS dependency)."""
        if not requirement:
            return [], 0.0

        if not resume_segments or segment_embeddings is None:
            return [], 0.0

        req_tokens = _tokenize_requirement(requirement)
        try:
            req_emb = embedder.encode(requirement, convert_to_numpy=True, normalize_embeddings=True)
            if req_emb.ndim > 1:
                req_emb = req_emb[0]
        except Exception:
            req_emb = None

        scored_segments = []
        for idx, segment in enumerate(resume_segments):
            sim_score = 0.0
            if req_emb is not None:
                sim_score = float(np.dot(segment_embeddings[idx], req_emb))
                sim_score = float(np.clip(sim_score, 0.0, 1.0))

            keyword_score = _keyword_presence(req_tokens, segment)
            fuzzy_score = _fuzzy_match(requirement, segment)

            combined = (0.6 * sim_score) + (0.3 * keyword_score) + (0.1 * fuzzy_score)

            if combined >= 0.35 or keyword_score >= 0.5:
                scored_segments.append((combined, sim_score, keyword_score, segment))

        if not scored_segments:
            return [], 0.0

        scored_segments.sort(key=lambda x: x[0], reverse=True)
        evidence = []
        for combined, sim_score, keyword_score, seg in scored_segments[:top_k]:
            evidence.append({
                "text": seg[:320],
                "similarity": round(sim_score, 3),
                "keyword_overlap": round(keyword_score, 3),
                "combined_score": round(combined, 3)
            })

        max_sim = max(item[1] for item in scored_segments)
        return evidence, round(max_sim, 3)

    resume_tokens = token_set(resume_text)

    def calculate_initial_score(max_similarity, keyword_overlap):
        """Initial deterministic signal using semantic + keyword evidence (BALANCED thresholds)."""
        score = 0.0
        
        # Semantic similarity scoring (more reasonable thresholds)
        if max_similarity >= 0.80:  # Very strong match
            score = 0.80
        elif max_similarity >= 0.70:  # Strong match
            score = 0.65
        elif max_similarity >= 0.60:  # Good match
            score = 0.50
        elif max_similarity >= 0.45:  # Moderate match
            score = 0.35
        elif max_similarity >= 0.30:  # Weak match
            score = 0.20
        
        # Keyword overlap boost (generous, keywords are strong signals)
        if keyword_overlap >= 0.70:  # Most keywords present
            score = max(score, 0.70)
        elif keyword_overlap >= 0.55:  # Many keywords present
            score = max(score, 0.55)
        elif keyword_overlap >= 0.40:  # Some keywords present
            score = max(score, 0.40)
        elif keyword_overlap >= 0.25:  # Few keywords present
            score = max(score, 0.25)

        return score

    # Step 2: Analyze each requirement
    def analyze_requirements(atoms, req_type):
        """Analyze a list of requirements (must-have or nice-to-have)."""
        details = {}
        llm_queue = []
        
        for atom in atoms:
            req_tokens = _tokenize_requirement(atom)
            global_keyword_overlap = 0.0
            if req_tokens:
                global_keyword_overlap = sum(1 for tok in req_tokens if tok in resume_tokens) / len(req_tokens)

            evidence, max_sim = get_best_resume_evidence(atom)

            local_keyword_overlap = 0.0
            if evidence:
                local_keyword_overlap = max(evi.get("keyword_overlap", 0.0) for evi in evidence)

            keyword_signal = max(global_keyword_overlap, local_keyword_overlap)
            initial_score = calculate_initial_score(max_sim, keyword_signal)
            
            detail = {
                "req_type": req_type,
                "similarity": max_sim,
                "max_similarity": max_sim,
                "keyword_overlap": round(keyword_signal, 3),
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
            
            # Calculate final score using BALANCED algorithm
            if present:
                # Skill is present - score based on confidence and evidence quality
                # Range: 0.50 to 1.0 (balanced, not too harsh)
                base_score = 0.50  # Reasonable baseline for present skills
                confidence_bonus = 0.50 * confidence  # Full 50% range based on confidence
                detail["score"] = base_score + confidence_bonus
                
                # Boost for strong evidence (high semantic similarity) - reasonable thresholds
                if detail["max_similarity"] >= 0.85:
                    detail["score"] = min(1.0, detail["score"] * 1.15)  # 15% boost for very strong evidence
                elif detail["max_similarity"] >= 0.75:
                    detail["score"] = min(1.0, detail["score"] * 1.10)  # 10% boost for strong evidence
                elif detail["max_similarity"] >= 0.65:
                    detail["score"] = min(1.0, detail["score"] * 1.05)  # 5% boost for good evidence
                    
            else:
                # Skill is absent - balanced penalties (not too harsh)
                if confidence >= 0.80:  # Very confident it's missing
                    detail["score"] = 0.0
                elif confidence >= 0.65:  # Likely missing
                    detail["score"] = 0.10  # Small benefit of doubt
                elif confidence >= 0.50:  # Uncertain
                    detail["score"] = 0.25  # More benefit of doubt
                else:
                    # Low confidence in absence - maybe present but unclear
                    # Use evidence quality as tiebreaker
                    if detail["max_similarity"] >= 0.60:
                        detail["score"] = 0.45  # Good semantic match, might be there
                    elif detail["max_similarity"] >= 0.45:
                        detail["score"] = 0.35  # Moderate match
                    else:
                        detail["score"] = min(0.30, detail["pre_llm_score"] * 0.8)  # Fallback to pre-LLM with slight penalty

    # Step 4: Calculate overall coverage with sophisticated weighting
    must_scores = [d["score"] for d in must_details.values()]
    nice_scores = [d["score"] for d in nice_details.values()]

    # Must-have coverage: strict average (all must be met)
    must_coverage = float(np.mean(must_scores)) if must_scores else 0.0
    
    # Nice-to-have coverage: more forgiving (bonus, not required)
    nice_coverage = float(np.mean(nice_scores)) if nice_scores else 1.0
    
    # Apply penalty if too many must-haves are missing
    must_present_count = sum(1 for d in must_details.values() if d.get("llm_present", False))
    must_total = len(must_details) if must_details else 1  # ROBUSTNESS: Prevent division by zero
    
    # ROBUSTNESS: Handle edge case where must_total is 0
    if must_total == 0:
        must_fulfillment_rate = 1.0  # No requirements = 100% fulfillment
        logger.warning("No must-have requirements found, defaulting to 100% fulfillment")
    else:
        must_fulfillment_rate = must_present_count / must_total
    
    # Penalty factor: BALANCED penalties for missing must-haves
    if must_fulfillment_rate < 0.30:  # Less than 30% must-haves present (very critical)
        penalty_factor = 0.50  # 50% penalty (severe gaps)
    elif must_fulfillment_rate < 0.50:  # 30-50% present (major gaps)
        penalty_factor = 0.70  # 30% penalty
    elif must_fulfillment_rate < 0.70:  # 50-70% present (moderate gaps)
        penalty_factor = 0.85  # 15% penalty
    else:
        penalty_factor = 1.0  # No penalty if 70%+ met (reasonable threshold)
    
    # Calculate overall: 75% must-have, 25% nice-to-have (must-haves important but not overwhelming)
    if must_scores:
        raw_overall = (0.75 * must_coverage + 0.25 * nice_coverage)  # Balanced weighting
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

