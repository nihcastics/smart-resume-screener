# 🎯 Quick Supabase Setup for Streamlit Cloud

## Step 1: Add Secrets to Streamlit Cloud

1. Go to: https://share.streamlit.io/
2. Find your app: `smart-resume-screener`
3. Click **Settings** ⚙️
4. Click **Secrets** 🔐
5. Paste this (replace with YOUR actual values from `.env` file):

```toml
GEMINI_API_KEY = "your_gemini_key_from_env_file"
DATABASE_URL = "your_database_url_from_env_file"
HF_TOKEN = "your_hf_token_from_env_file"
```

6. Click **Save**
7. Click **Reboot app**

## Step 2: Verify Connection

After reboot, check for these messages in your app:

✅ **Success indicators:**
- "💾 Database connected successfully!" (on app load)
- "💾 Saved to database! (Resume ID: X, Analysis ID: Y)" (after analysis)
- Recent tab shows saved analyses

❌ **Error indicators:**
- "⚠️ Database not connected" → Secrets not configured
- "❌ Database connection failed" → Check DATABASE_URL format

## Quick Test

Run a resume analysis and look for:
1. Success message: "💾 Saved to database! (Resume ID: 1, Analysis ID: 1)"
2. Go to Recent tab → Should show the analysis
3. In Supabase dashboard → Table Editor → Should see data in `resumes` and `analyses` tables

## Troubleshooting

**Problem:** "Database not connected"
**Fix:** Make sure secrets are added in Streamlit Cloud (not just `.env` file)

**Problem:** "Connection failed"
**Fix:** Check DATABASE_URL has `%40` instead of `@` in password

**Problem:** "No data in Recent tab"
**Fix:** Check Streamlit Cloud logs for specific error messages

---

✅ All set! Database will now save every analysis automatically.
