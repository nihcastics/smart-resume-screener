"""
Text Processing and NLP Utilities
ENTERPRISE-GRADE: Input validation, security hardening, resource limits
"""
import re
import numpy as np
import faiss
import logging
from typing import Any
from collections import Counter

# Configure logging
logger = logging.getLogger(__name__)

# SECURITY: Define limits to prevent resource exhaustion
MAX_TEXT_LENGTH = 100000  # 100KB max for NLP processing
MAX_CHUNK_COUNT = 200  # Maximum number of chunks to generate
MAX_REGEX_INPUT = 50000  # Max text length for regex operations (prevent ReDoS)

def normalize_text(s):
    s = s.lower().strip()
    s = re.sub(r'\s+', ' ', s)
    return s


def chunk_text(t, max_chars=1200, overlap=150, nlp=None):
    """
    Chunk text with ROBUSTNESS: input validation, size limits, error handling.
    """
    # ROBUSTNESS: Validate inputs
    if not t or not isinstance(t, str):
        logger.warning("Invalid input to chunk_text")
        return []
    
    # SECURITY: Limit input size
    if len(t) > MAX_TEXT_LENGTH:
        logger.warning(f"Text too long ({len(t)} chars), truncating to {MAX_TEXT_LENGTH}")
        t = t[:MAX_TEXT_LENGTH]
    
    t = re.sub(r'\n{3,}', '\n\n', t).strip()
    
    if nlp is None:
        logger.warning("NLP model not provided, using basic chunking")
        # Fallback: simple character-based chunking
        chunks = []
        for i in range(0, len(t), max_chars - overlap):
            chunk = t[i:i + max_chars]
            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks[:MAX_CHUNK_COUNT]  # SECURITY: Limit chunk count
    
    try:
        if "sentencizer" not in nlp.pipe_names:
            try:
                nlp.add_pipe("sentencizer")
            except:
                pass
        
        doc = nlp(t)
        sents = [s.text.strip() for s in getattr(doc, "sents", []) if s.text.strip()]
    except Exception as e:
        logger.error(f"NLP processing failed: {e}, falling back to basic chunking")
        # Fallback to simple chunking
        chunks = []
        for i in range(0, len(t), max_chars - overlap):
            chunk = t[i:i + max_chars]
            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks[:MAX_CHUNK_COUNT]
    
    chunks, buf = [], ""
    for s in sents:
        if len(buf) + len(s) + 1 <= max_chars:
            buf = (buf + " " + s).strip()
        else:
            if buf: 
                chunks.append(buf)
            if len(chunks) >= MAX_CHUNK_COUNT:  # SECURITY: Limit chunk count
                logger.warning(f"Reached maximum chunk limit ({MAX_CHUNK_COUNT})")
                break
            if overlap > 0 and len(buf) > overlap:
                buf = buf[-overlap:] + " " + s
            else:
                buf = s
    if buf and len(chunks) < MAX_CHUNK_COUNT: 
        chunks.append(buf)
    
    return chunks[:MAX_CHUNK_COUNT]  # SECURITY: Enforce limit


