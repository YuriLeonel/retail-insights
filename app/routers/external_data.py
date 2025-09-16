from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from decimal import Decimal
from app.database import get_async_db_dependency
from app.auth import get_current_user_async
from app.services.external_apis import external_data_service

router = APIRouter(prefix="/external", tags=["external-data"])


@router.get("/currency/rates")
async def get_currency_rates(
    base_currency: str = Query("USD", description="Base currency for exchange rates"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get current currency exchange rates.
    
    Returns exchange rates for various currencies based on the specified base currency.
    Data is cached for 1 hour to avoid excessive API calls.
    """
    try:
        rates = await external_data_service.get_currency_rates(base_currency)
        return {
            "base_currency": base_currency,
            "rates": {k: str(v) for k, v in rates.items()},  # Convert Decimal to string for JSON
            "timestamp": external_data_service.currency_service._last_update.isoformat() if external_data_service.currency_service._last_update else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching currency rates: {str(e)}")


@router.get("/currency/convert")
async def convert_currency(
    amount: float = Query(..., ge=0, description="Amount to convert"),
    from_currency: str = Query(..., description="Source currency code"),
    to_currency: str = Query(..., description="Target currency code"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Convert amount from one currency to another.
    
    Converts the specified amount from the source currency to the target currency
    using current exchange rates.
    """
    try:
        converted_amount = await external_data_service.convert_currency(
            Decimal(str(amount)), from_currency, to_currency
        )
        return {
            "original_amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "converted_amount": str(converted_amount),
            "exchange_rate": str(converted_amount / Decimal(str(amount)))
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting currency: {str(e)}")


@router.get("/currency/supported")
async def get_supported_currencies(
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get list of supported currencies.
    
    Returns a list of currency codes that are supported for exchange rate queries.
    """
    try:
        currencies = external_data_service.currency_service.get_supported_currencies()
        return {
            "supported_currencies": currencies,
            "count": len(currencies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching supported currencies: {str(e)}")


@router.get("/weather")
async def get_weather(
    city: str = Query(..., description="City name"),
    country_code: str = Query("", description="Country code (optional)"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get current weather data for a city.
    
    Returns current weather information including temperature, humidity, and conditions.
    Requires OPENWEATHER_API_KEY environment variable to be set.
    """
    try:
        weather_data = await external_data_service.get_weather_data(city, country_code)
        if weather_data is None:
            raise HTTPException(
                status_code=503, 
                detail="Weather service unavailable. Please check API key configuration."
            )
        return weather_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")


@router.get("/news")
async def get_business_news(
    country: str = Query("us", description="Country code for news"),
    limit: int = Query(10, ge=1, le=50, description="Number of news articles to return"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get business news headlines.
    
    Returns recent business news headlines for the specified country.
    Requires NEWS_API_KEY environment variable to be set.
    """
    try:
        news_data = await external_data_service.get_business_news(country, limit)
        return {
            "country": country,
            "articles": news_data,
            "count": len(news_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news data: {str(e)}")


@router.get("/all")
async def get_all_external_data(
    base_currency: str = Query("USD", description="Base currency for exchange rates"),
    weather_city: str = Query("London", description="City for weather data"),
    news_country: str = Query("us", description="Country for news data"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get all external data in one request.
    
    Returns currency rates, weather data, and news headlines in a single response.
    This endpoint is useful for dashboard applications that need multiple data sources.
    """
    try:
        all_data = await external_data_service.get_all_external_data(
            base_currency, weather_city, news_country
        )
        return all_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching external data: {str(e)}")


@router.get("/health")
async def external_data_health():
    """
    Health check endpoint for external data services.
    """
    return {
        "status": "healthy",
        "service": "external-data",
        "services": {
            "currency": "available",
            "weather": "available" if external_data_service.weather_service.api_key else "api_key_required",
            "news": "available" if external_data_service.news_service.api_key else "api_key_required"
        }
    }
