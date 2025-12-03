"""Alert rule model."""
from typing import List, Optional
from app.services.db import get_db_connection


class AlertRule:
    """Alert rule model for price monitoring."""
    
    def __init__(self, id=None, user_id=None, currency_symbol=None, 
                 condition=None, threshold_price=None, is_active=True, created_at=None):
        self.id = id
        self.user_id = user_id
        self.currency_symbol = currency_symbol
        self.condition = condition  # '>' or '<'
        self.threshold_price = threshold_price
        self.is_active = is_active
        self.created_at = created_at
    
    @staticmethod
    def create(user_id: int, currency_symbol: str, condition: str, threshold_price: float) -> 'AlertRule':
        """Create a new alert rule."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO alert_rules (user_id, currency_symbol, condition, threshold_price) 
                   VALUES (%s, %s, %s, %s) RETURNING id, is_active, created_at""",
                (user_id, currency_symbol.upper(), condition, threshold_price)
            )
            result = cur.fetchone()
            conn.commit()
            return AlertRule(
                id=result[0], user_id=user_id, currency_symbol=currency_symbol.upper(),
                condition=condition, threshold_price=threshold_price,
                is_active=result[1], created_at=result[2]
            )
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def find_by_user(user_id: int) -> List['AlertRule']:
        """Find all alert rules for a user."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """SELECT id, user_id, currency_symbol, condition, threshold_price, is_active, created_at 
                   FROM alert_rules WHERE user_id = %s ORDER BY created_at DESC""",
                (user_id,)
            )
            rows = cur.fetchall()
            return [
                AlertRule(id=r[0], user_id=r[1], currency_symbol=r[2], condition=r[3],
                         threshold_price=float(r[4]), is_active=r[5], created_at=r[6])
                for r in rows
            ]
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def find_by_id(rule_id: int) -> Optional['AlertRule']:
        """Find alert rule by ID."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """SELECT id, user_id, currency_symbol, condition, threshold_price, is_active, created_at 
                   FROM alert_rules WHERE id = %s""",
                (rule_id,)
            )
            row = cur.fetchone()
            if row:
                return AlertRule(id=row[0], user_id=row[1], currency_symbol=row[2], 
                               condition=row[3], threshold_price=float(row[4]),
                               is_active=row[5], created_at=row[6])
            return None
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def find_all_active() -> List['AlertRule']:
        """Find all active alert rules."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """SELECT id, user_id, currency_symbol, condition, threshold_price, is_active, created_at 
                   FROM alert_rules WHERE is_active = TRUE"""
            )
            rows = cur.fetchall()
            return [
                AlertRule(id=r[0], user_id=r[1], currency_symbol=r[2], condition=r[3],
                         threshold_price=float(r[4]), is_active=r[5], created_at=r[6])
                for r in rows
            ]
        finally:
            cur.close()
            conn.close()
    
    def update(self, currency_symbol: str = None, condition: str = None, 
               threshold_price: float = None, is_active: bool = None) -> bool:
        """Update alert rule."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            updates = []
            values = []
            if currency_symbol is not None:
                updates.append("currency_symbol = %s")
                values.append(currency_symbol.upper())
                self.currency_symbol = currency_symbol.upper()
            if condition is not None:
                updates.append("condition = %s")
                values.append(condition)
                self.condition = condition
            if threshold_price is not None:
                updates.append("threshold_price = %s")
                values.append(threshold_price)
                self.threshold_price = threshold_price
            if is_active is not None:
                updates.append("is_active = %s")
                values.append(is_active)
                self.is_active = is_active
            
            if updates:
                values.append(self.id)
                cur.execute(
                    f"UPDATE alert_rules SET {', '.join(updates)} WHERE id = %s",
                    values
                )
                conn.commit()
            return True
        finally:
            cur.close()
            conn.close()
    
    def delete(self) -> bool:
        """Delete alert rule."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM alert_rules WHERE id = %s", (self.id,))
            conn.commit()
            return True
        finally:
            cur.close()
            conn.close()

