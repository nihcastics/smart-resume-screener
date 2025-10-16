# 🚨 Streamlit Cloud Deployment Troubleshooting

## Current Status: Build Failing

If you're seeing `installer returned a non-zero exit code`, try these solutions in order:

---

## ✅ Solution 1: Reboot App (Try This First)

1. Go to your Streamlit Cloud dashboard: https://share.streamlit.io
2. Find your app in the list
3. Click the **⋮** menu (three dots)
4. Select **"Reboot app"**
5. Wait 10-15 minutes for full rebuild

**Latest commit**: `f210ab1` includes:
- ✅ Minimal requirements.txt
- ✅ setup.sh for spaCy model
- ✅ Optimized build order

---

## ✅ Solution 2: Clear Cache & Redeploy

1. In Streamlit Cloud dashboard, click your app
2. Click **Settings** (⚙️)
3. Scroll to **"Advanced settings"**
4. Click **"Clear cache"**
5. Click **"Reboot app"**

---

## ✅ Solution 3: Check Build Logs

In your Streamlit Cloud app dashboard:
1. Click **"Manage app"**
2. Look at the build logs
3. Find the specific package causing the error
4. If you see a specific package failing, let me know which one

Common errors:
- **torch timeout**: The ML model is too large
- **faiss-cpu build error**: Needs compilation
- **sentence-transformers**: Depends on torch

---

## 🚀 Solution 4: Alternative Deployment - Hugging Face Spaces

Hugging Face Spaces is **BETTER** for ML apps with heavy dependencies:

### Why Hugging Face Spaces?
- ✅ Handles torch/transformers better
- ✅ No timeout issues with ML models
- ✅ Built for AI/ML applications
- ✅ FREE tier available

### Deploy on Hugging Face:

1. **Create account**: https://huggingface.co/join
2. **Create new Space**:
   - Go to: https://huggingface.co/new-space
   - Name: `smart-resume-screener`
   - License: MIT
   - SDK: **Streamlit**
   - Click "Create Space"

3. **Connect GitHub repo**:
   ```bash
   # In your local terminal:
   cd "c:\Users\jenny\Downloads\Final Resume Screener\smart-resume-screener"
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/smart-resume-screener
   git push hf main
   ```

4. **Add secrets** in Hugging Face:
   - Go to Space Settings → Secrets
   - Add:
     ```
     GOOGLE_API_KEY=your_key
     MONGODB_URI=your_uri
     ```

5. **App will be live** at: `https://huggingface.co/spaces/YOUR_USERNAME/smart-resume-screener`

---

## 🔧 Solution 5: Simplify Dependencies (Last Resort)

If all else fails, we can create a lighter version that:
- Uses simpler NLP (no transformers)
- Removes FAISS vector search
- Keeps core functionality

Let me know if you want this version.

---

## 📊 What to Try Now:

1. **First**: Try rebooting the app in Streamlit Cloud (Solution 1)
2. **If that fails**: Clear cache (Solution 2)
3. **If still failing**: Share the specific error from build logs
4. **Alternative**: Deploy to Hugging Face Spaces (Solution 4) - Recommended for ML apps

---

## 💬 Need Help?

Tell me:
1. What error message you see in the build logs
2. Which solution you tried
3. Whether you prefer Streamlit Cloud or Hugging Face Spaces

I can then provide targeted fixes!