def parse_contacts(txt):
    """
    Extract contact information from text with SECURITY hardening against ReDoS.
    Returns dict with name, email, phone fields.
    """
    # SECURITY: Limit input size to prevent ReDoS attacks
    if len(txt) > MAX_REGEX_INPUT:
        logger.warning(f"Text too long ({len(txt)} chars) for regex, truncating to {MAX_REGEX_INPUT}")
        txt = txt[:MAX_REGEX_INPUT]
    
    # SECURITY: Use simpler, safer regex patterns
    try:
        # Extract email
        emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', txt, re.IGNORECASE)
        # Extract phone
        phones = re.findall(r'(\+?\d[\d\s().-]{8,}\d)', txt)
        # Extract name (try to find capitalized name patterns near top of document)
        names = re.findall(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', txt[:500], re.MULTILINE)
    except Exception as e:
        logger.error(f"Contact extraction failed: {e}")
        return {
            'name': 'Unknown',
            'email': 'Not found',
            'phone': 'Not found'
        }
    
    return {
        'name': names[0] if names else 'Unknown',
        'email': emails[0] if emails else 'Not found',
        'phone': phones[0] if phones else 'Not found'
    }


def build_index(embedder, chunks):
    embs = embedder.encode(chunks, batch_size=32, convert_to_numpy=True, normalize_embeddings=True)
    dim = embs.shape[1]
    idx = faiss.IndexFlatIP(dim)
    # Convert to float32 numpy array for FAISS (pyright signature is inaccurate)
    embs_float32 = np.asarray(embs, dtype=np.float32)
    add_fn: Any = getattr(idx, "add")
    add_fn(embs_float32)
    return idx, embs


def extract_sections(text):
    """Heuristic section splitter (no lexicons)."""
    lines = [l.strip() for l in text.splitlines()]
    blocks, cur, cur_title = [], [], "header"
    for l in lines:
        if re.match(r'^[A-Z][A-Za-z ]{1,40}:$|^[A-Z][A-Za-z &/]{1,50}$', l) and len(l.split())<=8:
            if cur:
                blocks.append((cur_title, "\n".join(cur).strip()))
                cur = []
            cur_title = l.strip(':').lower()
        else:
            cur.append(l)
    if cur:
        blocks.append((cur_title, "\n".join(cur).strip()))
    # fallback single block
    if not blocks:
        blocks = [("content", text)]
    return blocks


def token_set(text):
    return set(re.findall(r'[a-z0-9][a-z0-9+.#-]*', normalize_text(text)))


def contains_atom(atom, text_tokens, full_text=""):
    """
    Robust detection with multiple strategies:
    1. Exact match in full text (case-insensitive)
    2. All tokens present (subset matching)
    3. Fuzzy match for compound terms (60% threshold)
    4. Common abbreviations and variations
    """
    a = normalize_text(atom)
    if len(a) < 2: return False
    
    # Strategy 1: Exact substring match in full text
    if full_text:
        normalized_full = normalize_text(full_text)
        if a in normalized_full:
            return True
    
    # Strategy 2: Extract requirement tokens
    a_tok = set(re.findall(r'[a-z0-9][a-z0-9+.#-]*', a))
    if not a_tok: return False
    
    # Strategy 3: All tokens present (strict match)
    if a_tok.issubset(text_tokens):
        return True
    
    # Strategy 4: Fuzzy match for compound terms (lowered to 60% for better recall)
    if len(a_tok) > 1:
        matched = sum(1 for t in a_tok if t in text_tokens)
        match_ratio = matched / len(a_tok)
        if match_ratio >= 0.6:  # 60% threshold
            return True
    
    # Strategy 5: Common tech abbreviations and variations
    # e.g., "ai" matches "artificial intelligence", "ml" matches "machine learning"
    tech_expansions = {
        'ai': ['artificial', 'intelligence'],
        'ml': ['machine', 'learning'],
        'dl': ['deep', 'learning'],
        'nlp': ['natural', 'language', 'processing'],
        'cv': ['computer', 'vision'],
        'db': ['database'],
        'api': ['application', 'programming', 'interface'],
        'ci': ['continuous', 'integration'],
        'cd': ['continuous', 'deployment'],
        'devops': ['development', 'operations'],
        'aws': ['amazon', 'web', 'services'],
        'gcp': ['google', 'cloud', 'platform'],
        'k8s': ['kubernetes'],
    }
    
    for token in a_tok:
        if token in tech_expansions:
            expansion_words = tech_expansions[token]
            if any(word in text_tokens for word in expansion_words):
                return True
    
    return False


def extract_atoms_from_text(text, nlp, max_atoms=60):
    """Dynamic atom candidates from JD (no lexicons): noun-chunks + list parsing + compact phrases."""
    text = text.strip()
    doc = nlp(text)
    cands = []
    
    # Extract noun chunks (parser is required and verified at startup)
    for nc in doc.noun_chunks:
        s = normalize_text(nc.text)
        if 2 <= len(s) <= 50: cands.append(s)

    for seg in re.split(r'[\n]', text):
        parts = re.split(r'[|/•;,:()]', seg)
        for p in parts:
            p = normalize_text(p.strip(" -/•|,;:"))
            if 2 <= len(p) <= 50 and len(p.split()) <= 5:
                cands.append(p)

    pattern = re.compile(r'[a-z0-9][a-z0-9+.#-]*(?:\s+[a-z0-9][a-z0-9+.#-]*){0,4}')
    for m in pattern.finditer(normalize_text(text)):
        s = m.group(0).strip()
        if 2 <= len(s) <= 50:
            cands.append(s)

    # STRICT filtering: Remove all useless/generic words and phrases
    generic = ATOM_GENERIC_TOKENS
    blocked_phrases = ATOM_BLOCK_PHRASES

    filtered = []
    for c in cands:
        if not c:
            continue
        if any(phrase in c for phrase in blocked_phrases):
            continue
        tokens = c.split()
        meaningful = [t for t in tokens if t not in generic]
        if not meaningful:
            continue
        if len(meaningful) == 1 and meaningful[0] in ATOM_WEAK_SINGLE:
            continue
        if tokens and tokens[0] in ATOM_LEADING_ADJECTIVES:
            continue
        filtered.append(c)
    
    freq = Counter(filtered)
    scored = []
    for k,v in freq.items():
        tokens = k.split()
        boost = 1.15 if 1 <= len(tokens) <= 3 else 1.0
        scored.append((v*boost, -len(k), k))
    scored.sort(reverse=True)
    dedup, seen = [], set()
    for _,__,k in scored:
        if k not in seen:
            seen.add(k); dedup.append(k)
        if len(dedup) >= max_atoms: break
    return dedup

# --- ULTRA-STRICT ATOM VALIDATION FILTERS ---
# These lists have been expanded and optimized to eliminate ALL gibberish

ATOM_GENERIC_TOKENS = set([
    # Experience/skill descriptors (CRITICAL - must be very inclusive)
    "experience","experiences","experienced","skill","skills","skilled","tools","tool","technologies",
    "technology","knowledge","knowledgeable","projects","project","responsibilities","responsibility",
    "requirements","requirement","required","prefer","preferred","preferably","requirements",
    # Job roles (too generic - EXPANDED)
    "engineer","engineering","developer","development","analyst","analysis","internship","intern",
    "fresher","graduate","undergraduate","candidate","candidates","professional","professionals",
    "programmer","programming","designer","designing","architect","architecting","lead","leader",
    "manager","management","supervisor","associate","junior","senior","executive","director",
    # Qualifiers (STRICT - added more)
    "strong","stronger","strongest","good","better","best","excellent","exceptional","outstanding",
    "ability","abilities","able","capable","proficient","proficiency","competent","competency",
    "familiar","familiarity","comfortable","understanding","understands","comprehension",
    "adequate","adequate","sufficient","necessary","basic","fundamental","keen","expert","novice",
    # Action verbs (COMPREHENSIVE)
    "work","working","worked","team","teams","teaming","communication","communicate","communicating",
    "problem","problems","solving","solve","solved","teamwork","leadership","lead","leading",
    "management","manage","managing","managed","collaborate","collaboration","collaborating",
    "develop","developing","developed","design","designing","designed","build","building","built",
    "create","creating","created","implement","implementing","implemented","maintain","maintaining",
    "support","supporting","supported","help","helping","helped","assist","assisting","assisted",
    "drive","driving","driven","track","tracking","tracked","monitor","monitoring","monitored",
    "report","reporting","reported","analyze","analyzing","analyzed","analyse","analysing","analysed",
    "evaluate","evaluating","evaluated","assess","assessing","assessed","review","reviewing","reviewed",
    "test","testing","tested","ensure","ensuring","ensured","provide","providing","provided",
    "handle","handling","manage","manage","coordinate","use","using","apply","applying","handle",
    # Generic concepts (EXPANDED - more noise terms)
    "nice","have","having","foundation","foundations","basics","basic","understanding","concept",
    "concepts","process","processes","practice","practices","methodology","methodologies","principles",
    "principle","background","backgrounds","exposure","working","knowledge","competency","competencies",
    "capability","capabilities","qualification","qualifications","plus","bonus","ideal","ideally",
    "requirement","requirement","desirable","useful","helpful","important","need","needs","necessary",
    # Time/measurement (STRICT isolation)
    "year","years","month","months","level","levels","degree","minimum","maximum","at","least",
    "circa","period","duration","time","date","range","window","around","approximately",
    # Connectors/prepositions (EXTENSIVE - all noise)
    "with","without","using","use","used","via","through","across","within","including","such","like",
    "related","relevant","appropriate","suitable","equivalent","similar","other","others","various",
    "multiple","several","any","all","some","both","either","neither","each","every","general",
    "and","or","but","nor","yet","so","in","on","at","by","to","from","for","during","before","after",
    "as","of","into","out","up","down","over","under","above","below","between","among","about",
    # Weak descriptors
    "thing","things","stuff","etc","etc","otherwise","example","examples","illustration",
    "instance","including","component","element","aspect","feature","characteristic","trait",
    # Negations/exclusions
    "not","no","neither","non","un","im","ir","dis","de"
])

ATOM_BLOCK_PHRASES = {
    # Soft skill phrases - EXHAUSTIVE
    "nice to have","nice-to-have","nice to know","good to have","good-to-have","would be nice",
    "good knowledge","strong knowledge","strong foundation","solid foundation","deep understanding",
    "computer foundations","computer foundation","soft skills","strong communication","interpersonal skills",
    "good communication","excellent communication","communication skills","problem solving skills",
    "problem-solving skills","analytical skills","critical thinking","attention to detail",
    "leadership skills","teamwork skills","collaborative","collaboration","team player",
    # Generic requirement phrases - EXHAUSTIVE
    "experience with","experience in","knowledge of","understanding of","familiarity with",
    "exposure to","working knowledge","hands-on experience","practical experience","proven experience",
    "ability to","able to","capable of","proficiency in","proficient in","competency in","skilled in",
    "expertise in","background in","track record","demonstrated ability","strong understanding",
    "some experience","basic knowledge","fundamental understanding","working familiarity",
    # Job responsibilities (not skills) - EXPANDED
    "responsible for","work with","collaborate with","partner with","interact with","communicate with",
    "develop and","design and","build and","create and","implement and","maintain and","support and",
    "work closely","team environment","fast-paced environment","dynamic environment","agile environment",
    "must be able to","should be able to","required to","expected to","responsible to",
    # Vague qualifiers - EXHAUSTIVE
    "preferred qualifications","nice to haves","bonus points","plus points","additional skills",
    "good understanding","solid grasp","thorough understanding","comprehensive knowledge",
    "general knowledge","basic understanding","foundational knowledge","core concepts",
    "advanced understanding","deep knowledge","extensive experience","broad background",
    # More generic phrases
    "familiar with","basic familiarity","general familiarity","some knowledge of",
    "working in","working on","experience in","background in","training in",
    "introduction to","exposure to","introduction","familiarity","minimum knowledge",
    "basic skill","intermediate skill","advanced skill","expert level","mastery of",
    "can demonstrate","able to demonstrate","proven ability to show",
    "will be required","is required","must have","should have","nice to have",
    "highly desirable","would be beneficial","helpful to have","beneficial to have",
    "key skill","key competency","core skill","primary skill","secondary skill",
    "important role","critical role","essential role","important function"
}

ATOM_WEAK_SINGLE = {
    # EXPANDED - ALL single weak tokens
    "foundation","foundations","knowledge","understanding","experience","skill","skills","skillset",
    "competency","competencies","capability","capabilities","background","exposure","proficiency",
    "familiarity","expertise","qualification","qualifications","certification","certifications",
    "training","education","degree","masters","bachelor","phd","diploma","course","courses",
    "tool","tools","technology","technologies","technique","techniques","method","methods",
    "ability","abilities","trait","traits","characteristic","characteristics","competency",
    "requirement","requirements","specification","specifications","attribute","attributes",
    "strength","strengths","weakness","weaknesses","advantage","disadvantages",
    "area","areas","domain","domains","field","fields","practice","practices",
    "role","roles","position","positions","level","levels","tier","tiers",
    "type","types","category","categories","class","classes","group","groups",
    "aspect","aspects","element","elements","component","components","feature","features",
    "skill","skills","duty","duties","function","functions","responsibility","responsibilities",
    "item","items","thing","things","stuff","matter","matters","subject","subjects"
}

ATOM_LEADING_ADJECTIVES = {
    # EXPANDED - ALL qualifying adjectives
    "strong","good","excellent","basic","advanced","intermediate","solid","sound","robust",
    "deep","thorough","comprehensive","extensive","broad","general","specific","detailed",
    "proven","demonstrated","hands-on","practical","theoretical","applied","relevant","appropriate",
    "preferred","ideal","perfect","optimal","suitable","fit","fitting","appropriate",
    "better","best","superior","inferior","poor","weak","weak","strong","powerful",
    "fundamental","core","central","primary","secondary","main","major","minor",
    "essential","critical","crucial","vital","important","necessary","optional","required",
    "new","old","modern","legacy","recent","current","latest","outdated",
    "simple","complex","complicated","easy","difficult","hard","straightforward",
    "effective","efficient","productive","reliable","stable","consistent",
    "relevant","irrelevant","applicable","inapplicable","suitable","unsuitable"
}


def _detect_gibberish(s: str) -> bool:
    """
    Multi-pass gibberish detector.
    Returns True if atom is gibberish, False if it's likely valid.
    """
    # Too short
    if len(s) < 2:
        return True
    
    # All numbers or special chars
    if not any(c.isalpha() for c in s):
        return True
    
    # Single letter repeated
    if len(set(s.replace(" ", ""))) <= 2:
        return True
    
    # Too many special chars
    special_count = sum(1 for c in s if not c.isalnum() and c != " ")
    if special_count > len(s) * 0.5:
        return True
    
    # Repeated words (noise like "and and")
    words = s.split()
    if len(words) > 1 and words[0] == words[-1]:
        return True
    
    return False


def _tokenize_atom(atom: str):
    return re.findall(r"[a-z0-9][a-z0-9+.#-]*", normalize_text(atom))


def _is_valid_atom(atom: str):
    """
    Balanced validation: Filter gibberish while preserving valid technical terms.
    Uses pattern matching and heuristics instead of hardcoded lists.
    """
    s = normalize_text(atom)
    
    # ===== BASIC SANITY CHECKS =====
    if len(s) < 2 or len(s) > 60:
        return False
    if _detect_gibberish(s):
        return False
    if any(phrase in s for phrase in ATOM_BLOCK_PHRASES):
        return False
    
    tokens = _tokenize_atom(s)
    if not tokens:
        return False
    
    # ===== MEANINGFUL TOKEN CHECK =====
    meaningful = [t for t in tokens if t not in ATOM_GENERIC_TOKENS]
    
    # Must have at least one non-generic token
    if not meaningful:
        return False
    
    # ===== TECHNICAL HEURISTICS (pattern-based, not list-based) =====
    
    # Single token validation
    if len(meaningful) == 1:
        token = meaningful[0]
        
        # Reject if in weak list
        if token in ATOM_WEAK_SINGLE:
            return False
        
        # Accept if has technical indicators (numbers, caps, common patterns)
        # Examples: python3, AWS, k8s, C++, .NET, Node.js
        if any([
            any(c.isdigit() for c in token),  # Has numbers (python3, angular17, java11)
            any(c.isupper() for c in atom),  # Has uppercase (AWS, GCP, REST, API, SQL)
            '+' in atom or '#' in atom or '.' in atom,  # C++, C#, Node.js
            token.endswith('js') or token.endswith('sql'),  # JavaScript, MySQL
            token in {'api', 'rest', 'graphql', 'sql', 'nosql', 'oop', 'tdd', 'ci', 'cd', 'ml', 'ai', 'nlp'},
            len(token) <= 4 and token.isalpha(),  # Short acronyms (AWS, GCP, git, npm)
        ]):
            return True
        
        # Accept if matches common tech patterns
        tech_patterns = [
            r'.*script$',  # JavaScript, TypeScript
            r'.*sql$',     # MySQL, PostgreSQL
            r'.*db$',      # MongoDB, DynamoDB
            r'.*py$',      # NumPy, SciPy
            r'^[a-z]+\d+$',  # python3, java11, react18
        ]
        if any(re.match(pattern, token) for pattern in tech_patterns):
            return True
        
        # Reject single generic tokens (unless matched above)
        return False
    
    # ===== MULTI-TOKEN VALIDATION =====
    # Multiple meaningful tokens - more lenient (likely compound skills)
    
    # For multi-token phrases, check if they're meaningful compound skills
    # Examples: "react native", "machine learning", "rest api", "data structures"
    
    # Accept if has experience/year qualifiers (e.g., "5+ years python")
    if any(re.search(r'\d+\s*(year|yr|month|mo)', s) for s in [atom, s]):
        return True
    
    # Accept if has technical suffixes/prefixes
    technical_patterns = [
        r'.*script$',      # javascript, typescript
        r'.*sql$',         # mysql, postgresql
        r'.*db$',          # mongodb, dynamodb  
        r'.*py$',          # numpy, scipy
        r'.*js$',          # reactjs, vuejs, nodejs
        r'.*\.net$',       # asp.net
        r'^micro.*',       # microservices
        r'^web.*',         # web development, websocket
        r'^data.*',        # data science, data structures
        r'^full.*stack$',  # full stack
        r'^front.*end$',   # front end
        r'^back.*end$',    # back end
    ]
    
    if any(re.match(pattern, s, re.IGNORECASE) for pattern in technical_patterns):
        return True
    
    # Accept if contains numbers (version numbers, year requirements)
    if any(c.isdigit() for c in s):
        return True
    
    # Accept if contains uppercase in original (AWS, REST, SQL, API, CI/CD)
    if any(c.isupper() for c in atom):
        return True
    
    # Accept if contains special chars indicating tech (C++, C#, .NET)
    if any(char in atom for char in ['+', '#', '.']):
        return True
    
    # Accept compound phrases with 2-4 meaningful tokens
    # These are likely legitimate compound skills
    if 2 <= len(meaningful) <= 4:
        # Reject if too many adjectives
        adj_count = sum(1 for t in tokens if t in ATOM_LEADING_ADJECTIVES)
        if adj_count / max(len(tokens), 1) > 0.5:
            return False
        return True
    
    # Accept single meaningful tokens that are short (likely acronyms)
    if len(meaningful) == 1 and len(meaningful[0]) <= 5:
        return True
    
    return True  # Default to accepting if passed all filters above


def _canonical_atom(atom: str, nlp=None):
    """
    Create canonical form for deduplication, merging abbreviations with full forms.
    Examples: 'OS' and 'Operating Systems' → same canonical
    """
    s = normalize_text(atom)
    if not s:
        return ""
    
    # Common tech abbreviation mappings (for deduplication)
    abbreviation_map = {
        # CS Fundamentals
        'os': 'operating system',
        'operating systems': 'operating system',
        'dbms': 'database management system',
        'database management systems': 'database management system',
        'cn': 'computer network',
        'computer networks': 'computer network',
        'ds': 'data structure',
        'data structures': 'data structure',
        'algo': 'algorithm',
        'algorithms': 'algorithm',
        'oop': 'object oriented programming',
        'oops': 'object oriented programming',
        'object oriented': 'object oriented programming',
        
        # Cloud & DevOps
        'aws': 'amazon web services',
        'amazon web services': 'amazon web services',
        'gcp': 'google cloud platform',
        'google cloud': 'google cloud platform',
        'k8s': 'kubernetes',
        'ci cd': 'continuous integration',
        'ci/cd': 'continuous integration',
        
        # Databases
        'postgres': 'postgresql',
        'postgresql': 'postgresql',
        'mongo': 'mongodb',
        'mongodb': 'mongodb',
        
        # Languages
        'js': 'javascript',
        'javascript': 'javascript',
        'ts': 'typescript',
        'typescript': 'typescript',
        'py': 'python',
        
        # Frameworks
        'reactjs': 'react',
        'react.js': 'react',
        'nodejs': 'node',
        'node.js': 'node',
        'vuejs': 'vue',
        'vue.js': 'vue',
        
        # APIs
        'rest api': 'rest',
        'restful': 'rest',
        'rest apis': 'rest',
        'graphql api': 'graphql',
        
        # ML/AI
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'nlp': 'natural language processing',
        'cv': 'computer vision',
    }
    
    # Check if atom maps to a canonical form
    if s in abbreviation_map:
        return abbreviation_map[s]
    
    # Use NLP lemmatization for other terms
    if nlp is not None:
        try:
            doc = nlp(s)
            lemmas = [t.lemma_.lower() for t in doc if re.match(r"[a-z0-9][a-z0-9+.#-]*", t.lemma_.lower())]
            canned = " ".join(lemmas)
            if canned and canned in abbreviation_map:
                return abbreviation_map[canned]
            if canned:
                return canned
        except Exception:
            pass
    
    tokens = _tokenize_atom(s)
    canonical = " ".join(tokens)
    
    # Final check if tokenized form maps to canonical
    if canonical in abbreviation_map:
        return abbreviation_map[canonical]
    
    return canonical


def refine_atom_list(atoms, nlp=None, reserved_canonicals=None, limit=50):
    """
    Refine and deduplicate atoms while preserving ALL valid requirements.
    Increased limit to avoid losing requirements.
    """
    reserved = set(reserved_canonicals or [])
    best = {}
    order = []
    for idx, atom in enumerate(atoms):
        if not isinstance(atom, str):
            continue
        atom = normalize_text(atom)
        if not _is_valid_atom(atom):
            continue
        canonical = _canonical_atom(atom, nlp)
        if not canonical or canonical in reserved:
            continue
        current = best.get(canonical)
        if current is None:
            best[canonical] = {"value": atom, "index": idx}
            order.append(canonical)
        elif len(atom) < len(current["value"]):
            current["value"] = atom
    refined = [best[key]["value"] for key in order[:limit]]
    reserved.update(order[:limit])
    return refined, reserved


def extract_structured_entities(text, nlp):
    """
    Extract structured entities from resume using spaCy NER and custom patterns.
    Returns: dict with organizations, dates, skills, education, certifications
    """
    doc = nlp(text[:5000])  # Limit to first 5000 chars for efficiency
    
    entities = {
        "organizations": [],
        "dates": [],
        "skills": [],
        "education": [],
        "certifications": [],
        "technologies": []
    }
    
    # Extract named entities
    for ent in doc.ents:
        if ent.label_ == "ORG":
            org = ent.text.strip()
            if len(org) > 2 and org not in entities["organizations"]:
                entities["organizations"].append(org)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text.strip())
    
    # Extract education patterns
    education_patterns = [
        r'\b(bachelor|master|phd|doctorate|b\.?s\.?|m\.?s\.?|m\.?tech|b\.?tech|mba|ph\.?d\.?)\b.*?(?:in|of)\s+([a-z\s]+)',
        r'\b(undergraduate|graduate)\s+(?:degree|program)\s+in\s+([a-z\s]+)',
    ]
    for pattern in education_patterns:
        for match in re.finditer(pattern, text.lower()):
            degree = match.group(0).strip()
            if degree and len(degree) < 100:
                entities["education"].append(degree)
    
    # Extract certification patterns
    cert_keywords = ['certified', 'certification', 'certificate', 'credential']
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in cert_keywords):
            cert = line.strip()
            if 10 < len(cert) < 150:
                entities["certifications"].append(cert)
    
    # Extract technology mentions using dependency parsing
    tech_patterns = [
        r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|kotlin|swift|scala)\b',
        r'\b(react|angular|vue|node\.?js|django|flask|spring|express)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|jenkins|terraform|ansible)\b',
        r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch|cassandra)\b',
        r'\b(machine learning|deep learning|nlp|computer vision|ai|ml|dl)\b',
        r'\b(git|github|gitlab|bitbucket|jira|confluence)\b'
    ]
    
    for pattern in tech_patterns:
        for match in re.finditer(pattern, text.lower()):
            tech = match.group(0).strip()
            if tech and tech not in entities["technologies"]:
                entities["technologies"].append(tech)
    
    # Limit results
    entities["organizations"] = entities["organizations"][:15]
    entities["education"] = list(set(entities["education"]))[:5]
    entities["certifications"] = list(set(entities["certifications"]))[:10]
    entities["technologies"] = list(set(entities["technologies"]))[:30]
    
    return entities


