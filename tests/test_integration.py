"""Integration tests for CryptoAlert application."""
import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.services.db import get_db_connection, init_db
from app.models.user import User
from app.models.alert_rule import AlertRule


@pytest.fixture(scope='module')
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture(scope='module')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='module')
def init_database():
    """Initialize database for tests."""
    init_db()
    yield
    # Cleanup after tests
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM alert_rules WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%test%')")
        cur.execute("DELETE FROM users WHERE email LIKE '%test%'")
        conn.commit()
    finally:
        cur.close()
        conn.close()


class TestUserRegistration:
    """Integration tests for user registration flow."""
    
    def test_register_page_loads(self, client):
        """Test registration page loads correctly."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'User Registration' in response.data
    
    def test_register_new_user(self, client, init_database):
        """Test registering a new user."""
        test_email = 'test_integration@example.com'
        
        # Clean up any existing test user
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM alert_rules WHERE user_id IN (SELECT id FROM users WHERE email = %s)", (test_email,))
            cur.execute("DELETE FROM users WHERE email = %s", (test_email,))
            conn.commit()
        finally:
            cur.close()
            conn.close()
        
        # Register new user
        response = client.post('/register', data={
            'email': test_email,
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify user was created in database
        user = User.find_by_email(test_email)
        assert user is not None
        assert user.email == test_email
    
    def test_register_duplicate_email(self, client, init_database):
        """Test registering with an existing email fails."""
        test_email = 'test_duplicate@example.com'
        
        # Clean up and create first user
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE email = %s", (test_email,))
            conn.commit()
        finally:
            cur.close()
            conn.close()
        
        User.create(test_email, 'password123')
        
        # Try to register again
        response = client.post('/register', data={
            'email': test_email,
            'password': 'password123',
            'confirm_password': 'password123'
        })
        
        assert b'already registered' in response.data


class TestAlertRuleCreation:
    """Integration tests for alert rule CRUD operations."""
    
    def test_create_alert_rule_flow(self, client, init_database):
        """Test full flow: register user -> login -> create alert -> verify in DB."""
        test_email = 'test_alert_flow@example.com'
        
        # Clean up
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM alert_rules WHERE user_id IN (SELECT id FROM users WHERE email = %s)", (test_email,))
            cur.execute("DELETE FROM users WHERE email = %s", (test_email,))
            conn.commit()
        finally:
            cur.close()
            conn.close()
        
        # Register user
        client.post('/register', data={
            'email': test_email,
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        })
        
        # Get user ID
        user = User.find_by_email(test_email)
        assert user is not None
        
        # Create alert via form
        response = client.post('/alerts/create', data={
            'currency': 'BTC',
            'condition': '>',
            'threshold': '50000.00'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify alert was created in database
        alerts = AlertRule.find_by_user(user.id)
        assert len(alerts) >= 1
        
        btc_alert = next((a for a in alerts if a.currency_symbol == 'BTC'), None)
        assert btc_alert is not None
        assert btc_alert.condition == '>'
        assert btc_alert.threshold_price == 50000.00
        assert btc_alert.is_active is True


class TestHealthCheck:
    """Integration tests for health check endpoint."""
    
    def test_health_endpoint(self, client, init_database):
        """Test health check returns 200 when database is connected."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'


class TestLoginLogout:
    """Integration tests for login/logout flow."""
    
    def test_login_success(self, client, init_database):
        """Test successful login."""
        test_email = 'test_login@example.com'
        password = 'testpassword123'
        
        # Clean up and create user
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE email = %s", (test_email,))
            conn.commit()
        finally:
            cur.close()
            conn.close()
        
        User.create(test_email, password)
        
        # Login
        response = client.post('/login', data={
            'email': test_email,
            'password': password
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Login successful' in response.data
    
    def test_login_wrong_password(self, client, init_database):
        """Test login with wrong password fails."""
        test_email = 'test_wrong_pass@example.com'
        
        # Clean up and create user
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE email = %s", (test_email,))
            conn.commit()
        finally:
            cur.close()
            conn.close()
        
        User.create(test_email, 'correctpassword')
        
        # Try wrong password
        response = client.post('/login', data={
            'email': test_email,
            'password': 'wrongpassword'
        })
        
        assert b'Invalid email or password' in response.data
    
    def test_logout(self, client, init_database):
        """Test logout clears session."""
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
