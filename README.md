#  Smart Resume Screener

A modern, AI-powered resume screening application with stunning visuals and professional-grade UI/UX.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![React](https://img.shields.io/badge/React-18.3-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120-009688.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab.svg)

##  Features

-  **LLM-Powered Skill Extraction** - Intelligent skill matching using Google Gemini with context awareness, abbreviation recognition, and synonym handling
-  **AI-Powered Analysis** - Advanced natural language processing with semantic similarity scoring
-  **Beautiful UI** - Stunning gradients, animations, and glassmorphism effects
-  **Real-time Processing** - Instant resume analysis with live progress indicators
-  **Secure Authentication** - JWT-based auth with PostgreSQL backend
-  **Comprehensive Scoring** - Multi-dimensional analysis with calibrated scoring algorithm (50% coverage, 35% semantic, 15% must-haves)
-  **Intelligent Skill Comparison** - Matched/missing/additional skills with confidence scores and rationales
-  **Analysis History** - Track and review past resume screenings
-  **Responsive Design** - Works perfectly on all devices

##  Architecture

```
smart-resume-screener/
 backend/              # FastAPI server
    main.py          # API endpoints and server configuration
    requirements.txt # Python dependencies
 frontend/            # React application
    src/
       components/  # Reusable UI components
       contexts/    # React contexts (Auth, etc.)
       pages/       # Page components
       services/    # API client and utilities
       App.jsx      # Main app component with routing
       main.jsx     # React entry point
       index.css    # TailwindCSS styles and animations
    package.json     # Node dependencies
    vite.config.js   # Vite configuration with proxy
    tailwind.config.js
 modules/             # Python business logic
    auth.py          # Authentication logic
    database.py      # Database operations
    llm_operations.py # LLM interactions and prompts
    resume_parser.py # Resume parsing (PDF, TXT, DOCX)
    scoring.py       # Requirement coverage scoring
    scoring_optimization.py # Calibrated final score calculation
    text_processing.py # NLP utilities (5-strategy skill extraction)
    abbreviation_mapping.py # Technical abbreviations and synonyms
    validation.py    # Resume and input validation
    prompt_enrichment.py # LLM prompt enhancement
 .env                 # Environment variables
 README.md           # This file
```

##  Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL** (or Supabase account)
- **Google AI API Key** (for Gemini)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv env
env\Scripts\activate  # Windows
# source env/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database (PostgreSQL/Supabase)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
DATABASE_URL=postgresql://user:pass@host:port/dbname

# AI Models
GOOGLE_API_KEY=your-gemini-api-key

# JWT Secret
JWT_SECRET=your-super-secret-key-change-in-production
```

##  Tech Stack

### Frontend
- **React 18** - Modern UI library
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **JWT** - Token-based authentication
- **Pydantic** - Data validation
- **Python-dotenv** - Environment management

### AI & NLP
- **Google Gemini 2.5-flash** - Advanced LLM for skill extraction and intelligent matching
- **spaCy** - NLP processing (named entity recognition, noun chunks)
- **Sentence Transformers** - Semantic embeddings (all-mpnet-base-v2, 768-dim vectors)
- **FAISS** - Vector similarity search for requirement coverage
- **PyMuPDF & pdfplumber** - Multi-strategy PDF parsing

### Database
- **PostgreSQL** - Production database
- **Supabase** - Backend-as-a-Service (optional)

##  Usage

### 1. Register an Account
Navigate to `/register` and create your account with:
- Full name
- Email address
- Secure password

### 2. Login
Use your credentials at `/login` to access the dashboard.

### 3. Analyze Resumes
1. **Upload Resume** - Drag & drop or click to select (PDF, TXT, DOC, DOCX)
2. **Paste Job Description** - Copy the job posting requirements
3. **Click "Analyze Resume"** - Watch the AI work its magic! 

### 4. Review Results
Get comprehensive insights including:
- **Match Score** - Calibrated compatibility score (0-10) with strict penalties for semantic mismatches
- **Coverage Analysis** - Requirement fulfillment with must-have vs nice-to-have breakdown
- **Semantic Matching** - NLP-based relevance scoring with requirement-level analysis
- **Intelligent Skill Comparison** - LLM-extracted matched, missing, and additional skills with context-specific rationales
- **Strengths** - Candidate's top competencies and advantages
- **Gaps** - Critical missing requirements with evidence
- **AI Recommendation** - Hire/pass decision with detailed reasoning

##  Intelligent Skill Extraction

Our proprietary skill extraction engine uses **5 complementary strategies** to accurately identify and match technical skills:

### Extraction Strategies
1. **Keyword Matching** - 200+ technical keywords (Python, React, AWS, Docker, etc.)
2. **Version Pattern Recognition** - Extracts versioned skills (Python 3.x, Java 11, React 18)
3. **Skills Section Parsing** - Dedicated parsing of "Technical Skills:" sections
4. **NLP Noun Chunks** - spaCy-based entity recognition with semantic filtering
5. **Acronym Detection** - Recognizes uppercase patterns (AWS, SQL, REST, API, K8s)

### Intelligent Matching
- **Abbreviation Awareness** - "OS" ↔ "Operating Systems", "DBMS" ↔ "Database Management Systems"
- **Synonym Recognition** - "React" = "React.js" = "ReactJS", "Node" = "Node.js"
- **Context Understanding** - "Django" implies "Python", "React" implies "JavaScript"
- **Framework→Language Inference** - Spring Boot → Java, Django → Python
- **Specific→General Matching** - PostgreSQL satisfies "SQL database", AWS Lambda satisfies "Serverless"

### Result
Extracts **80+ unique skills** with intelligent comparison returning matched/missing/additional skills with confidence scores.

##  Scoring Algorithm

The system uses a **calibrated, industry-standard scoring methodology**:

- **Coverage Score** (50% weight): Requirement fulfillment percentage with graduated penalties
- **Semantic Score** (35% weight): NLP-based relevance with requirement-level analysis
- **Must-Have Score** (15% weight): Critical requirement fulfillment with high penalties for gaps

**Penalty Tiers:**
- Semantic < 55%: -15% penalty
- Semantic < 40%: -30% penalty
- Coverage/Semantic mismatch (high coverage + low semantic): -15% penalty

**Example:** Resume with 96% coverage + 44% semantic match = **6.0-6.3/10** (strict evaluation)

##  API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Analysis
- `POST /api/analyze` - Analyze resume with comprehensive skill extraction and scoring (requires auth)
- `GET /api/analyses` - Get analysis history (requires auth)

### System
- `GET /` - Health check

##  Design System

### Colors
- **Primary**: Purple (#8b5cf6) to Pink (#d946ef) gradients
- **Secondary**: Blue (#3b82f6) to Cyan (#06b6d4)
- **Success**: Emerald (#10b981)
- **Warning**: Yellow (#f59e0b)
- **Danger**: Red (#ef4444)
- **Background**: Slate (#0f172a, #1e293b, #334155)

### Typography
- **Font**: Inter, system fonts
- **Headings**: Bold, gradient text effects
- **Body**: Slate-200 for readability

### Effects
- **Glassmorphism** - Backdrop blur with transparency
- **Gradients** - Vibrant, animated backgrounds
- **Glow Effects** - Subtle shadow glows on interactive elements
- **Smooth Animations** - Framer Motion powered transitions

##  Troubleshooting

### Skill Extraction Issues

**Issue: Getting 0 matched skills**
- Ensure LLM is properly configured (check `GOOGLE_API_KEY`)
- Verify resume and JD have sufficient technical content (50+ characters minimum)
- Check backend logs for LLM API errors

**Issue: Inaccurate skill matching**
- Verify spaCy model is installed: `python -m spacy download en_core_web_sm`
- Ensure abbreviation mappings are current in `modules/abbreviation_mapping.py`
- Check that FAISS index is built properly during initialization

### Frontend Issues

**Issue: Port 5173 already in use**
```bash
# Kill the process
npx kill-port 5173
# Or use a different port
npm run dev -- --port 5174
```

**Issue: Module not found**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Backend Issues

**Issue: Models not loading**
```bash
# Install required models
python -m spacy download en_core_web_sm
```

**Issue: Database connection failed**
- Check your `.env` file
- Verify Supabase credentials
- Ensure PostgreSQL is running

### Common Issues

**Issue: CORS errors**
- Check `backend/main.py` CORS settings
- Verify frontend URL matches allowed origins

**Issue: Authentication not working**
- Clear browser localStorage
- Check JWT_SECRET is set
- Verify token expiration time

##  Development

### Run Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Build for Production

```bash
# Frontend
cd frontend
npm run build

# Backend - use production WSGI server
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

##  Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes following conventional commits (`feat:`, `fix:`, `docs:`, etc.)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request with detailed description

### Development Guidelines
- Ensure all tests pass: `pytest` (backend), `npm test` (frontend)
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code (`npm run lint`)
- Update README for significant feature changes
- Include docstrings for all functions and classes

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Built with ❤️ using modern web technologies
- LLM-powered skill extraction powered by Google Gemini
- NLP infrastructure built on spaCy and Sentence Transformers
- UI/UX inspired by leading SaaS applications
- Open-source models and libraries from the community

---

**Made with ❤️ by nihcastics**

*Transforming recruitment with AI-powered intelligent skill extraction and beautiful design*

*Last Updated: October 2025*