def extract_technical_skills(text, nlp):
    """
    ROBUST technical skills extraction using multi-strategy approach.
    Extracts programming languages, frameworks, tools, databases, cloud platforms, etc.
    Returns: list of unique technical skills
    """
    if not text:
        return []
    
    skills = set()
    text_lower = text.lower()
    
    # ===== STRATEGY 1: COMPREHENSIVE KEYWORD MATCHING =====
    # This is the most reliable method - match known technical keywords
    
    technical_keywords = {
        # Programming Languages (EXHAUSTIVE)
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'golang',
        'rust', 'kotlin', 'swift', 'scala', 'php', 'perl', 'r', 'matlab', 'julia',
        'c', 'objective-c', 'dart', 'elixir', 'haskell', 'lua', 'groovy', 'shell', 'bash',
        
        # Frontend Frameworks & Libraries
        'react', 'reactjs', 'react.js', 'angular', 'vue', 'vuejs', 'vue.js', 'svelte',
        'ember', 'backbone', 'jquery', 'bootstrap', 'tailwind', 'material-ui', 'mui',
        'next', 'nextjs', 'next.js', 'nuxt', 'gatsby', 'redux', 'mobx', 'recoil',
        'webpack', 'vite', 'parcel', 'rollup', 'babel', 'sass', 'scss', 'less',
        
        # Backend Frameworks
        'django', 'flask', 'fastapi', 'express', 'expressjs', 'nest', 'nestjs',
        'spring', 'spring boot', 'struts', 'hibernate', 'laravel', 'symfony',
        'rails', 'ruby on rails', 'sinatra', 'asp.net', '.net', 'dotnet',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'mongo', 'redis',
        'cassandra', 'dynamodb', 'elasticsearch', 'oracle', 'sql server', 'mssql',
        'sqlite', 'mariadb', 'couchdb', 'neo4j', 'influxdb', 'firebase', 'firestore',
        
        # Cloud Platforms & Services
        'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud',
        'google cloud platform', 'ec2', 's3', 'lambda', 'cloudfront', 'rds', 'dynamodb',
        'ecs', 'eks', 'fargate', 'sagemaker', 'cloudwatch', 'iam',
        'azure functions', 'azure devops', 'app service', 'blob storage',
        'compute engine', 'app engine', 'cloud functions', 'bigquery', 'pub/sub',
        'heroku', 'digitalocean', 'linode', 'vercel', 'netlify', 'cloudflare',
        
        # DevOps & Tools
        'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab', 'github', 'bitbucket',
        'travis', 'circleci', 'terraform', 'ansible', 'puppet', 'chef', 'vagrant',
        'helm', 'prometheus', 'grafana', 'datadog', 'new relic', 'splunk',
        'ci/cd', 'cicd', 'git', 'svn', 'mercurial', 'jira', 'confluence',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'neural networks', 'nlp', 
        'natural language processing', 'computer vision', 'ai', 'artificial intelligence',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy',
        'scipy', 'matplotlib', 'seaborn', 'plotly', 'jupyter', 'opencv',
        'xgboost', 'lightgbm', 'catboost', 'hugging face', 'transformers',
        'spark', 'pyspark', 'hadoop', 'hive', 'kafka', 'airflow', 'mlflow',
        
        # Mobile Development
        'android', 'ios', 'react native', 'flutter', 'kotlin', 'swift', 'xamarin',
        'ionic', 'cordova', 'phonegap',
        
        # Testing & Quality
        'jest', 'mocha', 'chai', 'jasmine', 'pytest', 'unittest', 'junit', 'testng',
        'selenium', 'cypress', 'playwright', 'puppeteer', 'postman', 'insomnia',
        
        # Architecture & Patterns
        'microservices', 'serverless', 'rest', 'restful', 'rest api', 'graphql',
        'grpc', 'websocket', 'soap', 'mvc', 'mvvm', 'event-driven', 'message queue',
        'rabbitmq', 'activemq', 'zeromq',
        
        # Computer Science Fundamentals
        'data structures', 'algorithms', 'oop', 'object oriented programming',
        'functional programming', 'design patterns', 'system design',
        'operating systems', 'os', 'dbms', 'database management systems',
        'computer networks', 'cn', 'networking',
        
        # Other Technologies
        'linux', 'unix', 'windows', 'macos', 'nginx', 'apache', 'tomcat',
        'elasticsearch', 'solr', 'memcached', 'varnish', 'cdn',
        'oauth', 'jwt', 'saml', 'openid', 'ldap', 'active directory',
    }
    
    # Match technical keywords in text (with word boundaries)
    for keyword in technical_keywords:
        # Use regex with word boundaries for accurate matching
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower, re.IGNORECASE):
            skills.add(keyword)
    
    # ===== STRATEGY 2: VERSION-SPECIFIC PATTERNS =====
    # Match "Python 3.x", "Java 11", "React 18", etc.
    version_patterns = [
        r'\b(python|java|node|react|angular|vue|spring|django|php|ruby|go|rust)\s+\d+(?:\.\d+)*\b',
        r'\b([a-z]+(?:\s+[a-z]+)?)\s+version\s+\d+(?:\.\d+)*\b',
    ]
    
    for pattern in version_patterns:
        for match in re.finditer(pattern, text_lower):
            skill = match.group(0).strip()
            if len(skill) <= 30:
                # Extract base technology name
                base_tech = re.sub(r'\s+\d+.*$', '', skill).strip()
                skills.add(base_tech)  # Add base (e.g., "python")
                skills.add(skill)      # Add version-specific (e.g., "python 3.x")
    
    # ===== STRATEGY 3: SKILLS SECTION PARSING =====
    # Extract from dedicated "Skills" sections
    skills_section_pattern = r'(?:technical\s+)?skills?\s*[:\-]?\s*([^\n]+(?:\n(?!\n)[^\n]+){0,20})'
    
    for match in re.finditer(skills_section_pattern, text_lower):
        section_text = match.group(1)
        # Split by common delimiters
        skill_candidates = re.split(r'[,;•|/\n\t]', section_text)
        
        for candidate in skill_candidates:
            candidate = candidate.strip()
            # Remove common prefixes
            candidate = re.sub(r'^(?:experience\s+(?:with|in)|knowledge\s+of|proficient\s+in|skilled\s+in)\s+', '', candidate)
            candidate = candidate.strip()
            
            # Validate: 2-40 chars, contains alphanumeric
            if 2 <= len(candidate) <= 40 and any(c.isalnum() for c in candidate):
                # Check if it's a known keyword or looks technical
                if (candidate in technical_keywords or
                    any(char in candidate for char in ['+', '#', '.']) or  # C++, C#, .NET
                    any(c.isdigit() for c in candidate) or  # Has version number
                    any(c.isupper() for c in candidate[:min(5, len(candidate))])):  # Starts with caps (AWS, SQL)
                    skills.add(candidate)
    
    # ===== STRATEGY 4: NOUN CHUNK EXTRACTION (NLP) =====
    # Use spaCy to extract technical-looking noun chunks
    if nlp:
        try:
            doc = nlp(text[:6000])  # Limit for performance
            
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                
                # Filter for technical indicators
                if (2 <= len(chunk_text) <= 40 and
                    not chunk_text.startswith(('the ', 'a ', 'an ', 'my ', 'your '))):
                    
                    # Check if contains technical terms
                    tech_indicators = [
                        'system', 'framework', 'library', 'tool', 'platform', 'language',
                        'database', 'service', 'api', 'cloud', 'server', 'network'
                    ]
                    
                    if any(ind in chunk_text for ind in tech_indicators):
                        # Extract the core technical term
                        core = re.sub(r'\b(?:the|a|an|my|your|our|this|that|these|those)\b', '', chunk_text).strip()
                        if core and len(core) >= 2:
                            skills.add(core)
        except Exception as e:
            logger.warning(f"NLP chunk extraction failed: {e}")
    
    # ===== STRATEGY 5: ACRONYM & ABBREVIATION DETECTION =====
    # Find uppercase acronyms (AWS, SQL, REST, API, ML, AI, etc.)
    acronym_pattern = r'\b[A-Z]{2,6}\b'
    for match in re.finditer(acronym_pattern, text):
        acronym = match.group(0)
        acronym_lower = acronym.lower()
        # Check if it's a known technical acronym
        if acronym_lower in technical_keywords or len(acronym) <= 4:
            skills.add(acronym_lower)
    
    # ===== FINAL CLEANUP =====
    # Remove generic noise words
    generic_noise = {
        'experience', 'knowledge', 'skill', 'skills', 'ability', 'working', 'using',
        'with', 'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to',
        'development', 'developer', 'engineer', 'engineering', 'software',
        'tools', 'technologies', 'frameworks', 'languages', 'programming'
    }
    
    cleaned_skills = []
    for skill in skills:
        if skill not in generic_noise and len(skill) >= 2:
            cleaned_skills.append(skill)
    
    # Deduplicate and limit
    unique_skills = list(set(cleaned_skills))
    
    # Sort by length (shorter = more specific, likely tech names)
    unique_skills.sort(key=lambda x: (len(x), x))
    
    logger.info(f"✅ Extracted {len(unique_skills)} technical skills from resume")
    
    return unique_skills[:80]  # Return top 80 skills


