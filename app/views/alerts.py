"""Alert management views."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.views.auth import login_required, get_current_user
from app.models.alert_rule import AlertRule
from app.services.coingecko import CoinGeckoService

alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')


@alerts_bp.route('/')
@login_required
def list_alerts():
    """List all alerts for current user."""
    user = get_current_user()
    alerts = AlertRule.find_by_user(user.id)
    currencies = CoinGeckoService.get_supported_currencies()
    return render_template('alerts.html', alerts=alerts, currencies=currencies, user=user)


@alerts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_alert():
    """Create a new alert rule."""
    user = get_current_user()
    currencies = CoinGeckoService.get_supported_currencies()
    
    if request.method == 'POST':
        currency = request.form.get('currency', '').upper()
        condition = request.form.get('condition', '')
        threshold = request.form.get('threshold', '')
        
        # Validation
        if not currency or not condition or not threshold:
            flash('Please fill in all fields', 'error')
            return render_template('alert_form.html', currencies=currencies, user=user)
        
        if currency not in [s for s in currencies.values()]:
            flash('Unsupported cryptocurrency', 'error')
            return render_template('alert_form.html', currencies=currencies, user=user)
        
        if condition not in ['>', '<']:
            flash('Invalid condition type', 'error')
            return render_template('alert_form.html', currencies=currencies, user=user)
        
        try:
            threshold_price = float(threshold)
            if threshold_price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            flash('Please enter a valid price', 'error')
            return render_template('alert_form.html', currencies=currencies, user=user)
        
        # Create alert
        try:
            AlertRule.create(
                user_id=user.id,
                currency_symbol=currency,
                condition=condition,
                threshold_price=threshold_price
            )
            flash('Alert rule created successfully!', 'success')
            return redirect(url_for('alerts.list_alerts'))
        except Exception as e:
            flash(f'Failed to create alert: {str(e)}', 'error')
            return render_template('alert_form.html', currencies=currencies, user=user)
    
    return render_template('alert_form.html', currencies=currencies, user=user)


@alerts_bp.route('/edit/<int:alert_id>', methods=['GET', 'POST'])
@login_required
def edit_alert(alert_id):
    """Edit an existing alert rule."""
    user = get_current_user()
    alert = AlertRule.find_by_id(alert_id)
    
    if not alert or alert.user_id != user.id:
        flash('Alert rule not found', 'error')
        return redirect(url_for('alerts.list_alerts'))
    
    currencies = CoinGeckoService.get_supported_currencies()
    
    if request.method == 'POST':
        currency = request.form.get('currency', '').upper()
        condition = request.form.get('condition', '')
        threshold = request.form.get('threshold', '')
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        if not currency or not condition or not threshold:
            flash('Please fill in all fields', 'error')
            return render_template('alert_form.html', alert=alert, currencies=currencies, user=user)
        
        try:
            threshold_price = float(threshold)
            if threshold_price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            flash('Please enter a valid price', 'error')
            return render_template('alert_form.html', alert=alert, currencies=currencies, user=user)
        
        # Update alert
        try:
            alert.update(
                currency_symbol=currency,
                condition=condition,
                threshold_price=threshold_price,
                is_active=is_active
            )
            flash('Alert rule updated successfully!', 'success')
            return redirect(url_for('alerts.list_alerts'))
        except Exception as e:
            flash(f'Failed to update alert: {str(e)}', 'error')
            return render_template('alert_form.html', alert=alert, currencies=currencies, user=user)
    
    return render_template('alert_form.html', alert=alert, currencies=currencies, user=user)


@alerts_bp.route('/delete/<int:alert_id>', methods=['POST'])
@login_required
def delete_alert(alert_id):
    """Delete an alert rule."""
    user = get_current_user()
    alert = AlertRule.find_by_id(alert_id)
    
    if not alert or alert.user_id != user.id:
        flash('Alert rule not found', 'error')
        return redirect(url_for('alerts.list_alerts'))
    
    try:
        alert.delete()
        flash('Alert rule deleted', 'success')
    except Exception as e:
        flash(f'Failed to delete alert: {str(e)}', 'error')
    
    return redirect(url_for('alerts.list_alerts'))


@alerts_bp.route('/toggle/<int:alert_id>', methods=['POST'])
@login_required
def toggle_alert(alert_id):
    """Toggle alert active status."""
    user = get_current_user()
    alert = AlertRule.find_by_id(alert_id)
    
    if not alert or alert.user_id != user.id:
        flash('Alert rule not found', 'error')
        return redirect(url_for('alerts.list_alerts'))
    
    try:
        alert.update(is_active=not alert.is_active)
        status = 'enabled' if alert.is_active else 'disabled'
        flash(f'Alert rule {status}', 'success')
    except Exception as e:
        flash(f'Operation failed: {str(e)}', 'error')
    
    return redirect(url_for('alerts.list_alerts'))
