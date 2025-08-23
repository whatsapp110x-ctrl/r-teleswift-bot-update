import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "12345"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Your database URI from mongodb
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DB_URI = DATABASE_URL if DATABASE_URL else os.environ.get("DB_URI", "")

# Your database name
DB_NAME = os.environ.get("DATABASE_NAME", "techvj_bot")

# Bot workers - optimized for better performance
BOT_WORKERS = int(os.environ.get("BOT_WORKERS", "6"))

# Sleep threshold - reduced for faster responses
SLEEP_THRESHOLD = int(os.environ.get("SLEEP_THRESHOLD", "30"))

# File size limits
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", "2147483648"))
MAX_BATCH_SIZE = int(os.environ.get("MAX_BATCH_SIZE", "25"))  # Reduced for stability

# Optimized timeout settings
CONNECTION_TIMEOUT = int(os.environ.get("CONNECTION_TIMEOUT", "20"))  # Reduced
USER_INPUT_TIMEOUT = int(os.environ.get("USER_INPUT_TIMEOUT", "120"))  # Reduced
LOGIN_TIMEOUT = int(os.environ.get("LOGIN_TIMEOUT", "90"))  # Reduced
OTP_TIMEOUT = int(os.environ.get("OTP_TIMEOUT", "90"))  # Reduced
PASSWORD_TIMEOUT = int(os.environ.get("PASSWORD_TIMEOUT", "60"))

# Progress and upload settings
PROGRESS_UPDATE_INTERVAL = int(os.environ.get("PROGRESS_UPDATE_INTERVAL", "3"))  # Faster updates
PROGRESS_THROTTLE = int(os.environ.get("PROGRESS_THROTTLE", "3"))  # Reduced throttle
DOWNLOAD_CHUNK_SIZE = int(os.environ.get("DOWNLOAD_CHUNK_SIZE", "1024"))
UPLOAD_CHUNK_SIZE = int(os.environ.get("UPLOAD_CHUNK_SIZE", "1024"))

# Retry settings - optimized
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "2"))  # Reduced retries
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", "3"))  # Faster retry
MINIMAL_DELAY = int(os.environ.get("MINIMAL_DELAY", "1"))

# Connection pool - optimized
CONNECTION_POOL_SIZE = int(os.environ.get("CONNECTION_POOL_SIZE", "8"))
MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", "2"))  # Reduced

# Session settings
SESSION_STRING_SIZE = int(os.environ.get("SESSION_STRING_SIZE", "300"))  # Reduced minimum

# Thumbnail settings
THUMBNAIL_QUALITY = int(os.environ.get("THUMBNAIL_QUALITY", "75"))  # Reduced for speed
THUMBNAIL_MAX_SIZE = int(os.environ.get("THUMBNAIL_MAX_SIZE", "524288"))  # 512KB

# Rest of the config remains the same but with performance optimizations
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "❌ This content is restricted and cannot be downloaded.")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split(",") if x.strip()]
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "")
BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", True))
BROADCAST_SLEEP_TIME = int(os.environ.get("BROADCAST_SLEEP_TIME", "1"))
AUTO_DELETE = bool(os.environ.get("AUTO_DELETE", False))
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "300"))
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "")
USER_SESSION_LIMIT = int(os.environ.get("USER_SESSION_LIMIT", "1"))
MAINTENANCE_MODE = bool(os.environ.get("MAINTENANCE_MODE", False))

# Rate limiting - optimized for better UX
RATE_LIMIT_MESSAGES = int(os.environ.get("RATE_LIMIT_MESSAGES", "15"))  # Reduced
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "45"))  # Reduced

