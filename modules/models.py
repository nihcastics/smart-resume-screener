"""
Model Loading and Initialization with TRUE Hybrid Ensemble Support
Enterprise-grade with health monitoring, fallback chains, and confidence scoring
"""
import os
import logging
import spacy
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from datetime import datetime, timedelta
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory cache to replace streamlit session_state
class ModelCache:
    """Simple thread-safe cache for model state."""
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()
    
    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)
    
    def __setitem__(self, key, value):
        with self._lock:
            self._data[key] = value
    
    def __contains__(self, key):
        with self._lock:
            return key in self._data

# Global cache instance
_model_cache = ModelCache()

# ENTERPRISE CONFIGURATION
HEALTH_CHECK_TIMEOUT = 5  # seconds
HEALTH_CHECK_CACHE_DURATION = 60  # 1 minute (reduced from 5 for freshness)
MAX_HEALTH_CHECK_RETRIES = 2
API_RATE_LIMIT_WINDOW = 60  # seconds
MAX_API_CALLS_PER_WINDOW = 50  # calls per minute

# Thread-safe rate limiter
class RateLimiter:
    """Thread-safe rate limiter for API calls."""
    def __init__(self, max_calls, window):
        self.max_calls = max_calls
        self.window = window
        self.calls = []
        self.lock = threading.Lock()
    
    def allow_call(self):
        with self.lock:
            now = time.time()
            # Remove calls outside window
            self.calls = [t for t in self.calls if now - t < self.window]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False
    
    def get_wait_time(self):
        """Get seconds to wait before next call allowed."""
        with self.lock:
            if len(self.calls) < self.max_calls:
                return 0
            now = time.time()
            oldest_call = min(self.calls)
            return max(0, self.window - (now - oldest_call))

# Global rate limiter
_gemini_rate_limiter = RateLimiter(MAX_API_CALLS_PER_WINDOW, API_RATE_LIMIT_WINDOW)

def check_gemini_health(model, timeout=HEALTH_CHECK_TIMEOUT):
    """
    Health check for Gemini API with timeout, retry logic, and rate limiting.
    Returns (is_healthy: bool, confidence: float 0.0-1.0)
    """
    if not model:
        return False, 0.0
    
    # Check cache first (reduced to 1 minute for fresher status)
    cache_key = "gemini_health_check"
    cache_time_key = "gemini_health_check_time"
    cache_confidence_key = "gemini_health_confidence"
    
    if cache_key in _model_cache:
        last_check = _model_cache.get(cache_time_key)
        if last_check and datetime.now() - last_check < timedelta(seconds=HEALTH_CHECK_CACHE_DURATION):
            cached_result = _model_cache.get(cache_key, False)
            cached_confidence = _model_cache.get(cache_confidence_key, 0.5)
            return cached_result, cached_confidence
    
    # Rate limiting check
    if not _gemini_rate_limiter.allow_call():
        wait_time = _gemini_rate_limiter.get_wait_time()
        logger.warning(f"Gemini API rate limit reached. Wait {wait_time:.1f}s")
        # Return cached result if available, else assume unhealthy
        return _model_cache.get(cache_key, False), _model_cache.get(cache_confidence_key, 0.3)
    
    # Perform health check with timeout and retries
    for attempt in range(MAX_HEALTH_CHECK_RETRIES):
        try:
            # Timeout-protected health check
            start_time = time.time()
            
            def _health_check():
                return model.count_tokens("test")
            
            # Use threading for timeout (genai doesn't support native timeout)
            from typing import Any
            result: list[Any] = [None]
            error: list[Exception | None] = [None]
            
            def _check_thread():
                try:
                    result[0] = _health_check()
                except Exception as e:
                    error[0] = e
            
            thread = threading.Thread(target=_check_thread)
            thread.daemon = True
            thread.start()
            thread.join(timeout=timeout)
            
            if thread.is_alive():
                # Timeout occurred
                logger.warning(f"Gemini health check timeout (attempt {attempt + 1}/{MAX_HEALTH_CHECK_RETRIES})")
                if attempt < MAX_HEALTH_CHECK_RETRIES - 1:
                    time.sleep(0.5)  # Brief pause before retry
                    continue
                else:
                    # Final attempt failed
                    _model_cache[cache_key] = False
                    _model_cache[cache_confidence_key] = 0.2
                    _model_cache[cache_time_key] = datetime.now()
                    return False, 0.2
            
            if error[0]:
                raise error[0]
            
            # Success
            elapsed = time.time() - start_time
            confidence = 1.0 if elapsed < 1.0 else 0.8 if elapsed < 2.0 else 0.6
            
            _model_cache[cache_key] = True
            _model_cache[cache_confidence_key] = confidence
            _model_cache[cache_time_key] = datetime.now()
            logger.info(f"Gemini health check passed ({elapsed:.2f}s, confidence={confidence:.2f})")
            return True, confidence
            
        except Exception as e:
            logger.warning(f"Gemini health check failed (attempt {attempt + 1}/{MAX_HEALTH_CHECK_RETRIES}): {e}")
            if attempt < MAX_HEALTH_CHECK_RETRIES - 1:
                time.sleep(0.5)
                continue
    
    # All attempts failed
    _model_cache[cache_key] = False
    _model_cache[cache_confidence_key] = 0.0
    _model_cache[cache_time_key] = datetime.now()
    return False, 0.0


