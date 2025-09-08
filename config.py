"""
Configuration file for Resume Analyzer
"""

import os

# LM Studio settings (with environment variable support)
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "google/gemma-3-12b")
# DEFAULT_MODEL = "meta-llama-3.1-8b-instruct"

# LLM settings (with environment variable support)
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "4096"))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.0"))  # Deterministic results
DEFAULT_SEED = int(os.getenv("DEFAULT_SEED", "42"))  # Fixed seed for reproducibility

# Timeout settings
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))  # 2 minutes per request

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File settings
DEFAULT_ENCODING = "utf-8"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Processing settings
MAX_CONCURRENT_REQUESTS = 5
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds

# Page processing settings (for large resumes)
PAGE_SIZE_LINES = int(os.getenv("PAGE_SIZE_LINES", "50"))  # Lines per page
LARGE_RESUME_THRESHOLD = int(os.getenv("LARGE_RESUME_THRESHOLD", "100"))  # Lines threshold for page-based processing