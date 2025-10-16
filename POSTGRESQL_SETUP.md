# PostgreSQL Setup Guide for Smart Resume Screener

## ✅ Migration Complete!
The app has been successfully migrated from MongoDB to PostgreSQL.

---

## 🎯 Quick Setup Options

### **Option 1: Supabase (Recommended - Free Forever Tier)**

**Best for:** Production deployment, automatic backups, great free tier

1. **Create Account**: Go to [supabase.com](https://supabase.com) and sign up
2. **Create New Project**:
   - Click "New Project"
   - Choose a name: `resume-screener-db`
   - Set database password (save this!)
   - Select region (closest to you)
   - Wait 2 minutes for provisioning

3. **Get Connection String**:
   - Go to Project Settings → Database
   - Scroll to "Connection string" → Select "URI"
   - Copy the connection string (looks like):
     ```
     postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
     ```
   - **Important**: Replace `[YOUR-PASSWORD]` with your actual password

4. **Add to Your Project**:
   - Open `.env` file (or create it in project root)
   - Add this line:
     ```env
     DATABASE_URL=postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
     ```

5. **Done!** Tables will be created automatically on first run.

**Free Tier Limits:**
- ✅ 500 MB database (enough for thousands of resumes)
- ✅ Unlimited API requests
- ✅ Automatic backups
- ✅ No credit card required

---

### **Option 2: Neon (Serverless PostgreSQL)**

**Best for:** Serverless deployment, automatic scaling

1. **Create Account**: Go to [neon.tech](https://neon.tech)
2. **Create New Project**:
   - Click "Create Project"
   - Name: `resume-screener`
   - Region: Choose closest
3. **Copy Connection String**:
   - On dashboard, click "Connection Details"
   - Copy "Connection string"
   - Example:
     ```
     postgresql://user:pass@ep-cool-forest-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
     ```
4. **Add to `.env`**:
   ```env
   DATABASE_URL=your_connection_string_here
   ```

**Free Tier:**
- ✅ 512 MB storage
- ✅ Auto-suspend after inactivity (saves resources)
- ✅ Instant wake-up

---

### **Option 3: Railway (Full Platform)**

**Best for:** Want database + hosting in one place

1. **Create Account**: [railway.app](https://railway.app)
2. **New Project** → **Provision PostgreSQL**
3. **Get Connection String**:
   - Click PostgreSQL service
   - Go to "Connect" tab
   - Copy "Postgres Connection URL"
4. **Add to `.env`**:
   ```env
   DATABASE_URL=your_railway_connection_string
   ```

**Free Tier:**
- ✅ $5 credit/month (enough for hobby projects)
- ✅ Can also host your Streamlit app here

---

### **Option 4: ElephantSQL (Classic PostgreSQL Hosting)**

**Best for:** Simple, straightforward PostgreSQL hosting

1. **Sign Up**: [elephantsql.com](https://www.elephantsql.com)
2. **Create Instance**:
   - Click "Create New Instance"
   - Name: `resume-screener`
   - Plan: "Tiny Turtle" (free)
   - Select region
3. **Get URL**:
   - Click on your instance
   - Copy the URL from "Details" section
4. **Add to `.env`**:
   ```env
   DATABASE_URL=postgres://user:pass@ruby.db.elephantsql.com/database
   ```

**Free Tier:**
- ✅ 20 MB storage
- ✅ 5 concurrent connections

---

### **Option 5: Local PostgreSQL (Development)**

**Best for:** Local testing, no internet required

#### Windows:
1. Download PostgreSQL: [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Install with default settings
3. Remember the password you set for `postgres` user
4. Open pgAdmin 4 (installed with PostgreSQL)
5. Create database: `resume_screener_db`
6. Connection string:
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/resume_screener_db
   ```

#### Mac (with Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15
createdb resume_screener_db
```
Connection string:
```env
DATABASE_URL=postgresql://localhost:5432/resume_screener_db
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb resume_screener_db
```
Connection string:
```env
DATABASE_URL=postgresql://postgres@localhost:5432/resume_screener_db
```

---

## 🔧 Installation Steps

### 1. **Install Dependencies**

```bash
# Navigate to project directory
cd "c:\Users\jenny\Downloads\Final Resume Screener\smart-resume-screener"

# Activate virtual environment
.\env\Scripts\activate

# Install PostgreSQL driver
pip install psycopg2-binary
```

### 2. **Configure Database**

Create or edit `.env` file in project root:

```env
# Gemini AI (required)
GEMINI_API_KEY=your_gemini_api_key_here

# PostgreSQL Database (choose one option above)
DATABASE_URL=postgresql://user:password@host:port/database

# Optional: Sentence Transformer Model
SENTENCE_MODEL_NAME=all-mpnet-base-v2
```

### 3. **Test Connection**

Run the app:
```bash
streamlit run app.py
```

Look for these messages in terminal:
- ✅ `PostgreSQL connected successfully!`
- ✅ `Database ready with tables: resumes, analyses`

If you see errors:
- ❌ Check your `DATABASE_URL` format
- ❌ Ensure database exists and is accessible
- ❌ Verify firewall allows connection

---

## 📊 Database Schema

The app automatically creates these tables:

### **`resumes` table**
```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    text TEXT,
    chunks JSONB,
    entities JSONB,
    technical_skills JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **`analyses` table**
```sql
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
    jd_text TEXT,
    plan JSONB,
    profile JSONB,
    coverage JSONB,
    cue_alignment JSONB,
    final_analysis JSONB,
    semantic_score REAL,
    coverage_score REAL,
    llm_fit_score REAL,
    final_score REAL,
    fit_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Indexes** (for performance)
- `resumes.email`
- `resumes.created_at`
- `analyses.created_at`
- `analyses.resume_id`

---

## 🎯 What Changed from MongoDB?

### Code Changes:
- ✅ Replaced `pymongo` with `psycopg2-binary`
- ✅ `init_mongodb()` → `init_postgresql()`
- ✅ SQL queries instead of MongoDB operations
- ✅ JSONB columns for flexible nested data
- ✅ Proper foreign keys and relationships

### Environment Variables:
- ❌ **Old**: `MONGO_URI=mongodb+srv://...`
- ✅ **New**: `DATABASE_URL=postgresql://...`

### Benefits:
- ✅ Structured data with proper relationships
- ✅ SQL queries for complex analytics
- ✅ Better data integrity (ACID compliance)
- ✅ More hosting options (Supabase, Neon, Railway, etc.)
- ✅ Easier to query and analyze resume data

---

## 🔍 Verification Checklist

After setup, verify everything works:

1. **Database Connection**:
   - [ ] Terminal shows: `✅ PostgreSQL connected successfully!`
   - [ ] No error messages about DATABASE_URL

2. **Tables Created**:
   - [ ] Terminal shows: `📊 Database ready with tables: resumes, analyses`
   - [ ] Check in Supabase/Neon dashboard: Tables exist

3. **Data Saving**:
   - [ ] Upload a resume and run analysis
   - [ ] See: `💾 Analysis saved to database successfully!`
   - [ ] Check "Recent" tab - see your analysis

4. **Data Retrieval**:
   - [ ] "Recent" tab loads without errors
   - [ ] Can see previously analyzed resumes

---

## 🆘 Troubleshooting

### Error: "could not connect to server"
**Solution**: Check your DATABASE_URL format and internet connection

### Error: "password authentication failed"
**Solution**: Verify password in DATABASE_URL matches your database password

### Error: "database does not exist"
**Solution**: 
- For Supabase/Neon: Database auto-created, use provided URL
- For local: Run `createdb resume_screener_db`

### Error: "SSL connection required"
**Solution**: Add `?sslmode=require` to end of DATABASE_URL:
```env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### Recent tab shows no data
**Solution**: Normal if fresh database. Upload and analyze a resume first.

---

## 🚀 Next Steps

1. **Choose a database option** (Supabase recommended)
2. **Get your DATABASE_URL**
3. **Add to `.env` file**
4. **Install psycopg2-binary**: `pip install psycopg2-binary`
5. **Run the app**: `streamlit run app.py`
6. **Test with a resume**

---

## 📞 Need Help?

Common issues solved:
- Database not connecting → Check DATABASE_URL format
- Tables not created → Check database permissions
- Data not saving → Check terminal for error messages
- Slow queries → Add more indexes (see schema above)

The app will continue working even if database connection fails - it just won't save/load history.

---

**✨ You're all set! The app now uses PostgreSQL for better performance and reliability.**