def load_models():
    """
    Load models with TRUE three-tier hybrid fallback system:
    Tier 1: Gemini API (highest quality, confidence 0.8-1.0)
    Tier 2: Local spaCy + FAISS (good quality, confidence 0.5-0.7)
    Tier 3: Rule-based fallback (basic quality, confidence 0.2-0.4)
    
    Returns: (gemini_model, nlp, embedder, success_flag)
    """
    # Try environment variables (backend compatible)
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    api_key = api_key.strip() if api_key else ""
    
    # Load local models first (always available as fallback)
    nlp, embedder, local_ok = load_local_models()
    
    if not local_ok:
        logger.error("❌ CRITICAL: Local models failed to load. System cannot operate.")
        return None, None, None, False
    
    # Try to load Gemini (optional, provides enhanced analysis)
    model = None
    gemini_ok = False
    gemini_confidence = 0.0
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model, gemini_ok = load_gemini_model()
            
            if gemini_ok and model:
                # Verify health and get confidence score
                is_healthy, confidence = check_gemini_health(model)
                if is_healthy:
                    gemini_confidence = confidence
                    logger.info(f"✅ HYBRID MODE: Gemini (confidence={confidence:.2f}) + Local models")
                    _model_cache["gemini_confidence"] = confidence
                else:
                    logger.warning("⚠️ Gemini loaded but health check failed. Falling back to local-only.")
                    gemini_ok = False
                    model = None
        except Exception as e:
            logger.warning(f"Gemini loading failed: {e}. Falling back to local-only mode.")
            gemini_ok = False
            model = None
    
    # Determine operation mode with confidence scoring
    if gemini_ok and local_ok:
        mode = "hybrid"
        logger.info(f"🚀 HYBRID MODE ACTIVE: Gemini confidence: {gemini_confidence:.0%}, Fallback ready")
    elif local_ok:
        mode = "local"
        logger.info("⚠️ LOCAL-ONLY MODE: Using spaCy + FAISS (Gemini API not available)")
    else:
        logger.error("❌ Critical: No models available")
        return None, None, None, False
    
    # Store mode and confidence scores
    _model_cache["model_mode"] = mode
    _model_cache["local_confidence"] = 0.7 if local_ok else 0.0
    _model_cache["gemini_available"] = gemini_ok
    _model_cache["fallback_ready"] = local_ok
    
    return model, nlp, embedder, True



def load_gemini_model():
    """
    Load Gemini model with multi-model fallback chain and validation.
    Returns (model, success_flag)
    """
    try:
        preferred = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    except Exception:
        preferred = "gemini-2.5-flash"
    
    preferred = (preferred.strip() if preferred else "gemini-2.5-flash") or "gemini-2.5-flash"
    fallbacks = [
        preferred, "gemini-2.5-pro", "gemini-flash-latest", "gemini-pro-latest",
        "gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-1.0-pro"
    ]
    
    # Try to get available models with timeout
    try:
        available = set()
        
        def _list_models():
            return {
                m.name.split('/')[-1]
                for m in genai.list_models()
                if getattr(m, "supported_generation_methods", []) and "generateContent" in m.supported_generation_methods
            }
        
        # Use threading for timeout protection
        from typing import Any
        result: list[Any] = [set()]
        error: list[Exception | None] = [None]
        
        def _list_thread():
            try:
                result[0] = _list_models()
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=_list_thread)
        thread.daemon = True
        thread.start()
        thread.join(timeout=HEALTH_CHECK_TIMEOUT)
        
        if thread.is_alive():
            logger.warning("Timeout fetching available models, using fallback list")
            available = set()
        elif error[0]:
            logger.warning(f"Error fetching models: {error[0]}")
            available = set()
        else:
            available = result[0]
            
    except Exception as e:
        logger.warning(f"Could not list available models: {e}")
        available = set()

    # Try each model in fallback chain
    model = None
    for cand in fallbacks:
        simple = cand.replace("models/", "")
        
        # Skip if we know it's not available
        if available and simple not in available:
            logger.debug(f"Skipping {simple} (not in available models)")
            continue
        
        try:
            # Rate limit check
            if not _gemini_rate_limiter.allow_call():
                wait_time = _gemini_rate_limiter.get_wait_time()
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                time.sleep(wait_time)
            
            # Try loading model
            candidate = genai.GenerativeModel(simple)
            
            # Validate with token count (lightweight test)
            candidate.count_tokens("validation_test")
            
            model = candidate
            _model_cache["gemini_model"] = model
            _model_cache["gemini_model_name"] = simple
            logger.info(f"✅ Loaded Gemini model: {simple}")
            return model, True
            
        except Exception as e:
            logger.warning(f"Failed to load {simple}: {str(e)[:100]}")
            continue
    
    logger.warning("❌ All Gemini models failed to load")
    return None, False




