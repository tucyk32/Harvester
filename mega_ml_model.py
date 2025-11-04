#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mega_ml_model.py
----------------
MEGA MODEL ML - łączy WSZYSTKIE dane z harvesterów w jeden potężny model ML!
Analiza historyczna, predykcja, clustering, NLP - WSZYSTKO!
"""

import pandas as pd
import numpy as np
import json
import sqlite3
from pathlib import Path
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, mean_squared_error, silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# NLP imports
import re
import spacy
from collections import Counter

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MegaMLModel:
    def __init__(self):
        self.data = {}
        self.unified_data = None
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.features = {}
        self.nlp = None
        
        # Initialize NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found. NLP features will be limited.")
    
    def load_all_data(self):
        """Ładuje WSZYSTKIE dane z wszystkich źródeł"""
        logger.info("🔥 LOADING ALL DATA FROM ALL SOURCES!")
        
        data_paths = {
            'advanced_harvester': 'data/cache/harvested_data.csv',
            'scientific_papers': 'data/scientific_cache/scientific_papers.csv', 
            'real_data_complete': 'data/real_data_complete.csv',
            'real_harvested': 'data/real_harvested_data.csv',
            'ml_complete': 'data/unified_output/ml_complete_dataset.csv',
            'ml_features': 'data/unified_output/ml_features_dataset.csv',
            'ml_high_confidence': 'data/unified_output/ml_high_confidence_dataset.csv',
            'ml_timeseries': 'data/unified_output/ml_timeseries_dataset.csv'
        }
        
        for name, path in data_paths.items():
            try:
                if Path(path).exists():
                    df = pd.read_csv(path, encoding='utf-8')
                    self.data[name] = df
                    logger.info(f"✅ {name}: {len(df)} records loaded")
                else:
                    logger.warning(f"⚠️  {path} not found")
            except Exception as e:
                logger.error(f"❌ Error loading {name}: {e}")
        
        logger.info(f"📊 Total datasets loaded: {len(self.data)}")
        return self.data
    
    def unify_all_data(self):
        """Unifikuje wszystkie dane w jeden mega dataset"""
        logger.info("🔧 UNIFYING ALL DATA INTO MEGA DATASET!")
        
        unified_records = []
        
        for dataset_name, df in self.data.items():
            logger.info(f"🔄 Processing {dataset_name}: {len(df)} records")
            
            for idx, row in df.iterrows():
                # Base record structure
                record = {
                    'source_dataset': dataset_name,
                    'record_id': f"{dataset_name}_{idx}",
                    'title': '',
                    'content': '',
                    'date_info': '',
                    'year': None,
                    'jd': None,
                    'am_day': None,
                    'language': '',
                    'category': '',
                    'confidence': 0.5,
                    'data_source': '',
                    'url': ''
                }
                
                # Map fields from different datasets
                if dataset_name == 'advanced_harvester':
                    record.update({
                        'title': str(row.get('title', '')),
                        'content': str(row.get('content', '')),
                        'year': row.get('year_abs', None),
                        'jd': row.get('jd', None),
                        'am_day': row.get('am_day', None),
                        'language': str(row.get('language', '')),
                        'category': str(row.get('category', '')),
                        'data_source': str(row.get('source', '')),
                        'url': str(row.get('url', ''))
                    })
                
                elif dataset_name == 'scientific_papers':
                    record.update({
                        'title': str(row.get('title', '')),
                        'content': str(row.get('abstract', '')),
                        'year': row.get('year', None),
                        'category': 'scientific_paper',
                        'data_source': str(row.get('source', 'scientific')),
                        'url': str(row.get('url', ''))
                    })
                
                elif 'real_data' in dataset_name:
                    record.update({
                        'title': str(row.get('title', '')),
                        'content': str(row.get('abstract', row.get('content', ''))),
                        'year': row.get('year', None),
                        'category': str(row.get('category', '')),
                        'data_source': str(row.get('data_source', '')),
                        'url': str(row.get('url', ''))
                    })
                
                elif 'ml_' in dataset_name:
                    record.update({
                        'title': str(row.get('title', '')),
                        'content': str(row.get('content', '')),
                        'year': row.get('year', None),
                        'jd': row.get('jd', None),
                        'am_day': row.get('am_day', None),
                        'category': str(row.get('category', '')),
                        'confidence': row.get('confidence', 0.5),
                        'data_source': str(row.get('source', ''))
                    })
                
                # Clean and validate
                if record['year'] and not pd.isna(record['year']):
                    try:
                        record['year'] = int(float(record['year']))
                    except:
                        record['year'] = None
                
                # Calculate JD/AM_day if missing but year available
                if record['year'] and not record['jd']:
                    record['jd'] = self.year_to_jd(record['year'])
                    record['am_day'] = record['jd'] - 1721668.5 if record['jd'] else None
                
                unified_records.append(record)
        
        self.unified_data = pd.DataFrame(unified_records)
        logger.info(f"🎯 UNIFIED DATASET CREATED: {len(self.unified_data)} total records!")
        
        return self.unified_data
    
    def year_to_jd(self, year):
        """Convert year to approximate Julian Day (Jan 1st)"""
        try:
            if year > 1582:  # Gregorian
                jd = 1721425.5 + 365.25 * year + int(year/100) - int(year/400)
            else:  # Julian
                jd = 1721425.5 + 365.25 * year
            return jd
        except:
            return None
    
    def extract_features(self):
        """Ekstraktuje features dla ML"""
        logger.info("🧠 EXTRACTING ML FEATURES!")
        
        if self.unified_data is None:
            logger.error("No unified data available!")
            return
        
        df = self.unified_data.copy()
        
        # Basic features
        df['title_length'] = df['title'].str.len().fillna(0)
        df['content_length'] = df['content'].str.len().fillna(0)
        df['has_year'] = (~df['year'].isna()).astype(int)
        df['has_jd'] = (~df['jd'].isna()).astype(int)
        
        # Temporal features
        df['century'] = df['year'] // 100
        df['era'] = np.where(df['year'] < 0, 'BCE', 'CE')
        df['year_category'] = pd.cut(df['year'], 
                                   bins=[-np.inf, -1000, 0, 500, 1000, 1500, 1800, 1900, 2000, np.inf],
                                   labels=['ancient', 'classical', 'early', 'medieval', 'renaissance', 
                                          'early_modern', 'industrial', 'modern', 'contemporary'])
        
        # Text features (simplified without spaCy)
        logger.info("🔤 Extracting text features...")
        
        # Simple text-based features
        df['has_person'] = df['content'].str.contains(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', na=False).astype(int)
        df['has_place'] = df['content'].str.contains(r'\b(city|country|region|area|place|location)\b', case=False, na=False).astype(int)
        df['has_org'] = df['content'].str.contains(r'\b(university|institute|organization|company|group)\b', case=False, na=False).astype(int)
        
        # Additional text features
        df['has_numbers'] = df['content'].str.contains(r'\d+', na=False).astype(int)
        df['has_keywords'] = df['content'].str.contains(r'\b(research|study|analysis|investigation|discovery)\b', case=False, na=False).astype(int)
        
        if self.nlp:
            logger.info("🔤 Enhanced NLP features available but using simplified version for performance")
        else:
            logger.info("🔤 Using simplified text features (spaCy not available)")
        
        # Category encoding
        le_category = LabelEncoder()
        df['category_encoded'] = le_category.fit_transform(df['category'].fillna('unknown'))
        self.encoders['category'] = le_category
        
        # Source encoding
        le_source = LabelEncoder()
        df['source_encoded'] = le_source.fit_transform(df['data_source'].fillna('unknown'))
        self.encoders['source'] = le_source
        
        # Dataset encoding
        le_dataset = LabelEncoder()
        df['dataset_encoded'] = le_dataset.fit_transform(df['source_dataset'])
        self.encoders['dataset'] = le_dataset
        
        self.features = df
        logger.info(f"✅ Features extracted: {len(df.columns)} columns")
        
        return df
    
    def train_classification_models(self):
        """Trenuje modele klasyfikacji"""
        logger.info("🎯 TRAINING CLASSIFICATION MODELS!")
        
        if self.features is None:
            logger.error("No features available!")
            return
        
        df = self.features.copy()
        
        # Prepare features for classification
        feature_cols = ['title_length', 'content_length', 'has_year', 'has_jd', 
                       'century', 'has_person', 'has_place', 'has_org', 'confidence']
        
        X = df[feature_cols].fillna(0)
        
        # Classify by category
        y_category = df['category_encoded']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y_category, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['classification'] = scaler
        
        # Train Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = rf_model.score(X_train_scaled, y_train)
        test_score = rf_model.score(X_test_scaled, y_test)
        
        logger.info(f"🎯 Random Forest Category Classifier:")
        logger.info(f"   Train accuracy: {train_score:.3f}")
        logger.info(f"   Test accuracy: {test_score:.3f}")
        
        self.models['category_classifier'] = rf_model
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("🔍 Feature Importance:")
        for _, row in feature_importance.head().iterrows():
            logger.info(f"   {row['feature']}: {row['importance']:.3f}")
        
        return rf_model
    
    def train_regression_models(self):
        """Trenuje modele regresji dla przewidywania dat"""
        logger.info("📊 TRAINING REGRESSION MODELS!")
        
        if self.features is None:
            return
        
        df = self.features[~self.features['year'].isna()].copy()
        
        if len(df) == 0:
            logger.warning("No data with years for regression!")
            return
        
        # Features for year prediction
        feature_cols = ['title_length', 'content_length', 'category_encoded', 
                       'source_encoded', 'has_person', 'has_place', 'has_org']
        
        X = df[feature_cols].fillna(0)
        y = df['year']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['regression'] = scaler
        
        # Train Gradient Boosting
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        gb_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = gb_model.predict(X_train_scaled)
        test_pred = gb_model.predict(X_test_scaled)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        
        logger.info(f"📊 Gradient Boosting Year Predictor:")
        logger.info(f"   Train MSE: {train_mse:.1f}")
        logger.info(f"   Test MSE: {test_mse:.1f}")
        logger.info(f"   Train RMSE: {np.sqrt(train_mse):.1f} years")
        logger.info(f"   Test RMSE: {np.sqrt(test_mse):.1f} years")
        
        self.models['year_predictor'] = gb_model
        
        return gb_model
    
    def perform_clustering(self):
        """Wykonuje clustering wydarzeń historycznych"""
        logger.info("🎪 PERFORMING EVENT CLUSTERING!")
        
        if self.features is None:
            return
        
        df = self.features.copy()
        
        # Features for clustering
        feature_cols = ['title_length', 'content_length', 'century', 'category_encoded',
                       'has_person', 'has_place', 'has_org', 'confidence']
        
        X = df[feature_cols].fillna(0)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['clustering'] = scaler
        
        # K-Means clustering
        n_clusters = min(8, len(X) // 10)  # Adaptive cluster count
        if n_clusters < 2:
            logger.warning("Not enough data for clustering!")
            return
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Evaluate clustering
        silhouette = silhouette_score(X_scaled, clusters)
        
        logger.info(f"🎪 K-Means Clustering Results:")
        logger.info(f"   Clusters: {n_clusters}")
        logger.info(f"   Silhouette Score: {silhouette:.3f}")
        
        # Add clusters to data
        df['cluster'] = clusters
        self.features = df
        self.models['kmeans'] = kmeans
        
        # Analyze clusters
        logger.info("🔍 Cluster Analysis:")
        for i in range(n_clusters):
            cluster_data = df[df['cluster'] == i]
            top_categories = cluster_data['category'].value_counts().head(3)
            avg_year = cluster_data['year'].mean()
            
            logger.info(f"   Cluster {i}: {len(cluster_data)} events")
            logger.info(f"     Avg Year: {avg_year:.0f}" if not pd.isna(avg_year) else "     Avg Year: Unknown")
            logger.info(f"     Top Categories: {list(top_categories.index)}")
        
        return kmeans
    
    def analyze_temporal_patterns(self):
        """Analizuje wzorce temporalne"""
        logger.info("⏰ ANALYZING TEMPORAL PATTERNS!")
        
        if self.features is None:
            return
        
        df = self.features[~self.features['year'].isna()].copy()
        
        if len(df) == 0:
            logger.warning("No temporal data available!")
            return
        
        # Time series analysis
        df['decade'] = (df['year'] // 10) * 10
        decade_counts = df['decade'].value_counts().sort_index()
        
        logger.info("📊 Events by Decade (top 10):")
        for decade, count in decade_counts.head(10).items():
            logger.info(f"   {decade}s: {count} events")
        
        # Category trends over time
        category_time = df.groupby(['century', 'category']).size().unstack(fill_value=0)
        
        logger.info("📈 Category Trends by Century:")
        for category in category_time.columns[:5]:  # Top 5 categories
            trend = category_time[category]
            logger.info(f"   {category}: {trend.sum()} total events")
        
        return decade_counts, category_time
    
    def generate_insights(self):
        """Generuje insights z analizy ML"""
        logger.info("💡 GENERATING ML INSIGHTS!")
        
        insights = {
            'data_summary': {
                'total_records': len(self.unified_data) if self.unified_data is not None else 0,
                'datasets_used': list(self.data.keys()),
                'records_per_dataset': {name: len(df) for name, df in self.data.items()}
            },
            'temporal_coverage': {},
            'model_performance': {},
            'clustering_results': {},
            'top_categories': {},
            'recommendations': []
        }
        
        if self.features is not None:
            df = self.features
            
            # Temporal coverage
            if not df['year'].isna().all():
                insights['temporal_coverage'] = {
                    'earliest_year': int(df['year'].min()),
                    'latest_year': int(df['year'].max()),
                    'span_years': int(df['year'].max() - df['year'].min()),
                    'records_with_dates': int((~df['year'].isna()).sum())
                }
            
            # Top categories
            insights['top_categories'] = df['category'].value_counts().head(10).to_dict()
            
            # Model performance
            for model_name, model in self.models.items():
                if hasattr(model, 'score'):
                    insights['model_performance'][model_name] = "Trained successfully"
            
            # Clustering
            if 'cluster' in df.columns:
                insights['clustering_results'] = {
                    'n_clusters': df['cluster'].nunique(),
                    'cluster_sizes': df['cluster'].value_counts().to_dict()
                }
            
            # Recommendations
            insights['recommendations'] = [
                f"Dataset contains {len(df)} total records from {len(self.data)} sources",
                f"Temporal span: {insights['temporal_coverage'].get('span_years', 0)} years",
                f"Most common category: {df['category'].mode().iloc[0] if len(df) > 0 else 'Unknown'}",
                "Models trained for classification, regression, and clustering",
                "Ready for advanced historical analysis and prediction"
            ]
        
        # Save insights
        with open('mega_ml_insights.json', 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("💾 Insights saved to mega_ml_insights.json")
        
        return insights
    
    def run_complete_ml_pipeline(self):
        """Uruchamia kompletny pipeline ML"""
        logger.info("🚀🚀🚀 STARTING MEGA ML PIPELINE! 🚀🚀🚀")
        
        start_time = datetime.now()
        
        try:
            # 1. Load all data
            self.load_all_data()
            
            # 2. Unify data
            self.unify_all_data()
            
            # 3. Extract features
            self.extract_features()
            
            # 4. Train models
            self.train_classification_models()
            self.train_regression_models()
            
            # 5. Clustering
            self.perform_clustering()
            
            # 6. Temporal analysis
            self.analyze_temporal_patterns()
            
            # 7. Generate insights
            insights = self.generate_insights()
            
            elapsed = datetime.now() - start_time
            
            logger.info("🎉🎉🎉 MEGA ML PIPELINE COMPLETED! 🎉🎉🎉")
            logger.info(f"⏱️  Total time: {elapsed.total_seconds():.1f} seconds")
            logger.info(f"📊 Total records processed: {len(self.unified_data) if self.unified_data is not None else 0}")
            logger.info(f"🤖 Models trained: {len(self.models)}")
            logger.info(f"📈 Features extracted: {len(self.features.columns) if self.features is not None else 0}")
            
            return insights
            
        except Exception as e:
            logger.error(f"💥 ERROR in ML pipeline: {e}")
            raise

def main():
    """Main function"""
    print("🔥🔥🔥 MEGA ML MODEL - WSZYSTKIE DANE W JEDEN MODEL! 🔥🔥🔥")
    
    model = MegaMLModel()
    insights = model.run_complete_ml_pipeline()
    
    print("\n📊 MEGA ML RESULTS:")
    print(f"📈 Total Records: {insights['data_summary']['total_records']}")
    print(f"📅 Temporal Span: {insights['temporal_coverage'].get('span_years', 0)} years")
    print(f"🤖 Models Trained: {len(insights['model_performance'])}")
    print(f"🎪 Clusters Found: {insights['clustering_results'].get('n_clusters', 0)}")
    
    print("\n🏆 TOP CATEGORIES:")
    for category, count in list(insights['top_categories'].items())[:5]:
        print(f"  🥇 {category}: {count} records")
    
    print("\n💡 RECOMMENDATIONS:")
    for rec in insights['recommendations']:
        print(f"  ✅ {rec}")
    
    print(f"\n💾 Full insights saved to: mega_ml_insights.json")
    print(f"🎯 MEGA ML MODEL READY FOR HISTORICAL DOMINATION! 🎯")

if __name__ == "__main__":
    main()