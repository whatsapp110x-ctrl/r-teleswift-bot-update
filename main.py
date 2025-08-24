#!/usr/bin/env python3
"""
Main entry point for R-TeleSwiftBot💖 - 24/7 Auto-Restart Edition
Runs both Flask web app and Telegram bot with auto-restart functionality
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

# Global variables for restart management
restart_required = False
bot_process = None
flask_thread = None
restart_count = 0
MAX_RESTARTS = 100  # Maximum restarts before giving up

def run_flask_app():
    """Run Flask web application - optimized for 24/7"""
    try:
        from app import app
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting Flask app on port {port} - 24/7 Mode")
        
        # Optimized Flask settings for 24/7 operation
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
    """Run Telegram bot with auto-restart capability"""
    global restart_required, restart_count
    
    while True:
        try:
            restart_count += 1
            logger.info(f"Starting R-TeleSwiftBot💖 - Attempt {restart_count}")
            
            # Small delay to prevent rapid restarts
            if restart_count > 1:
                time.sleep(5)
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Import and run bot
                from bot import main as bot_main
                logger.info("R-TeleSwiftBot💖 starting...")
                loop.run_until_complete(bot_main())
            except Exception as e:
                logger.error(f"Bot error (attempt {restart_count}): {e}")
                if restart_count >= MAX_RESTARTS:
                    logger.critical("Maximum restart attempts reached. Stopping auto-restart.")
                    break
            finally:
                try:
                    loop.close()
                except:
                    pass
            
            # If we reach here, the bot stopped - restart it
            if not restart_required:
                logger.warning(f"Bot stopped unexpectedly. Auto-restarting in 10 seconds... (Attempt {restart_count + 1})")
                time.sleep(10)
            else:
                logger.info("Bot restart requested")
                restart_required = False
                time.sleep(3)
        
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Critical bot thread error: {e}")
            if restart_count >= MAX_RESTARTS:
                logger.critical("Maximum restart attempts reached due to critical errors.")
                break
            time.sleep(15)  # Longer delay for critical errors

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global restart_required
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    restart_required = False
    
    # Give some time for cleanup
    time.sleep(2)
    
    logger.info("R-TeleSwiftBot💖 shutting down...")
    os._exit(0)

def monitor_bot():
    """Monitor bot health and restart if necessary"""
    global restart_required, restart_count
    
    while True:
        try:
            time.sleep(300)  # Check every 5 minutes
            
            # Simple health check - you can expand this
            current_time = datetime.now()
            logger.info(f"Health check - Bot running for {restart_count} cycles at {current_time}")
            
            # You can add more sophisticated health checks here
            
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            time.sleep(60)

def auto_restart_scheduler():
    """Schedule automatic restarts (optional - every 24 hours)"""
    global restart_required
    
    while True:
        try:
            # Restart every 24 hours for maintenance
            time.sleep(24 * 60 * 60)  # 24 hours
            
            logger.info("Scheduled 24-hour restart initiated")
            restart_required = True
            
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(3600)  # Wait 1 hour before trying again

# For Gunicorn, expose the Flask app directly
from app import app

def main():
    """Main function with 24/7 auto-restart capability"""
    global flask_thread, restart_count
    
    try:
        # Register signal handlers
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info("Starting R-TeleSwiftBot💖 - 24/7 Auto-Restart Edition")
        logger.info(f"Environment: {'Production' if os.environ.get('RENDER') else 'Development'}")
        logger.info("🚀 24/7 Auto-restart system activated")
        
        # Start Flask app in background thread
        flask_thread = threading.Thread(target=run_flask_app, daemon=True)
        flask_thread.start()
        logger.info("Flask web server started in background")
        
        # Start bot monitor in background thread
        monitor_thread = threading.Thread(target=monitor_bot, daemon=True)
        monitor_thread.start()
        logger.info("Bot health monitor started")
        
        # Start auto-restart scheduler in background thread
        scheduler_thread = threading.Thread(target=auto_restart_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("24-hour restart scheduler started")
        
        # Run Telegram bot in main thread with auto-restart
        logger.info("Starting main bot process with auto-restart capability")
        run_telegram_bot()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        restart_count += 1
        if restart_count < MAX_RESTARTS:
            logger.info("Restarting application due to error...")
            time.sleep(5)
            main()  # Recursive restart
        else:
            logger.critical("Maximum restart attempts reached. Application stopping.")
    finally:
        logger.info("R-TeleSwiftBot💖 shutdown complete")

def restart_bot():
    """Function to manually restart the bot"""
    global restart_required
    logger.info("Manual restart requested")
    restart_required = True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 R-TeleSwiftBot💖 stopped by user")
    except Exception as e:
        logger.error(f"Fatal Error: {e}")
        print(f"💥 Fatal Error: {e}")
        # Try to restart one more time
        time.sleep(10)
        try:
            main()
        except:
            print("💀 Unable to restart. Application terminated.")
