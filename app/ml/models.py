import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, silhouette_score
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime, timedelta
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class CustomerSegmentationModel:
    """Customer segmentation using RFM analysis and K-Means clustering"""
    
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.segment_names = {
            0: "Champions",
            1: "Loyal Customers", 
            2: "Potential Loyalists",
            3: "At Risk",
            4: "Lost Customers"
        }
    
    def calculate_rfm_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RFM (Recency, Frequency, Monetary) features"""
        # Calculate recency (days since last order)
        df['recency'] = (datetime.now() - pd.to_datetime(df['last_order_date'])).dt.days
        
        # Calculate frequency (number of orders)
        df['frequency'] = df['total_orders']
        
        # Calculate monetary value (total spent)
        df['monetary'] = df['total_spent']
        
        # Log transform monetary to handle skewness
        df['monetary_log'] = np.log1p(df['monetary'])
        
        return df[['customer_id', 'recency', 'frequency', 'monetary', 'monetary_log']]
    
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train the segmentation model"""
        try:
            # Calculate RFM features
            rfm_df = self.calculate_rfm_features(df)
            
            # Prepare features for clustering
            features = ['recency', 'frequency', 'monetary_log']
            X = rfm_df[features].values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train K-Means
            self.kmeans.fit(X_scaled)
            
            # Calculate silhouette score
            silhouette_avg = silhouette_score(X_scaled, self.kmeans.labels_)
            
            self.is_trained = True
            
            return {
                "status": "success",
                "n_clusters": self.n_clusters,
                "silhouette_score": silhouette_avg,
                "n_samples": len(X),
                "features": features
            }
            
        except Exception as e:
            logger.error(f"Error training segmentation model: {e}")
            return {"status": "error", "error": str(e)}
    
    def predict_segment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict customer segments"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        rfm_df = self.calculate_rfm_features(df)
        features = ['recency', 'frequency', 'monetary_log']
        X = rfm_df[features].values
        X_scaled = self.scaler.transform(X)
        
        segments = self.kmeans.predict(X_scaled)
        rfm_df['segment'] = segments
        rfm_df['segment_name'] = rfm_df['segment'].map(self.segment_names)
        
        return rfm_df
    
    def get_segment_characteristics(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Get characteristics of each segment"""
        if not self.is_trained:
            raise ValueError("Model must be trained before getting characteristics")
        
        rfm_df = self.predict_segment(df)
        
        characteristics = {}
        for segment_id, segment_name in self.segment_names.items():
            segment_data = rfm_df[rfm_df['segment'] == segment_id]
            if len(segment_data) > 0:
                characteristics[segment_name] = {
                    "count": len(segment_data),
                    "avg_recency": segment_data['recency'].mean(),
                    "avg_frequency": segment_data['frequency'].mean(),
                    "avg_monetary": segment_data['monetary'].mean(),
                    "percentage": len(segment_data) / len(rfm_df) * 100
                }
        
        return characteristics
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        model_data = {
            'kmeans': self.kmeans,
            'scaler': self.scaler,
            'n_clusters': self.n_clusters,
            'segment_names': self.segment_names,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        self.kmeans = model_data['kmeans']
        self.scaler = model_data['scaler']
        self.n_clusters = model_data['n_clusters']
        self.segment_names = model_data['segment_names']
        self.is_trained = model_data['is_trained']
        logger.info(f"Model loaded from {filepath}")


class ChurnPredictionModel:
    """Customer churn prediction using Random Forest"""
    
    def __init__(self):
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.feature_importance = {}
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for churn prediction"""
        # Calculate days since last order
        df['days_since_last_order'] = (datetime.now() - pd.to_datetime(df['last_order_date'])).dt.days
        
        # Calculate order frequency (orders per month)
        df['order_frequency'] = df['total_orders'] / max(1, (datetime.now() - pd.to_datetime(df['first_order_date'])).dt.days / 30)
        
        # Calculate average order value
        df['avg_order_value'] = df['total_spent'] / df['total_orders']
        
        # Calculate customer lifetime (days)
        df['customer_lifetime'] = (pd.to_datetime(df['last_order_date']) - pd.to_datetime(df['first_order_date'])).dt.days
        
        # Create churn label (customers who haven't ordered in 90+ days)
        df['is_churned'] = (df['days_since_last_order'] > 90).astype(int)
        
        return df
    
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train the churn prediction model"""
        try:
            # Create features
            feature_df = self.create_features(df)
            
            # Select features for training
            feature_columns = [
                'total_orders', 'total_spent', 'days_since_last_order',
                'order_frequency', 'avg_order_value', 'customer_lifetime'
            ]
            
            X = feature_df[feature_columns].fillna(0)
            y = feature_df['is_churned']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.rf_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.rf_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Get feature importance
            self.feature_names = feature_columns
            self.feature_importance = dict(zip(
                feature_columns, 
                self.rf_model.feature_importances_
            ))
            
            self.is_trained = True
            
            return {
                "status": "success",
                "accuracy": accuracy,
                "n_samples": len(X),
                "n_features": len(feature_columns),
                "feature_importance": self.feature_importance,
                "classification_report": classification_report(y_test, y_pred, output_dict=True)
            }
            
        except Exception as e:
            logger.error(f"Error training churn model: {e}")
            return {"status": "error", "error": str(e)}
    
    def predict_churn_probability(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict churn probability for customers"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        feature_df = self.create_features(df)
        feature_columns = [
            'total_orders', 'total_spent', 'days_since_last_order',
            'order_frequency', 'avg_order_value', 'customer_lifetime'
        ]
        
        X = feature_df[feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Get probabilities
        churn_probabilities = self.rf_model.predict_proba(X_scaled)[:, 1]
        
        # Add predictions to dataframe
        feature_df['churn_probability'] = churn_probabilities
        feature_df['risk_level'] = pd.cut(
            churn_probabilities, 
            bins=[0, 0.3, 0.7, 1.0], 
            labels=['low', 'medium', 'high']
        )
        
        return feature_df
    
    def get_customer_recommendations(self, customer_data: Dict[str, Any]) -> List[str]:
        """Get personalized recommendations for a customer"""
        recommendations = []
        
        days_since_last = customer_data.get('days_since_last_order', 0)
        total_orders = customer_data.get('total_orders', 0)
        avg_order_value = customer_data.get('avg_order_value', 0)
        
        if days_since_last > 60:
            recommendations.append("Send re-engagement email with special offers")
        
        if total_orders < 3:
            recommendations.append("Offer first-time buyer incentives")
        
        if avg_order_value < 50:
            recommendations.append("Suggest product bundles to increase order value")
        
        if days_since_last > 30 and total_orders > 5:
            recommendations.append("Offer loyalty program benefits")
        
        if not recommendations:
            recommendations.append("Continue current engagement strategy")
        
        return recommendations
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        model_data = {
            'rf_model': self.rf_model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Churn model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        self.rf_model = model_data['rf_model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.feature_importance = model_data['feature_importance']
        self.is_trained = model_data['is_trained']
        logger.info(f"Churn model loaded from {filepath}")


class MLModelManager:
    """Manager for all ML models"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.segmentation_model = CustomerSegmentationModel()
        self.churn_model = ChurnPredictionModel()
        
        # Try to load existing models
        self._load_existing_models()
    
    def _load_existing_models(self):
        """Load existing trained models if available"""
        segmentation_path = self.models_dir / "segmentation_model.pkl"
        churn_path = self.models_dir / "churn_model.pkl"
        
        try:
            if segmentation_path.exists():
                self.segmentation_model.load_model(str(segmentation_path))
                logger.info("Loaded existing segmentation model")
        except Exception as e:
            logger.warning(f"Could not load segmentation model: {e}")
        
        try:
            if churn_path.exists():
                self.churn_model.load_model(str(churn_path))
                logger.info("Loaded existing churn model")
        except Exception as e:
            logger.warning(f"Could not load churn model: {e}")
    
    def save_all_models(self):
        """Save all trained models"""
        segmentation_path = self.models_dir / "segmentation_model.pkl"
        churn_path = self.models_dir / "churn_model.pkl"
        
        if self.segmentation_model.is_trained:
            self.segmentation_model.save_model(str(segmentation_path))
        
        if self.churn_model.is_trained:
            self.churn_model.save_model(str(churn_path))
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        return {
            "segmentation_model": {
                "is_trained": self.segmentation_model.is_trained,
                "n_clusters": self.segmentation_model.n_clusters if self.segmentation_model.is_trained else None
            },
            "churn_model": {
                "is_trained": self.churn_model.is_trained,
                "n_features": len(self.churn_model.feature_names) if self.churn_model.is_trained else 0
            },
            "models_directory": str(self.models_dir)
        }
