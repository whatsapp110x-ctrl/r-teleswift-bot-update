#!/usr/bin/env python3
"""
Main entry point for VJ Save Restricted Content Bot
Runs both Flask web app and Telegram bot concurrently for Render deployment
"""

import os
import sys
import logging
import asyncio
import threading
import signal
from concurrent.futures import ThreadPoolExecutor
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
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
        
        # Run Flask app directly
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
            
    except Exception as e:
        logger.error(f"Flask app error: {e}")
        raise

def run_telegram_bot():
    """Run Telegram bot in separate thread with proper event loop"""
    try:
        import time
        time.sleep(3)  # Give Flask time to start
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Import and run bot
            from bot import main as bot_main
            logger.info("Starting Telegram bot in separate thread")
            loop.run_until_complete(bot_main())
        except Exception as e:
            logger.error(f"Bot error in thread: {e}")
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Bot thread error: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    os._exit(0)

# For Gunicorn, expose the Flask app directly
from app import app

def main():
    """Main function to run both Flask and Telegram bot"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info("Starting VJ Save Restricted Content Bot")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Environment: {'Production' if os.environ.get('RENDER') else 'Development'}")
        
        # Start Telegram bot in background thread
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot thread started in background")
        
        # Run Flask app in main thread
        run_flask_app()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()
