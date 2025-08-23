import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "12345"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Your database URI from mongodb
# If not provided, bot will run in limited mode
DB_URI = os.environ.get("DATABASE_URL", "mongodb://localhost:27017")

# Your database name
DB_NAME = os.environ.get("DATABASE_NAME", "techvj_bot")

# Bot workers - number of concurrent workers for handling updates
BOT_WORKERS = int(os.environ.get("BOT_WORKERS", "4"))

# Sleep threshold for flood wait handling (in seconds)
SLEEP_THRESHOLD = int(os.environ.get("SLEEP_THRESHOLD", "60"))

# Maximum file size for downloads (in bytes) - 2GB default
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", "2147483648"))

# Maximum batch size for bulk downloads
MAX_BATCH_SIZE = int(os.environ.get("MAX_BATCH_SIZE", "50"))

# Download settings
DOWNLOAD_CHUNK_SIZE = int(os.environ.get("DOWNLOAD_CHUNK_SIZE", "1024"))
UPLOAD_CHUNK_SIZE = int(os.environ.get("UPLOAD_CHUNK_SIZE", "1024"))

# Progress update interval (in seconds)
PROGRESS_UPDATE_INTERVAL = int(os.environ.get("PROGRESS_UPDATE_INTERVAL", "2"))
PROGRESS_THROTTLE = int(os.environ.get("PROGRESS_THROTTLE", "5"))

# Connection settings
CONNECTION_TIMEOUT = int(os.environ.get("CONNECTION_TIMEOUT", "30"))
CONNECTION_POOL_SIZE = int(os.environ.get("CONNECTION_POOL_SIZE", "10"))

# Retry settings
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", "5"))
MINIMAL_DELAY = int(os.environ.get("MINIMAL_DELAY", "1"))

# Concurrent downloads
MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", "3"))

# Thumbnail settings
THUMBNAIL_QUALITY = int(os.environ.get("THUMBNAIL_QUALITY", "90"))
THUMBNAIL_MAX_SIZE = int(os.environ.get("THUMBNAIL_MAX_SIZE", "1048576"))  # 1MB

# Error message for restricted content
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "❌ This content is restricted and cannot be downloaded.")

# Log level
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Admin user IDs (comma separated)
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split(",") if x.strip()]

# Force subscribe channel (optional)
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "")
