import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", ""))

# Your Mongodb Database Url
DB_URI = os.environ.get("DB_URI", "")

# Database name
DB_NAME = os.environ.get("DB_NAME", "")

# Error message display toggle
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "True").lower() == "true"

# Session string size validation
SESSION_STRING_SIZE = 351

# OPTIMIZED PERFORMANCE SETTINGS
PROGRESS_UPDATE_INTERVAL = 2  # Reasonable progress updates
MAX_BATCH_SIZE = 100  # Reduced for stability
USER_INPUT_TIMEOUT = 300  # 5 minutes timeout
MAX_FILE_SIZE = 1.5 * 1024 * 1024 * 1024  # 1.5GB limit

# STABLE PERFORMANCE SETTINGS
DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB chunks
MAX_CONCURRENT_DOWNLOADS = 5  # Reduced for stability
CONNECTION_TIMEOUT = 120  # 2 minutes timeout
MAX_RETRIES = 5  # More retries
RETRY_DELAY = 2  # 2 second delay between retries

# BALANCED BOT PERFORMANCE
BOT_WORKERS = 50  # Reduced workers for stability
SLEEP_THRESHOLD = 60  # Higher threshold to prevent rate limits
CONNECTION_POOL_SIZE = 10  # Smaller connection pool

# Thumbnail quality settings
THUMBNAIL_QUALITY = 85  # Good quality
THUMBNAIL_MAX_SIZE = 1920  # Full HD thumbnails

# STABILITY CONSTANTS
MINIMAL_DELAY = 0.1  # Small delay
UPLOAD_CHUNK_SIZE = 512 * 1024  # 512KB upload chunks
PROGRESS_THROTTLE = 1  # 1 second progress throttling

# Flask and deployment settings
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Session management
SESSION_TIMEOUT = 3600  # 1 hour session timeout
SESSION_CLEANUP_INTERVAL = 300  # 5 minutes cleanup interval
