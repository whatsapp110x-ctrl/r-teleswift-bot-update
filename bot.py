# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import logging
import sys
from pyrogram.client import Client
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
        logger.info("Bot instance created successfully")

    async def start(self):
        try:
            await super().start()
            bot_info = await self.get_me()
            logger.info(f"Bot Started Successfully! @{bot_info.username}")
            print(f"🤖 Bot Started: @{bot_info.username}")
            print("🔥 Powered By @Ashish")
            
            # Verify database connection
            try:
                from database.db import db
                # Test database connection
                test_user = await db.col.find_one({})
                logger.info("Database connection verified")
                print("💾 Database: Connected")
            except Exception as db_error:
                logger.error(f"Database connection error: {db_error}")
                print(f"⚠️ Database Warning: {db_error}")
                
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
    """Main function to run the bot"""
    bot = Bot()
    try:
        await bot.start()
        logger.info("Bot is running and ready to receive messages")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        # Don't re-raise in main, let it handle gracefully
    finally:
        try:
            await bot.stop()
        except:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal Error: {e}")

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
