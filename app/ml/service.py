import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.models import Customer, Order, OrderItem
from app.ml.models import MLModelManager, CustomerSegmentationModel, ChurnPredictionModel

logger = logging.getLogger(__name__)


class MLService:
    """Service for machine learning operations"""
    
    def __init__(self):
        self.model_manager = MLModelManager()
    
    async def prepare_customer_data(self, db: AsyncSession) -> pd.DataFrame:
        """Prepare customer data for ML models"""
        try:
            # Query to get customer data with order statistics
            query = (
                select(
                    Customer.customer_id,
                    Customer.customer_name,
                    Customer.country,
                    func.count(func.distinct(Order.order_id)).label('total_orders'),
                    func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_spent'),
                    func.min(Order.invoice_date).label('first_order_date'),
                    func.max(Order.invoice_date).label('last_order_date')
                )
                .select_from(
                    Customer.__table__
                    .join(Order.__table__, Customer.customer_id == Order.customer_id)
                    .join(OrderItem.__table__, Order.order_id == OrderItem.order_id)
                )
                .group_by(Customer.customer_id, Customer.customer_name, Customer.country)
            )
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            # Convert to DataFrame
            data = []
            for row in rows:
                data.append({
                    'customer_id': row.customer_id,
                    'customer_name': row.customer_name,
                    'country': row.country,
                    'total_orders': row.total_orders or 0,
                    'total_spent': float(row.total_spent or 0),
                    'first_order_date': row.first_order_date,
                    'last_order_date': row.last_order_date
                })
            
            df = pd.DataFrame(data)
            
            # Convert date columns
            df['first_order_date'] = pd.to_datetime(df['first_order_date'])
            df['last_order_date'] = pd.to_datetime(df['last_order_date'])
            
            # Filter out customers with no orders
            df = df[df['total_orders'] > 0]
            
            logger.info(f"Prepared data for {len(df)} customers")
            return df
            
        except Exception as e:
            logger.error(f"Error preparing customer data: {e}")
            raise
    
    async def train_segmentation_model(self, db: AsyncSession) -> Dict[str, Any]:
        """Train customer segmentation model"""
        try:
            # Prepare data
            df = await self.prepare_customer_data(db)
            
            if len(df) < 10:
                return {
                    "status": "error",
                    "error": "Insufficient data for training. Need at least 10 customers."
                }
            
            # Train model
            result = self.model_manager.segmentation_model.train(df)
            
            if result["status"] == "success":
                # Save model
                self.model_manager.save_all_models()
                
                # Get segment characteristics
                characteristics = self.model_manager.segmentation_model.get_segment_characteristics(df)
                result["segment_characteristics"] = characteristics
            
            return result
            
        except Exception as e:
            logger.error(f"Error training segmentation model: {e}")
            return {"status": "error", "error": str(e)}
    
    async def train_churn_model(self, db: AsyncSession) -> Dict[str, Any]:
        """Train customer churn prediction model"""
        try:
            # Prepare data
            df = await self.prepare_customer_data(db)
            
            if len(df) < 20:
                return {
                    "status": "error",
                    "error": "Insufficient data for training. Need at least 20 customers."
                }
            
            # Train model
            result = self.model_manager.churn_model.train(df)
            
            if result["status"] == "success":
                # Save model
                self.model_manager.save_all_models()
            
            return result
            
        except Exception as e:
            logger.error(f"Error training churn model: {e}")
            return {"status": "error", "error": str(e)}
    
    async def predict_customer_segments(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Predict customer segments for all customers"""
        try:
            if not self.model_manager.segmentation_model.is_trained:
                return []
            
            # Prepare data
            df = await self.prepare_customer_data(db)
            
            # Predict segments
            predictions_df = self.model_manager.segmentation_model.predict_segment(df)
            
            # Convert to list of dictionaries
            results = []
            for _, row in predictions_df.iterrows():
                results.append({
                    "customer_id": int(row['customer_id']),
                    "customer_name": row.get('customer_name'),
                    "country": row.get('country'),
                    "segment": int(row['segment']),
                    "segment_name": row['segment_name'],
                    "recency": int(row['recency']),
                    "frequency": int(row['frequency']),
                    "monetary": float(row['monetary'])
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error predicting customer segments: {e}")
            return []
    
    async def predict_churn_risk(self, db: AsyncSession, customer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Predict churn risk for customers"""
        try:
            if not self.model_manager.churn_model.is_trained:
                return []
            
            # Prepare data
            df = await self.prepare_customer_data(db)
            
            # Filter for specific customer if requested
            if customer_id:
                df = df[df['customer_id'] == customer_id]
                if len(df) == 0:
                    return []
            
            # Predict churn
            predictions_df = self.model_manager.churn_model.predict_churn_probability(df)
            
            # Convert to list of dictionaries
            results = []
            for _, row in predictions_df.iterrows():
                # Get recommendations
                customer_data = {
                    'days_since_last_order': row['days_since_last_order'],
                    'total_orders': row['total_orders'],
                    'avg_order_value': row['avg_order_value']
                }
                recommendations = self.model_manager.churn_model.get_customer_recommendations(customer_data)
                
                results.append({
                    "customer_id": int(row['customer_id']),
                    "customer_name": row.get('customer_name'),
                    "country": row.get('country'),
                    "churn_probability": float(row['churn_probability']),
                    "risk_level": str(row['risk_level']),
                    "days_since_last_order": int(row['days_since_last_order']),
                    "total_orders": int(row['total_orders']),
                    "total_spent": float(row['total_spent']),
                    "recommendations": recommendations
                })
            
            # Sort by churn probability (highest first)
            results.sort(key=lambda x: x['churn_probability'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error predicting churn risk: {e}")
            return []
    
    async def get_model_insights(self, db: AsyncSession) -> Dict[str, Any]:
        """Get insights from trained models"""
        try:
            insights = {
                "model_status": self.model_manager.get_model_status(),
                "customer_data_summary": {},
                "segmentation_insights": {},
                "churn_insights": {}
            }
            
            # Get customer data summary
            df = await self.prepare_customer_data(db)
            insights["customer_data_summary"] = {
                "total_customers": len(df),
                "avg_orders_per_customer": df['total_orders'].mean(),
                "avg_spent_per_customer": df['total_spent'].mean(),
                "total_revenue": df['total_spent'].sum()
            }
            
            # Get segmentation insights
            if self.model_manager.segmentation_model.is_trained:
                segment_predictions = await self.predict_customer_segments(db)
                segment_counts = {}
                for pred in segment_predictions:
                    segment_name = pred['segment_name']
                    segment_counts[segment_name] = segment_counts.get(segment_name, 0) + 1
                
                insights["segmentation_insights"] = {
                    "total_segments": len(segment_counts),
                    "segment_distribution": segment_counts
                }
            
            # Get churn insights
            if self.model_manager.churn_model.is_trained:
                churn_predictions = await self.predict_churn_risk(db)
                high_risk_customers = [p for p in churn_predictions if p['risk_level'] == 'high']
                medium_risk_customers = [p for p in churn_predictions if p['risk_level'] == 'medium']
                
                insights["churn_insights"] = {
                    "total_customers_analyzed": len(churn_predictions),
                    "high_risk_customers": len(high_risk_customers),
                    "medium_risk_customers": len(medium_risk_customers),
                    "avg_churn_probability": np.mean([p['churn_probability'] for p in churn_predictions]) if churn_predictions else 0
                }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting model insights: {e}")
            return {"error": str(e)}
    
    async def retrain_models(self, db: AsyncSession) -> Dict[str, Any]:
        """Retrain all models with fresh data"""
        try:
            results = {
                "segmentation_training": {},
                "churn_training": {},
                "status": "success"
            }
            
            # Train segmentation model
            seg_result = await self.train_segmentation_model(db)
            results["segmentation_training"] = seg_result
            
            # Train churn model
            churn_result = await self.train_churn_model(db)
            results["churn_training"] = churn_result
            
            # Check if both models trained successfully
            if (seg_result.get("status") != "success" or 
                churn_result.get("status") != "success"):
                results["status"] = "partial_success"
            
            return results
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
            return {"status": "error", "error": str(e)}


# Global instance
ml_service = MLService()
