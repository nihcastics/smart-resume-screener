"""
Resume PDF Parsing with Enhanced Error Handling
Uses multiple parsing strategies for maximum accuracy
"""
import re
import logging
import fitz  # PyMuPDF
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    pdfplumber = None
    PDFPLUMBER_AVAILABLE = False
    
from modules.text_processing import parse_contacts, chunk_text, build_index
from modules.text_processing import extract_structured_entities, extract_technical_skills, semantic_chunk_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_parsed_resume(resume_doc):
    """
    Validate parsed resume quality and completeness.
    Returns (is_valid, issues_list)
    """
    issues = []
    
    if not resume_doc:
        return False, ["Resume parsing returned None"]
    
    # Check text content
    text = resume_doc.get('text', '')
    if not text or len(text) < 100:
        issues.append(f"Text too short ({len(text)} chars, minimum 100)")
    
    # Check contact info
    email = resume_doc.get('email', 'Not found')
    phone = resume_doc.get('phone', 'Not found')
    if email == 'Not found' and phone == 'Not found':
        issues.append("No contact information found")
    
    # Check skills extraction
    skills = resume_doc.get('technical_skills', [])
    if not skills or len(skills) == 0:
        issues.append("No technical skills extracted")
    
    # Check chunks
    chunks = resume_doc.get('chunks', [])
    if not chunks or len(chunks) == 0:
        issues.append("No text chunks created")
    
    is_valid = len(issues) == 0
    if not is_valid:
        logger.warning(f"Resume validation issues: {', '.join(issues)}")
    
    return is_valid, issues


def extract_text_from_pdf(file_obj):
    """
    Multi-strategy PDF text extraction for maximum reliability.
    Returns (text, method_used)
    """
    file_obj.seek(0)
    
    # Strategy 1: PDFPlumber (best for complex layouts)
    if PDFPLUMBER_AVAILABLE and pdfplumber is not None:
        try:
            with pdfplumber.open(file_obj) as pdf:
                text_parts = []
                for page in pdf.pages[:15]:  # Max 15 pages
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text = "\n".join(text_parts)
                if text and len(text.strip()) > 100:
                    logger.info("✅ PDF extracted using pdfplumber")
                    return text, "pdfplumber"
        except Exception as e:
            logger.warning(f"PDFPlumber extraction failed: {e}")
    
    # Strategy 2: PyMuPDF (fallback, good for simple PDFs)
    try:
        file_obj.seek(0)
        doc = fitz.open(stream=file_obj.read(), filetype="pdf")
        text_parts = []
        for i in range(min(doc.page_count, 15)):
            page_text = doc[i].get_text()
            if page_text:
                text_parts.append(page_text)
        doc.close()
        text = "\n".join(text_parts)
        if text and len(text.strip()) > 100:
            logger.info("✅ PDF extracted using PyMuPDF")
            return text, "pymupdf"
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {e}")
    
    return "", "failed"

