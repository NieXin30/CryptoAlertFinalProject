"""CoinGecko API service for fetching cryptocurrency prices."""
import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class CoinGeckoService:
    """Service for interacting with CoinGecko API."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Mapping from CoinGecko ID to symbol
    COIN_IDS = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'binancecoin': 'BNB',
        'ripple': 'XRP',
        'cardano': 'ADA',
        'solana': 'SOL',
        'dogecoin': 'DOGE'
    }
    
    def __init__(self):
        self.api_key = os.getenv('COINGECKO_API_KEY')
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        headers = {'Accept': 'application/json'}
        if self.api_key:
            headers['x-cg-demo-api-key'] = self.api_key
        return headers
    
    def get_prices(self) -> Dict[str, float]:
        """Fetch current prices for all supported cryptocurrencies.
        
        Returns:
            Dict mapping currency symbol (e.g., 'BTC') to USD price.
        """
        try:
            coin_ids = ','.join(self.COIN_IDS.keys())
            url = f"{self.BASE_URL}/simple/price"
            params = {
                'ids': coin_ids,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to symbol-based dict
            prices = {}
            for coin_id, symbol in self.COIN_IDS.items():
                if coin_id in data and 'usd' in data[coin_id]:
                    prices[symbol] = data[coin_id]['usd']
            
            return prices
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch prices from CoinGecko: {e}")
    
    def get_price(self, coin_id: str) -> Optional[float]:
        """Fetch current price for a specific cryptocurrency.
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin').
            
        Returns:
            USD price or None if not found.
        """
        try:
            url = f"{self.BASE_URL}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if coin_id in data and 'usd' in data[coin_id]:
                return data[coin_id]['usd']
            return None
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch price from CoinGecko: {e}")
    
    @classmethod
    def get_symbol_for_coin(cls, coin_id: str) -> Optional[str]:
        """Get symbol for a CoinGecko coin ID."""
        return cls.COIN_IDS.get(coin_id)
    
    @classmethod
    def get_coin_for_symbol(cls, symbol: str) -> Optional[str]:
        """Get CoinGecko coin ID for a symbol."""
        symbol = symbol.upper()
        for coin_id, sym in cls.COIN_IDS.items():
            if sym == symbol:
                return coin_id
        return None
    
    @classmethod
    def get_supported_currencies(cls) -> Dict[str, str]:
        """Get all supported currencies."""
        return cls.COIN_IDS.copy()

