from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_async_db_dependency
from app.auth import get_current_user_async
from app.crud.analytics import (
    get_top_customers_async,
    get_top_products_async,
    get_sales_trends_async,
    get_revenue_by_country_async,
    get_customer_segments_async,
    get_kpis_async
)
from app.schemas.analytics import (
    TopCustomer, TopProduct, SalesTrend, RevenueByCountry,
    CustomerSegment, KPI, AnalyticsResponse
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/top-customers", response_model=List[TopCustomer])
async def get_top_customers(
    limit: int = Query(10, ge=1, le=100, description="Number of top customers to return"),
    country: Optional[str] = Query(None, description="Filter by country"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get top customers by total spending with optional filters.
    
    Returns customers ranked by total revenue with additional metrics like
    order count, average order value, and last order date.
    """
    try:
        customers = await get_top_customers_async(
            db=db,
            limit=limit,
            country=country,
            start_date=start_date,
            end_date=end_date
        )
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving top customers: {str(e)}")


@router.get("/top-products", response_model=List[TopProduct])
async def get_top_products(
    limit: int = Query(10, ge=1, le=100, description="Number of top products to return"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get top products by revenue and quantity sold.
    
    Returns products ranked by total revenue with metrics like
    quantity sold, average price, and order count.
    """
    try:
        products = await get_top_products_async(
            db=db,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving top products: {str(e)}")


@router.get("/sales-trends", response_model=List[SalesTrend])
async def get_sales_trends(
    period: str = Query("month", regex="^(month|quarter|year)$", description="Time period for aggregation"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get sales trends over time.
    
    Returns revenue, order count, customer count, and average order value
    aggregated by the specified time period (month, quarter, or year).
    """
    try:
        trends = await get_sales_trends_async(
            db=db,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sales trends: {str(e)}")


@router.get("/revenue-by-country", response_model=List[RevenueByCountry])
async def get_revenue_by_country(
    limit: int = Query(20, ge=1, le=100, description="Number of countries to return"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get revenue breakdown by country.
    
    Returns countries ranked by total revenue with metrics like
    order count, customer count, and average order value.
    """
    try:
        countries = await get_revenue_by_country_async(
            db=db,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        return countries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving revenue by country: {str(e)}")


@router.get("/customer-segments", response_model=List[CustomerSegment])
async def get_customer_segments(
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get customer segments based on RFM analysis.
    
    Returns customer segments (Champions, Loyal Customers, At Risk, etc.)
    with metrics like customer count, total revenue, and average order value.
    """
    try:
        segments = await get_customer_segments_async(db=db)
        return segments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving customer segments: {str(e)}")


@router.get("/kpis", response_model=List[KPI])
async def get_kpis(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get key performance indicators.
    
    Returns KPIs like total revenue, order count, and average order value
    with period-over-period comparisons.
    """
    try:
        kpis = await get_kpis_async(db=db, start_date=start_date, end_date=end_date)
        return kpis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving KPIs: {str(e)}")


@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_analytics_dashboard(
    limit: int = Query(10, ge=1, le=50, description="Number of items to return for top lists"),
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get comprehensive analytics dashboard data.
    
    Returns a complete analytics overview including top customers, products,
    sales trends, revenue by country, customer segments, and KPIs.
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Fetch all analytics data in parallel
        import asyncio
        
        top_customers, top_products, sales_trends, revenue_by_country, customer_segments, kpis = await asyncio.gather(
            get_top_customers_async(db, limit, None, start_date, end_date),
            get_top_products_async(db, limit, start_date, end_date),
            get_sales_trends_async(db, "month", start_date, end_date),
            get_revenue_by_country_async(db, limit, start_date, end_date),
            get_customer_segments_async(db),
            get_kpis_async(db, start_date, end_date)
        )
        
        return AnalyticsResponse(
            top_customers=top_customers,
            top_products=top_products,
            sales_trends=sales_trends,
            revenue_by_country=revenue_by_country,
            customer_segments=customer_segments,
            kpis=kpis,
            generated_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics dashboard: {str(e)}")


@router.get("/health")
async def analytics_health():
    """
    Health check endpoint for analytics service.
    """
    return {
        "status": "healthy",
        "service": "analytics",
        "timestamp": datetime.now().isoformat()
    }
