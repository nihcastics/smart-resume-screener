#!/usr/bin/env python3
"""
Smart Resume Screener - Setup Script
Ensures all dependencies are installed and configured properly.
"""

import sys
import subprocess
import os
from pathlib import Path

def print_step(step_num, message):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {message}")
    print(f"{'='*60}")

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("\nCreating .env template...")
        with open(".env", "w") as f:
            f.write("""# Environment Variables Configuration

# Google Gemini API Key (REQUIRED)
# Get your free API key at: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# MongoDB Connection URI (Optional)
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/dbname
MONGO_URI=

# Hugging Face Hub Token (Optional - for model downloads)
HF_TOKEN=
""")
        print("✅ Created .env template file")
        print("⚠️  Please edit .env and add your GEMINI_API_KEY")
        return False
    
    # Check if API key is set
    with open(".env", "r") as f:
        content = f.read()
        if "GEMINI_API_KEY=your_api_key_here" in content or "GEMINI_API_KEY=" not in content:
            print("⚠️  .env file exists but GEMINI_API_KEY is not configured")
            print("Please edit .env and add your API key from: https://makersuite.google.com/app/apikey")
            return False
    
    print("✅ .env file configured")
    return True

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        🎯 Smart Resume Screener - Setup Wizard          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print("✅ Python version is compatible")
    
    # Step 2: Install requirements
    print_step(2, "Installing Python packages")
    success = run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Package installation"
    )
    if not success:
        print("⚠️  Some packages may have failed to install. Continuing...")
    
    # Step 3: Verify spaCy model
    print_step(3, "Verifying spaCy model")
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model 'en_core_web_sm' is installed")
        except OSError:
            print("⚠️  spaCy model not found, attempting to download...")
            run_command(
                [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
                "spaCy model download"
            )
    except ImportError:
        print("❌ spaCy not installed. Please run: pip install spacy")
        return False
    
    # Step 4: Check .env file
    print_step(4, "Checking environment configuration")
    env_ok = check_env_file()
    
    # Step 5: Test imports
    print_step(5, "Testing critical imports")
    imports = [
        ("streamlit", "Streamlit"),
        ("pymupdf", "PyMuPDF"),
        ("sentence_transformers", "Sentence Transformers"),
        ("google.generativeai", "Google Generative AI"),
        ("pymongo", "PyMongo"),
    ]
    
    all_imports_ok = True
    for module, name in imports:
        try:
            __import__(module)
            print(f"✅ {name} - OK")
        except ImportError:
            print(f"❌ {name} - NOT FOUND")
            all_imports_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    if all_imports_ok and env_ok:
        print("✅ All checks passed!")
        print("\n🚀 You can now run the application:")
        print("   streamlit run app.py")
    elif all_imports_ok and not env_ok:
        print("⚠️  Dependencies installed but environment not configured")
        print("\n📝 Next steps:")
        print("   1. Edit .env file and add your GEMINI_API_KEY")
        print("   2. Get API key from: https://makersuite.google.com/app/apikey")
        print("   3. Run: streamlit run app.py")
    else:
        print("❌ Some dependencies are missing")
        print("\n📝 Next steps:")
        print("   1. Run: pip install -r requirements.txt")
        print("   2. Configure .env file with your API key")
        print("   3. Run this setup script again")
    
    print("\n" + "="*60)
    return all_imports_ok and env_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
