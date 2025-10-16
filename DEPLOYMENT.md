# Deployment Guide

## ⚠️ Important: Streamlit Apps CANNOT Run on Vercel

**Vercel does NOT support Streamlit applications** because:
- ❌ Streamlit requires WebSocket connections
- ❌ Vercel's serverless functions have memory/timeout limits
- ❌ Streamlit needs a persistent Python server (not Node.js)
- ❌ Error: `ERR_OUT_OF_RANGE` buffer overflow in Node.js runtime

**Do not attempt Vercel deployment - it will fail.**

---

## ✅ RECOMMENDED: Streamlit Community Cloud (FREE)

### 📝 Step-by-Step Deployment on Streamlit Community Cloud:

#### Step 1: Access Streamlit Cloud
- Visit: **https://share.streamlit.io**
- Click **"Sign in"** button
- Choose **"Continue with GitHub"**

#### Step 2: Create New App
- Click the **"New app"** button in top-right
- OR visit: https://share.streamlit.io/deploy

#### Step 3: Configure Your App
Fill in the deployment form:

**Repository:**
- Repository: `nihcastics/smart-resume-screener`
- Branch: `main`
- Main file path: `app.py`

#### Step 4: Add Environment Secrets
- Click **"Advanced settings"**
- In the **"Secrets"** section, paste:

```toml
GOOGLE_API_KEY = "your_actual_google_gemini_api_key_here"
MONGODB_URI = "your_actual_mongodb_connection_string_here"
```

⚠️ **Important**: Replace with your actual API keys from your local `.env` file!

#### Step 5: Deploy!
- Click **"Deploy!"** button
- Wait 2-3 minutes for initial deployment
- Your app will be live at: `https://nihcastics-smart-resume-screener.streamlit.app`

#### Step 6: Manage Your App
- View logs in real-time
- Auto-redeploys on every git push to `main`
- Edit secrets anytime in app settings
- Monitor usage in dashboard

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

## 🎯 Recommended Action

**Use Streamlit Community Cloud** - it's specifically designed for Streamlit apps and is completely free!
