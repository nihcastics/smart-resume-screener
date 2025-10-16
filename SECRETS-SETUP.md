# 🔑 STREAMLIT CLOUD SECRETS - COPY THIS EXACTLY

## ⚠️ IMPORTANT: Add These Secrets to Your Streamlit Cloud App

### How to Add Secrets:

1. Go to **https://share.streamlit.io**
2. Click on your app
3. Click **"Settings"** (⚙️ icon)
4. Click **"Secrets"** in the left menu
5. **Copy the content below** and paste it into the secrets editor
6. Click **"Save"**
7. The app will automatically restart

---

## 📋 Copy This into Streamlit Cloud Secrets:

**IMPORTANT**: Get your actual values from your local `.env` file!

```toml
# Google Gemini API Key
GEMINI_API_KEY = "paste_your_gemini_key_from_env_file"

# MongoDB Connection URI
MONGO_URI = "paste_your_mongodb_uri_from_env_file"

# Hugging Face Token (for model downloads)
HF_TOKEN = "paste_your_huggingface_token_from_env_file"
```

### 📝 Your Actual Values (from .env file):
- GEMINI_API_KEY: Starts with `AIzaSy...`
- MONGO_URI: Starts with `mongodb+srv://...`
- HF_TOKEN: Starts with `hf_...`

Copy these from your `.env` file and paste them in Streamlit Cloud secrets!

---

## ✅ Verification:

After saving, your app should:
- ✅ Connect to Google Gemini successfully
- ✅ Connect to MongoDB successfully
- ✅ No more "Gemini model unavailable" error

---

## 🔐 Security Note:

- These values are from your local `.env` file
- They are stored securely in Streamlit Cloud
- They are NOT visible in your GitHub repository (gitignored)
- Only you can see them in your Streamlit Cloud dashboard

---

## 🆘 Still Having Issues?

Make sure:
1. ✅ No extra spaces or quotes around the values
2. ✅ TOML format is correct (key = "value")
3. ✅ Secrets are saved (click Save button)
4. ✅ App has restarted after saving secrets
