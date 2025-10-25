# Backend Deployment Guide - Google Cloud Run

This guide explains how to deploy the Smart Resume Screener backend to Google Cloud Run separately from the frontend (which runs on Vercel).

## Why separate backend deployment?

The backend requires native Python packages (torch, faiss, spacy with models) that:
- Cannot be installed in Vercel's serverless environment
- Need Docker for proper compilation and runtime support
- Benefit from persistent resources and longer timeout windows

## Architecture

```
Frontend (React + Vite)        Backend (FastAPI + Python ML)
        ↓                                ↓
     Vercel                        Google Cloud Run
     ↓                                ↓
https://smart-resume-screener-*.vercel.app  →  https://srs-backend-*.run.app/api
```

## Prerequisites

1. **Google Cloud Account** with:
   - Billing enabled (Cloud Run is free tier friendly: ~$1/month for typical usage)
   - gcloud CLI installed locally
   - Docker installed locally

2. **Credentials**:
   - GOOGLE_API_KEY (Gemini API key)
   - DATABASE_URL (PostgreSQL/Supabase connection string)
   - JWT_SECRET (random secret for JWT tokens)

## One-Time Setup (First Deployment)

### Step 1: Authenticate with Google Cloud

```bash
# Install gcloud CLI from: https://cloud.google.com/sdk/docs/install
# Then authenticate:
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Enable required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 3: Set environment variables

```bash
# Replace with your actual values
export GOOGLE_API_KEY="AIzaSyDCzBkKmH4XJdFa2RZ6gJzgIJXOsWplkyw"
export DATABASE_URL="postgresql://postgres.yytxzajsnldfpitapwzg:Jenny%40may16@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
export JWT_SECRET="your-random-secret-key-here"
export PROJECT_ID=$(gcloud config get-value project)
```

## Deployment Options

### Option A: Manual Docker Build & Push (Fastest for first-time testing)

```bash
# 1. Build Docker image locally
cd smart-resume-screener
docker build -f backend/Dockerfile -t gcr.io/$PROJECT_ID/smart-resume-screener-backend:latest .

# 2. Configure Docker to push to Google Container Registry
gcloud auth configure-docker

# 3. Push image to registry
docker push gcr.io/$PROJECT_ID/smart-resume-screener-backend:latest

# 4. Deploy to Cloud Run
gcloud run deploy smart-resume-screener-backend \
  --image gcr.io/$PROJECT_ID/smart-resume-screener-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900s \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY,DATABASE_URL=$DATABASE_URL,JWT_SECRET=$JWT_SECRET

# 5. Get the backend URL from output
# Example: https://smart-resume-screener-backend-abc123-uc.a.run.app
```

### Option B: Automated with Cloud Build (Recommended for production)

This automatically builds and deploys on every push to `main` branch.

```bash
# 1. Create a Cloud Build trigger in Google Cloud Console
#    Settings → Cloud Build → Triggers → Create Trigger
#    Connect your GitHub repo (nihcastics/smart-resume-screener)
#    Trigger name: smart-resume-screener-backend
#    Branch: main
#    Build configuration: Cloud Build configuration file (cloudbuild.yaml)
#    Substitutions:
#      _GOOGLE_API_KEY: your-api-key
#      _DATABASE_URL: your-db-url
#      _JWT_SECRET: your-jwt-secret

# 2. Push changes to main branch - Cloud Build automatically:
#    - Builds Docker image
#    - Pushes to Container Registry
#    - Deploys to Cloud Run
```

## Post-Deployment

### Step 4: Verify Backend is Running

```bash
# Get the Cloud Run service URL
BACKEND_URL=$(gcloud run services describe smart-resume-screener-backend \
  --region us-central1 --format 'value(status.url)')

echo "Backend URL: $BACKEND_URL"

# Test health endpoint
curl $BACKEND_URL/

