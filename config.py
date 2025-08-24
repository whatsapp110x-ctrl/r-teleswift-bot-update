import os

def safe_int(value, default=0):
    """Safely convert value to int, handling decimals and invalid values"""
    try:
        if isinstance(value, str) and value.strip() == "":
            return default
        # First try float conversion, then int
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False):
    """Safely convert value to bool"""
    try:
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        return bool(value)
    except (ValueError, TypeError):
        return default

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = safe_int(os.environ.get("API_ID", "12345"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Your database URI from mongodb
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DB_URI = DATABASE_URL if DATABASE_URL else os.environ.get("DB_URI", "")

# Your database name
DB_NAME = os.environ.get("DATABASE_NAME", "techvj_bot")

# Bot workers - optimized for better performance
BOT_WORKERS = safe_int(os.environ.get("BOT_WORKERS", "6"))

# Sleep threshold - reduced for faster responses
SLEEP_THRESHOLD = safe_int(os.environ.get("SLEEP_THRESHOLD", "30"))

# File size limits
MAX_FILE_SIZE = safe_int(os.environ.get("MAX_FILE_SIZE", "2147483648"))
MAX_BATCH_SIZE = safe_int(os.environ.get("MAX_BATCH_SIZE", "25"))

# Optimized timeout settings
CONNECTION_TIMEOUT = safe_int(os.environ.get("CONNECTION_TIMEOUT", "20"))
USER_INPUT_TIMEOUT = safe_int(os.environ.get("USER_INPUT_TIMEOUT", "120"))
LOGIN_TIMEOUT = safe_int(os.environ.get("LOGIN_TIMEOUT", "90"))
OTP_TIMEOUT = safe_int(os.environ.get("OTP_TIMEOUT", "90"))
PASSWORD_TIMEOUT = safe_int(os.environ.get("PASSWORD_TIMEOUT", "60"))

# Progress and upload settings
PROGRESS_UPDATE_INTERVAL = safe_int(os.environ.get("PROGRESS_UPDATE_INTERVAL", "2"))
PROGRESS_THROTTLE = safe_int(os.environ.get("PROGRESS_THROTTLE", "2"))
DOWNLOAD_CHUNK_SIZE = safe_int(os.environ.get("DOWNLOAD_CHUNK_SIZE", "1024"))
UPLOAD_CHUNK_SIZE = safe_int(os.environ.get("UPLOAD_CHUNK_SIZE", "1024"))

# Enhanced thumbnail settings
THUMBNAIL_QUALITY = safe_int(os.environ.get("THUMBNAIL_QUALITY", "95"))  # Higher quality
THUMBNAIL_MAX_SIZE = safe_int(os.environ.get("THUMBNAIL_MAX_SIZE", "1048576"))  # 1MB limit
THUMBNAIL_WIDTH = safe_int(os.environ.get("THUMBNAIL_WIDTH", "320"))
THUMBNAIL_HEIGHT = safe_int(os.environ.get("THUMBNAIL_HEIGHT", "320"))
ENABLE_THUMBNAIL_CACHE = safe_bool(os.environ.get("ENABLE_THUMBNAIL_CACHE", "True"))
THUMBNAIL_CACHE_TIME = safe_int(os.environ.get("THUMBNAIL_CACHE_TIME", "3600"))  # 1 hour

# Speed tracking settings
SPEED_UPDATE_INTERVAL = safe_int(os.environ.get("SPEED_UPDATE_INTERVAL", "1"))  # Update every 1 second
SPEED_CALCULATION_WINDOW = safe_int(os.environ.get("SPEED_CALCULATION_WINDOW", "5"))  # 5 second window
ENABLE_REALTIME_SPEED = safe_bool(os.environ.get("ENABLE_REALTIME_SPEED", "True"))

# Enhanced progress settings
SHOW_PROGRESS_PERCENTAGE = safe_bool(os.environ.get("SHOW_PROGRESS_PERCENTAGE", "True"))
SHOW_PROGRESS_SPEED = safe_bool(os.environ.get("SHOW_PROGRESS_SPEED", "True"))
SHOW_PROGRESS_ETA = safe_bool(os.environ.get("SHOW_PROGRESS_ETA", "True"))
SHOW_PROGRESS_FILENAME = safe_bool(os.environ.get("SHOW_PROGRESS_FILENAME", "True"))
PROGRESS_MESSAGE_TEMPLATE = os.environ.get("PROGRESS_MESSAGE_TEMPLATE", "enhanced")

# Retry settings - optimized
MAX_RETRIES = safe_int(os.environ.get("MAX_RETRIES", "2"))
RETRY_DELAY = safe_int(os.environ.get("RETRY_DELAY", "3"))
MINIMAL_DELAY = safe_int(os.environ.get("MINIMAL_DELAY", "1"))

# Connection pool - optimized
CONNECTION_POOL_SIZE = safe_int(os.environ.get("CONNECTION_POOL_SIZE", "8"))
MAX_CONCURRENT_DOWNLOADS = safe_int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", "2"))

# Session settings
SESSION_STRING_SIZE = safe_int(os.environ.get("SESSION_STRING_SIZE", "300"))

# Error message for restricted content
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "❌ This content is restricted and cannot be downloaded.")

# Log level
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Admin user IDs (comma separated) - FIXED
ADMINS_STR = os.environ.get("ADMINS", "")
if ADMINS_STR:
    try:
        ADMINS = [safe_int(x.strip()) for x in ADMINS_STR.split(",") if x.strip() and safe_int(x.strip()) > 0]
    except:
        ADMINS = []
else:
    ADMINS = []

# Rest of your existing configuration remains the same...
# (All other settings from your original config.py)

# Force subscribe channel (optional)
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "")

