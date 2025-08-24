#!/usr/bin/env python3
"""
Main entry point for R-TeleSwiftBot💖 - SIMPLIFIED 24/7 Edition
"""

import os
import sys
import logging
import asyncio
import threading
import signal
import time
import nest_asyncio

# Apply nest_asyncio
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_flask_app():
    """Run Flask web application"""
    try:
        from app import app
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting Flask app on port {port}")
        
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False, 
            threaded=True,
            use_reloader=False,
            use_debugger=False
        )
            
    except Exception as e:
        logger.error(f"Flask app error: {e}")
        raise

def run_telegram_bot():
    """Run Telegram bot - SIMPLIFIED"""
    max_restarts = 20
    restart_count = 0
    
    while restart_count < max_restarts:
        try:
            restart_count += 1
            logger.info(f"Starting R-TeleSwiftBot💖 - Attempt {restart_count}")
            
            if restart_count > 1:
                time.sleep(5)
            
            # Create new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                from bot import main as bot_main
                logger.info("R-TeleSwiftBot💖 starting...")
                loop.run_until_complete(bot_main())
            except Exception as e:
                logger.error(f"Bot error (attempt {restart_count}): {e}")
                if restart_count >= max_restarts:
                    logger.critical("Maximum restart attempts reached.")
                    break
            finally:
                try:
                    loop.close()
                except:
                    pass
            
            logger.warning(f"Bot stopped. Auto-restarting... (Attempt {restart_count + 1})")
            time.sleep(10)
        
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Critical bot error: {e}")
            if restart_count >= max_restarts:
                break
            time.sleep(15)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    os._exit(0)

# For Gunicorn, expose the Flask app
from app import app

def main():
    """SIMPLIFIED main function"""
    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info("Starting R-TeleSwiftBot💖 - 24/7 Edition")
        logger.info("👑 Owner: Ashish 🥵")
        
        # Start Flask in background
        flask_thread = threading.Thread(target=run_flask_app, daemon=True)
        flask_thread.start()
        logger.info("Flask server started")
        
        # Run bot in main thread
        logger.info("Starting bot process...")
        run_telegram_bot()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        logger.info("R-TeleSwiftBot💖 shutdown complete")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 R-TeleSwiftBot💖 stopped by user")
    except Exception as e:
        logger.error(f"Fatal Error: {e}")
        print(f"💥 Fatal Error: {e}")
