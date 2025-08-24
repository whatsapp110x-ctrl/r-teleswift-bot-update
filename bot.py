# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import logging
import sys
import time
import nest_asyncio
from datetime import datetime
from pyrogram import Client  # FIXED: This was missing
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
            "r_teleswift_bot_24x7",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=BOT_WORKERS,
            sleep_threshold=SLEEP_THRESHOLD,
            max_concurrent_transmissions=20  # Increased for better performance
        )
        self.start_time = datetime.utcnow()
        self.restart_count = 0
        logger.info("R-TeleSwiftBot💖 24/7 instance created successfully")

    async def start(self):
        try:
            await super().start()
            bot_info = await self.get_me()
            self.restart_count += 1
            
            logger.info(f"🚀 R-TeleSwiftBot💖 Started Successfully! @{bot_info.username}")
            logger.info(f"🔄 Restart Count: {self.restart_count}")
            logger.info(f"⏰ Start Time: {self.start_time}")
            
            print(f"🤖 R-TeleSwiftBot💖 Online: @{bot_info.username}")
            print(f"👑 Owner: Ashish 🥵")
            print(f"💖 24/7 Auto-Restart Mode Activated")
            print(f"🔄 Restart #: {self.restart_count}")
            print(f"⚡ Ultra High Speed Mode: ON")
            
            # Initialize database connection - non-blocking
            asyncio.create_task(self._init_database())
                
        except Exception as e:
            logger.error(f"Failed to start R-TeleSwiftBot💖: {e}")
            print(f"❌ Bot Start Error: {e}")
            raise

    async def _init_database(self):
        """Initialize database in background to avoid blocking bot startup"""
        try:
            await asyncio.sleep(2)  # Brief delay to let bot start
            from database.db import db
            db_success = await db.initialize()
            if db_success:
                logger.info("💾 Database: Connected")
                print("💾 Database: Connected & Ready")
            else:
                logger.warning("⚠️ Database: Using fallback mode")
                print("⚠️ Database: Fallback mode active")
        except Exception as db_error:
            logger.warning(f"Database initialization warning: {db_error}")
            print(f"⚠️ Database: Fallback mode active")

    async def stop(self, *args):
        try:
            await super().stop()
            logger.info("R-TeleSwiftBot💖 stopped - preparing for restart")
            print("🔄 R-TeleSwiftBot💖 Stopped - Auto-restart in progress...")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

    async def restart(self):
        """Restart the bot gracefully"""
        logger.info("Restarting R-TeleSwiftBot💖...")
        await self.stop()
        await asyncio.sleep(3)
        await self.start()

async def main():
    """Enhanced main function with 24/7 operation and auto-restart"""
    bot = None
    max_restart_attempts = 100
    restart_count = 0
    
    while restart_count < max_restart_attempts:
        try:
            restart_count += 1
            logger.info(f"Starting R-TeleSwiftBot💖 - 24/7 Edition (Attempt: {restart_count})")
            
            bot = Bot()
            bot.restart_count = restart_count
            await bot.start()
            
            logger.info("R-TeleSwiftBot💖 is running 24/7 and ready to receive messages")
            
            # Keep the bot running with auto-restart capability
            while True:
                try:
                    await asyncio.sleep(300)  # Check every 5 minutes
                    
                    # Simple health check
                    if bot and not bot.is_connected:
                        logger.warning("Bot disconnected, triggering restart...")
                        break
                        
                except asyncio.CancelledError:
                    logger.info("Bot operation cancelled")
                    break
                except Exception as health_error:
                    logger.error(f"Health check error: {health_error}")
                    break
            
        except KeyboardInterrupt:
            logger.info("R-TeleSwiftBot💖 stopped by user")
            break
        except (ConnectionError, AuthKeyUnregistered, SessionExpired) as conn_error:
            logger.error(f"Connection error (attempt {restart_count}): {conn_error}")
            if restart_count < max_restart_attempts:
                wait_time = min(30, restart_count * 5)  # Progressive backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            continue
        except Exception as e:
            logger.error(f"Bot error (attempt {restart_count}): {e}")
            if restart_count < max_restart_attempts:
                wait_time = min(60, restart_count * 10)  # Progressive backoff for unknown errors
                logger.info(f"Auto-restarting in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            continue
        finally:
            if bot:
                try:
                    await bot.stop()
                except Exception as stop_error:
                    logger.error(f"Error during bot stop: {stop_error}")
        
        # If we exit the inner loop, restart
        if restart_count < max_restart_attempts:
            logger.info(f"Restarting R-TeleSwiftBot💖 (Attempt {restart_count + 1})")
            await asyncio.sleep(5)
    
    logger.critical(f"Maximum restart attempts ({max_restart_attempts}) reached. Bot stopping.")
    print(f"💀 Maximum restart attempts reached. Bot stopped after {restart_count} attempts.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 R-TeleSwiftBot💖 stopped by user")
    except Exception as e:
        logger.error(f"Fatal Error: {e}")
        print(f"💥 Fatal Error: {e}")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