# Broadcasting settings
BROADCAST_AS_COPY = safe_bool(os.environ.get("BROADCAST_AS_COPY", "True"))
BROADCAST_SLEEP_TIME = safe_int(os.environ.get("BROADCAST_SLEEP_TIME", "1"))

# Auto delete settings
AUTO_DELETE = safe_bool(os.environ.get("AUTO_DELETE", "False"))
AUTO_DELETE_TIME = safe_int(os.environ.get("AUTO_DELETE_TIME", "300"))

# Custom caption
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "")

# User limits
USER_SESSION_LIMIT = safe_int(os.environ.get("USER_SESSION_LIMIT", "1"))

# Bot maintenance mode
MAINTENANCE_MODE = safe_bool(os.environ.get("MAINTENANCE_MODE", "False"))

# Rate limiting
RATE_LIMIT_MESSAGES = safe_int(os.environ.get("RATE_LIMIT_MESSAGES", "20"))
RATE_LIMIT_WINDOW = safe_int(os.environ.get("RATE_LIMIT_WINDOW", "60"))

# Statistics
ENABLE_STATS = safe_bool(os.environ.get("ENABLE_STATS", "True"))
STATS_UPDATE_INTERVAL = safe_int(os.environ.get("STATS_UPDATE_INTERVAL", "60"))

# Logging settings  
LOG_CHAT_ID = os.environ.get("LOG_CHAT_ID", "")
LOG_FILE_NAME = os.environ.get("LOG_FILE_NAME", "bot.log")

# Premium features
PREMIUM_USERS_STR = os.environ.get("PREMIUM_USERS", "")
if PREMIUM_USERS_STR:
    try:
        PREMIUM_USERS = [safe_int(x.strip()) for x in PREMIUM_USERS_STR.split(",") if x.strip() and safe_int(x.strip()) > 0]
    except:
        PREMIUM_USERS = []
else:
    PREMIUM_USERS = []

# File naming
PRESERVE_FILENAME = safe_bool(os.environ.get("PRESERVE_FILENAME", "True"))

# Download location
DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./downloads/")

# Temp file cleanup
CLEANUP_TEMP_FILES = safe_bool(os.environ.get("CLEANUP_TEMP_FILES", "True"))
TEMP_FILE_LIFETIME = safe_int(os.environ.get("TEMP_FILE_LIFETIME", "3600"))

# Bot info
BOT_USERNAME = os.environ.get("BOT_USERNAME", "")
BOT_NAME = os.environ.get("BOT_NAME", "VJ Save Content Bot")

# Channel/Group settings
FORCE_SUB_MESSAGE = os.environ.get("FORCE_SUB_MESSAGE", "❌ You must join our channel first!")

