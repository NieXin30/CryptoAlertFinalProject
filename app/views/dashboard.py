"""Dashboard views."""
from flask import Blueprint, render_template, session, redirect, url_for
from app.views.auth import login_required, get_current_user
from app.models.price_history import PriceHistory
from app.models.alert_rule import AlertRule
from app.services.coingecko import CoinGeckoService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    """Main dashboard page."""
    # Get latest prices from database
    prices = PriceHistory.get_latest_prices()
    
    # Get supported currencies with their full names
    currencies = CoinGeckoService.get_supported_currencies()
    
    # Prepare price data for display
    price_data = []
    for coin_id, symbol in currencies.items():
        price = prices.get(symbol)
        price_data.append({
            'symbol': symbol,
            'name': coin_id.capitalize(),
            'price': price
        })
    
    # Check if user is logged in
    user = None
    user_alerts = []
    if 'user_id' in session:
        user = get_current_user()
        if user:
            user_alerts = AlertRule.find_by_user(user.id)
    
    return render_template('dashboard.html', 
                         prices=price_data, 
                         user=user, 
                         alerts=user_alerts)

