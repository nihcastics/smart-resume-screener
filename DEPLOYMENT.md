# Deployment Guide

## ⚠️ Important: Streamlit Apps on Vercel

Vercel is **not recommended** for Streamlit applications because:
- Streamlit requires WebSocket connections
- Vercel's serverless functions have timeout limits
- Streamlit needs a persistent server

## ✅ Recommended: Streamlit Community Cloud (FREE)

### Steps to Deploy on Streamlit Community Cloud:

1. **Visit**: https://streamlit.io/cloud
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Select**:
   - Repository: `nihcastics/smart-resume-screener`
   - Branch: `main`
   - Main file path: `app.py`
5. **Advanced Settings** → Add your secrets:
   ```toml
   GOOGLE_API_KEY = "your_google_api_key"
   MONGODB_URI = "your_mongodb_connection_string"
   ```
6. **Click "Deploy"**

Your app will be live at: `https://nihcastics-smart-resume-screener.streamlit.app`

### Features:
- ✅ FREE hosting
- ✅ Automatic updates on git push
- ✅ Built specifically for Streamlit
- ✅ No timeout issues
- ✅ Easy secret management

---

## Alternative Options

### Option 1: Render.com (FREE tier available)
1. Visit https://render.com
2. Create a new Web Service
3. Connect GitHub repo
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add environment variables in dashboard

### Option 2: Railway.app (FREE $5 credit monthly)
1. Visit https://railway.app
2. New Project → Deploy from GitHub
3. Select repository
4. Add environment variables
5. Deploy automatically

### Option 3: Heroku (Paid)
Requires Procfile and setup.sh - more complex setup

---

## For Vercel (Not Recommended for Streamlit)

If you still want to try Vercel despite limitations:

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   cd "c:\Users\jenny\Downloads\Final Resume Screener\smart-resume-screener"
   vercel
   ```

3. Follow prompts
4. Add environment variables in Vercel dashboard

**Note**: The app may not work properly due to Streamlit's architecture.

---

## 🎯 Recommended Action

**Use Streamlit Community Cloud** - it's specifically designed for Streamlit apps and is completely free!
