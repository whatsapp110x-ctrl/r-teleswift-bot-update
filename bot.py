# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import logging
import sys
import time
import nest_asyncio
from datetime import datetime
from pyrogram.client import Client
from pyrogram.errors import FloodWait, AuthKeyUnregistered, SessionExpired
from config import API_ID, API_HASH, BOT_TOKEN, BOT_WORKERS, SLEEP_THRESHOLD

# Apply nest_asyncio for compatibility
nest_asyncio.apply()

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress noisy logs
logging.getLogger("pyrogram.crypto.aes").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.session").setLevel(logging.WARNING)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "techvj_save_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=BOT_WORKERS,
            sleep_threshold=SLEEP_THRESHOLD,
            max_concurrent_transmissions=10
        )
        self.start_time = datetime.utcnow()
        logger.info("Bot instance created successfully")

    async def start(self):
        try:
            await super().start()
            bot_info = await self.get_me()
            logger.info(f"Bot Started Successfully! @{bot_info.username}")
            print(f"🤖 Bot Started: @{bot_info.username}")
            print("🔥 Powered By @VJ_Botz")
            
            # Initialize database connection - non-blocking
            asyncio.create_task(self._init_database())
                
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            print(f"❌ Bot Start Error: {e}")
            raise

    async def _init_database(self):
        """Initialize database in background to avoid blocking bot startup"""
        try:
            await asyncio.sleep(1)  # Brief delay to let bot start
            from database.db import db
            db_success = await db.initialize()
            if db_success:
                logger.info("Database connection established")
                print("💾 Database: Connected")
            else:
                logger.warning("Database connection failed - using fallback mode")
                print("⚠️ Database: Using fallback mode")
        except Exception as db_error:
            logger.warning(f"Database initialization warning: {db_error}")
            print(f"⚠️ Database: Fallback mode active")

    async def stop(self, *args):
        try:
            await super().stop()
            logger.info("Bot stopped successfully")
            print("👋 Bot Stopped - Goodbye!")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

async def main():
    """Enhanced main function with better error handling"""
    bot = None
    try:
        logger.info("Starting VJ Save Restricted Content Bot")
        bot = Bot()
        await bot.start()
        logger.info("Bot is running and ready to receive messages")
        
        # Keep the bot running without excessive operations
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        # Don't re-raise, just log and exit gracefully
        
    finally:
        if bot:
            try:
                await bot.stop()
            except Exception as stop_error:
                logger.error(f"Error during bot stop: {stop_error}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal Error: {e}")
        print(f"💥 Fatal Error: {e}")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
