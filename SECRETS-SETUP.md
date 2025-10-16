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

## 📋 Copy This (Replace with Your Values If Different):

```toml
# Google Gemini API Key
GEMINI_API_KEY = "AIzaSyCm22mt3bsmj4jVyUaJxMA1dTvdSTq4U_Y"

# MongoDB Connection URI
MONGO_URI = "mongodb+srv://sachinshiva1612_db_user:IFNVixjfLJQbXqt@cluster0.irfzzbt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
```

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
