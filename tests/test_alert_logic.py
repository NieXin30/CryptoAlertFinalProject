"""Unit tests for alert logic."""
import pytest
from app.services.alert import AlertService
from app.models.alert_rule import AlertRule


class MockAlertRule:
    """Mock alert rule for testing."""
    def __init__(self, condition, threshold_price):
        self.condition = condition
        self.threshold_price = threshold_price


class TestAlertLogic:
    """Test cases for alert triggering logic."""
    
    def test_price_above_threshold_greater_condition(self):
        """Test: price > threshold when condition is '>'."""
        rule = MockAlertRule(condition='>', threshold_price=50000.0)
        current_price = 55000.0
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is True
    
    def test_price_below_threshold_greater_condition(self):
        """Test: price < threshold when condition is '>'."""
        rule = MockAlertRule(condition='>', threshold_price=50000.0)
        current_price = 45000.0
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is False
    
    def test_price_equal_threshold_greater_condition(self):
        """Test: price == threshold when condition is '>' (should not trigger)."""
        rule = MockAlertRule(condition='>', threshold_price=50000.0)
        current_price = 50000.0
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is False
    
    def test_price_below_threshold_less_condition(self):
        """Test: price < threshold when condition is '<'."""
        rule = MockAlertRule(condition='<', threshold_price=50000.0)
        current_price = 45000.0
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is True
    
    def test_price_above_threshold_less_condition(self):
        """Test: price > threshold when condition is '<'."""
        rule = MockAlertRule(condition='<', threshold_price=50000.0)
        current_price = 55000.0
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is False
    
    def test_price_equal_threshold_less_condition(self):
        """Test: price == threshold when condition is '<' (should not trigger)."""
        rule = MockAlertRule(condition='<', threshold_price=50000.0)
        current_price = 50000.0
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is False
    
    def test_small_price_difference_above(self):
        """Test: small price difference triggers correctly."""
        rule = MockAlertRule(condition='>', threshold_price=0.00001234)
        current_price = 0.00001235
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is True
    
    def test_small_price_difference_below(self):
        """Test: small price difference below threshold."""
        rule = MockAlertRule(condition='<', threshold_price=0.00001234)
        current_price = 0.00001233
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is True
    
    def test_large_price_values(self):
        """Test: large price values work correctly."""
        rule = MockAlertRule(condition='>', threshold_price=99999999.99)
        current_price = 100000000.00
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is True
    
    def test_invalid_condition_returns_false(self):
        """Test: invalid condition returns False."""
        rule = MockAlertRule(condition='=', threshold_price=50000.0)
        current_price = 50000.0
        
        result = AlertService.check_rule_triggered(rule, current_price)
        
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

