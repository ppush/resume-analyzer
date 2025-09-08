# Resume Analyzer Configuration

## config.py File

All main application settings are moved to `config.py` file for convenient management.

### LM Studio Settings

```python
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-3-12b"
# DEFAULT_MODEL = "meta-llama-3.1-8b-instruct"
```

**How to change model:**
1. Open `config.py` file
2. Comment out current model: `# DEFAULT_MODEL = "google/gemma-3-12b"`
3. Uncomment desired model: `DEFAULT_MODEL = "meta-llama-3.1-8b-instruct"`

### LLM Settings

```python
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 0.0  # Deterministic results
DEFAULT_SEED = 42  # Fixed seed for reproducibility
```

### Timeout Settings

```python
LLM_TIMEOUT = 120  # 2 minutes per request
```

### Logging Settings

```python
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### File Settings

```python
DEFAULT_ENCODING = "utf-8"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
```

### Processing Settings

```python
MAX_CONCURRENT_REQUESTS = 5
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds
```

## Usage

All modules automatically import settings from `config.py`:

```python
from config import LM_STUDIO_URL, DEFAULT_MODEL, LLM_TIMEOUT
```

## Changing Settings

To change settings, simply edit `config.py` file and restart the application. All changes will take effect immediately.