# Login settings
LOGIN_ATTEMPTS_LIMIT = safe_int(os.environ.get("LOGIN_ATTEMPTS_LIMIT", "3"))
LOGIN_COOLDOWN_TIME = safe_int(os.environ.get("LOGIN_COOLDOWN_TIME", "300"))

# Progress bar settings
PROGRESS_BAR_LENGTH = safe_int(os.environ.get("PROGRESS_BAR_LENGTH", "20"))

# File type restrictions
ALLOWED_FILE_TYPES = os.environ.get("ALLOWED_FILE_TYPES", "video,document,photo,audio").split(",")

# Quality settings
VIDEO_QUALITY = os.environ.get("VIDEO_QUALITY", "high")
PHOTO_QUALITY = os.environ.get("PHOTO_QUALITY", "high")

# Concurrent session limits
MAX_CONCURRENT_SESSIONS = safe_int(os.environ.get("MAX_CONCURRENT_SESSIONS", "5"))

# Cache settings
ENABLE_CACHE = safe_bool(os.environ.get("ENABLE_CACHE", "False"))
CACHE_EXPIRY_TIME = safe_int(os.environ.get("CACHE_EXPIRY_TIME", "1800"))

# Security settings
ENABLE_FLOOD_PROTECTION = safe_bool(os.environ.get("ENABLE_FLOOD_PROTECTION", "True"))
FLOOD_LIMIT = safe_int(os.environ.get("FLOOD_LIMIT", "10"))
FLOOD_WINDOW = safe_int(os.environ.get("FLOOD_WINDOW", "60"))

# Message settings
DELETE_PROGRESS_MESSAGES = safe_bool(os.environ.get("DELETE_PROGRESS_MESSAGES", "True"))
PROGRESS_MESSAGE_LIFETIME = safe_int(os.environ.get("PROGRESS_MESSAGE_LIFETIME", "30"))

# Additional timeout settings
MESSAGE_TIMEOUT = safe_int(os.environ.get("MESSAGE_TIMEOUT", "300"))
DOWNLOAD_TIMEOUT = safe_int(os.environ.get("DOWNLOAD_TIMEOUT", "600"))
UPLOAD_TIMEOUT = safe_int(os.environ.get("UPLOAD_TIMEOUT", "600"))

# Batch processing settings
BATCH_PROCESSING_DELAY = safe_int(os.environ.get("BATCH_PROCESSING_DELAY", "2"))
BATCH_PROGRESS_UPDATE_FREQUENCY = safe_int(os.environ.get("BATCH_PROGRESS_UPDATE_FREQUENCY", "5"))

# File validation settings
VALIDATE_FILE_SIZE = safe_bool(os.environ.get("VALIDATE_FILE_SIZE", "True"))
VALIDATE_FILE_TYPE = safe_bool(os.environ.get("VALIDATE_FILE_TYPE", "True"))

# Network settings
CONNECTION_RETRIES = safe_int(os.environ.get("CONNECTION_RETRIES", "3"))
REQUEST_TIMEOUT = safe_int(os.environ.get("REQUEST_TIMEOUT", "30"))

# User interaction settings
CANCEL_TIMEOUT = safe_int(os.environ.get("CANCEL_TIMEOUT", "60"))
HELP_TIMEOUT = safe_int(os.environ.get("HELP_TIMEOUT", "300"))

# Session management
SESSION_CLEANUP_INTERVAL = safe_int(os.environ.get("SESSION_CLEANUP_INTERVAL", "3600"))
INACTIVE_SESSION_TIMEOUT = safe_int(os.environ.get("INACTIVE_SESSION_TIMEOUT", "86400"))

# Error handling
ERROR_RETRY_DELAY = safe_int(os.environ.get("ERROR_RETRY_DELAY", "5"))
MAX_ERROR_RETRIES = safe_int(os.environ.get("MAX_ERROR_RETRIES", "3"))

# Notification settings
NOTIFY_ADMIN_ON_ERROR = safe_bool(os.environ.get("NOTIFY_ADMIN_ON_ERROR", "False"))
NOTIFY_USER_ON_COMPLETION = safe_bool(os.environ.get("NOTIFY_USER_ON_COMPLETION", "True"))

