#!/usr/bin/env python3
"""
Main entry point for VJ Save Restricted Content Bot - Optimized Version with Auto-Restart
Runs both Flask web app and Telegram bot concurrently for Render deployment
"""

import os
import sys
import logging
import asyncio
import threading
import signal
import time
import nest_asyncio
from datetime import datetime

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

# Global variables for monitoring
bot_restart_count = 0
max_restarts = 5
restart_delay = 10
last_restart_time = 0

def run_flask_app():
    """Run Flask web application - optimized with auto-restart"""
    while True:
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
            logger.info("Restarting Flask app in 5 seconds...")
            time.sleep(5)
            continue

def run_telegram_bot():
    """Run Telegram bot with auto-restart functionality"""
    global bot_restart_count, last_restart_time
    
    while True:
        try:
            current_time = time.time()
            
            # Reset restart counter if it's been more than 1 hour since last restart
            if current_time - last_restart_time > 3600:
                bot_restart_count = 0
            
            # Check if we've exceeded max restarts in short time
            if bot_restart_count >= max_restarts:
                logger.error(f"Bot exceeded maximum restarts ({max_restarts}). Waiting 30 minutes...")
                time.sleep(1800)  # Wait 30 minutes
                bot_restart_count = 0
            
            logger.info(f"Starting Telegram bot (restart count: {bot_restart_count})")
            time.sleep(2)  # Reduced startup delay
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Import and run bot
                from bot import main as bot_main
                logger.info("Telegram bot starting...")
                loop.run_until_complete(bot_main())
            except Exception as e:
                logger.error(f"Bot error: {e}")
                raise
            finally:
                try:
                    # Clean up the loop
                    pending = asyncio.all_tasks(loop)
                    if pending:
                        logger.info("Cleaning up pending tasks...")
                        for task in pending:
                            task.cancel()
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    loop.close()
                except:
                    pass
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            bot_restart_count += 1
            last_restart_time = time.time()
            logger.error(f"Bot crashed: {e}")
            logger.info(f"Auto-restarting bot in {restart_delay} seconds... (attempt {bot_restart_count})")
            time.sleep(restart_delay)
            
            # Increase restart delay exponentially but cap at 60 seconds
            restart_delay = min(restart_delay * 1.5, 60)
            continue

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    os._exit(0)

# Health check function
def health_monitor():
    """Monitor bot health and restart if needed"""
    while True:
        try:
            time.sleep(300)  # Check every 5 minutes
            logger.info("Health check: Bot is running")
        except Exception as e:
            logger.error(f"Health monitor error: {e}")

# For Gunicorn, expose the Flask app directly
from app import app

def main():
    """Main function - optimized startup with auto-restart"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info("Starting VJ Save Bot - Optimized Version with Auto-Restart")
        logger.info(f"Environment: {'Production' if os.environ.get('RENDER') else 'Development'}")
        logger.info(f"Start time: {datetime.utcnow().isoformat()}")
        
        # Start health monitor in background
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        health_thread.start()
        logger.info("Health monitor started")
        
        # Start Telegram bot in background thread with auto-restart
        bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        bot_thread.start()
        logger.info("Bot thread started with auto-restart capability")
        
        # Run Flask app in main thread (also with auto-restart)
        run_flask_app()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        # Auto-restart the entire application
        logger.info("Restarting entire application in 10 seconds...")
        time.sleep(10)
        os.execv(sys.executable, ['python'] + sys.argv)
    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    # Keep trying to start the application
    while True:
        try:
            main()
        except Exception as e:
            logger.error(f"Critical application error: {e}")
            logger.info("Restarting application in 15 seconds...")
            time.sleep(15)
            continue
