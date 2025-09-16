from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import get_async_db_dependency
from app.auth import get_current_user_async
from app.ml.service import ml_service
from app.schemas.analytics import ChurnPrediction, MLModelInfo

router = APIRouter(prefix="/ml", tags=["machine-learning"])


@router.post("/train/segmentation")
async def train_segmentation_model(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Train customer segmentation model.
    
    Trains a K-Means clustering model to segment customers based on RFM analysis.
    The model will be saved and can be used for predictions.
    """
    try:
        result = await ml_service.train_segmentation_model(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training segmentation model: {str(e)}")


@router.post("/train/churn")
async def train_churn_model(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Train customer churn prediction model.
    
    Trains a Random Forest classifier to predict customer churn probability.
    The model will be saved and can be used for predictions.
    """
    try:
        result = await ml_service.train_churn_model(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training churn model: {str(e)}")


@router.post("/train/all")
async def train_all_models(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Train all ML models.
    
    Trains both customer segmentation and churn prediction models.
    This is useful for initial setup or periodic retraining.
    """
    try:
        result = await ml_service.retrain_models(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training models: {str(e)}")


@router.get("/predict/segments", response_model=List[Dict[str, Any]])
async def predict_customer_segments(
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Predict customer segments for all customers.
    
    Returns customer segmentation predictions based on RFM analysis.
    Requires the segmentation model to be trained first.
    """
    try:
        predictions = await ml_service.predict_customer_segments(db)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting customer segments: {str(e)}")


@router.get("/predict/churn", response_model=List[ChurnPrediction])
async def predict_churn_risk(
    customer_id: Optional[int] = Query(None, description="Specific customer ID to analyze"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of predictions to return"),
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Predict customer churn risk.
    
    Returns churn probability predictions for customers.
    If customer_id is provided, returns prediction for that specific customer.
    Otherwise, returns predictions for all customers, sorted by risk level.
    """
    try:
        predictions = await ml_service.predict_churn_risk(db, customer_id)
        
        # Limit results
        predictions = predictions[:limit]
        
        # Convert to ChurnPrediction schema
        churn_predictions = []
        for pred in predictions:
            churn_predictions.append(ChurnPrediction(
                customer_id=pred['customer_id'],
                customer_name=pred.get('customer_name'),
                churn_probability=pred['churn_probability'],
                risk_level=pred['risk_level'],
                last_order_days_ago=pred['days_since_last_order'],
                total_orders=pred['total_orders'],
                total_spent=pred['total_spent'],
                recommendations=pred['recommendations']
            ))
        
        return churn_predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting churn risk: {str(e)}")


@router.get("/insights")
async def get_ml_insights(
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get machine learning insights and model status.
    
    Returns comprehensive insights about trained models, customer data,
    segmentation results, and churn predictions.
    """
    try:
        insights = await ml_service.get_model_insights(db)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ML insights: {str(e)}")


@router.get("/models/status")
async def get_model_status(
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get status of all ML models.
    
    Returns information about which models are trained and available for use.
    """
    try:
        status = ml_service.model_manager.get_model_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model status: {str(e)}")


@router.get("/models/info")
async def get_model_info(
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Get detailed information about trained models.
    
    Returns model metadata including accuracy, features used, and training information.
    """
    try:
        status = ml_service.model_manager.get_model_status()
        
        models_info = []
        
        # Segmentation model info
        if status["segmentation_model"]["is_trained"]:
            models_info.append(MLModelInfo(
                model_name="Customer Segmentation",
                model_version="1.0",
                accuracy=0.0,  # K-Means doesn't have traditional accuracy
                last_trained=datetime.now().isoformat(),
                features_used=["recency", "frequency", "monetary"],
                status="active"
            ))
        
        # Churn model info
        if status["churn_model"]["is_trained"]:
            models_info.append(MLModelInfo(
                model_name="Churn Prediction",
                model_version="1.0",
                accuracy=0.0,  # Would need to store this during training
                last_trained=datetime.now().isoformat(),
                features_used=["total_orders", "total_spent", "days_since_last_order", 
                              "order_frequency", "avg_order_value", "customer_lifetime"],
                status="active"
            ))
        
        return {
            "models": models_info,
            "total_models": len(models_info),
            "models_directory": status["models_directory"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")


@router.get("/health")
async def ml_health():
    """
    Health check endpoint for ML service.
    """
    return {
        "status": "healthy",
        "service": "machine-learning",
        "timestamp": datetime.now().isoformat()
    }