# Performance settings
ENABLE_STATS = bool(os.environ.get("ENABLE_STATS", True))
STATS_UPDATE_INTERVAL = int(os.environ.get("STATS_UPDATE_INTERVAL", "120"))  # Less frequent
LOG_CHAT_ID = os.environ.get("LOG_CHAT_ID", "")
LOG_FILE_NAME = os.environ.get("LOG_FILE_NAME", "bot.log")
PREMIUM_USERS = [int(x) for x in os.environ.get("PREMIUM_USERS", "").split(",") if x.strip()]
PRESERVE_FILENAME = bool(os.environ.get("PRESERVE_FILENAME", True))
DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./downloads/")
CLEANUP_TEMP_FILES = bool(os.environ.get("CLEANUP_TEMP_FILES", True))
TEMP_FILE_LIFETIME = int(os.environ.get("TEMP_FILE_LIFETIME", "1800"))  # Reduced
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
BOT_NAME = os.environ.get("BOT_NAME", "VJ Save Content Bot")
FORCE_SUB_MESSAGE = os.environ.get("FORCE_SUB_MESSAGE", "❌ You must join our channel first!")
LOGIN_ATTEMPTS_LIMIT = int(os.environ.get("LOGIN_ATTEMPTS_LIMIT", "3"))
LOGIN_COOLDOWN_TIME = int(os.environ.get("LOGIN_COOLDOWN_TIME", "180"))  # Reduced
PROGRESS_BAR_LENGTH = int(os.environ.get("PROGRESS_BAR_LENGTH", "15"))  # Reduced
ALLOWED_FILE_TYPES = os.environ.get("ALLOWED_FILE_TYPES", "video,document,photo,audio").split(",")
VIDEO_QUALITY = os.environ.get("VIDEO_QUALITY", "high")
PHOTO_QUALITY = os.environ.get("PHOTO_QUALITY", "high")
MAX_CONCURRENT_SESSIONS = int(os.environ.get("MAX_CONCURRENT_SESSIONS", "3"))  # Reduced

# Cache and performance
ENABLE_CACHE = bool(os.environ.get("ENABLE_CACHE", True))  # Enabled for performance
CACHE_EXPIRY_TIME = int(os.environ.get("CACHE_EXPIRY_TIME", "900"))  # Reduced
ENABLE_FLOOD_PROTECTION = bool(os.environ.get("ENABLE_FLOOD_PROTECTION", True))
FLOOD_LIMIT = int(os.environ.get("FLOOD_LIMIT", "8"))  # Reduced
FLOOD_WINDOW = int(os.environ.get("FLOOD_WINDOW", "45"))  # Reduced
DELETE_PROGRESS_MESSAGES = bool(os.environ.get("DELETE_PROGRESS_MESSAGES", True))
PROGRESS_MESSAGE_LIFETIME = int(os.environ.get("PROGRESS_MESSAGE_LIFETIME", "20"))  # Reduced

# Additional optimized timeouts
MESSAGE_TIMEOUT = int(os.environ.get("MESSAGE_TIMEOUT", "180"))  # Reduced
DOWNLOAD_TIMEOUT = int(os.environ.get("DOWNLOAD_TIMEOUT", "300"))  # Reduced
UPLOAD_TIMEOUT = int(os.environ.get("UPLOAD_TIMEOUT", "300"))  # Reduced
BATCH_PROCESSING_DELAY = int(os.environ.get("BATCH_PROCESSING_DELAY", "1"))  # Reduced
BATCH_PROGRESS_UPDATE_FREQUENCY = int(os.environ.get("BATCH_PROGRESS_UPDATE_FREQUENCY", "3"))  # Faster
VALIDATE_FILE_SIZE = bool(os.environ.get("VALIDATE_FILE_SIZE", True))
VALIDATE_FILE_TYPE = bool(os.environ.get("VALIDATE_FILE_TYPE", True))
CONNECTION_RETRIES = int(os.environ.get("CONNECTION_RETRIES", "2"))  # Reduced
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "20"))  # Reduced
CANCEL_TIMEOUT = int(os.environ.get("CANCEL_TIMEOUT", "30"))  # Reduced
HELP_TIMEOUT = int(os.environ.get("HELP_TIMEOUT", "180"))  # Reduced

