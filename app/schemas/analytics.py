from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


class TopCustomer(BaseModel):
    customer_id: int
    customer_name: Optional[str]
    total_spent: Decimal
    total_orders: int
    avg_order_value: Decimal
    last_order_date: Optional[datetime]
    country: Optional[str]


class TopProduct(BaseModel):
    product_id: int
    stock_code: str
    description: Optional[str]
    total_quantity_sold: int
    total_revenue: Decimal
    avg_price: Decimal
    order_count: int


class SalesTrend(BaseModel):
    period: str  # e.g., "2024-01", "2024-Q1"
    total_revenue: Decimal
    total_orders: int
    total_customers: int
    avg_order_value: Decimal


class RevenueByCountry(BaseModel):
    country: str
    total_revenue: Decimal
    total_orders: int
    customer_count: int
    avg_order_value: Decimal


class CustomerSegment(BaseModel):
    segment: str
    customer_count: int
    total_revenue: Decimal
    avg_order_value: Decimal
    avg_orders_per_customer: Decimal
    description: str


class ChurnPrediction(BaseModel):
    customer_id: int
    customer_name: Optional[str]
    churn_probability: float
    risk_level: str  # "low", "medium", "high"
    last_order_days_ago: int
    total_orders: int
    total_spent: Decimal
    recommendations: List[str]


class CohortAnalysis(BaseModel):
    cohort_period: str
    cohort_size: int
    retention_rates: Dict[str, float]  # period -> retention rate


class KPI(BaseModel):
    metric_name: str
    value: Decimal
    period: str
    change_from_previous: Optional[Decimal]
    change_percentage: Optional[float]


class AnalyticsResponse(BaseModel):
    top_customers: List[TopCustomer]
    top_products: List[TopProduct]
    sales_trends: List[SalesTrend]
    revenue_by_country: List[RevenueByCountry]
    customer_segments: List[CustomerSegment]
    kpis: List[KPI]
    generated_at: datetime


class MLModelInfo(BaseModel):
    model_name: str
    model_version: str
    accuracy: float
    last_trained: datetime
    features_used: List[str]
    status: str  # "active", "training", "error"


class PredictionRequest(BaseModel):
    customer_id: int
    features: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    customer_id: int
    prediction: Any
    confidence: float
    model_info: MLModelInfo
    generated_at: datetime
