from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF
import spacy
import json
from sentence_transformers import SentenceTransformer
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables and initialize components
load_dotenv()
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = mongo_client["resume_db"]
resumes_collection = db["resumes"]

app = FastAPI(title="Smart Resume Screener API", include_in_schema=False)

# Parsing function
def parse_resume(file_path: str):
    # Extract raw text
    if file_path.endswith('.pdf'):
        doc = fitz.open(file_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
    else:  # Assume text file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    
    # NLP-based extraction with spaCy
    doc = nlp(text)
    skills = set(ent.text for ent in doc.ents if ent.label_ in ["SKILL", "PRODUCT"])
    experience = [
        {"role": ent.text, "duration": " ".join(e.text for e in doc.ents if e.label_ == "DATE")}
        for ent in doc.ents if ent.label_ == "ORG"
    ]
    education = [
        {"institution": ent.text, "year": " ".join(e.text for e in doc.ents if e.label_ == "DATE")}
        for ent in doc.ents if ent.label_ == "ORG" and any(kw in text.lower() for kw in ["university", "college"])
    ]
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Unknown")
    
    # Embeddings for RAG
    combined_text = " ".join(skills) + " " + " ".join(exp["role"] for exp in experience) + " " + " ".join(edu["institution"] for edu in education)
    embeddings = embedder.encode(combined_text)
    
    # Structure output
    extracted_data = {
        "name": name,
        "skills": list(skills),
        "experience": experience,
        "education": education,
        "embeddings": embeddings.tolist()  # Convert to list for MongoDB
    }
    
    # Store in MongoDB
    resumes_collection.insert_one({"file": os.path.basename(file_path), "data": extracted_data})
    
    return extracted_data

# API endpoint for uploading resumes
@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join("resumes", file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    result = parse_resume(file_path)
    return {"filename": file.filename, "extracted_data": result}
