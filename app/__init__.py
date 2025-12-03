"""Flask application factory."""
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    # Register blueprints
    from app.views.auth import auth_bp
    from app.views.dashboard import dashboard_bp
    from app.views.alerts import alerts_bp
    from app.views.cron import cron_bp
    from app.views.health import health_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(cron_bp)
    app.register_blueprint(health_bp)
    
    return app

