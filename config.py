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
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "")

# Database name
DB_NAME = os.environ.get("DB_NAME", "")

# Error message display toggle
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "True").lower() == "true"

# Session string size validation
SESSION_STRING_SIZE = 351

# EXTREME SPEED OPTIMIZATIONS - No waiting time
PROGRESS_UPDATE_INTERVAL = 1  # Ultra-fast progress updates
MAX_BATCH_SIZE = 1000  # Maximum batch size for power users
USER_INPUT_TIMEOUT = 600
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024

# MAXIMUM PERFORMANCE SETTINGS
DOWNLOAD_CHUNK_SIZE = 2 * 1024 * 1024  # 2MB chunks for maximum speed
MAX_CONCURRENT_DOWNLOADS = 20  # Double concurrent downloads
CONNECTION_TIMEOUT = 60  # Longer timeout to prevent drops
MAX_RETRIES = 3  # Faster retries
RETRY_DELAY = 0.5  # Minimal retry delay

# EXTREME BOT PERFORMANCE
BOT_WORKERS = 200  # Maximum workers for ultimate speed
SLEEP_THRESHOLD = 1  # Minimal sleep threshold
CONNECTION_POOL_SIZE = 20  # Large connection pool

# Thumbnail quality settings
THUMBNAIL_QUALITY = 95  # Maximum HD thumbnail quality
THUMBNAIL_MAX_SIZE = 2560  # 2K resolution thumbnails

# SPEED OPTIMIZATION CONSTANTS
MINIMAL_DELAY = 0.01  # Absolute minimum delay
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB upload chunks
PROGRESS_THROTTLE = 0.5  # Progress update throttling

# Flask and deployment settings
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
