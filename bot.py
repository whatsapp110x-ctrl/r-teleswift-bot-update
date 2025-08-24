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
            "r_teleswift_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=BOT_WORKERS,
            sleep_threshold=SLEEP_THRESHOLD,
            max_concurrent_transmissions=15  # Increased for better speed
        )
        self.start_time = datetime.utcnow()
        self.is_running = False
        logger.info("R-TeleSwiftBot💖 instance created successfully")

    async def start(self):
        try:
            await super().start()
            self.is_running = True
            bot_info = await self.get_me()
            logger.info(f"R-TeleSwiftBot💖 Started Successfully! @{bot_info.username}")
            print(f"🤖 R-TeleSwiftBot💖 Started: @{bot_info.username}")
            print("💖 Powered By R-TeleSwiftBot")
            print("🚀 Ultra High Speed Mode Activated")
            print("🔄 Auto-Restart Enabled - 24/7 Operation")
            
            # Initialize database connection - non-blocking
            asyncio.create_task(self._init_database())
                
        except Exception as e:
            logger.error(f"Failed to start R-TeleSwiftBot💖: {e}")
            print(f"❌ Bot Start Error: {e}")
            self.is_running = False
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
            self.is_running = False
            await super().stop()
            logger.info("R-TeleSwiftBot💖 stopped successfully")
            print("👋 R-TeleSwiftBot💖 Stopped - Goodbye!")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

    async def restart(self):
        """Restart the bot gracefully"""
        try:
            logger.info("Restarting R-TeleSwiftBot💖...")
            await self.stop()
            await asyncio.sleep(5)
            await self.start()
        except Exception as e:
            logger.error(f"Restart error: {e}")
            raise

async def main():
    """Enhanced main function with robust error handling and auto-restart"""
    bot = None
    retry_count = 0
    max_retries = 3
    
    while True:
        try:
            logger.info(f"Starting R-TeleSwiftBot💖 - Ultra High Speed Edition (attempt {retry_count + 1})")
            
            bot = Bot()
            await bot.start()
            
            if not bot.is_running:
                raise Exception("Bot failed to start properly")
            
            logger.info("R-TeleSwiftBot💖 is running and ready to receive messages")
            print("✅ Bot is now running 24/7 with auto-restart capability")
            
            # Reset retry count on successful start
            retry_count = 0
            
            # Keep the bot running with health monitoring
            while bot.is_running:
                try:
                    await asyncio.sleep(60)  # Check every minute
                    
                    # Basic health check
                    if bot and hasattr(bot, 'get_me'):
                        try:
                            await asyncio.wait_for(bot.get_me(), timeout=10.0)
                        except asyncio.TimeoutError:
                            logger.warning("Health check timeout - bot may be unresponsive")
                        except Exception as health_error:
                            logger.error(f"Health check failed: {health_error}")
                            raise Exception("Health check failed")
                            
                except asyncio.CancelledError:
                    logger.info("Bot operation cancelled")
                    break
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    raise
            
        except KeyboardInterrupt:
            logger.info("R-TeleSwiftBot💖 stopped by user")
            break
        except (AuthKeyUnregistered, SessionExpired) as auth_error:
            logger.error(f"Authentication error: {auth_error}")
            logger.info("Waiting 30 seconds before retry...")
            await asyncio.sleep(30)
            retry_count += 1
        except Exception as e:
            logger.error(f"Bot error: {e}")
            retry_count += 1
            
            if retry_count >= max_retries:
                logger.error(f"Max retries ({max_retries}) exceeded. Resetting retry count and continuing...")
                retry_count = 0
                await asyncio.sleep(60)  # Wait longer after max retries
            else:
                wait_time = min(retry_count * 10, 60)  # Progressive backoff, max 60 seconds
                logger.info(f"Retrying in {wait_time} seconds... (attempt {retry_count}/{max_retries})")
                await asyncio.sleep(wait_time)
            
        finally:
            if bot and bot.is_running:
                try:
                    await bot.stop()
                except Exception as stop_error:
                    logger.error(f"Error during bot stop: {stop_error}")
        
        # Small delay before restart attempt
        if retry_count > 0:
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 R-TeleSwiftBot💖 stopped by user")
    except Exception as e:
        logger.error(f"Fatal Error: {e}")
        print(f"💥 Fatal Error: {e}")
        # Auto-restart even on fatal errors
        print("🔄 Attempting restart in 10 seconds...")
        time.sleep(10)
        os.execv(sys.executable, ['python'] + sys.argv)

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
