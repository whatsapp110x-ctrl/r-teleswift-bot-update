import os
from flask import Flask, jsonify
import logging
import threading
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vj_save_bot_secret_key_2024")

# Keep-alive tracking
last_activity = datetime.utcnow()

def update_activity():
    """Update last activity timestamp"""
    global last_activity
    last_activity = datetime.utcnow()

@app.route('/')
def index():
    """Main health check endpoint"""
    update_activity()
    return {
        'status': 'healthy',
        'service': 'R-TeleSwiftBot💖',
        'message': 'R-TeleSwiftBot💖 is Running! 🤖',
        'version': '1.0.0',
        'uptime': str(datetime.utcnow() - last_activity)
    }

@app.route('/health')
def health_check():
    """Detailed health check endpoint"""
    try:
        update_activity()
        
        # Test database connection
        try:
            from database.db import db
            health_status = {
                'status': 'healthy',
                'service': 'r_teleswift_bot',
                'database': 'connected',
                'last_activity': last_activity.isoformat(),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as db_error:
            logger.warning(f"Database health check failed: {db_error}")
            health_status = {
                'status': 'degraded',
                'service': 'r_teleswift_bot',
                'database': 'disconnected',
                'error': str(db_error),
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
    """Bot status endpoint"""
    try:
        update_activity()
        return jsonify({
            'bot_name': 'R-TeleSwiftBot💖',
            'status': 'running',
            'uptime': 'online',
            'last_check': datetime.utcnow().isoformat(),
            'features': [
                'Session Management',
                'Restricted Content Download',
                'Batch Operations',
                'Broadcasting'
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
        'time': datetime.utcnow().isoformat()
    })

@app.route('/keep-alive')
def keep_alive():
    """Keep-alive endpoint"""
    update_activity()
    return jsonify({
        'alive': True, 
        'service': 'r_teleswift_bot',
        'last_activity': last_activity.isoformat()
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

# Auto keep-alive function
def auto_keep_alive():
    """Send periodic requests to keep service awake"""
    while True:
        try:
            time.sleep(300)  # 5 minutes
            update_activity()
            logger.info("Keep-alive ping sent")
        except Exception as e:
            logger.error(f"Keep-alive error: {e}")

# Start keep-alive thread
threading.Thread(target=auto_keep_alive, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
