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

# Session settings
SESSION_STRING_SIZE = int(os.environ.get("SESSION_STRING_SIZE", "351"))

# Error message for restricted content
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "❌ This content is restricted and cannot be downloaded.")

# Log level
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Admin user IDs (comma separated)
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split(",") if x.strip()]

# Force subscribe channel (optional)
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "")

# Broadcasting settings
BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", True))

# Auto delete settings
AUTO_DELETE = bool(os.environ.get("AUTO_DELETE", False))
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "300"))  # 5 minutes

# File caption settings
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "")

# User limits
USER_SESSION_LIMIT = int(os.environ.get("USER_SESSION_LIMIT", "1"))

# Bot maintenance mode
MAINTENANCE_MODE = bool(os.environ.get("MAINTENANCE_MODE", False))

# Rate limiting
RATE_LIMIT_MESSAGES = int(os.environ.get("RATE_LIMIT_MESSAGES", "20"))
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))  # seconds

# Statistics
ENABLE_STATS = bool(os.environ.get("ENABLE_STATS", True))

# Logging settings  
LOG_CHAT_ID = os.environ.get("LOG_CHAT_ID", "")

# Premium features
PREMIUM_USERS = [int(x) for x in os.environ.get("PREMIUM_USERS", "").split(",") if x.strip()]

# File naming
PRESERVE_FILENAME = bool(os.environ.get("PRESERVE_FILENAME", True))

# Download location
DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./downloads/")

# Temp file cleanup
CLEANUP_TEMP_FILES = bool(os.environ.get("CLEANUP_TEMP_FILES", True))
TEMP_FILE_LIFETIME = int(os.environ.get("TEMP_FILE_LIFETIME", "3600"))  # 1 hour

# Bot info
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
BOT_NAME = os.environ.get("BOT_NAME", "VJ Save Content Bot")

# Channel/Group settings
FORCE_SUB_MESSAGE = os.environ.get("FORCE_SUB_MESSAGE", "❌ You must join our channel first!")

# Login settings
LOGIN_ATTEMPTS_LIMIT = int(os.environ.get("LOGIN_ATTEMPTS_LIMIT", "3"))
LOGIN_COOLDOWN_TIME = int(os.environ.get("LOGIN_COOLDOWN_TIME", "300"))  # 5 minutes

# Progress bar settings
PROGRESS_BAR_LENGTH = int(os.environ.get("PROGRESS_BAR_LENGTH", "20"))

# File type restrictions
ALLOWED_FILE_TYPES = os.environ.get("ALLOWED_FILE_TYPES", "video,document,photo,audio").split(",")

# Quality settings
VIDEO_QUALITY = os.environ.get("VIDEO_QUALITY", "high")
PHOTO_QUALITY = os.environ.get("PHOTO_QUALITY", "high")

# Concurrent session limits
MAX_CONCURRENT_SESSIONS = int(os.environ.get("MAX_CONCURRENT_SESSIONS", "5"))

# Cache settings
ENABLE_CACHE = bool(os.environ.get("ENABLE_CACHE", False))
CACHE_EXPIRY_TIME = int(os.environ.get("CACHE_EXPIRY_TIME", "1800"))  # 30 minutes

# Security settings
ENABLE_FLOOD_PROTECTION = bool(os.environ.get("ENABLE_FLOOD_PROTECTION", True))
FLOOD_LIMIT = int(os.environ.get("FLOOD_LIMIT", "10"))
FLOOD_WINDOW = int(os.environ.get("FLOOD_WINDOW", "60"))  # seconds

# Message settings
DELETE_PROGRESS_MESSAGES = bool(os.environ.get("DELETE_PROGRESS_MESSAGES", True))
PROGRESS_MESSAGE_LIFETIME = int(os.environ.get("PROGRESS_MESSAGE_LIFETIME", "30"))  # seconds
