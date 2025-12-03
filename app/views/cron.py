"""Cron job API endpoints."""
from flask import Blueprint, jsonify
from datetime import datetime
from app.services.coingecko import CoinGeckoService
from app.services.email import EmailService
from app.services.alert import AlertService
from app.models.price_history import PriceHistory

cron_bp = Blueprint('cron', __name__, url_prefix='/api/cron')


@cron_bp.route('/collect-data', methods=['GET', 'POST'])
def collect_data():
    """Collect cryptocurrency prices from CoinGecko API.
    
    This endpoint is triggered by Vercel Cron Job every minute.
    """
    try:
        # Fetch prices from CoinGecko
        coingecko = CoinGeckoService()
        prices = coingecko.get_prices()
        
        if not prices:
            raise Exception("No prices returned from CoinGecko")
        
        # Store prices in database
        timestamp = datetime.utcnow()
        PriceHistory.bulk_create(prices, timestamp)
        
        return jsonify({
            'success': True,
            'message': f'Collected {len(prices)} prices',
            'prices': prices,
            'timestamp': timestamp.isoformat()
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        
        # Send admin alert on failure
        email_service = EmailService()
        email_service.send_admin_alert(error_msg, "数据收集任务")
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@cron_bp.route('/analyze-data', methods=['GET', 'POST'])
def analyze_data():
    """Analyze prices and trigger alerts.
    
    This endpoint is triggered by Vercel Cron Job every minute.
    """
    try:
        alert_service = AlertService()
        checked, triggered = alert_service.process_alerts()
        
        return jsonify({
            'success': True,
            'message': f'Checked {checked} alerts, triggered {triggered}',
            'alerts_checked': checked,
            'alerts_triggered': triggered
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        
        # Send admin alert on failure
        email_service = EmailService()
        email_service.send_admin_alert(error_msg, "数据分析任务")
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

