# Smart Resume Screener

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

An intelligent resume screening system powered by AI that analyzes resumes against job requirements using advanced NLP and semantic matching.

## ✨ Features

- 🎯 **AI-Powered Analysis**: Uses Google Gemini 2.5-flash for intelligent resume parsing
- 📊 **Interactive Visualizations**: Beautiful charts and graphs for insights
- 🔍 **Semantic Matching**: Advanced fuzzy matching with partial credit scoring
- 💼 **Comprehensive Assessment**: Evaluates skills, experience, cultural fit, and more
- 🎨 **Modern UI**: Animated gradients, glassmorphism effects, and responsive design
- 📈 **Requirements Coverage**: Detailed breakdown of job requirement matches
- 🤖 **LLM Integration**: Multi-model fallback chain for reliability

## 🚀 Live Demo

[Deploy on Streamlit Cloud](https://streamlit.io/cloud) - Follow the [Deployment Guide](DEPLOYMENT.md)

## 🛠️ Tech Stack

- **Frontend**: Streamlit with custom CSS animations
- **AI/ML**: Google Gemini, SentenceTransformer (all-mpnet-base-v2)
- **Visualization**: Plotly (Gauge & Radar charts)
- **Database**: MongoDB Atlas
- **PDF Processing**: PyMuPDF (fitz)
- **NLP**: spaCy (en_core_web_sm)

## 📋 Requirements

- Python 3.12+
- Google Gemini API Key
- MongoDB Atlas URI

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nihcastics/smart-resume-screener.git
   cd smart-resume-screener
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv env
   # Windows
   .\env\Scripts\activate
   # Mac/Linux
   source env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your API keys:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     MONGODB_URI=your_mongodb_uri_here
     ```

5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📝 Usage

1. **Enter Job Requirements**: Paste the job description or requirements
2. **Upload Resume**: Upload PDF resume file
3. **View Analysis**: Get comprehensive scoring and insights
4. **Review Matches**: See detailed requirement coverage and candidate assessment

## 🎨 Features Showcase

### Scoring System
- **Overall Score**: 0-100 scale with dynamic color coding
- **Multi-dimensional Radar**: Technical skills, soft skills, experience, education, certifications
- **Fuzzy Semantic Matching**: 3-tier partial credit system (1.0, 0.6, 0.3)

### Visual Design
- Animated gradient backgrounds
- Glassmorphism cards with backdrop blur
- 3D hover effects and transitions
- Interactive Plotly charts with glow effects

### Assessment Categories
- 💪 Strengths & Achievements
- 🤝 Cultural Fit Indicators
- ⚙️ Technical Competencies
- 📈 Development Areas

## 🔐 Security

- Environment variables secured with `.gitignore`
- API keys never committed to repository
- `.env.example` provided as template

## 📦 Project Structure

```
smart-resume-screener/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── DEPLOYMENT.md         # Deployment instructions
├── README.md             # This file
├── api/                  # API modules
│   ├── main.py          # Core logic
│   └── parsing.py       # Resume parsing
└── env/                  # Virtual environment (not in git)
```

## 🌐 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Recommended**: Streamlit Community Cloud (FREE)
- Visit: https://streamlit.io/cloud
- Connect GitHub repository
- Add secrets in dashboard
- Deploy in one click!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**nihcastics**
- GitHub: [@nihcastics](https://github.com/nihcastics)
- Repository: [smart-resume-screener](https://github.com/nihcastics/smart-resume-screener)

## 🙏 Acknowledgments

- Google Gemini AI for LLM capabilities
- Streamlit for the amazing framework
- HuggingFace for SentenceTransformers
- Plotly for interactive visualizations

---

Made with ❤️ using Streamlit