# View API docs
# Visit: $BACKEND_URL/docs in your browser
```

### Step 5: Update Frontend with Backend URL

In Vercel Dashboard:
1. Go to Project Settings → Environment Variables
2. Add/update:
   - Key: `VITE_API_URL`
   - Value: `https://smart-resume-screener-backend-abc123-uc.a.run.app` (your Cloud Run URL)
3. Redeploy frontend:
   - Go to Deployments → Select latest → Redeploy

Or via Vercel CLI:
```bash
echo "https://your-cloud-run-url" | npx vercel env add VITE_API_URL production
npx vercel --prod --yes
```

## Testing End-to-End

```bash
# 1. Visit frontend
https://smart-resume-screener-*.vercel.app

# 2. Register/Login
# Use credentials: test@example.com / password

# 3. Upload resume and paste JD
# Should show analysis results

# 4. Check backend logs if issues
gcloud run logs read smart-resume-screener-backend --region us-central1 --limit 50
```

## Cost Estimation (Google Cloud Run)

- **Compute**: $0.00002400 per CPU-second
- **Memory**: $0.0000025 per GB-second
- **Requests**: First 2M free per month, then $0.40 per 1M
- **Network**: Outbound traffic $0.12/GB

**Typical monthly cost for 100 analyses/day**:
- ~$2-5/month (mostly memory usage)
- First analysis of the day: cold-start (~3-5s)
- Subsequent analyses: ~1-2s (warm start)

## Updating Backend

### Push code updates:

```bash
# Option A: If using Cloud Build trigger
git add .
git commit -m "feat: update backend logic"
git push origin main
# → Automatically builds and deploys

# Option B: Manual deployment
docker build -f backend/Dockerfile -t gcr.io/$PROJECT_ID/smart-resume-screener-backend:latest .
docker push gcr.io/$PROJECT_ID/smart-resume-screener-backend:latest
gcloud run deploy smart-resume-screener-backend \
  --image gcr.io/$PROJECT_ID/smart-resume-screener-backend:latest \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY,DATABASE_URL=$DATABASE_URL,JWT_SECRET=$JWT_SECRET
```

## Scaling & Configuration

### Increase memory/CPU for long-running analyses:
```bash
gcloud run deploy smart-resume-screener-backend \
  --region us-central1 \
  --memory 4Gi \
  --cpu 4 \
  --timeout 1200s
```

### View metrics in Cloud Console:
- Go to: Cloud Run → smart-resume-screener-backend → Metrics
- Monitor: CPU usage, memory, request duration, error rate

## Troubleshooting

### Issue: Cold start timeout (first request slow)
- **Solution**: Use Cloud Scheduler to ping backend every 5 minutes (keeps warm)
```bash
gcloud scheduler jobs create http keep-backend-warm \
  --schedule="*/5 * * * *" \
  --uri="$BACKEND_URL/" \
  --http-method=GET
```

### Issue: Out of memory errors
- **Solution**: Increase memory in deployment (step above) or optimize FAISS index loading

### Issue: Database connection refused
- **Solution**: 
  - Verify DATABASE_URL is correct
  - Check Supabase IP whitelist (allow all or specific Cloud Run IP)
  - Check DB is running and accessible

### Issue: 500 errors in API responses
- **Solution**: Check logs:
```bash
gcloud run logs read smart-resume-screener-backend --region us-central1 --limit 100
```

## Summary

**Frontend** → Vercel (static React app)  
**Backend** → Google Cloud Run (FastAPI + Python ML)  
**Database** → Supabase PostgreSQL  
**LLM API** → Google Gemini  

Total deployment: **Frontend on Vercel + Backend on Cloud Run = Full stack, production-ready!** 🚀

---

For questions or issues, check logs:
```bash
# Frontend logs
# Vercel Dashboard → smart-resume-screener → Deployments → Logs

# Backend logs
gcloud run logs read smart-resume-screener-backend --region us-central1 --limit 50
```
