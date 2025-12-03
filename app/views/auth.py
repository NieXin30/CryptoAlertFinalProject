"""Authentication views."""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get the currently logged in user."""
    if 'user_id' in session:
        return User.find_by_id(session['user_id'])
    return None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        
        # Check if user exists
        existing_user = User.find_by_email(email)
        if existing_user:
            flash('This email is already registered', 'error')
            return render_template('register.html')
        
        # Create user
        try:
            user = User.create(email, password)
            session['user_id'] = user.id
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        user = User.find_by_email(email)
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """User logout."""
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile and password change."""
    user = get_current_user()
    
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not old_password or not new_password:
            flash('Please fill in all password fields', 'error')
            return render_template('profile.html', user=user)
        
        if not user.check_password(old_password):
            flash('Current password is incorrect', 'error')
            return render_template('profile.html', user=user)
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('profile.html', user=user)
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters', 'error')
            return render_template('profile.html', user=user)
        
        user.update_password(new_password)
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('profile.html', user=user)