def semantic_chunk_text(text, nlp, embedder, max_chars=800, overlap=200):
    """
    Advanced semantic chunking: splits text intelligently using sentence boundaries
    and semantic coherence for better RAG retrieval.
    """
    # First pass: sentence-based splitting
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    # Ensure sentencizer is available
    if "sentencizer" not in nlp.pipe_names:
        try:
            nlp.add_pipe("sentencizer")
        except:
            pass
    
    doc = nlp(text)
    sentences = [s.text.strip() for s in getattr(doc, "sents", []) if s.text.strip()]
    
    if not sentences:
        # Fallback: split by paragraphs
        sentences = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Build chunks with semantic awareness
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sent in sentences:
        sent_length = len(sent)
        
        # If adding this sentence exceeds max_chars, finalize current chunk
        if current_length + sent_length > max_chars and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)
            
            # Keep last few sentences for overlap (semantic continuity)
            if overlap > 0:
                overlap_sents = []
                overlap_len = 0
                for s in reversed(current_chunk):
                    if overlap_len + len(s) <= overlap:
                        overlap_sents.insert(0, s)
                        overlap_len += len(s)
                    else:
                        break
                current_chunk = overlap_sents
                current_length = overlap_len
            else:
                current_chunk = []
                current_length = 0
        
        current_chunk.append(sent)
        current_length += sent_length
    
    # Add final chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    # If no chunks created, return whole text
    if not chunks:
        chunks = [text]
    
    return chunks


def retrieve_relevant_context(query, faiss_index, chunks, embedder, top_k=3):
    """
    RAG: Retrieve most relevant resume chunks for a given query using FAISS.
    Returns: list of (chunk_text, similarity_score) tuples
    """
    if not chunks or faiss_index is None:
        return []
    
    try:
        # Encode query
        query_emb = embedder.encode(query, convert_to_numpy=True, normalize_embeddings=True)
        if query_emb.ndim > 1:
            query_emb = query_emb[0]
        
        # Search FAISS index
        query_emb = query_emb.reshape(1, -1).astype(np.float32)
        similarities, indices = faiss_index.search(query_emb, min(top_k, len(chunks)))
        
        # Build results
        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if 0 <= idx < len(chunks):
                results.append((chunks[idx], float(sim)))
        
        return results
    except Exception:
        return []
