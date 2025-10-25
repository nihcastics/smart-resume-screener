# Render Deployment Guide - Smart Resume Screener Backend

Deploy your FastAPI backend to Render in **3 minutes** with Docker.

## Why Render?

✅ No CLI setup (unlike gcloud)  
✅ Built-in Docker support  
✅ Auto-deploys from GitHub (push = deploy)  
✅ Free tier available  
✅ Pay-as-you-go pricing ($7-12/month typical)  
✅ Perfect for ML workloads (torch, faiss, spacy)  

## Architecture

```
Frontend (React)              Backend (FastAPI)
    ↓                              ↓
Vercel (free tier)          Render (Docker, $7/mo)
    ↓                              ↓
https://smart-resume-screener-*.vercel.app  →  https://smart-resume-screener-backend-*.onrender.com
```

## One-Click Deployment (No CLI needed!)

### Step 1: Go to Render Dashboard

Visit: https://dashboard.render.com (sign up if needed with GitHub)

### Step 2: Create New Web Service

1. Click **"New +"** button
2. Select **"Web Service"**
3. Connect your GitHub repo:
   - Search: `nihcastics/smart-resume-screener`
   - Click "Connect" and authorize

### Step 3: Configure Service

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `smart-resume-screener-backend` |
| **Runtime** | Docker |
| **Region** | Oregon (or nearest to you) |
| **Branch** | `main` |
| **Dockerfile** | `./backend/Dockerfile` |
| **Plan** | Starter ($7/month) |

### Step 4: Add Environment Variables

Before clicking Deploy, add these under "Advanced":

| Key | Value | Notes |
|-----|-------|-------|
| `GOOGLE_API_KEY` | `AIzaSyDCzBkKmH4XJdFa2RZ6gJzgIJXOsWplkyw` | Your Gemini API key |
| `DATABASE_URL` | `postgresql://postgres.yytxzajsnldfpitapwzg:Jenny%40may16@aws-1-ap-south-1.pooler.supabase.com:6543/postgres` | Your PostgreSQL URL |
| `JWT_SECRET` | `your-random-secret-key-min-32-chars` | Generate random string |
| `GEMINI_MODEL_NAME` | `gemini-2.5-flash` | LLM model name |
| `SENTENCE_MODEL_NAME` | `all-mpnet-base-v2` | Embedding model |

### Step 5: Deploy

Click **"Create Web Service"** and wait ~3-5 minutes for:
- Docker build
- Image push
- Container startup

You'll see logs scroll by. When done, you'll get a URL like:
```
https://smart-resume-screener-backend-abc123xyz.onrender.com
```

### Step 6: Verify Backend is Running

```bash
# Test health endpoint
curl https://smart-resume-screener-backend-abc123xyz.onrender.com/

# View API docs (replace URL)
# https://smart-resume-screener-backend-abc123xyz.onrender.com/docs
```

## Update Frontend with Backend URL

Once backend is deployed and running:

### Option A: Via Vercel Dashboard (Easy)

1. Go to Vercel Dashboard → smart-resume-screener
2. Settings → Environment Variables
3. Add/Update:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://smart-resume-screener-backend-abc123xyz.onrender.com`
4. Click "Save"
5. Go to Deployments → Click latest deployment → "Redeploy"

### Option B: Via Vercel CLI

```powershell
# Set the backend URL (replace with your actual URL)
$BACKEND_URL = "https://smart-resume-screener-backend-abc123xyz.onrender.com"

# Add environment variable
echo $BACKEND_URL | npx vercel env add VITE_API_URL production

# Redeploy frontend
npx vercel --prod --yes
```

## Test End-to-End

1. **Visit frontend**: https://smart-resume-screener-*.vercel.app
2. **Register** with test email/password
3. **Upload a resume** (PDF, TXT, or DOCX)
4. **Paste a job description**
5. **Click "Analyze Resume"** and watch it process
6. **Review results** (match score, skills, gaps, recommendations)

If you see API errors, check Render logs:
- Render Dashboard → smart-resume-screener-backend → Logs

## Render Pricing & Costs

| Component | Cost |
|-----------|------|
| Starter Instance | $7/month |
| Build minutes | Free (500/month included) |
| Bandwidth | Free |
| **Total** | **~$7-12/month** |

**Free tier option** (if you need it): Available but spins down after 15 min of inactivity (slow cold starts). Upgrade to Starter ($7) for always-on.

## Auto-Updates (Continuous Deployment)

Every time you push to GitHub `main` branch:
1. Render automatically detects the change
2. Rebuilds Docker image
3. Deploys new version
4. No manual steps needed!

To deploy updates:
```bash
git add .
git commit -m "feat: improve skill extraction"
git push origin main
# → Automatically deploys to Render in ~2 minutes
```

## Troubleshooting

### Issue: Deployment stuck building
- **Cause**: Docker build taking too long (pip install of large packages)
- **Solution**: Wait 5-10 minutes, or check logs for errors

### Issue: 502 Bad Gateway / 500 errors
- **Cause**: Backend crashed, missing env vars, or database connection failed
- **Solution**: 
  - Check Render logs for error messages
  - Verify all env vars are set correctly
  - Verify DATABASE_URL is reachable

### Issue: Frontend shows "Cannot reach API"
- **Cause**: `VITE_API_URL` not set in Vercel or backend not running
- **Solution**:
  - Confirm backend URL in Vercel env vars
  - Test backend directly: curl the backend URL
  - Redeploy frontend

### Issue: Cold start takes 30+ seconds
- **Cause**: First request to backend wakes it from sleep
- **Solution**: 
  - This is normal for Starter plan
  - Upgrade to Pro for faster cold starts
  - Or use Render's free tier with always-on disabled (accept slower starts)

## Monitoring

In Render Dashboard:

1. **Metrics**: CPU, memory, request count
2. **Logs**: Real-time backend logs (helpful for debugging)
3. **Events**: Deployment history and restarts
4. **Settings**: Scale resources, add replicas

## What's Next?

- ✅ Frontend on Vercel
- ✅ Backend on Render
- ✅ Database on Supabase
- ✅ LLM: Google Gemini API

**Full stack deployed! 🚀**

---

**Questions?**
- Check Render logs: Dashboard → Logs tab
- Check Vercel logs: Dashboard → Deployments → Logs
- Backend API docs: `https://your-backend-url.onrender.com/docs`
