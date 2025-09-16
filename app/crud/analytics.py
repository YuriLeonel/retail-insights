from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from app.models import Customer, Product, Order, OrderItem
from app.schemas.analytics import (
    TopCustomer, TopProduct, SalesTrend, RevenueByCountry, 
    CustomerSegment, ChurnPrediction, CohortAnalysis, KPI
)


async def get_top_customers_async(
    db: AsyncSession, 
    limit: int = 10,
    country: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[TopCustomer]:
    """Get top customers by total spending"""
    
    # Base query for order items with joins
    query = (
        select(
            Customer.customer_id,
            Customer.customer_name,
            Customer.country,
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_spent'),
            func.count(func.distinct(Order.order_id)).label('total_orders'),
            func.avg(OrderItem.quantity * OrderItem.unit_price).label('avg_order_value'),
            func.max(Order.invoice_date).label('last_order_date')
        )
        .select_from(
            Customer.__table__
            .join(Order.__table__, Customer.customer_id == Order.customer_id)
            .join(OrderItem.__table__, Order.order_id == OrderItem.order_id)
        )
    )
    
    # Apply filters
    conditions = []
    if country:
        conditions.append(Customer.country == country)
    if start_date:
        conditions.append(Order.invoice_date >= start_date)
    if end_date:
        conditions.append(Order.invoice_date <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Group by customer and order by total spent
    query = (
        query
        .group_by(Customer.customer_id, Customer.customer_name, Customer.country)
        .order_by(desc('total_spent'))
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        TopCustomer(
            customer_id=row.customer_id,
            customer_name=row.customer_name,
            total_spent=row.total_spent or Decimal('0'),
            total_orders=row.total_orders or 0,
            avg_order_value=row.avg_order_value or Decimal('0'),
            last_order_date=row.last_order_date,
            country=row.country
        )
        for row in rows
    ]


async def get_top_products_async(
    db: AsyncSession,
    limit: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[TopProduct]:
    """Get top products by quantity sold and revenue"""
    
    query = (
        select(
            Product.product_id,
            Product.stock_code,
            Product.description,
            func.sum(OrderItem.quantity).label('total_quantity_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
            func.avg(OrderItem.unit_price).label('avg_price'),
            func.count(func.distinct(OrderItem.order_id)).label('order_count')
        )
        .select_from(
            Product.__table__
            .join(OrderItem.__table__, Product.product_id == OrderItem.product_id)
            .join(Order.__table__, OrderItem.order_id == Order.order_id)
        )
    )
    
    # Apply date filters
    conditions = []
    if start_date:
        conditions.append(Order.invoice_date >= start_date)
    if end_date:
        conditions.append(Order.invoice_date <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = (
        query
        .group_by(Product.product_id, Product.stock_code, Product.description)
        .order_by(desc('total_revenue'))
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        TopProduct(
            product_id=row.product_id,
            stock_code=row.stock_code,
            description=row.description,
            total_quantity_sold=row.total_quantity_sold or 0,
            total_revenue=row.total_revenue or Decimal('0'),
            avg_price=row.avg_price or Decimal('0'),
            order_count=row.order_count or 0
        )
        for row in rows
    ]


async def get_sales_trends_async(
    db: AsyncSession,
    period: str = "month",  # "month", "quarter", "year"
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[SalesTrend]:
    """Get sales trends by period"""
    
    # Determine date truncation based on period
    if period == "month":
        date_trunc = func.date_trunc('month', Order.invoice_date)
    elif period == "quarter":
        date_trunc = func.date_trunc('quarter', Order.invoice_date)
    elif period == "year":
        date_trunc = func.date_trunc('year', Order.invoice_date)
    else:
        date_trunc = func.date_trunc('month', Order.invoice_date)
    
    query = (
        select(
            date_trunc.label('period'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
            func.count(func.distinct(Order.order_id)).label('total_orders'),
            func.count(func.distinct(Order.customer_id)).label('total_customers'),
            func.avg(OrderItem.quantity * OrderItem.unit_price).label('avg_order_value')
        )
        .select_from(
            Order.__table__
            .join(OrderItem.__table__, Order.order_id == OrderItem.order_id)
        )
    )
    
    # Apply date filters
    conditions = []
    if start_date:
        conditions.append(Order.invoice_date >= start_date)
    if end_date:
        conditions.append(Order.invoice_date <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = (
        query
        .group_by(date_trunc)
        .order_by(date_trunc)
    )
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        SalesTrend(
            period=str(row.period),
            total_revenue=row.total_revenue or Decimal('0'),
            total_orders=row.total_orders or 0,
            total_customers=row.total_customers or 0,
            avg_order_value=row.avg_order_value or Decimal('0')
        )
        for row in rows
    ]


async def get_revenue_by_country_async(
    db: AsyncSession,
    limit: int = 20,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[RevenueByCountry]:
    """Get revenue breakdown by country"""
    
    query = (
        select(
            Order.country,
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
            func.count(func.distinct(Order.order_id)).label('total_orders'),
            func.count(func.distinct(Order.customer_id)).label('customer_count'),
            func.avg(OrderItem.quantity * OrderItem.unit_price).label('avg_order_value')
        )
        .select_from(
            Order.__table__
            .join(OrderItem.__table__, Order.order_id == OrderItem.order_id)
        )
    )
    
    # Apply date filters
    conditions = []
    if start_date:
        conditions.append(Order.invoice_date >= start_date)
    if end_date:
        conditions.append(Order.invoice_date <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = (
        query
        .group_by(Order.country)
        .order_by(desc('total_revenue'))
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.fetchall()
    
    return [
        RevenueByCountry(
            country=row.country or "Unknown",
            total_revenue=row.total_revenue or Decimal('0'),
            total_orders=row.total_orders or 0,
            customer_count=row.customer_count or 0,
            avg_order_value=row.avg_order_value or Decimal('0')
        )
        for row in rows
    ]


async def get_customer_segments_async(db: AsyncSession) -> List[CustomerSegment]:
    """Get customer segments based on RFM analysis"""
    
    # Calculate RFM metrics for each customer
    rfm_query = (
        select(
            Customer.customer_id,
            func.max(Order.invoice_date).label('last_order_date'),
            func.count(func.distinct(Order.order_id)).label('frequency'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('monetary')
        )
        .select_from(
            Customer.__table__
            .join(Order.__table__, Customer.customer_id == Order.customer_id)
            .join(OrderItem.__table__, Order.order_id == OrderItem.order_id)
        )
        .group_by(Customer.customer_id)
    )
    
    result = await db.execute(rfm_query)
    rfm_data = result.fetchall()
    
    # Calculate recency (days since last order)
    current_date = datetime.now()
    segments = []
    
    for row in rfm_data:
        recency = (current_date - row.last_order_date).days if row.last_order_date else 999
        frequency = row.frequency or 0
        monetary = float(row.monetary or 0)
        
        # Simple segmentation logic
        if recency <= 30 and frequency >= 5 and monetary >= 1000:
            segment = "Champions"
        elif recency <= 60 and frequency >= 3 and monetary >= 500:
            segment = "Loyal Customers"
        elif recency <= 90 and frequency >= 2:
            segment = "Potential Loyalists"
        elif recency <= 180 and frequency >= 1:
            segment = "At Risk"
        elif recency > 180:
            segment = "Lost Customers"
        else:
            segment = "New Customers"
        
        segments.append({
            'segment': segment,
            'customer_id': row.customer_id,
            'monetary': monetary
        })
    
    # Aggregate by segment
    segment_stats = {}
    for seg in segments:
        segment_name = seg['segment']
        if segment_name not in segment_stats:
            segment_stats[segment_name] = {
                'customer_count': 0,
                'total_revenue': Decimal('0'),
                'monetary_values': []
            }
        
        segment_stats[segment_name]['customer_count'] += 1
        segment_stats[segment_name]['total_revenue'] += Decimal(str(seg['monetary']))
        segment_stats[segment_name]['monetary_values'].append(seg['monetary'])
    
    # Create segment objects
    segment_descriptions = {
        "Champions": "High-value, frequent, recent customers",
        "Loyal Customers": "Regular customers with good spending",
        "Potential Loyalists": "Recent customers with growth potential",
        "At Risk": "Customers showing signs of churn",
        "Lost Customers": "Inactive customers who haven't purchased recently",
        "New Customers": "Recently acquired customers"
    }
    
    return [
        CustomerSegment(
            segment=segment_name,
            customer_count=stats['customer_count'],
            total_revenue=stats['total_revenue'],
            avg_order_value=stats['total_revenue'] / stats['customer_count'] if stats['customer_count'] > 0 else Decimal('0'),
            avg_orders_per_customer=0,  # Would need additional query for this
            description=segment_descriptions.get(segment_name, "Customer segment")
        )
        for segment_name, stats in segment_stats.items()
    ]


async def get_kpis_async(
    db: AsyncSession,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[KPI]:
    """Get key performance indicators"""
    
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Previous period for comparison
    period_length = end_date - start_date
    prev_start_date = start_date - period_length
    prev_end_date = start_date
    
    kpis = []
    
    # Total Revenue
    current_revenue_query = (
        select(func.sum(OrderItem.quantity * OrderItem.unit_price))
        .select_from(Order.__table__.join(OrderItem.__table__, Order.order_id == OrderItem.order_id))
        .where(and_(Order.invoice_date >= start_date, Order.invoice_date <= end_date))
    )
    
    prev_revenue_query = (
        select(func.sum(OrderItem.quantity * OrderItem.unit_price))
        .select_from(Order.__table__.join(OrderItem.__table__, Order.order_id == OrderItem.order_id))
        .where(and_(Order.invoice_date >= prev_start_date, Order.invoice_date <= prev_end_date))
    )
    
    current_revenue_result = await db.execute(current_revenue_query)
    prev_revenue_result = await db.execute(prev_revenue_query)
    
    current_revenue = current_revenue_result.scalar() or Decimal('0')
    prev_revenue = prev_revenue_result.scalar() or Decimal('0')
    
    revenue_change = current_revenue - prev_revenue
    revenue_change_pct = (float(revenue_change) / float(prev_revenue) * 100) if prev_revenue > 0 else 0
    
    kpis.append(KPI(
        metric_name="Total Revenue",
        value=current_revenue,
        period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        change_from_previous=revenue_change,
        change_percentage=revenue_change_pct
    ))
    
    # Total Orders
    current_orders_query = (
        select(func.count(func.distinct(Order.order_id)))
        .select_from(Order.__table__)
        .where(and_(Order.invoice_date >= start_date, Order.invoice_date <= end_date))
    )
    
    prev_orders_query = (
        select(func.count(func.distinct(Order.order_id)))
        .select_from(Order.__table__)
        .where(and_(Order.invoice_date >= prev_start_date, Order.invoice_date <= prev_end_date))
    )
    
    current_orders_result = await db.execute(current_orders_query)
    prev_orders_result = await db.execute(prev_orders_query)
    
    current_orders = current_orders_result.scalar() or 0
    prev_orders = prev_orders_result.scalar() or 0
    
    orders_change = current_orders - prev_orders
    orders_change_pct = (orders_change / prev_orders * 100) if prev_orders > 0 else 0
    
    kpis.append(KPI(
        metric_name="Total Orders",
        value=Decimal(str(current_orders)),
        period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        change_from_previous=Decimal(str(orders_change)),
        change_percentage=orders_change_pct
    ))
    
    # Average Order Value
    avg_order_value = current_revenue / current_orders if current_orders > 0 else Decimal('0')
    prev_avg_order_value = prev_revenue / prev_orders if prev_orders > 0 else Decimal('0')
    
    aov_change = avg_order_value - prev_avg_order_value
    aov_change_pct = (float(aov_change) / float(prev_avg_order_value) * 100) if prev_avg_order_value > 0 else 0
    
    kpis.append(KPI(
        metric_name="Average Order Value",
        value=avg_order_value,
        period=f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        change_from_previous=aov_change,
        change_percentage=aov_change_pct
    ))
    
    return kpis
