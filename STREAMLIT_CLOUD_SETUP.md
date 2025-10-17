# 🚀 Streamlit Cloud Setup Guide

## ⚠️ IMPORTANT: Supabase Database Configuration

Your app needs **Streamlit Secrets** configured to connect to the Supabase database.

### 📋 Step-by-Step Instructions

#### 1. Go to Streamlit Cloud Dashboard
- Visit: https://share.streamlit.io/
- Find your `smart-resume-screener` app
- Click on the app name to open settings

#### 2. Add Secrets
- Click **⚙️ Settings** (gear icon in top right)
- Click **🔐 Secrets** in the left sidebar
- Paste this content into the secrets editor (replace with your actual values):

```toml
# Google Gemini API Key (get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY = "your_gemini_api_key_here"

# PostgreSQL Database URL (from Supabase Dashboard → Settings → Database)
# Format: postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
# IMPORTANT: URL-encode special characters in password (@ becomes %40, # becomes %23, etc.)
DATABASE_URL = "postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres"

# Hugging Face Hub Token (get from https://huggingface.co/settings/tokens)
HF_TOKEN = "your_hf_token_here"
```

**Where to find your values:**
- `GEMINI_API_KEY`: Your Google AI API key from the `.env` file
- `DATABASE_URL`: Your Supabase connection string (remember to URL-encode the password)
- `HF_TOKEN`: Your Hugging Face token from the `.env` file

#### 3. Save & Reboot
- Click **Save** button
- Click **Reboot app** to apply changes

---

## ✅ Verification

After rebooting, you should see:
- ✅ **"Database connected successfully!"** message on app load
- 💾 **"Saved to database!"** message after each analysis
- 📊 Recent analyses appearing in the **Recent** tab

---

## 🔍 Troubleshooting

### Issue: "Database not connected" warning

**Solution 1: Check Secrets Format**
- Ensure no extra spaces before/after `=`
- Use quotes around values: `DATABASE_URL = "postgresql://..."`
- Make sure password `@` is encoded as `%40`

**Solution 2: Verify Supabase Connection**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **Database**
4. Copy the **Connection string** (URI format)
5. Replace `[YOUR-PASSWORD]` with your actual password, **URL-encoded**
   - Example: If password is `MyP@ss`, use `MyP%40ss` (@ becomes %40)

**Solution 3: Check App Logs**
- In Streamlit Cloud, click **Manage app** → **Logs**
- Look for database connection messages:
  - ✅ "PostgreSQL connected successfully!" = Working
  - ❌ "PostgreSQL connection failed" = Check secrets

---

## 📊 Database Tables

Your Supabase database has these tables:

### `resumes` table
- Stores candidate information
- Columns: id, name, email, phone, text, chunks, entities, technical_skills, created_at

### `analyses` table
- Stores screening results
- Columns: id, resume_id, jd_text, plan, profile, coverage, cue_alignment, final_analysis, scores, created_at

---

## 🔗 Quick Links

- **Streamlit Cloud**: https://share.streamlit.io/
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Your GitHub Repo**: https://github.com/nihcastics/smart-resume-screener

---

## 🆘 Need Help?

If database still not connecting after following these steps:
1. Check Streamlit Cloud logs for specific error messages
2. Verify Supabase project is active (not paused)
3. Test connection string format is correct
4. Ensure password is properly URL-encoded in DATABASE_URL