# Performance settings
MEMORY_LIMIT = safe_int(os.environ.get("MEMORY_LIMIT", "1073741824"))
CPU_LIMIT = safe_int(os.environ.get("CPU_LIMIT", "80"))

# Debug settings
DEBUG_MODE = safe_bool(os.environ.get("DEBUG_MODE", "False"))
VERBOSE_LOGGING = safe_bool(os.environ.get("VERBOSE_LOGGING", "False"))

# Additional constants
PYROGRAM_SESSION_NAME = os.environ.get("PYROGRAM_SESSION_NAME", "techvj_session")
MEDIA_CACHE_TIME = safe_int(os.environ.get("MEDIA_CACHE_TIME", "3600"))
USER_CACHE_TIME = safe_int(os.environ.get("USER_CACHE_TIME", "1800"))

# Status message settings
STATUS_UPDATE_INTERVAL = safe_int(os.environ.get("STATUS_UPDATE_INTERVAL", "10"))
SHOW_DETAILED_STATUS = safe_bool(os.environ.get("SHOW_DETAILED_STATUS", "True"))

# File processing settings
PROCESS_IMAGES = safe_bool(os.environ.get("PROCESS_IMAGES", "True"))
PROCESS_VIDEOS = safe_bool(os.environ.get("PROCESS_VIDEOS", "True"))
PROCESS_DOCUMENTS = safe_bool(os.environ.get("PROCESS_DOCUMENTS", "True"))
PROCESS_AUDIO = safe_bool(os.environ.get("PROCESS_AUDIO", "True"))

# Queue settings
DOWNLOAD_QUEUE_SIZE = safe_int(os.environ.get("DOWNLOAD_QUEUE_SIZE", "100"))
UPLOAD_QUEUE_SIZE = safe_int(os.environ.get("UPLOAD_QUEUE_SIZE", "50"))

# Language settings
DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "en")
TIMEZONE = os.environ.get("TIMEZONE", "UTC")

# Webhook settings
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
WEBHOOK_PORT = safe_int(os.environ.get("WEBHOOK_PORT", "8443"))

# Feature flags
ENABLE_BATCH_DOWNLOAD = safe_bool(os.environ.get("ENABLE_BATCH_DOWNLOAD", "True"))
ENABLE_SINGLE_DOWNLOAD = safe_bool(os.environ.get("ENABLE_SINGLE_DOWNLOAD", "True"))
ENABLE_USER_REGISTRATION = safe_bool(os.environ.get("ENABLE_USER_REGISTRATION", "True"))
ENABLE_SESSION_MANAGEMENT = safe_bool(os.environ.get("ENABLE_SESSION_MANAGEMENT", "True"))

# Additional timeouts and limits
MAX_MESSAGE_LENGTH = safe_int(os.environ.get("MAX_MESSAGE_LENGTH", "4096"))
MAX_CAPTION_LENGTH = safe_int(os.environ.get("MAX_CAPTION_LENGTH", "1024"))
MAX_FILENAME_LENGTH = safe_int(os.environ.get("MAX_FILENAME_LENGTH", "255"))

# Backup and recovery settings
ENABLE_AUTO_BACKUP = safe_bool(os.environ.get("ENABLE_AUTO_BACKUP", "False"))
BACKUP_INTERVAL = safe_int(os.environ.get("BACKUP_INTERVAL", "86400"))
BACKUP_RETENTION_DAYS = safe_int(os.environ.get("BACKUP_RETENTION_DAYS", "7"))

# Advanced settings
ENABLE_ANALYTICS = safe_bool(os.environ.get("ENABLE_ANALYTICS", "True"))
ANALYTICS_UPDATE_INTERVAL = safe_int(os.environ.get("ANALYTICS_UPDATE_INTERVAL", "300"))
ENABLE_METRICS = safe_bool(os.environ.get("ENABLE_METRICS", "True"))
METRICS_PORT = safe_int(os.environ.get("METRICS_PORT", "9090"))

# Validation check
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")

if API_ID == 12345 or not API_HASH:
    raise ValueError("Valid API_ID and API_HASH are required!")

# Debug info
if DEBUG_MODE:
    print(f"Config loaded - ADMINS: {ADMINS}, BOT_WORKERS: {BOT_WORKERS}")
