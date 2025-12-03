"""Health check endpoint."""
from flask import Blueprint, jsonify
from app.services.db import get_db_connection

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """Health check endpoint.
    
    Returns HTTP 200 if application is healthy.
    """
    try:
        # Test database connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

