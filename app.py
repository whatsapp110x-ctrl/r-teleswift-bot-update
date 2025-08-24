import os
from flask import Flask, jsonify
import logging
import threading
import time
import psutil
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "r_teleswift_bot_secret_key_2024")

# Keep-alive tracking
last_activity = datetime.utcnow()
bot_health_status = {"status": "starting", "last_check": datetime.utcnow()}

def update_activity():
    """Update last activity timestamp"""
    global last_activity
    last_activity = datetime.utcnow()

def update_bot_health(status, details=None):
    """Update bot health status"""
    global bot_health_status
    bot_health_status = {
        "status": status,
        "last_check": datetime.utcnow(),
        "details": details or {}
    }

@app.route('/')
def index():
    """Main health check endpoint"""
    update_activity()
    return {
        'status': 'healthy',
        'service': 'R-TeleSwiftBot💖',
        'message': 'R-TeleSwiftBot💖 is Running! 🤖',
        'version': '2.0.0',
        'features': ['24/7 Operation', 'Auto-Restart', 'Ultra High Speed'],
        'uptime': str(datetime.utcnow() - last_activity),
        'bot_health': bot_health_status
    }

@app.route('/health')
def health_check():
    """Detailed health check endpoint with system monitoring"""
    try:
        update_activity()
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Test database connection
        try:
            from database.db import db
            db_status = 'connected'
        except Exception as db_error:
            logger.warning(f"Database health check failed: {db_error}")
            db_status = 'disconnected'
        
        health_status = {
            'status': 'healthy',
            'service': 'r_teleswift_bot',
            'database': db_status,
            'bot_health': bot_health_status,
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': (disk.used / disk.total) * 100,
                'available_memory_mb': memory.available / (1024*1024)
            },
            'last_activity': last_activity.isoformat(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'r_teleswift_bot',
            'error': str(e)
        }), 500

@app.route('/status')
def status():
    """Bot status endpoint with enhanced monitoring"""
    try:
        update_activity()
        return jsonify({
            'bot_name': 'R-TeleSwiftBot💖',
            'status': 'running',
            'uptime': 'online',
            'last_check': datetime.utcnow().isoformat(),
            'bot_health': bot_health_status,
            'features': [
                'Session Management',
                'Restricted Content Download',
                'Serial Batch Operations',
                'Broadcasting',
                'Ultra High Speed Downloads',
                '24/7 Auto-Restart Operation'
            ]
        })
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ping')
def ping():
    """Simple ping endpoint to keep service awake"""
    update_activity()
    return jsonify({
        'pong': True, 
        'service': 'r_teleswift_bot', 
        'time': datetime.utcnow().isoformat(),
        'auto_restart': 'enabled'
    })

@app.route('/keep-alive')
def keep_alive():
    """Keep-alive endpoint"""
    update_activity()
    return jsonify({
        'alive': True, 
        'service': 'r_teleswift_bot',
        'last_activity': last_activity.isoformat(),
        'continuous_operation': '24/7'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'R-TeleSwiftBot💖 API',
        'available_endpoints': [
            '/',
            '/health',
            '/status',
            '/ping',
            '/keep-alive'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong with the bot service'
    }), 500

# Enhanced auto keep-alive function
def auto_keep_alive():
    """Send periodic requests to keep service awake with enhanced monitoring"""
    while True:
        try:
            time.sleep(300)  # 5 minutes
            update_activity()
            update_bot_health("monitoring", {"keep_alive": True, "timestamp": datetime.utcnow().isoformat()})
            logger.info("Keep-alive ping sent with health update")
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")

# Start keep-alive thread
threading.Thread(target=auto_keep_alive, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
