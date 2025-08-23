import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "12345"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Your database URI from mongodb
DB_URI = os.environ.get("DATABASE_URL", "")

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

# Start message
START_MSG = os.environ.get("START_MSG", """
🎉 **Welcome to VJ Save Restricted Content Bot!** 

📱 **How to use:**
1. Send me any Telegram post link
2. I'll download and send the content to you
3. For batch downloads, use range format: `link/start-end`

✨ **Features:**
• Single post download
• Bulk/batch download
• High-quality media downloads
• Fast and reliable

👨‍💻 **Developer:** @VJ_Botz
🔥 **Channel:** @Tech_VJ

Send me a Telegram link to get started!
""")

# Help message
HELP_MSG = os.environ.get("HELP_MSG", """
📖 **Help & Commands**

**Commands:**
• `/start` - Start the bot
• `/help` - Show this help message
• `/login` - Login with your Telegram account
• `/logout` - Logout from your account
• `/cancel` - Cancel current operation

**How to use:**
1. Login with `/login` command first
2. Send any Telegram post link
3. For single post: `https://t.me/channel/123`
4. For batch: `https://t.me/channel/123-130`

**Link formats supported:**
• `https://t.me/username/123`
• `https://t.me/c/123456789/123`
• `https://t.me/b/123456789_123/123`

**Batch download:**
• Use format: `link/start-end`
• Max batch size: 50 messages
• Example: `https://t.me/channel/100-150`

Need help? Contact: @VJ_Botz
""")
