import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "12345"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Database configuration with fallback
DATABASE_URL = os.environ.get("DATABASE_URL", "")
DB_URI = DATABASE_URL if DATABASE_URL else os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DATABASE_NAME", "techvj_bot")

# Performance optimized settings
BOT_WORKERS = int(os.environ.get("BOT_WORKERS", "8"))  # Increased workers
SLEEP_THRESHOLD = int(os.environ.get("SLEEP_THRESHOLD", "10"))  # Reduced for speed

# File handling - optimized for speed
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", "2147483648"))  # 2GB
MAX_BATCH_SIZE = int(os.environ.get("MAX_BATCH_SIZE", "50"))  # Increased batch size

# High-speed download/upload settings
DOWNLOAD_CHUNK_SIZE = int(os.environ.get("DOWNLOAD_CHUNK_SIZE", "2048"))  # Increased chunk size
UPLOAD_CHUNK_SIZE = int(os.environ.get("UPLOAD_CHUNK_SIZE", "2048"))    # Increased chunk size

# Optimized timeout settings for speed
CONNECTION_TIMEOUT = int(os.environ.get("CONNECTION_TIMEOUT", "30"))
USER_INPUT_TIMEOUT = int(os.environ.get("USER_INPUT_TIMEOUT", "120"))
LOGIN_TIMEOUT = int(os.environ.get("LOGIN_TIMEOUT", "90"))
OTP_TIMEOUT = int(os.environ.get("OTP_TIMEOUT", "90"))
PASSWORD_TIMEOUT = int(os.environ.get("PASSWORD_TIMEOUT", "60"))

# Progress tracking - optimized for real-time updates
PROGRESS_UPDATE_INTERVAL = int(os.environ.get("PROGRESS_UPDATE_INTERVAL", "2"))  # Faster updates
PROGRESS_THROTTLE = int(os.environ.get("PROGRESS_THROTTLE", "2"))  # Reduced throttle

# Retry settings - optimized for speed vs reliability balance
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "2"))  # Reduced for speed
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", "2"))  # Faster retry
MINIMAL_DELAY = int(os.environ.get("MINIMAL_DELAY", "0.5"))  # Minimal delay

# Connection pool - high performance settings
CONNECTION_POOL_SIZE = int(os.environ.get("CONNECTION_POOL_SIZE", "12"))  # Increased pool
MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", "5"))  # Increased concurrency

# Session and thumbnail settings
SESSION_STRING_SIZE = int(os.environ.get("SESSION_STRING_SIZE", "300"))
THUMBNAIL_QUALITY = int(os.environ.get("THUMBNAIL_QUALITY", "70"))  # Optimized quality
THUMBNAIL_MAX_SIZE = int(os.environ.get("THUMBNAIL_MAX_SIZE", "524288"))  # 512KB

# Admin configuration
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split(",") if x.strip()]

# Additional optimized settings
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "❌ This content is restricted and cannot be downloaded.")
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "")
CUSTOM_CAPTION = os.environ.get("CUSTOM_CAPTION", "")

# Performance monitoring
ENABLE_STATS = bool(os.environ.get("ENABLE_STATS", True))
STATS_UPDATE_INTERVAL = int(os.environ.get("STATS_UPDATE_INTERVAL", "30"))  # seconds

# Broadcasting settings
BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", True))
BROADCAST_SLEEP_TIME = int(os.environ.get("BROADCAST_SLEEP_TIME", "0.5"))  # Faster broadcasting

# Auto cleanup and maintenance
AUTO_DELETE = bool(os.environ.get("AUTO_DELETE", True))
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "180"))  # 3 minutes
CLEANUP_TEMP_FILES = bool(os.environ.get("CLEANUP_TEMP_FILES", True))
TEMP_FILE_LIFETIME = int(os.environ.get("TEMP_FILE_LIFETIME", "1800"))  # 30 minutes

# Quality and format settings
VIDEO_QUALITY = os.environ.get("VIDEO_QUALITY", "high")
PHOTO_QUALITY = os.environ.get("PHOTO_QUALITY", "high")
PRESERVE_FILENAME = bool(os.environ.get("PRESERVE_FILENAME", True))

# Security and rate limiting
ENABLE_FLOOD_PROTECTION = bool(os.environ.get("ENABLE_FLOOD_PROTECTION", True))
FLOOD_LIMIT = int(os.environ.get("FLOOD_LIMIT", "15"))  # Increased limit
FLOOD_WINDOW = int(os.environ.get("FLOOD_WINDOW", "60"))  # seconds

# Feature flags
ENABLE_BATCH_DOWNLOAD = bool(os.environ.get("ENABLE_BATCH_DOWNLOAD", True))
ENABLE_SINGLE_DOWNLOAD = bool(os.environ.get("ENABLE_SINGLE_DOWNLOAD", True))
ENABLE_USER_REGISTRATION = bool(os.environ.get("ENABLE_USER_REGISTRATION", True))
ENABLE_SESSION_MANAGEMENT = bool(os.environ.get("ENABLE_SESSION_MANAGEMENT", True))

# Advanced performance settings
MAX_CONCURRENT_SESSIONS = int(os.environ.get("MAX_CONCURRENT_SESSIONS", "10"))  # Increased
ENABLE_CACHE = bool(os.environ.get("ENABLE_CACHE", True))
CACHE_EXPIRY_TIME = int(os.environ.get("CACHE_EXPIRY_TIME", "900"))  # 15 minutes

# Download location and file management
DOWNLOAD_LOCATION = os.environ.get("DOWNLOAD_LOCATION", "./downloads/")
MAX_MESSAGE_LENGTH = int(os.environ.get("MAX_MESSAGE_LENGTH", "4096"))
MAX_CAPTION_LENGTH = int(os.environ.get("MAX_CAPTION_LENGTH", "1024"))
MAX_FILENAME_LENGTH = int(os.environ.get("MAX_FILENAME_LENGTH", "255"))

# Additional constants for optimized performance
PYROGRAM_SESSION_NAME = os.environ.get("PYROGRAM_SESSION_NAME", "techvj_speed_session")
MEDIA_CACHE_TIME = int(os.environ.get("MEDIA_CACHE_TIME", "1800"))  # 30 minutes
USER_CACHE_TIME = int(os.environ.get("USER_CACHE_TIME", "900"))  # 15 minutes

# Status and monitoring
STATUS_UPDATE_INTERVAL = int(os.environ.get("STATUS_UPDATE_INTERVAL", "5"))  # Faster updates
SHOW_DETAILED_STATUS = bool(os.environ.get("SHOW_DETAILED_STATUS", True))

# Network optimization
CONNECTION_RETRIES = int(os.environ.get("CONNECTION_RETRIES", "2"))  # Reduced retries
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "25"))  # seconds

# User interaction optimization
CANCEL_TIMEOUT = int(os.environ.get("CANCEL_TIMEOUT", "30"))  # Reduced timeout
LOGIN_ATTEMPTS_LIMIT = int(os.environ.get("LOGIN_ATTEMPTS_LIMIT", "3"))
LOGIN_COOLDOWN_TIME = int(os.environ.get("LOGIN_COOLDOWN_TIME", "180"))  # 3 minutes

# Debug and logging
DEBUG_MODE = bool(os.environ.get("DEBUG_MODE", False))
VERBOSE_LOGGING = bool(os.environ.get("VERBOSE_LOGGING", False))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