# Session management - optimized
SESSION_CLEANUP_INTERVAL = int(os.environ.get("SESSION_CLEANUP_INTERVAL", "7200"))  # Less frequent
INACTIVE_SESSION_TIMEOUT = int(os.environ.get("INACTIVE_SESSION_TIMEOUT", "43200"))  # 12 hours
ERROR_RETRY_DELAY = int(os.environ.get("ERROR_RETRY_DELAY", "3"))  # Reduced
MAX_ERROR_RETRIES = int(os.environ.get("MAX_ERROR_RETRIES", "2"))  # Reduced
NOTIFY_ADMIN_ON_ERROR = bool(os.environ.get("NOTIFY_ADMIN_ON_ERROR", False))
NOTIFY_USER_ON_COMPLETION = bool(os.environ.get("NOTIFY_USER_ON_COMPLETION", True))

# Resource limits
MEMORY_LIMIT = int(os.environ.get("MEMORY_LIMIT", "1073741824"))
CPU_LIMIT = int(os.environ.get("CPU_LIMIT", "70"))  # Reduced
DEBUG_MODE = bool(os.environ.get("DEBUG_MODE", False))
VERBOSE_LOGGING = bool(os.environ.get("VERBOSE_LOGGING", False))

# Additional optimizations
PYROGRAM_SESSION_NAME = os.environ.get("PYROGRAM_SESSION_NAME", "techvj_session")
MEDIA_CACHE_TIME = int(os.environ.get("MEDIA_CACHE_TIME", "1800"))  # Reduced
USER_CACHE_TIME = int(os.environ.get("USER_CACHE_TIME", "900"))  # Reduced
STATUS_UPDATE_INTERVAL = int(os.environ.get("STATUS_UPDATE_INTERVAL", "15"))  # Faster
SHOW_DETAILED_STATUS = bool(os.environ.get("SHOW_DETAILED_STATUS", True))

# Feature processing
PROCESS_IMAGES = bool(os.environ.get("PROCESS_IMAGES", True))
PROCESS_VIDEOS = bool(os.environ.get("PROCESS_VIDEOS", True))
PROCESS_DOCUMENTS = bool(os.environ.get("PROCESS_DOCUMENTS", True))
PROCESS_AUDIO = bool(os.environ.get("PROCESS_AUDIO", True))
DOWNLOAD_QUEUE_SIZE = int(os.environ.get("DOWNLOAD_QUEUE_SIZE", "50"))  # Reduced
UPLOAD_QUEUE_SIZE = int(os.environ.get("UPLOAD_QUEUE_SIZE", "25"))  # Reduced
DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "en")
TIMEZONE = os.environ.get("TIMEZONE", "UTC")

# Webhook settings
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.environ.get("WEBHOOK_PORT", "8443"))

# Feature flags
ENABLE_BATCH_DOWNLOAD = bool(os.environ.get("ENABLE_BATCH_DOWNLOAD", True))
ENABLE_SINGLE_DOWNLOAD = bool(os.environ.get("ENABLE_SINGLE_DOWNLOAD", True))
ENABLE_USER_REGISTRATION = bool(os.environ.get("ENABLE_USER_REGISTRATION", True))
ENABLE_SESSION_MANAGEMENT = bool(os.environ.get("ENABLE_SESSION_MANAGEMENT", True))
MAX_MESSAGE_LENGTH = int(os.environ.get("MAX_MESSAGE_LENGTH", "4096"))
MAX_CAPTION_LENGTH = int(os.environ.get("MAX_CAPTION_LENGTH", "1024"))
MAX_FILENAME_LENGTH = int(os.environ.get("MAX_FILENAME_LENGTH", "200"))  # Reduced

# Backup settings
ENABLE_AUTO_BACKUP = bool(os.environ.get("ENABLE_AUTO_BACKUP", False))
BACKUP_INTERVAL = int(os.environ.get("BACKUP_INTERVAL", "86400"))
BACKUP_RETENTION_DAYS = int(os.environ.get("BACKUP_RETENTION_DAYS", "3"))  # Reduced

# Analytics - optimized
ENABLE_ANALYTICS = bool(os.environ.get("ENABLE_ANALYTICS", False))  # Disabled for performance
ANALYTICS_UPDATE_INTERVAL = int(os.environ.get("ANALYTICS_UPDATE_INTERVAL", "600"))  # Less frequent
ENABLE_METRICS = bool(os.environ.get("ENABLE_METRICS", False))  # Disabled for performance
METRICS_PORT = int(os.environ.get("METRICS_PORT", "9090"))
