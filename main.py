#!/usr/bin/env python3
"""
Main entry point for VJ Save Restricted Content Bot - Optimized Version
Runs both Flask web app and Telegram bot concurrently for Render deployment
"""

import os
import sys
import logging
import asyncio
import threading
import signal
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
    """Run Flask web application - optimized"""
    try:
        from app import app
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting Flask app on port {port}")
        
        # Optimized Flask settings
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
    """Run Telegram bot in separate thread - optimized"""
    try:
        import time
        time.sleep(2)  # Reduced startup delay
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Import and run bot
            from bot import main as bot_main
            logger.info("Starting Telegram bot")
            loop.run_until_complete(bot_main())
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            try:
                loop.close()
            except:
                pass
        
    except Exception as e:
        logger.error(f"Bot thread error: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    os._exit(0)

# For Gunicorn, expose the Flask app directly
from app import app

def main():
    """Main function - optimized startup"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info("Starting VJ Save Bot - Optimized Version")
        logger.info(f"Environment: {'Production' if os.environ.get('RENDER') else 'Development'}")
        
        # Start Telegram bot in background thread
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot thread started")
        
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
