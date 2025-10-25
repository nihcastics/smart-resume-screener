#  Smart Resume Screener

A modern, AI-powered resume screening application with stunning visuals and professional-grade UI/UX.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![React](https://img.shields.io/badge/React-18.3-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120-009688.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab.svg)

##  Features

-  **AI-Powered Analysis** - Advanced natural language processing using Google Gemini
-  **Beautiful UI** - Stunning gradients, animations, and glassmorphism effects
-  **Real-time Processing** - Instant resume analysis with live progress indicators
-  **Secure Authentication** - JWT-based auth with PostgreSQL backend
-  **Comprehensive Scoring** - Multi-dimensional analysis with detailed insights
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
    llm_operations.py # LLM interactions
    resume_parser.py # Resume parsing
    scoring.py       # Scoring algorithms
    text_processing.py # NLP utilities
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
- **Google Gemini** - Large language model
- **spaCy** - NLP processing
- **Sentence Transformers** - Semantic embeddings
- **FAISS** - Vector similarity search

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
- **Match Score** - Overall compatibility percentage
- **Strengths** - What the candidate excels at
- **Gaps** - Missing requirements
- **AI Recommendation** - Hire/pass decision with reasoning

##  API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Analysis
- `POST /api/analyze` - Analyze resume (requires auth)
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
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Built with  using modern web technologies
- UI/UX inspired by leading SaaS applications
- AI powered by Google Gemini and open-source NLP models

---

**Made with  by Your Team**

*Transforming recruitment with AI and beautiful design*
