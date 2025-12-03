"""Price history model."""
from typing import List, Optional, Dict
from datetime import datetime
from app.services.db import get_db_connection


class PriceHistory:
    """Price history model for storing cryptocurrency prices."""
    
    def __init__(self, id=None, currency_symbol=None, price_usd=None, timestamp=None):
        self.id = id
        self.currency_symbol = currency_symbol
        self.price_usd = price_usd
        self.timestamp = timestamp
    
    @staticmethod
    def create(currency_symbol: str, price_usd: float, timestamp: datetime = None) -> 'PriceHistory':
        """Create a new price record."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO price_history (currency_symbol, price_usd, timestamp) 
                   VALUES (%s, %s, %s) RETURNING id""",
                (currency_symbol.upper(), price_usd, timestamp)
            )
            result = cur.fetchone()
            conn.commit()
            return PriceHistory(id=result[0], currency_symbol=currency_symbol.upper(),
                               price_usd=price_usd, timestamp=timestamp)
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_latest_prices() -> Dict[str, float]:
        """Get latest price for each currency."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """SELECT DISTINCT ON (currency_symbol) currency_symbol, price_usd 
                   FROM price_history 
                   ORDER BY currency_symbol, timestamp DESC"""
            )
            rows = cur.fetchall()
            return {row[0]: float(row[1]) for row in rows}
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_latest_price(currency_symbol: str) -> Optional[float]:
        """Get latest price for a specific currency."""
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """SELECT price_usd FROM price_history 
                   WHERE currency_symbol = %s 
                   ORDER BY timestamp DESC LIMIT 1""",
                (currency_symbol.upper(),)
            )
            row = cur.fetchone()
            return float(row[0]) if row else None
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def bulk_create(prices: Dict[str, float], timestamp: datetime = None) -> List['PriceHistory']:
        """Bulk create price records."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        conn = get_db_connection()
        cur = conn.cursor()
        created = []
        try:
            for symbol, price in prices.items():
                cur.execute(
                    """INSERT INTO price_history (currency_symbol, price_usd, timestamp) 
                       VALUES (%s, %s, %s) RETURNING id""",
                    (symbol.upper(), price, timestamp)
                )
                result = cur.fetchone()
                created.append(PriceHistory(
                    id=result[0], currency_symbol=symbol.upper(),
                    price_usd=price, timestamp=timestamp
                ))
            conn.commit()
            return created
        finally:
            cur.close()
            conn.close()

