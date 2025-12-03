"""Alert service for checking and triggering price alerts."""
from typing import List, Tuple
from app.models.alert_rule import AlertRule
from app.models.price_history import PriceHistory
from app.models.user import User
from app.services.email import EmailService


class AlertService:
    """Service for managing and triggering price alerts."""
    
    def __init__(self):
        self.email_service = EmailService()
    
    @staticmethod
    def check_rule_triggered(rule: AlertRule, current_price: float) -> bool:
        """Check if an alert rule is triggered by the current price.
        
        Args:
            rule: The alert rule to check.
            current_price: Current price of the cryptocurrency.
            
        Returns:
            True if the rule condition is met.
        """
        if rule.condition == '>':
            return current_price > rule.threshold_price
        elif rule.condition == '<':
            return current_price < rule.threshold_price
        return False
    
    def process_alerts(self) -> Tuple[int, int]:
        """Process all active alerts and send notifications.
        
        Returns:
            Tuple of (alerts_checked, alerts_triggered).
        """
        # Get all active rules
        active_rules = AlertRule.find_all_active()
        
        # Get latest prices
        latest_prices = PriceHistory.get_latest_prices()
        
        alerts_checked = 0
        alerts_triggered = 0
        
        for rule in active_rules:
            alerts_checked += 1
            
            # Get current price for this currency
            current_price = latest_prices.get(rule.currency_symbol)
            
            if current_price is None:
                continue
            
            # Check if rule is triggered
            if self.check_rule_triggered(rule, current_price):
                alerts_triggered += 1
                
                # Get user email
                user = User.find_by_id(rule.user_id)
                if user:
                    # Send notification
                    self.email_service.send_alert_email(
                        to_email=user.email,
                        currency=rule.currency_symbol,
                        condition=rule.condition,
                        threshold=rule.threshold_price,
                        current_price=current_price
                    )
                    
                    # Deactivate the rule after triggering
                    rule.update(is_active=False)
        
        return alerts_checked, alerts_triggered

