# Smart Resume Screener

AI-powered resume screening system using Google Gemini, semantic matching, and advanced NLP.

## Features

- 🎯 AI-Powered Analysis with Google Gemini
- 📊 Interactive Visualizations (Plotly charts)
- 🔍 Semantic Matching with partial credit scoring
- 💼 Comprehensive Skills & Experience Assessment
- 🎨 Modern UI with animated gradients

## Tech Stack

- Streamlit, Google Gemini, SentenceTransformer
- MongoDB Atlas, PyMuPDF, spaCy
- Plotly, FAISS

## Quick Start

```bash
git clone https://github.com/nihcastics/smart-resume-screener.git
cd smart-resume-screener
pip install -r requirements.txt
streamlit run app.py
```

## Environment Variables

Create `.env` file:
```
GEMINI_API_KEY=your_key
MONGO_URI=your_mongodb_uri
HF_TOKEN=your_huggingface_token
```

## Deployment (Streamlit Cloud)

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Add secrets in Settings → Secrets:
   ```toml
   GEMINI_API_KEY = "your_key"
   MONGO_URI = "your_uri"
   HF_TOKEN = "your_token"
   ```
5. Deploy!

---

Made with ❤️ by [nihcastics](https://github.com/nihcastics)
