#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
astronomical_mega_ml_integrator.py
----------------------------------
Rozszerzenie MEGA ML MODEL o dane astronomiczne!
Łączy wszystkie dane historyczne z astronomią w jeden potężny system ML.
"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
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

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Import existing mega ML model
from mega_ml_model import MegaMLModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AstronomicalMegaMLIntegrator(MegaMLModel):
    """Rozszerzony MEGA ML Model z integracją danych astronomicznych"""

    def __init__(self):
        super().__init__()
        self.astronomical_data = {}
        self.astronomical_features = None
        self.astronomical_models = {}
        self.combined_data = None

    def load_astronomical_data(self):
        """Ładuje wszystkie dane astronomiczne"""
        logger.info("🌌 LOADING ASTRONOMICAL DATA!")

        astronomical_files = [
            'astronomical_antyk_późny.json',
            'astronomical_antyk_wczesny.json',
            'astronomical_nowożytność.json',
            'astronomical_prehistoria.json',
            'astronomical_wczesne_średniowiecze.json',
            'astronomical_wiek_xix.json',
            'astronomical_współczesność.json',
            'astronomical_wysokie_średniowiecze.json'
        ]

        all_events = []

        for file_name in astronomical_files:
            file_path = Path(file_name)
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Extract events from the correct structure
                    results = data.get('results', {})
                    for epoch_key, events in results.items():
                        if isinstance(events, list):
                            all_events.extend(events)

                    logger.info(f"✅ {file_name}: {len(events) if 'events' in locals() else 0} events loaded")
                except Exception as e:
                    logger.error(f"❌ Error loading {file_name}: {e}")
            else:
                logger.warning(f"⚠️  {file_name} not found")

        logger.info(f"🌟 Total astronomical events loaded: {len(all_events)}")
        return all_events

    def process_astronomical_data(self, events):
        """Przetwarza dane astronomiczne do formatu DataFrame"""
        logger.info("🔧 PROCESSING ASTRONOMICAL DATA!")

        processed_events = []

        for event in events:
            processed_event = {
                'event_id': event.get('id', ''),
                'title': event.get('title', ''),
                'description': event.get('description', ''),
                'category': event.get('category', 'ASTRONOMY'),
                'subcategory': event.get('subcategory', ''),
                'year': event.get('year', None),
                'jd': event.get('jd', None),
                'source': event.get('source', ''),
                'epoch': event.get('epoch', ''),
                'magnitude': event.get('magnitude', None),
                'coordinates': event.get('coordinates', ''),
                'visibility': event.get('visibility', ''),
                'duration': event.get('duration', ''),
                'significance': event.get('significance', ''),
                'astronomical_type': 'event'
            }

            # Clean year
            if processed_event['year']:
                try:
                    processed_event['year'] = float(processed_event['year'])
                except:
                    processed_event['year'] = None

            processed_events.append(processed_event)

        df = pd.DataFrame(processed_events)
        logger.info(f"✅ Processed {len(df)} astronomical events into DataFrame")

        return df

    def extract_astronomical_features(self, df):
        """Ekstraktuje features specyficzne dla danych astronomicznych"""
        logger.info("🧠 EXTRACTING ASTRONOMICAL FEATURES!")

        # Basic text features
        df['title_length'] = df['title'].str.len().fillna(0)
        df['description_length'] = df['description'].str.len().fillna(0)

        # Temporal features
        df['century'] = df['year'] // 100 if df['year'].notna().any() else None
        df['decade'] = (df['year'] // 10) * 10 if df['year'].notna().any() else None

        # Categorical encodings
        le_subcategory = LabelEncoder()
        df['subcategory_encoded'] = le_subcategory.fit_transform(df['subcategory'].fillna('unknown'))
        self.encoders['astronomical_subcategory'] = le_subcategory

        le_source = LabelEncoder()
        df['source_encoded'] = le_source.fit_transform(df['source'].fillna('unknown'))
        self.encoders['astronomical_source'] = le_source

        le_epoch = LabelEncoder()
        df['epoch_encoded'] = le_epoch.fit_transform(df['epoch'].fillna('unknown'))
        self.encoders['astronomical_epoch'] = le_epoch

        # Astronomical specific features
        df['has_magnitude'] = (~df['magnitude'].isna()).astype(int)
        df['has_coordinates'] = (df['coordinates'] != '').astype(int)
        df['has_visibility'] = (df['visibility'] != '').astype(int)
        df['has_duration'] = (df['duration'] != '').astype(int)

        # Significance score (if available)
        df['significance_score'] = pd.to_numeric(df['significance'], errors='coerce').fillna(0)

        # Meteor shower specific features
        df['is_meteor_shower'] = (df['subcategory'] == 'METEOR_SHOWER').astype(int)
        df['is_solar_event'] = (df['subcategory'] == 'SOLAR_EVENT').astype(int)
        df['is_comet'] = (df['subcategory'] == 'COMET').astype(int)

        self.astronomical_features = df
        logger.info(f"✅ Astronomical features extracted: {len(df.columns)} columns")

        return df

    def train_astronomical_models(self):
        """Trenuje modele ML specyficzne dla danych astronomicznych"""
        logger.info("🎯 TRAINING ASTRONOMICAL ML MODELS!")

        if self.astronomical_features is None:
            logger.error("No astronomical features available!")
            return

        df = self.astronomical_features.copy()

        # 1. Subcategory Classification
        feature_cols = ['title_length', 'description_length', 'century', 'decade',
                       'source_encoded', 'epoch_encoded', 'has_magnitude', 'has_coordinates',
                       'has_visibility', 'has_duration', 'significance_score']

        X = df[feature_cols].fillna(0)
        y = df['subcategory_encoded']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_classifier.fit(X_train_scaled, y_train)

        train_score = rf_classifier.score(X_train_scaled, y_train)
        test_score = rf_classifier.score(X_test_scaled, y_test)

        logger.info(f"🌟 Astronomical Subcategory Classifier:")
        logger.info(f"   Train accuracy: {train_score:.4f}")
        logger.info(f"   Test accuracy: {test_score:.4f}")

        self.astronomical_models['subcategory_classifier'] = rf_classifier
        self.scalers['astronomical_classification'] = scaler

        # 2. Clustering astronomical events
        n_clusters = min(8, len(X) // 100)  # Adaptive clustering
        if n_clusters >= 2:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_train_scaled)

            silhouette = silhouette_score(X_train_scaled, clusters)
            logger.info(f"🎪 Astronomical Clustering: {n_clusters} clusters, silhouette: {silhouette:.3f}")

            self.astronomical_models['astronomical_kmeans'] = kmeans

        return rf_classifier

    def combine_historical_astronomical_data(self):
        """Łączy dane historyczne z astronomią"""
        logger.info("🔗 COMBINING HISTORICAL AND ASTRONOMICAL DATA!")

        if self.unified_data is None:
            logger.warning("No historical data available!")
            return

        if self.astronomical_features is None:
            logger.warning("No astronomical data available!")
            return

        # Add astronomical type to historical data
        hist_df = self.unified_data.copy()
        hist_df['astronomical_type'] = 'historical'

        # Prepare astronomical data for merging
        astro_df = self.astronomical_features.copy()
        astro_df = astro_df.rename(columns={
            'title': 'title',
            'description': 'content',
            'subcategory': 'category',
            'source': 'data_source'
        })

        # Add missing columns to astronomical data
        for col in hist_df.columns:
            if col not in astro_df.columns:
                astro_df[col] = None

        # Combine datasets
        combined_df = pd.concat([hist_df, astro_df], ignore_index=True)
        combined_df['is_astronomical'] = (combined_df['astronomical_type'] == 'event').astype(int)

        self.combined_data = combined_df
        logger.info(f"🎯 Combined dataset: {len(combined_df)} total records")
        logger.info(f"   Historical: {len(hist_df)} records")
        logger.info(f"   Astronomical: {len(astro_df)} records")

        return combined_df

    def train_combined_models(self):
        """Trenuje modele na połączonych danych historyczno-astronomicznych"""
        logger.info("🚀 TRAINING COMBINED HISTORICAL-ASTRONOMICAL MODELS!")

        if self.combined_data is None:
            logger.error("No combined data available!")
            return

        df = self.combined_data.copy()

        # Features for combined analysis
        feature_cols = ['title_length', 'content_length', 'has_year', 'century',
                       'category_encoded', 'source_encoded', 'is_astronomical',
                       'has_person', 'has_place', 'has_org']

        # Add astronomical features if available
        astronomical_cols = ['subcategory_encoded', 'epoch_encoded', 'has_magnitude',
                           'has_coordinates', 'significance_score']
        for col in astronomical_cols:
            if col in df.columns:
                feature_cols.append(col)

        X = df[feature_cols].fillna(0)
        y = df['is_astronomical']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train combined classifier
        combined_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        combined_classifier.fit(X_train_scaled, y_train)

        train_score = combined_classifier.score(X_train_scaled, y_train)
        test_score = combined_classifier.score(X_test_scaled, y_test)

        logger.info(f"🔗 Combined Historical-Astronomical Classifier:")
        logger.info(f"   Train accuracy: {train_score:.4f}")
        logger.info(f"   Test accuracy: {test_score:.4f}")

        self.models['combined_classifier'] = combined_classifier
        self.scalers['combined'] = scaler

        return combined_classifier

    def analyze_astro_historical_patterns(self):
        """Analizuje wzorce między zdarzeniami astronomicznymi a historycznymi"""
        logger.info("🔍 ANALYZING ASTRO-HISTORICAL PATTERNS!")

        if self.combined_data is None:
            return

        df = self.combined_data.copy()

        # Temporal correlation analysis
        historical_by_year = df[df['is_astronomical'] == 0].groupby('year').size()
        astronomical_by_year = df[df['is_astronomical'] == 1].groupby('year').size()

        # Find years with both types of events
        common_years = set(historical_by_year.index) & set(astronomical_by_year.index)

        logger.info(f"📊 Years with both historical and astronomical events: {len(common_years)}")

        if common_years:
            # Correlation analysis
            hist_counts = historical_by_year.loc[list(common_years)]
            astro_counts = astronomical_by_year.loc[list(common_years)]

            correlation = hist_counts.corr(astro_counts)
            logger.info(f"📈 Correlation between historical and astronomical events: {correlation:.3f}")

        # Category analysis
        astro_categories = df[df['is_astronomical'] == 1]['category'].value_counts()
        hist_categories = df[df['is_astronomical'] == 0]['category'].value_counts()

        logger.info("🌌 Top Astronomical Categories:")
        for cat, count in astro_categories.head(5).items():
            logger.info(f"   {cat}: {count}")

        logger.info("📜 Top Historical Categories:")
        for cat, count in hist_categories.head(5).items():
            logger.info(f"   {cat}: {count}")

        return {
            'correlation': correlation if 'correlation' in locals() else None,
            'common_years': len(common_years),
            'astro_categories': astro_categories.to_dict(),
            'hist_categories': hist_categories.to_dict()
        }

    def generate_combined_insights(self):
        """Generuje insights z połączonej analizy"""
        logger.info("💡 GENERATING COMBINED INSIGHTS!")

        insights = {
            'data_summary': {
                'total_records': len(self.combined_data) if self.combined_data is not None else 0,
                'historical_records': 0,
                'astronomical_records': 0,
                'combined_accuracy': 0.0
            },
            'astronomical_analysis': {},
            'pattern_analysis': {},
            'model_performance': {},
            'recommendations': []
        }

        if self.combined_data is not None:
            df = self.combined_data
            insights['data_summary']['historical_records'] = (df['is_astronomical'] == 0).sum()
            insights['data_summary']['astronomical_records'] = (df['is_astronomical'] == 1).sum()

        if self.astronomical_features is not None:
            astro_df = self.astronomical_features
            insights['astronomical_analysis'] = {
                'subcategories': astro_df['subcategory'].value_counts().to_dict(),
                'epochs': astro_df['epoch'].value_counts().to_dict(),
                'sources': astro_df['source'].value_counts().to_dict(),
                'year_range': {
                    'min': float(astro_df['year'].min()),
                    'max': float(astro_df['year'].max())
                } if astro_df['year'].notna().any() else None
            }

        # Pattern analysis
        pattern_results = self.analyze_astro_historical_patterns()
        if pattern_results:
            insights['pattern_analysis'] = pattern_results

        # Model performance
        for model_name, model in {**self.models, **self.astronomical_models}.items():
            if hasattr(model, 'score'):
                insights['model_performance'][model_name] = "Trained successfully"

        # Recommendations
        insights['recommendations'] = [
            f"Combined dataset: {insights['data_summary']['total_records']} records",
            f"Astronomical events: {insights['data_summary']['astronomical_records']}",
            f"Historical events: {insights['data_summary']['historical_records']}",
            "Astronomical ML models trained for subcategory classification",
            "Combined historical-astronomical analysis available",
            "Ready for advanced astro-historical pattern discovery"
        ]

        # Save insights
        with open('astronomical_mega_ml_insights.json', 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)

        logger.info("💾 Combined insights saved to astronomical_mega_ml_insights.json")

        return insights

    def run_complete_astronomical_pipeline(self):
        """Uruchamia kompletny pipeline astronomiczno-historyczny"""
        logger.info("🚀🌌🚀 STARTING ASTRONOMICAL MEGA ML PIPELINE! 🚀🌌🚀")

        start_time = datetime.now()

        try:
            # 1. Load historical data (parent class)
            self.load_all_data()
            self.unify_all_data()
            self.extract_features()

            # 2. Load astronomical data
            astronomical_events = self.load_astronomical_data()
            astronomical_df = self.process_astronomical_data(astronomical_events)
            self.extract_astronomical_features(astronomical_df)

            # 3. Train astronomical models
            self.train_astronomical_models()

            # 4. Combine datasets
            self.combine_historical_astronomical_data()

            # 5. Train combined models
            self.train_combined_models()

            # 6. Analyze patterns
            self.analyze_astro_historical_patterns()

            # 7. Generate insights
            insights = self.generate_combined_insights()

            elapsed = datetime.now() - start_time

            logger.info("🎉🌟🎉 ASTRONOMICAL MEGA ML PIPELINE COMPLETED! 🎉🌟🎉")
            logger.info(f"⏱️  Total time: {elapsed.total_seconds():.1f} seconds")
            logger.info(f"📊 Historical records: {insights['data_summary']['historical_records']}")
            logger.info(f"🌌 Astronomical records: {insights['data_summary']['astronomical_records']}")
            logger.info(f"🤖 Models trained: {len(self.models) + len(self.astronomical_models)}")

            return insights

        except Exception as e:
            logger.error(f"💥 ERROR in astronomical pipeline: {e}")
            raise

def main():
    """Main function"""
    print("🚀🌌🚀 ASTRONOMICAL MEGA ML INTEGRATOR! 🚀🌌🚀")
    print("Łączenie danych historycznych z astronomią w jeden potężny system ML!")

    integrator = AstronomicalMegaMLIntegrator()
    insights = integrator.run_complete_astronomical_pipeline()

    print("\n📊 ASTRONOMICAL MEGA ML RESULTS:")
    print(f"📈 Total Records: {insights['data_summary']['total_records']}")
    print(f"📜 Historical: {insights['data_summary']['historical_records']}")
    print(f"🌌 Astronomical: {insights['data_summary']['astronomical_records']}")
    print(f"🤖 Models Trained: {len(insights['model_performance'])}")

    if 'pattern_analysis' in insights and insights['pattern_analysis'].get('correlation'):
        print(f"📈 Astro-Historical Correlation: {insights['pattern_analysis']['correlation']:.3f}")

    print("\n🌌 TOP ASTRONOMICAL SUBCATEGORIES:")
    subcats = insights['astronomical_analysis'].get('subcategories', {})
    for subcat, count in list(subcats.items())[:5]:
        print(f"  ⭐ {subcat}: {count} events")

    print("\n💡 RECOMMENDATIONS:")
    for rec in insights['recommendations']:
        print(f"  ✅ {rec}")

    print(f"\n💾 Full insights saved to: astronomical_mega_ml_insights.json")
    print(f"🎯 ASTRONOMICAL MEGA ML SYSTEM READY FOR COSMIC DOMINATION! 🎯")

if __name__ == "__main__":
    main()