# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import logging
import sys
import time
from datetime import datetime
from pyrogram.client import Client
from pyrogram.errors import FloodWait, AuthKeyUnregistered, SessionExpired
from config import API_ID, API_HASH, BOT_TOKEN, BOT_WORKERS, SLEEP_THRESHOLD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "techvj_save_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=BOT_WORKERS,
            sleep_threshold=SLEEP_THRESHOLD
        )
        self.start_time = datetime.utcnow()
        logger.info("Bot instance created successfully")

    async def start(self):
        try:
            await super().start()
            bot_info = await self.get_me()
            logger.info(f"Bot Started Successfully! @{bot_info.username}")
            print(f"🤖 Bot Started: @{bot_info.username}")
            print("🔥 Powered By @Ashish")
            
            # Verify database connection with retry
            for attempt in range(3):
                try:
                    from database.db import db
                    # Test database connection
                    test_user = await db.col.find_one({})
                    logger.info("Database connection verified")
                    print("💾 Database: Connected")
                    break
                except Exception as db_error:
                    logger.warning(f"Database connection attempt {attempt + 1} failed: {db_error}")
                    if attempt == 2:
                        print(f"⚠️ Database Warning: {db_error}")
                    await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            print(f"❌ Bot Start Error: {e}")
            raise

    async def stop(self, *args):
        try:
            await super().stop()
            logger.info("Bot stopped successfully")
            print("👋 Bot Stopped - Goodbye!")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

async def main():
    """Main function with enhanced auto-restart capability"""
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        bot = Bot()
        try:
            await bot.start()
            logger.info("Bot is running and ready to receive messages")
            
            # Keep the bot running with enhanced health checks
            consecutive_errors = 0
            while True:
                try:
                    # Health check every 30 seconds
                    await bot.get_me()
                    consecutive_errors = 0
                    await asyncio.sleep(30)
                    
                except FloodWait as fw:
                    logger.warning(f"FloodWait: {fw.value}s")
                    await asyncio.sleep(fw.value + 5)
                    consecutive_errors = 0
                    
                except (AuthKeyUnregistered, SessionExpired) as auth_error:
                    logger.error(f"Bot session expired: {auth_error}")
                    break
                    
                except Exception as health_error:
                    consecutive_errors += 1
                    logger.error(f"Bot health check failed ({consecutive_errors}): {health_error}")
                    
                    if consecutive_errors >= 5:
                        logger.error("Too many consecutive errors, restarting bot")
                        break
                    
                    await asyncio.sleep(10 * consecutive_errors)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
            
        except Exception as e:
            retry_count += 1
            logger.error(f"Bot crashed (attempt {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                wait_time = min(300, 30 * retry_count)  # Exponential backoff, max 5 minutes
                logger.info(f"Restarting in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("Max retries reached. Bot shutting down.")
                
        finally:
            try:
                await bot.stop()
            except Exception as stop_error:
                logger.error(f"Error stopping bot: {stop_error}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal Error: {e}")
        logger.error(f"Fatal error: {e}")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
