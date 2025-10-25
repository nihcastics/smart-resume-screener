# 🚀 Complete Deployment Guide: Render + Vercel

This guide walks you through deploying the Smart Resume Screener application with:
- **Frontend**: React app on Vercel (free tier)
- **Backend**: FastAPI server on Render ($7/month)
- **Database**: PostgreSQL on Supabase (free tier)

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Render)](#backend-deployment-render)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Connecting Frontend to Backend](#connecting-frontend-to-backend)
5. [End-to-End Testing](#end-to-end-testing)
6. [Troubleshooting](#troubleshooting)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

Before you start, make sure you have:

### 1. GitHub Account
- ✅ Repository created at: https://github.com/nihcastics/smart-resume-screener
- ✅ Latest code pushed to `main` branch
- ✅ Verify files exist in repo: `Dockerfile`, `render.yaml`, `backend/main.py`, `frontend/src/`

### 2. Required API Keys & Credentials
- 📌 **Google Gemini API Key**: `AIzaSyDCzBkKmH4XJdFa2RZ6gJzgIJXOsWplkyw`
- 📌 **Supabase Database URL**: `postgresql://postgres.yytxzajsnldfpitapwzg:Jenny%40may16@aws-1-ap-south-1.pooler.supabase.com:6543/postgres`
- 📌 **JWT Secret**: Generate a random 32+ character string (see [Generate JWT Secret](#generate-jwt-secret))

### 3. Accounts Created
- ✅ GitHub: https://github.com/nihcastics (already have)
- ⏳ Render: https://dashboard.render.com (sign up if needed)
- ⏳ Vercel: https://vercel.com (sign up if needed)

### 4. Generate JWT Secret
Run this command to generate a secure JWT secret:

**On Windows PowerShell:**
```powershell
$bytes = [System.Text.Encoding]::UTF8.GetBytes((1..32 | ForEach-Object { [char](Get-Random -Minimum 33 -Maximum 126) }) -join '')
[Convert]::ToBase64String($bytes)
```

**On Mac/Linux:**
```bash
openssl rand -base64 32
```

**Example Output:**
```
TnF3c2QzWjhgYSVoNWoyajprNFl6OHQwOSN5YWwrOFI4ZTVCM3Y0c0Y=
```

💾 **Save this value somewhere safe - you'll need it for both Render and Vercel**

---

## Backend Deployment (Render)

Render will automatically build and deploy your Docker container from the GitHub repository.

### Step 1: Create a Render Account & Connect GitHub

**1.1** Go to https://dashboard.render.com
**1.2** Click **"Sign up"** (if you don't have an account)
**1.3** Choose **"Sign up with GitHub"**
**1.4** Authorize Render to access your GitHub account
- Confirm your GitHub credentials
- Grant permission to access repositories
- You'll be redirected to Render dashboard

### Step 2: Create a New Web Service

**2.1** In Render dashboard, click **"New +"** button (top-right)
**2.2** Select **"Web Service"**

You'll see a list of your GitHub repositories.

**2.3** Find and click on **`smart-resume-screener`** repository

A deployment form will appear. Continue to Step 3.

### Step 3: Fill Deployment Form (Critical)

**Form Field: Name**
- Value: `smart-resume-screener-backend`
- ℹ️ This will be part of your backend URL

**Form Field: Region**
- Value: **Oregon** (US-based, good for latency)
- Alternative: **Frankfurt** (if you prefer EU)

**Form Field: Branch**
- Value: `main` (should be default)
- Verify the latest code is on `main` branch

**Form Field: Runtime**
- Value: **Docker**
- ℹ️ Render will auto-detect `./Dockerfile` at project root

**Form Field: Plan**
- Value: **Starter** ($7/month)
  - Includes: 750 free compute hours/month (enough for continuous running)
  - Specs: Shared CPU, 512MB RAM
  - Perfect for this ML backend

### Step 4: Add Environment Variables

⚠️ **IMPORTANT: Add these BEFORE clicking Deploy**

**4.1** Scroll down to **"Environment"** section

**4.2** Click **"Add Environment Variable"** and fill in each:

| Variable Name | Value | Notes |
|---|---|---|
| `GOOGLE_API_KEY` | `AIzaSyDCzBkKmH4XJdFa2RZ6gJzgIJXOsWplkyw` | Gemini API key for LLM |
| `DATABASE_URL` | `postgresql://postgres.yytxzajsnldfpitapwzg:Jenny%40may16@aws-1-ap-south-1.pooler.supabase.com:6543/postgres` | Supabase PostgreSQL |
| `JWT_SECRET` | `<your_generated_secret>` | Replace with generated secret from Prerequisites |
| `GEMINI_MODEL_NAME` | `gemini-2.5-flash` | Latest Gemini model |
| `SENTENCE_MODEL_NAME` | `all-mpnet-base-v2` | Sentence embeddings model |
| `PYTHONUNBUFFERED` | `1` | For real-time logs in Render |

**Example:** Adding `GOOGLE_API_KEY`
1. Click "Add Environment Variable"
2. Key field: `GOOGLE_API_KEY`
3. Value field: `AIzaSyDCzBkKmH4XJdFa2RZ6gJzgIJXOsWplkyw`
4. Click checkmark to confirm

Repeat for all 6 variables.

### Step 5: Deploy Backend

**5.1** Scroll down and click **"Create Web Service"** button (blue button at bottom)

**✨ Deployment started!**

### Step 6: Wait for Build & Deployment

Render will now:
1. **Clone your GitHub repo** (~30 seconds)
2. **Build Docker image** (~3-5 minutes)
   - Downloads Python 3.11-slim base image
   - Installs system dependencies (ffmpeg, tesseract, etc.)
   - Installs Python packages (torch, faiss, transformers, etc.)
   - This is slow first time but uses cache on redeploys
3. **Push image to Render registry** (~1 minute)
4. **Start container** (~1 minute)
5. **Health checks pass** (~30 seconds)

**Estimated total: 5-10 minutes**

### Step 7: Get Backend URL

Once deployment is complete:

**7.1** You'll see a green checkmark ✅ and "Live" status

**7.2** At the top, find your backend URL:
```
https://smart-resume-screener-backend-xxxxxx.onrender.com
```

**💾 Save this URL - you need it for frontend deployment**

Example: `https://smart-resume-screener-backend-abc123.onrender.com`

### Step 8: Test Backend Health

**8.1** Open a new browser tab and visit:
```
https://your-backend-url/docs
```
(Replace `your-backend-url` with actual URL from Step 7)

**Expected result:** FastAPI interactive docs page loads
- Shows all API endpoints
- Green checkmark next to `/` endpoint indicates health check passed

**8.2** Test a simple endpoint in the browser:
```
https://your-backend-url/
```

**Expected result:** Returns `{"status":"healthy"}`

If you see these, backend is ✅ deployed successfully!

---

## Frontend Deployment (Vercel)

### Step 1: Create a Vercel Account & Connect GitHub

**1.1** Go to https://vercel.com
**1.2** Click **"Sign Up"**
**1.3** Choose **"Continue with GitHub"**
**1.4** Authorize Vercel to access your GitHub account
- Confirm your GitHub credentials
- Grant permission to access repositories
- You'll be redirected to Vercel dashboard

### Step 2: Import Your Repository

**2.1** On Vercel dashboard, click **"Add New..."** → **"Project"**

**2.2** Search for your repository:
- Look for: `smart-resume-screener`
- Click **"Import"**

A project configuration page will appear. Continue to Step 3.

### Step 3: Configure Project Settings

**3.1** Project Name
- Should auto-fill as: `smart-resume-screener`
- Can change to: `smart-resume-screener-frontend`

**3.2** Framework Preset
- Should auto-detect: **Vite**
- If not, manually select: **Vite**

**3.3** Root Directory
- Should auto-detect: `./frontend`
- If blank, set to: `./frontend`

**3.4** Build Command
- Should show: `npm run build`
- ✅ Correct - leave as is

**3.5** Output Directory
- Should show: `dist`
- ✅ Correct - leave as is

### Step 4: Add Environment Variable

**4.1** Scroll down to **"Environment Variables"** section

**4.2** Add the backend URL:

| Variable | Value |
|---|---|
| `VITE_API_URL` | `https://your-backend-url` |

Replace `your-backend-url` with the Render backend URL from [Backend Deployment Step 7](#step-7-get-backend-url).

**Example:**
- Key: `VITE_API_URL`
- Value: `https://smart-resume-screener-backend-abc123.onrender.com`

**4.3** Click **"Add"** to confirm

### Step 5: Deploy Frontend

**5.1** Scroll down and click **"Deploy"** button (blue button at bottom)

**✨ Deployment started!**

### Step 6: Wait for Build & Deployment

Vercel will now:
1. **Clone your GitHub repo** (~10 seconds)
2. **Install dependencies** (~30 seconds)
   - Runs `npm install` in frontend directory
3. **Build React app** (~1-2 minutes)
   - Vite bundler creates optimized production build
4. **Upload to CDN** (~30 seconds)
   - Distributed across Vercel's global network

**Estimated total: 2-5 minutes**

### Step 7: Get Frontend URL

Once deployment is complete:

**7.1** You'll see deployment complete message

**7.2** Your frontend URL:
```
https://smart-resume-screener-xxxxx.vercel.app
```

**💾 Save this URL - this is your public application URL**

Example: `https://smart-resume-screener-abc123.vercel.app`

### Step 8: Test Frontend

**8.1** Open a new browser tab and visit your frontend URL

**Expected result:** 
- Resume Screener application loads
- Beautiful UI with animated background
- No console errors

**8.2** Try logging in:
- Click "Login" (if shown)
- Or go directly to Dashboard

**Expected result:**
- Login page appears or Dashboard loads
- No 404 or API errors

---

## Connecting Frontend to Backend

### Understanding the Connection

When your frontend runs in the browser:
1. User uploads resume PDF
2. Frontend sends HTTP request to backend API
3. Backend processes resume (extracts skills, scores, etc.)
4. Backend returns results to frontend
5. Frontend displays results to user

The connection happens through the `VITE_API_URL` environment variable you set during frontend deployment.

### If Frontend Can't Connect to Backend

The frontend won't work if it can't reach the backend. Here's how to fix it:

#### Method 1: Update in Vercel Dashboard (Recommended)

**1.1** Go to https://vercel.com/dashboard

**1.2** Click on your `smart-resume-screener` project

**1.3** Click **"Settings"** (top menu)

**1.4** Go to **"Environment Variables"**

**1.5** Find `VITE_API_URL`
- Click the three-dot menu next to it
- Click **"Edit"**
- Verify the URL is correct (check Render backend URL)
- Make sure there's no trailing slash: ✅ `https://smart-resume-screener-backend-xxx.onrender.com`
- Click **"Save"**

**1.6** Trigger redeploy:
- Go to **"Deployments"** tab
- Click **"..."** on the latest deployment
- Select **"Redeploy"**
- Wait 2-3 minutes for frontend to rebuild

#### Method 2: Verify Backend is Running

**2.1** Go to https://dashboard.render.com

**2.2** Click on `smart-resume-screener-backend`

**2.3** Check status:
- Should show **"Live"** (green) ✅
- If "Deploying" or "Building", wait for completion
- If "Failed", see [Troubleshooting](#troubleshooting)

**2.4** Test backend endpoint:
```
https://your-backend-url/
```
Should return `{"status":"healthy"}`

### Verifying Connection Works

**3.1** Open your frontend: `https://your-frontend-url`

**3.2** Open browser Developer Tools:
- Press `F12` or right-click → "Inspect"
- Go to **"Console"** tab

**3.3** Try to interact with the app (upload resume, login, etc.)

**3.4** Check for errors:
- ✅ No errors = connection working
- ❌ `CORS error` = backend not responding or wrong URL
- ❌ `404 Not Found` = wrong backend URL

If you see errors, follow [Troubleshooting](#troubleshooting) section.

---

## End-to-End Testing

### Complete User Flow Test

**Test 1: User Registration & Login**

1. Open your frontend URL
2. Click "Register" (or "Sign Up")
3. Fill in:
   - Email: `test@example.com`
   - Password: `TestPassword123!`
   - Confirm Password: `TestPassword123!`
4. Click "Register"
5. Expected: Success message, redirected to login
6. Click "Login"
7. Enter email and password
8. Click "Login"
9. Expected: Dashboard loads

**Test 2: Resume Upload & Analysis**

1. Make sure you're logged in on Dashboard
2. Click "Upload Resume" or "New Analysis"
3. Select a PDF file from your computer
4. Click "Analyze" or "Process"
5. Wait for processing (30-60 seconds)
6. Expected: Results show
   - Extracted skills
   - Score breakdown
   - Skill matches
   - Job fit percentage

**Test 3: Mobile Responsiveness**

1. Open DevTools (F12)
2. Click device toggle (phone icon)
3. Select "iPhone 12" or "Pixel 5"
4. Navigate through app
5. Expected: Layout looks good, no overflow, readable text

**Test 4: Error Handling**

1. Try uploading a non-PDF file
2. Expected: Error message appears
3. Try logging out
4. Try accessing dashboard without login
5. Expected: Redirected to login page

### Performance Check

**1.1** Open frontend URL

**1.2** Open DevTools → "Performance" tab

**1.3** Click "Record" button (red circle)

**1.4** Wait 2-3 seconds, click "Stop"

**Metrics to check:**
- ✅ First Contentful Paint (FCP) < 1.5s (good)
- ✅ Largest Contentful Paint (LCP) < 2.5s (good)
- ✅ Cumulative Layout Shift (CLS) < 0.1 (good)

If much slower, check:
- Vercel deployment finished building
- No large images in frontend
- Backend not overloaded

---

## Troubleshooting

### Backend Issues

#### ❌ Backend Deployment Failed - "Build Error"

**Symptoms:**
- Render shows "Deploy failed"
- Red error message in logs

**Steps to fix:**

**1. Check Render logs:**
1. Go to https://dashboard.render.com
2. Click `smart-resume-screener-backend`
3. Scroll to "Logs" section
4. Look for error messages (red text)

**2. Common errors and fixes:**

**Error: "No space left on device"**
- Backend is too large to build on free tier
- Solution: Use Starter plan (requires paid account)

**Error: "ModuleNotFoundError: torch"**
- Requirements not installed correctly
- Solution:
  1. Check `backend/requirements.txt` exists
  2. Push to GitHub: `git push origin main`
  3. Trigger redeploy: Render dashboard → three-dot menu → "Clear build cache and deploy"

**Error: "Cannot find module 'modules'**
- Docker COPY path incorrect
- Solution:
  1. Check root `Dockerfile` exists in repo root
  2. Check `render.yaml` has `dockerfilePath: ./Dockerfile`
  3. Push changes: `git push origin main`
  4. Redeploy

**3. Force redeploy from scratch:**
1. Render dashboard → `smart-resume-screener-backend`
2. Click **"..."** (three-dot menu)
3. Click **"Clear build cache and deploy"**
4. Wait 10+ minutes for full rebuild

#### ❌ Backend Returns 502 Error

**Symptoms:**
- Backend URL shows "502 Bad Gateway"
- Health check keeps failing

**Steps to fix:**

**1. Check if container crashed:**
1. Go to Render dashboard
2. Check status (should be green "Live")
3. If red, click to see error

**2. Check logs for runtime errors:**
1. Render dashboard → `smart-resume-screener-backend`
2. Scroll to "Logs"
3. Look for Python errors (starting with `Traceback`)

**3. Common runtime errors:**

**Error: "ModuleNotFoundError"**
- Python import missing
- Solution: Check `backend/main.py` imports are correct

**Error: "Connection refused"**
- Database connection failed
- Solution:
  1. Check `DATABASE_URL` env var set correctly
  2. Test database connection from your computer:
  ```bash
  psql postgresql://postgres.yytxzajsnldfpitapwzg:Jenny%40may16@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
  ```

**4. Restart container:**
1. Render dashboard → `smart-resume-screener-backend`
2. Click **"..."** menu
3. Click **"Restart"**
4. Wait 30 seconds for restart

#### ❌ Backend Slow or Timing Out

**Symptoms:**
- API requests take > 30 seconds
- "503 Service Unavailable" errors

**Causes:**
- First request after inactivity (cold start)
- ML model initialization takes time
- Starter plan has limited CPU

**Solutions:**

**1. Prevent cold starts:**
- Setup Render Cron Job to ping backend every 10 minutes
- Guide: See [Monitoring & Maintenance](#monitoring--maintenance)

**2. Optimize code:**
- Cache ML models in memory
- Use async processing
- Reduce PDF processing steps

**3. Upgrade plan:**
- Starter ($7/mo) → Standard ($25/mo)
- Standard includes dedicated CPU (faster)

---

### Frontend Issues

#### ❌ Frontend Deployment Failed

**Symptoms:**
- Vercel shows "Deployment failed"

**Steps to fix:**

**1. Check Vercel logs:**
1. Go to https://vercel.com/dashboard
2. Click `smart-resume-screener`
3. Click "Deployments" tab
4. Click on failed deployment
5. Look for error in logs

**2. Common errors:**

**Error: "Cannot find module 'react'"**
- Dependencies not installed
- Solution:
  1. Check `frontend/package.json` exists
  2. Check all imports in `frontend/src/` are correct
  3. Push to GitHub: `git push origin main`
  4. Trigger redeploy: Vercel dashboard → "Redeploy"

**Error: "npm ERR! 404"**
- Package not found on npm
- Solution:
  1. Check `frontend/package.json` for typos
  2. Fix version numbers (e.g., `"react": "^19.0.0"`)
  3. Push to GitHub

**3. Force redeploy:**
1. Vercel dashboard → Deployments tab
2. Click on latest deployment
3. Click **"Redeploy"**
4. Wait 2-3 minutes

#### ❌ Frontend Shows Blank Page

**Symptoms:**
- Frontend URL loads but shows nothing
- No errors in console

**Steps to fix:**

**1. Check DevTools console:**
1. Open frontend URL
2. Press F12
3. Go to "Console" tab
4. Any red errors?

**2. Common issues:**

**Issue: "Failed to fetch API URL"**
- Frontend can't reach backend
- Solution: See [Connecting Frontend to Backend](#connecting-frontend-to-backend)

**Issue: "Module not found"**
- Component import path wrong
- Solution:
  1. Check all imports in `frontend/src/` files
  2. Run locally first: `cd frontend && npm run dev`
  3. Fix errors, push to GitHub, redeploy

**3. Clear cache and refresh:**
1. Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
2. Clear browsing data
3. Refresh page

#### ❌ Cannot Login from Frontend

**Symptoms:**
- Login button doesn't work
- "Cannot connect to server" error

**Steps to fix:**

**1. Check backend is running:**
1. Visit backend health endpoint in browser:
   ```
   https://your-backend-url/
   ```
2. Should show: `{"status":"healthy"}`
3. If not, fix backend first

**2. Check frontend environment variable:**
1. Vercel dashboard → Settings → Environment Variables
2. Find `VITE_API_URL`
3. Should be: `https://your-backend-url` (no trailing slash)
4. If wrong or missing, update and redeploy

**3. Check browser console for CORS errors:**
1. Press F12
2. Go to Console tab
3. Look for "CORS" errors
4. If CORS error:
   - Backend needs to allow requests from frontend domain
   - Update `backend/main.py` CORS settings

**4. Test API manually:**
1. Open browser Developer Console (F12)
2. Go to Console tab
3. Run this:
   ```javascript
   fetch('https://your-backend-url/').then(r => r.json()).then(console.log)
   ```
4. Should show: `{status: "healthy"}`
5. If error, backend is not accessible

---

### Common Connection Issues

#### ❌ "CORS Error" When Frontend Calls Backend

**Error message:** `Access to XMLHttpRequest at 'https://backend-url' from origin 'https://frontend-url' has been blocked by CORS policy`

**Fix:**

**1. Add frontend URL to backend CORS:**
1. Edit `backend/main.py`
2. Find CORS configuration:
   ```python
   allow_origins=["http://localhost:3000", "http://localhost:5173"]
   ```
3. Add your frontend URL:
   ```python
   allow_origins=["http://localhost:3000", "http://localhost:5173", "https://your-frontend-url"]
   ```
4. Replace `your-frontend-url` with actual Vercel URL
5. Example: `"https://smart-resume-screener-abc123.vercel.app"`
6. Push to GitHub: `git add . && git commit -m "fix: add frontend URL to CORS" && git push origin main`
7. Redeploy backend: Render dashboard → ... menu → "Redeploy"

#### ❌ 404 "Not Found" When Frontend Calls Backend

**Error message:** `404 Not Found`

**Cause:** Frontend sending request to wrong backend URL or endpoint doesn't exist

**Fix:**

**1. Check backend URL:**
1. Vercel dashboard → Environment Variables
2. Check `VITE_API_URL` is correct (no typos, no trailing slash)
3. Redeploy if changed: Deployments → ... → Redeploy

**2. Check endpoint exists:**
1. Visit backend endpoint in browser: `https://your-backend-url/api/resume/analyze`
2. If 404, endpoint doesn't exist
3. Check `backend/main.py` has this route defined

#### ❌ "Connection Refused" or "Network Error"

**Error message:** `Failed to fetch` or `Connection refused`

**Cause:** Backend is down or frontend can't reach it

**Fix:**

**1. Verify backend is running:**
1. Go to Render dashboard
2. Check status is "Live" (green)
3. If not, see [Backend Issues](#backend-issues)

**2. Check URL is correct:**
1. Vercel → Environment Variables → `VITE_API_URL`
2. Copy URL and paste in browser
3. Add `/` at end: `https://url/`
4. Should show: `{"status":"healthy"}`
5. If not, URL is wrong

**3. Check internet connection:**
1. Both frontend and backend visible?
2. Try from different network (mobile hotspot)
3. Try from different browser

---

## Monitoring & Maintenance

### Setup Backend Uptime Monitoring

To prevent Render's 15-minute idle timeout from stopping your backend:

#### Option 1: Render Cron Job (Recommended)

**1.1** Go to Render dashboard

**1.2** Click `smart-resume-screener-backend`

**1.3** Go to **"Cron Jobs"** tab

**1.4** Click **"New Cron Job"**

**1.5** Fill in:
- Command: `curl https://<your-backend-url>/`
- Schedule: `0 */10 * * * *` (every 10 minutes)
- Replace `<your-backend-url>` with actual URL

**1.6** Click **"Save"**

This pings your backend every 10 minutes to keep it alive.

#### Option 2: External Uptime Monitor

Use a free service like:
- **Uptimerobot.com** (free tier, 5-minute intervals)
- **Healthchecks.io** (free tier)
- **Pingdom** (limited free tier)

All work the same way: ping your backend URL periodically.

### View Backend Logs

**To debug issues in real-time:**

**1.1** Go to Render dashboard

**1.2** Click `smart-resume-screener-backend`

**1.3** Scroll to **"Logs"** section

**1.4** Logs auto-refresh every few seconds

**Reading logs:**
- 🟢 Green text = normal operations
- 🔵 Blue text = API requests
- 🟡 Yellow text = warnings
- 🔴 Red text = errors (fix these!)

**Example log:**
```
2024-10-25 14:23:45 INFO: Resume analysis started
2024-10-25 14:23:52 INFO: Skills extracted: Python, React, FastAPI
2024-10-25 14:23:55 INFO: Scoring complete: 8.5/10
```

### Monitor Frontend Performance

**1.1** Go to Vercel dashboard

**1.2** Click `smart-resume-screener`

**1.3** Click **"Analytics"** tab

**View metrics:**
- **Requests**: How many users
- **Performance**: Page load times
- **Errors**: Any broken pages

### Update Dependencies

Keep software up-to-date for security and fixes:

#### Backend Updates

**1.1** On your computer, navigate to project:
```bash
cd "c:\Users\jenny\Downloads\Final Resume Screener\smart-resume-screener"
```

**1.2** Update Python packages:
```bash
pip install --upgrade -r backend/requirements.txt
```

**1.3** Check for newer versions:
```bash
pip list --outdated
```

**1.4** Update specific package:
```bash
pip install --upgrade torch
```

**1.5** Update requirements.txt:
```bash
pip freeze > backend/requirements.txt
```

**1.6** Push to GitHub:
```bash
git add backend/requirements.txt
git commit -m "chore: update Python dependencies"
git push origin main
```

**1.7** Render auto-redeploys with new deps

#### Frontend Updates

**1.1** On your computer:
```bash
cd frontend
```

**1.2** Check for outdated packages:
```bash
npm outdated
```

**1.3** Update all packages:
```bash
npm update
```

**1.4** Or update specific package:
```bash
npm install react@latest
```

**1.5** Push to GitHub:
```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: update frontend dependencies"
git push origin main
```

**1.6** Vercel auto-redeploys

### Backup Database

Your Supabase database is automatically backed up, but you can also:

**1.1** Go to https://app.supabase.com

**1.2** Click your project

**1.3** Go to **"Settings"** → **"Backups"**

**1.4** Manual backup: Click **"Request backup"**

---

## Summary Checklist

### ✅ Deployment Checklist

- [ ] **Backend (Render)**
  - [ ] Render account created
  - [ ] GitHub connected to Render
  - [ ] Web Service created from repo
  - [ ] All 6 environment variables set
  - [ ] Deployment completed (shows "Live")
  - [ ] Backend URL saved: `https://...`
  - [ ] Health check passed: `/` returns `{"status":"healthy"}`
  - [ ] FastAPI docs accessible: `/docs` shows endpoints

- [ ] **Frontend (Vercel)**
  - [ ] Vercel account created
  - [ ] GitHub connected to Vercel
  - [ ] Project imported from repo
  - [ ] `VITE_API_URL` environment variable set with backend URL
  - [ ] Deployment completed
  - [ ] Frontend URL saved: `https://...`
  - [ ] Frontend loads without errors
  - [ ] Console has no red errors

- [ ] **Testing**
  - [ ] Backend `/` endpoint returns healthy
  - [ ] Frontend loads and displays
  - [ ] Can register new account
  - [ ] Can login with account
  - [ ] Can upload resume PDF
  - [ ] Resume analysis completes
  - [ ] Results display correctly
  - [ ] Mobile view looks good

- [ ] **Maintenance**
  - [ ] Uptime monitor setup (optional but recommended)
  - [ ] Familiar with viewing logs
  - [ ] Know how to restart backend/frontend
  - [ ] Know how to update dependencies

---

## Additional Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

---

## Need Help?

If something goes wrong:

1. **Check the logs** (backend: Render logs, frontend: browser console)
2. **Read error message carefully** (usually tells you what's wrong)
3. **Try refreshing** (often fixes temporary glitches)
4. **Check connection between frontend and backend** (most common issue)
5. **Verify all environment variables** (copy-paste to avoid typos)
6. **Restart services** (Render: click ... → Restart, Vercel: click Redeploy)

**Last resort:** Delete deployment and start fresh from Step 1

---

**🎉 Congratulations!** Your Smart Resume Screener is now live on the internet!

Share your frontend URL with users to let them try it out.
