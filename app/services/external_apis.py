import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import json
import os
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class CurrencyExchangeService:
    """Service for fetching and caching currency exchange rates"""
    
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4"
        self.cache_duration = timedelta(hours=1)
        self._cache = {}
        self._last_update = None
    
    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, Decimal]:
        """
        Get current exchange rates for a base currency.
        Uses caching to avoid excessive API calls.
        """
        cache_key = f"rates_{base_currency}"
        now = datetime.now()
        
        # Check if cache is still valid
        if (cache_key in self._cache and 
            self._last_update and 
            now - self._last_update < self.cache_duration):
            return self._cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/latest/{base_currency}")
                response.raise_for_status()
                data = response.json()
                
                # Convert rates to Decimal for precision
                rates = {
                    currency: Decimal(str(rate))
                    for currency, rate in data.get("rates", {}).items()
                }
                
                # Cache the results
                self._cache[cache_key] = rates
                self._last_update = now
                
                logger.info(f"Updated exchange rates for {base_currency}")
                return rates
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch exchange rates: {e}")
            # Return cached data if available, otherwise return empty dict
            return self._cache.get(cache_key, {})
        except Exception as e:
            logger.error(f"Unexpected error fetching exchange rates: {e}")
            return self._cache.get(cache_key, {})
    
    async def convert_currency(
        self, 
        amount: Decimal, 
        from_currency: str, 
        to_currency: str
    ) -> Decimal:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        rates = await self.get_exchange_rates(from_currency)
        if to_currency not in rates:
            raise ValueError(f"Currency {to_currency} not found in exchange rates")
        
        return amount * rates[to_currency]
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return [
            "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD",
            "MXN", "SGD", "HKD", "NOK", "TRY", "RUB", "INR", "BRL", "ZAR", "KRW"
        ]


class WeatherService:
    """Service for fetching weather data (example external API)"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather_by_city(self, city: str, country_code: str = "") -> Optional[Dict[str, Any]]:
        """Get current weather for a city"""
        if not self.api_key:
            logger.warning("OpenWeather API key not configured")
            return None
        
        try:
            location = f"{city},{country_code}" if country_code else city
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": location,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            return None


class NewsService:
    """Service for fetching news data (example external API)"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    async def get_business_news(self, country: str = "us", limit: int = 10) -> List[Dict[str, Any]]:
        """Get business news for a specific country"""
        if not self.api_key:
            logger.warning("News API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/top-headlines",
                    params={
                        "country": country,
                        "category": "business",
                        "pageSize": limit,
                        "apiKey": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("articles", [])
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch news data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {e}")
            return []


class ExternalDataService:
    """Main service for managing all external data integrations"""
    
    def __init__(self):
        self.currency_service = CurrencyExchangeService()
        self.weather_service = WeatherService()
        self.news_service = NewsService()
    
    async def get_currency_rates(self, base_currency: str = "USD") -> Dict[str, Decimal]:
        """Get currency exchange rates"""
        return await self.currency_service.get_exchange_rates(base_currency)
    
    async def convert_currency(
        self, 
        amount: Decimal, 
        from_currency: str, 
        to_currency: str
    ) -> Decimal:
        """Convert currency"""
        return await self.currency_service.convert_currency(amount, from_currency, to_currency)
    
    async def get_weather_data(self, city: str, country_code: str = "") -> Optional[Dict[str, Any]]:
        """Get weather data"""
        return await self.weather_service.get_weather_by_city(city, country_code)
    
    async def get_business_news(self, country: str = "us", limit: int = 10) -> List[Dict[str, Any]]:
        """Get business news"""
        return await self.news_service.get_business_news(country, limit)
    
    async def get_all_external_data(
        self, 
        base_currency: str = "USD",
        weather_city: str = "London",
        news_country: str = "us"
    ) -> Dict[str, Any]:
        """Get all external data in one call"""
        try:
            # Fetch all external data in parallel
            currency_rates, weather_data, news_data = await asyncio.gather(
                self.get_currency_rates(base_currency),
                self.get_weather_data(weather_city),
                self.get_business_news(news_country, 5),
                return_exceptions=True
            )
            
            return {
                "currency_rates": currency_rates if not isinstance(currency_rates, Exception) else {},
                "weather": weather_data if not isinstance(weather_data, Exception) else None,
                "news": news_data if not isinstance(news_data, Exception) else [],
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error fetching external data: {e}")
            return {
                "currency_rates": {},
                "weather": None,
                "news": [],
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }


# Global instance
external_data_service = ExternalDataService()
