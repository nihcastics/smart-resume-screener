# 🔧 Fix: "Cannot assign requested address" Error

## Problem
```
❌ Database connection failed: connection to server at "db.eiqqakeekdkshykysoxb.supabase.co" 
(2406:da1a:6b0:f604:8aea:ad59:f5ae:cee6), port 5432 failed: Cannot assign requested address
```

This error means the IPv6 address is failing. **Solution: Use Supabase Connection Pooler instead.**

---

## ✅ Solution: Use Connection Pooler

The Connection Pooler is more reliable and avoids IPv6 issues.

### Step 1: Get Pooler Connection String

1. Go to **Supabase Dashboard**: https://supabase.com/dashboard
2. Select your project: `smart-resume-screener` (or your project name)
3. Click **Settings** (gear icon) in left sidebar
4. Click **Database**
5. Scroll down to **Connection Pooling** section
6. Find the **"Transaction"** mode connection string

It will look like this:
```
postgresql://postgres.eiqqakeekdkshykysoxb:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

### Step 2: Prepare Your Connection String

**Replace `[YOUR-PASSWORD]` with your actual password, URL-encoded:**

If your password is: `Jenny@may16`
URL-encode it to: `Jenny%40may16` (@ becomes %40)

Final connection string:
```
postgresql://postgres.eiqqakeekdkshykysoxb:Jenny%40may16@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

### Step 3: Update Streamlit Secrets

1. Go to **Streamlit Cloud**: https://share.streamlit.io/
2. Find your app: `smart-resume-screener`
3. Click **Settings** ⚙️ → **Secrets** 🔐
4. Update the `DATABASE_URL` line with your pooler URL:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
DATABASE_URL = "postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true"
HF_TOKEN = "your_hf_token_here"
```

**Replace with YOUR actual values from your `.env` file!**

5. Click **Save**
6. Click **Reboot app**

---

## 🎯 Key Differences

| Direct Connection | Connection Pooler |
|------------------|-------------------|
| `db.xxxxx.supabase.co` | `aws-0-us-east-1.pooler.supabase.com` |
| Port `5432` | Port `6543` |
| Can fail with IPv6 | ✅ Works reliably |
| No connection pooling | ✅ Better performance |

---

## ✅ Verification

After rebooting, you should see:
- ✅ **"💾 Database connected successfully!"** (no errors)
- ✅ Analyses saving with ID confirmation
- ✅ Recent tab populating with saved data

---

## 📝 Local Development (.env file)

Update your local `.env` file with the connection pooler URL:

```env
# Use connection pooler for both cloud and local
DATABASE_URL=postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

Replace with your actual connection pooler string from Supabase dashboard.
This ensures consistency between local and cloud environments.

---

## 🆘 Still Having Issues?

If connection still fails:

1. **Check Supabase Project Status**
   - Dashboard → Make sure project is not paused
   - Check if database is active

2. **Verify Password Encoding**
   - Special characters must be URL-encoded
   - `@` → `%40`
   - `#` → `%23`
   - `&` → `%26`

3. **Check Streamlit Cloud Logs**
   - Manage app → Logs
   - Look for detailed error messages

4. **Test Connection Locally**
   ```bash
   python -c "import psycopg2; conn = psycopg2.connect('your_pooler_url_here'); print('✅ Connected!')"
   ```

---

✅ **This should fix your connection issue!** The pooler is the recommended way to connect to Supabase from cloud platforms like Streamlit.