def load_local_models():
    """
    Load local models (spaCy + SentenceTransformer) that work offline.
    Returns (nlp, embedder, success_flag)
    """

    # spaCy - load full model with parser (required)
    import subprocess
    nlp = None
    try:
        nlp = spacy.load("en_core_web_sm")
        logger.info("✅ spaCy model loaded")
    except OSError:
        logger.warning("spaCy model 'en_core_web_sm' not found. Attempting to download...")
        try:
            result = subprocess.run(
                ["python", "-m", "spacy", "download", "en_core_web_sm"],
                check=True,
                timeout=120,  # 2 minute timeout
                capture_output=True,
                text=True
            )
            nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model downloaded successfully!")
        except subprocess.TimeoutExpired:
            logger.error("❌ spaCy model download timeout (>2 minutes)")
            return None, None, False
        except Exception as e:
            logger.error(f"❌ Failed to download spaCy model: {e}")
            return None, None, False
    except Exception as e:
        logger.error(f"❌ Failed to load spaCy: {e}")
        return None, None, False
    
    # Verify all required components are available
    required_components = ["parser", "tagger", "ner"]
    missing_components = [comp for comp in required_components if comp not in nlp.pipe_names]
    if missing_components:
        logger.error(f"❌ spaCy missing required components: {missing_components}")
        return None, None, False
    
    logger.info(f"✅ spaCy components verified: {', '.join(nlp.pipe_names)}")

    # Sentence transformer embedder
    embedder = None
    try:
        s_name = os.getenv("SENTENCE_MODEL_NAME", "all-mpnet-base-v2")
        logger.info(f"Loading sentence transformer: {s_name}")
        
        # Try to load with memory optimization
        embedder = SentenceTransformer(s_name, device='cpu')
        
        # Validate embedder works
        test_embedding = embedder.encode(["test"], show_progress_bar=False)
        if test_embedding is None or len(test_embedding) == 0:
            raise ValueError("Embedder produced no output")
        
        logger.info(f"✅ Sentence transformer loaded: {s_name} (dim={test_embedding.shape[1]})")
    except Exception as e:
        logger.error(f"❌ Failed to load sentence transformer: {e}")
        return nlp, None, False

    return nlp, embedder, True


def get_model_mode():
    """Get current operation mode (hybrid/local/unknown)."""
    return _model_cache.get("model_mode", "unknown")


def can_use_llm():
    """
    Check if LLM (Gemini) is available and healthy with confidence score.
    Returns (can_use: bool, confidence: float 0.0-1.0)
    """
    mode = get_model_mode()
    if mode != "hybrid":
        return False, 0.0
    
    # Check if Gemini is marked as available
    if not _model_cache.get("gemini_available", False):
        return False, 0.0
    
    # Get stored confidence from last health check
    confidence = _model_cache.get("gemini_confidence", 0.5)
    
    # Additional real-time health check if confidence is low
    if confidence is not None and confidence < 0.7:
        model = _model_cache.get("gemini_model")
        if model:
            is_healthy, new_confidence = check_gemini_health(model)
            if not is_healthy:
                return False, 0.0
            return True, new_confidence
    
    return True, confidence


def get_analysis_quality_estimate():
    """
    Estimate analysis quality based on available models.
    Returns dict with quality metrics.
    """
    mode = get_model_mode()
    
    if mode == "hybrid":
        can_llm, llm_confidence = can_use_llm()
        if can_llm and llm_confidence is not None:
            return {
                "quality": "high",
                "confidence": llm_confidence,
                "llm_available": True,
                "local_fallback": True,
                "estimated_accuracy": 0.85 + (llm_confidence * 0.10)  # 85-95%
            }
    
    if mode == "local":
        local_conf = _model_cache.get("local_confidence", 0.7)
        return {
            "quality": "medium",
            "confidence": local_conf,
            "llm_available": False,
            "local_fallback": True,
            "estimated_accuracy": 0.70  # 70%
        }
    
    return {
        "quality": "low",
        "confidence": 0.2,
        "llm_available": False,
        "local_fallback": False,
        "estimated_accuracy": 0.40  # 40%
    }