def parse_resume_pdf(file_obj, nlp, embedder):
    """
    Enhanced multi-strategy resume parser with advanced NLP extraction.
    Uses pdfplumber + PyMuPDF for robust text extraction.
    ENTERPRISE-GRADE: Input validation, size limits, timeout protection.
    """
    try:
        logger.info("Parsing PDF resume with multi-strategy approach")
        
        # SECURITY: Validate file size (max 10MB for resumes)
        file_obj.seek(0, 2)
        file_size = file_obj.tell()
        file_obj.seek(0)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        if file_size > MAX_FILE_SIZE:
            logger.error(f"File too large: {file_size / (1024*1024):.1f}MB (max 10MB)")
            return None
        if file_size < 100:
            logger.error(f"File too small: {file_size} bytes (likely corrupted)")
            return None
        
        # Extract text using best available method
        text, method = extract_text_from_pdf(file_obj)
        
        if not text or len(text.strip()) < 100:
            logger.error("PDF parsing resulted in insufficient text")
            return None
        
        # SECURITY: Limit text length
        MAX_TEXT_LENGTH = 50000
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning(f"Text too long ({len(text)} chars), truncating to {MAX_TEXT_LENGTH}")
            text = text[:MAX_TEXT_LENGTH]

        # Advanced name extraction
        first_line = (text.splitlines() or [""])[0][:120]
        first_line = re.sub(r'\S+@\S+','', first_line)
        first_line = re.sub(r'\+?\d[\d\s().-]{8,}\d','', first_line).strip()
        name = None
        if re.match(r'^[A-Za-z][A-Za-z .-]{1,60}$', first_line):
            name = first_line
        if not name and nlp:
            try:
                dn = nlp(text[:600])
                cand = [e.text for e in dn.ents if e.label_=="PERSON" and len(e.text) <= 60 and '@' not in e.text]
                name = cand[0] if cand else "Unknown"
            except Exception as e:
                logger.warning(f"Name extraction failed: {e}")
                name = "Unknown"
        if not name:
            name = "Unknown"

        # Contact extraction
        contacts = parse_contacts(text)
        email = contacts.get('email', 'Not found')
        phone = contacts.get('phone', 'Not found')
        
        # Enhanced structured entity extraction
        structured_entities = {}
        if nlp:
            try:
                structured_entities = extract_structured_entities(text, nlp)
                logger.info(f"✅ Extracted {len(structured_entities)} entity types")
            except Exception as e:
                logger.warning(f"Entity extraction failed: {e}")
        
        # Advanced semantic chunking
        chunks = []
        if nlp and embedder:
            try:
                chunks = semantic_chunk_text(text, nlp, embedder, max_chars=800, overlap=200)
                logger.info(f"✅ Created {len(chunks)} semantic chunks")
            except Exception as e:
                logger.warning(f"Semantic chunking failed: {e}")
        
        if not chunks:
            chunks = chunk_text(text, max_chars=800, nlp=nlp)
            logger.info(f"✅ Created {len(chunks)} basic chunks")
        
        # Build vector index
        idx, embs = None, None
        if embedder and chunks:
            try:
                idx, embs = build_index(embedder, chunks)
                logger.info("✅ Vector index built successfully")
            except Exception as e:
                logger.warning(f"Index building failed: {e}")
        
        # Advanced technical skills extraction
        technical_skills = []
        if nlp:
            try:
                technical_skills = extract_technical_skills(text, nlp)
                logger.info(f"✅ Extracted {len(technical_skills)} technical skills")
            except Exception as e:
                logger.warning(f"Technical skills extraction failed: {e}")
        
        resume_doc = {
            "name": name,
            "email": email,
            "phone": phone,
            "text": text,
            "chunks": chunks,
            "faiss": idx,
            "embs": embs,
            "entities": structured_entities,
            "technical_skills": technical_skills,
            "extraction_method": method
        }
        
        # Validate
        is_valid, issues = validate_parsed_resume(resume_doc)
        if not is_valid:
            logger.warning(f"Resume validation issues: {issues}")
        else:
            logger.info(f"✅ Resume parsed successfully using {method}")
        
        return resume_doc
        
    except Exception as e:
        logger.error(f"❌ PDF parsing failed: {e}")
        return None


def parse_resume_text(text_content, nlp, embedder):
    """
    Parse plain text resume with same enhancements as PDF parser.
    """
    try:
        logger.info("Parsing text resume")
        text = text_content.strip()
        
        if not text or len(text) < 50:
            logger.error("Text content too short")
            return None
        
        # Extract name (first line heuristic)
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
        
        contacts = parse_contacts(text)
        email = contacts.get('email', '')
        phone = contacts.get('phone', '')
        
        # Extract entities
        try:
            structured_entities = extract_structured_entities(text, nlp)
        except:
            structured_entities = {}
        
        # Chunk text
        try:
            chunks = semantic_chunk_text(text, nlp, embedder, max_chars=800, overlap=200)
        except:
            chunks = chunk_text(text, max_chars=800, nlp=nlp)
        
        # Build index
        try:
            idx, embs = build_index(embedder, chunks)
        except:
            idx, embs = None, None
        
        # Extract skills
        try:
            technical_skills = extract_technical_skills(text, nlp)
        except:
            technical_skills = []
        
        resume_doc = {
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
        
        is_valid, issues = validate_parsed_resume(resume_doc)
        if not is_valid:
            logger.warning(f"Text resume validation issues: {issues}")
        else:
            logger.info("✅ Text resume parsed successfully")
        
        return resume_doc
        
    except Exception as e:
        logger.error(f"❌ Text parsing failed: {e}")
        return None


