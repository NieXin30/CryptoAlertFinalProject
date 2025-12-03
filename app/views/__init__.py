"""Views package."""
from app.views.auth import auth_bp
from app.views.dashboard import dashboard_bp
from app.views.alerts import alerts_bp
from app.views.cron import cron_bp
from app.views.health import health_bp

__all__ = ['auth_bp', 'dashboard_bp', 'alerts_bp', 'cron_bp', 'health_bp']

