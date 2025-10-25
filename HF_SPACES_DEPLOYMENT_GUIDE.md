# Hugging Face Spaces Deployment - Step by Step

Your backend is now ready to deploy on **Hugging Face Spaces completely for FREE**. Follow these steps exactly:

## Step 1: Login to Hugging Face

1. Go to https://huggingface.co
2. Sign in with your account
3. If you don't have an account, create one (free)

## Step 2: Create a New Space

1. Go to https://huggingface.co/new-space
2. Fill in the form:
   - **Owner**: Select your username
   - **Space name**: `smart-resume-screener-backend`
   - **License**: Select `OpenRAIL` (or any license)
   - **Space SDK**: Select `Docker` (IMPORTANT!)
   - **Space hardware**: Select `CPU basic` (free, sufficient for this app)
3. Click **Create Space**
4. Wait for the page to load

## Step 3: Configure Environment Variables

1. In the Spaces page, click the **Settings** button (gear icon)
2. Go to the **Variables and secrets** section
3. Click **New variable** and add these secrets:

| Name | Value |
|------|-------|
| `GOOGLE_API_KEY` | Your Google Gemini API key |
| `JWT_SECRET` | Any secure random string (e.g., `your-secret-key-12345`) |
| `DATABASE_URL` | Your Supabase PostgreSQL URL |
| `GEMINI_MODEL_NAME` | `gemini-pro` |
| `SENTENCE_MODEL_NAME` | `all-MiniLM-L6-v2` |
| `PYTHONUNBUFFERED` | `1` |

4. Click **Save** after adding each variable

## Step 4: Get Your HF Token

1. Go to https://huggingface.co/settings/tokens
2. Click **New token**
3. Select **Write** access
4. Copy the token
5. Keep this token safe (don't share it!)

## Step 5: Push Your Code to HF Spaces

Open PowerShell and run these commands:

```powershell
cd "c:\Users\jenny\Downloads\Final Resume Screener\smart-resume-screener"

# Configure Git with HF token
git config --global user.email "your_email@example.com"
git config --global user.name "Your Name"

# Add HF Spaces as a remote (replace YOUR_USERNAME with your HF username)
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/smart-resume-screener-backend

# Push the code
git push hf main --force
```

**You'll be prompted for a password** - use your HF token as the password.

## Step 6: Wait for Deployment

1. Go back to your Space page on HF
2. You'll see a **Building** status
3. The build will take **10-15 minutes** (first time is slow because it's downloading ML models)
4. Watch the **Build logs** tab to see progress
5. When it says **"Running"**, your backend is live!

## Step 7: Get Your Backend URL

1. Look at the top of your Space page
2. You'll see a URL like: `https://YOUR_USERNAME-smart-resume-screener-backend.hf.space`
3. This is your backend URL!

## Step 8: Test Your Backend

1. Open your browser and go to: `https://YOUR_USERNAME-smart-resume-screener-backend.hf.space/health`
2. You should see JSON response: 
```json
{
  "status": "healthy",
  "service": "Smart Resume Screener Backend",
  "deployed_on": "Hugging Face Spaces"
}
```

3. To see API docs: `https://YOUR_USERNAME-smart-resume-screener-backend.hf.space/docs`

## Step 9: Update Frontend

Now update your frontend to use the HF Spaces backend:

1. Open `frontend/src/services/api.js`
2. Update the baseURL line to use your HF backend URL:

```javascript
// CHANGE THIS:
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// TO THIS:
const api = axios.create({
  baseURL: process.env.VITE_API_URL || 'http://localhost:8000',
});
```

3. In Vercel dashboard, add environment variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://YOUR_USERNAME-smart-resume-screener-backend.hf.space`

4. Redeploy frontend on Vercel

## Step 10: Test End-to-End

1. Go to your Vercel frontend URL
2. Register/Login
3. Upload a resume
4. Enter a job description
5. Click Analyze
6. Should work perfectly now!

---

## Troubleshooting

### Build Failed
- Check **Build logs** tab for errors
- Common issue: Missing environment variables - make sure all 6 are set

### App crashes after building
- Check **Logs** tab to see error messages
- Common issue: Out of memory - HF Spaces free tier has 16GB, our app uses ~3GB for models
- Solution: This is normal, wait 2-3 minutes for models to fully load

### Slow first request (30-60 seconds)
- **This is normal!** ML models load on first request
- Subsequent requests will be much faster
- HF Spaces will auto-sleep after inactivity and wake up when you access it

### CORS errors in browser
- Update Vercel environment variable to correct HF Spaces URL
- Make sure `VITE_API_URL` is set in Vercel

### Can't push code
- Make sure you're using HF token as password (not your HF password)
- Run: `git config --global credential.helper store` to save credentials

---

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| HF Spaces Backend | **FREE** | CPU basic tier, unlimited repos |
| Vercel Frontend | **FREE** | Hobby tier, auto-deploys |
| Supabase Database | **FREE** | 500MB storage, generous free tier |
| Google Gemini API | **FREE** | 60 calls/min free tier |
| **TOTAL** | **$0/month** | ✅ Completely FREE |

---

## Next Steps After Deployment

1. ✅ Backend running on HF Spaces
2. ✅ Frontend running on Vercel
3. ✅ Database on Supabase
4. **Test the full workflow**
5. **Share with friends**
6. **Celebrate! 🎉**

---

## Support

If you have issues:
1. Check HF Spaces **Build logs** and **App logs**
2. Check Vercel **Deployments** tab
3. Verify all environment variables are set correctly
4. Make sure database URL is correct

Happy deploying! 🚀
