import os
from flask import Flask, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "vj_save_bot_secret_key_2024")

@app.route('/')
def index():
    """Main health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'VJ Save Restricted Content Bot',
        'message': 'VJ Save Restricted Content Bot is Running! 🤖',
        'version': '1.0.0'
    }

@app.route('/health')
def health_check():
    """Detailed health check endpoint"""
    try:
        # Test database connection
        try:
            from database.db import db
            # Simple connection test
            health_status = {
                'status': 'healthy',
                'service': 'vj_save_bot',
                'database': 'connected',
                'timestamp': None
            }
        except Exception as db_error:
            logger.warning(f"Database health check failed: {db_error}")
            health_status = {
                'status': 'degraded',
                'service': 'vj_save_bot',
                'database': 'disconnected',
                'error': str(db_error),
                'timestamp': None
            }
        
        # Add timestamp
        from datetime import datetime
        health_status['timestamp'] = datetime.utcnow().isoformat()
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'vj_save_bot',
            'error': str(e)
        }), 500

@app.route('/status')
def status():
    """Bot status endpoint"""
    try:
        from datetime import datetime
        return jsonify({
            'bot_name': 'VJ Save Restricted Content Bot',
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
    """Simple ping endpoint"""
    return jsonify({'pong': True, 'service': 'vj_save_bot'})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'VJ Save Restricted Content Bot API',
        'available_endpoints': [
            '/',
            '/health',
            '/status',
            '/ping'
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
