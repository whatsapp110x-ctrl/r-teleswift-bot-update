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

# OPTIMIZED SETTINGS FOR STABILITY
PROGRESS_UPDATE_INTERVAL = 2
MAX_BATCH_SIZE = 50  # Reduced for stability
USER_INPUT_TIMEOUT = 300
MAX_FILE_SIZE = 1.5 * 1024 * 1024 * 1024  # 1.5GB

# BALANCED PERFORMANCE SETTINGS
DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB chunks
MAX_CONCURRENT_DOWNLOADS = 5  # Reduced concurrent downloads
CONNECTION_TIMEOUT = 120  # Increased timeout
MAX_RETRIES = 5  # More retries
RETRY_DELAY = 2  # Longer retry delay

# STABLE BOT PERFORMANCE
BOT_WORKERS = 50  # Reduced workers
SLEEP_THRESHOLD = 30  # Higher sleep threshold
CONNECTION_POOL_SIZE = 10  # Smaller pool

# Thumbnail quality settings
THUMBNAIL_QUALITY = 90
THUMBNAIL_MAX_SIZE = 1920

# STABILITY OPTIMIZATION CONSTANTS
MINIMAL_DELAY = 0.1
UPLOAD_CHUNK_SIZE = 512 * 1024  # 512KB upload chunks
PROGRESS_THROTTLE = 1

# Flask and deployment settings
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
