import streamlit as st
import fitz  # PyMuPDF
import spacy
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import OpenAI
from fastapi import FastAPI, UploadFile, File
import os
from dotenv import load_dotenv
import json
from typing import List, Dict
import time
import plotly.express as px

# Load environment variables and initialize components
load_dotenv()
nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))
app = FastAPI(title="Smart Resume Screener API")
st.set_page_config(layout="wide", page_title="Smart Resume Screener")

# In-memory storage with clustering for RAG
resume_store: Dict[str, Dict] = {}
faiss_index = faiss.IndexFlatL2(384)
cluster_centers = {}  # For graph-like grouping

# Enhanced parsing with error handling
def parse_resume(file_path: str) -> Dict:
    try:
        if file_path.endswith('.pdf'):
            doc = fitz.open(file_path)
            text = "".join(page.get_text() for page in doc)
            doc.close()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        doc = nlp(text)
        skills = [ent.text for ent in doc.ents if ent.label_ in ["SKILL", "PRODUCT"]]
        experience = [{"role": ent.text, "context": sent.text} for sent in doc.sents for ent in sent.ents if ent.label_ == "ORG"]
        education = [{"institution": ent.text, "year": next((e.text for e in doc.ents if e.label_ == "DATE"), "N/A")} for ent in doc.ents if ent.label_ == "ORG" and "university" in text.lower()]
        name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Unknown")
        embeddings = embedder.encode(" ".join(skills + [exp["role"] for exp in experience] + [edu["institution"] for edu in education]))
        faiss_index.add(np.array([embeddings]))
        data = {"name": name, "skills": skills, "experience": experience, "education": education, "embeddings": embeddings.tolist()}
        resume_store[file_path] = data
        # Simple clustering for RAG enhancement
        if embeddings.tolist() not in cluster_centers:
            cluster_centers[embeddings.tolist()] = data
        return data
    except Exception as e:
        return {"error": str(e), "name": name, "status": "failed"}

# Advanced RAG with clustering
def retrieve_similar(job_desc: str) -> List[Dict]:
    jd_emb = embedder.encode(job_desc)
    distances, indices = faiss_index.search(np.array([jd_emb]), k=min(3, len(resume_store)))
    similar = [list(resume_store.values())[i] for i in indices[0] if i < len(resume_store)]
    # Enhance with cluster context
    return [resume for resume in similar if any(np.dot(resume['embeddings'], jd_emb) / (np.linalg.norm(resume['embeddings']) * np.linalg.norm(jd_emb)) > 0.7 for center in cluster_centers.values())]

# Sophisticated hybrid scoring with prompt engineering
def compute_match(resume: Dict, job_desc: str) -> Dict:
    local_score = np.mean([np.dot(resume['embeddings'], embedder.encode(job_desc)) / (np.linalg.norm(resume['embeddings']) * np.linalg.norm(embedder.encode(job_desc)))]) * 10
    prompt = f"""Follow this reasoning:
1. Identify key skills and experience in the job description.
2. Match them with resume skills and experience contextually.
3. Adjust for education relevance.
4. Provide a 1-10 score with detailed justification.

Job Description: {job_desc}
Resume: {json.dumps(resume)}
Output JSON: {{"score": X, "justification": "Step-by-step reasoning..."}}"""
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    llm_data = json.loads(response.choices[0].message.content.strip())
    final_score = (local_score + llm_data["score"]) / 2
    return {"score": final_score, "justification": llm_data["justification"]}

# FastAPI endpoints
@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join("resumes", file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    data = parse_resume(file_path)
    return {"filename": file.filename, "data": data} if "error" not in data else {"error": data["error"]}

@app.post("/match/")
async def match_resume(job_desc: str):
    similar = retrieve_similar(job_desc)
    scores = [compute_match(resume, job_desc) for resume in similar[:2]]  # Limit to top 2 for speed
    return {"shortlisted": scores}

# Immersive Streamlit frontend with animations
def main():
    st.title("Smart Resume Screener 🎯")
    st.markdown("""
        <style>
        .stApp {background: linear-gradient(135deg, #e0f7fa, #ffffff); animation: fadeIn 1s;}
        .card {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); animation: slideUp 0.5s;}
        @keyframes fadeIn {from {opacity: 0;} to {opacity: 1;}}
        @keyframes slideUp {from {transform: translateY(20px); opacity: 0;} to {transform: translateY(0); opacity: 1;}}
        </style>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Upload Resumes", accept_multiple_files=True, type=["pdf", "txt"])
    job_desc = st.text_area("Job Description", height=200)
    
    if uploaded_files and job_desc:
        for file in uploaded_files:
            file_path = os.path.join("resumes", file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            with st.spinner("Parsing..."):
                time.sleep(1)  # Simulate processing
                parse_resume(file_path)
        if st.button("Screen Candidates"):
            with st.spinner("Matching..."):
                time.sleep(1.5)  # Simulate matching
                response = {"shortlisted": [compute_match(list(resume_store.values())[0], job_desc)]}
                for candidate in response["shortlisted"]:
                    with st.container():
                        st.markdown(f"**{list(resume_store.values())[0]['name']}**", unsafe_allow_html=True)
                        st.progress(candidate['score'] / 10, text=f"Match Score: {candidate['score']:.1f}/10")
                        st.write(candidate['justification'])
                        # Visual: Skill overlap chart
                        fig = px.bar(x=list(resume_store.values())[0]['skills'], y=[1]*len(list(resume_store.values())[0]['skills']), orientation='h', title="Skills Match")
                        st.plotly_chart(fig, use_container_width=True)

    if st.button("Run API"):
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8501, log_level="info")

if __name__ == "__main__":
    main()
