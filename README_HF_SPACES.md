# Deploying to Hugging Face Spaces

This guide will help you deploy the Smart Resume Screener backend to Hugging Face Spaces for **free**.

## Prerequisites

- Hugging Face account (free): https://huggingface.co/join
- HF token (create in account settings): https://huggingface.co/settings/tokens
- Git installed

## Step 1: Create a Space on Hugging Face

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name**: `smart-resume-screener-backend`
   - **License**: OpenRAIL
   - **Space SDK**: `Docker`
   - **Space hardware**: `CPU basic` (free tier)
3. Click **Create Space**

## Step 2: Set Environment Variables

In your Space settings (Settings tab), add these secrets:

```
GOOGLE_API_KEY=your_google_api_key_here
JWT_SECRET=your_jwt_secret_here
DATABASE_URL=your_database_url_here
GEMINI_MODEL_NAME=gemini-pro
SENTENCE_MODEL_NAME=all-MiniLM-L6-v2
PYTHONUNBUFFERED=1
```

## Step 3: Clone and Configure

```bash
# Clone your GitHub repo
git clone https://github.com/nihcastics/smart-resume-screener.git
cd smart-resume-screener

# Add HF Spaces as remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/smart-resume-screener-backend
```

## Step 4: Push to Hugging Face Spaces

```bash
git push hf main --force
```

The deployment will start automatically. Check the **App** tab to see the live backend!

## Testing

Once deployed, the API will be available at:
- `https://YOUR_USERNAME-smart-resume-screener-backend.hf.space`

Test the health endpoint:
```bash
curl https://YOUR_USERNAME-smart-resume-screener-backend.hf.space/health
```

## Frontend Configuration

Update your frontend to use the HF Spaces backend URL:

```javascript
// frontend/src/services/api.js
const apiUrl = import.meta.env.VITE_API_URL || 'https://YOUR_USERNAME-smart-resume-screener-backend.hf.space';
```

Or set the environment variable in Vercel:
```
VITE_API_URL=https://YOUR_USERNAME-smart-resume-screener-backend.hf.space
```

## Troubleshooting

**Build fails due to disk space:**
- HF Spaces has 50GB storage, but builds can be limited
- The Docker image is optimized to stay under 4GB

**Cold starts are slow:**
- ML models load on first request (30-60 seconds)
- This is normal - subsequent requests are faster

**Out of memory errors:**
- HF Spaces free tier has 16GB RAM
- Our app uses ~2-3GB for ML models
- Run only 1 uvicorn worker (already configured)

## Cost

✅ **Completely FREE**
- No credit card required
- Unlimited space for code/models
- Free CPU tier includes enough for this app

## Next Steps

1. Deploy frontend to Vercel (keep existing setup)
2. Update CORS in backend/main.py to include Vercel URL
3. Test end-to-end integration
