"""
Resume PDF Parsing
"""
import fitz  # PyMuPDF
from modules.text_processing import parse_contacts, chunk_text

def parse_resume_pdf(path, nlp, embedder):
    """
    Enhanced resume parser with multi-level NLP extraction.
    Extracts structured entities, skills, experience, education using spaCy NER + custom patterns.
    """
    doc = fitz.open(path)
    text = "\n".join([p.get_text() for p in doc])
    doc.close()
    if not text.strip(): return None

    # Name extraction that avoids emails/phones
    first_line = (text.splitlines() or [""])[0][:120]
    first_line = re.sub(r'\S+@\S+','', first_line)
    first_line = re.sub(r'\+?\d[\d\s().-]{8,}\d','', first_line).strip()
    name = None
    if re.match(r'^[A-Za-z][A-Za-z .-]{1,60}$', first_line):
        name = first_line
    if not name:
        try:
            dn = nlp(text[:600])
            cand = [e.text for e in dn.ents if e.label_=="PERSON" and len(e.text) <= 60 and '@' not in e.text]
            name = cand[0] if cand else "Unknown"
        except:
            name = "Unknown"

    email, phone = parse_contacts(text)
    
    # Enhanced: Extract structured entities using spaCy NER
    structured_entities = extract_structured_entities(text, nlp)
    
    # Enhanced: Semantic chunking with better overlap and sentence awareness
    chunks = semantic_chunk_text(text, nlp, embedder, max_chars=800, overlap=200)
    
    # Build vector index for RAG
    idx, embs = build_index(embedder, chunks)
    
    # Enhanced: Extract technical skills with pattern matching
    technical_skills = extract_technical_skills(text, nlp)
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "text": text,
        "chunks": chunks,
        "faiss": idx,
        "embs": embs,
        "entities": structured_entities,
        "technical_skills": technical_skills
    }

# ---- PostgreSQL helpers ----

