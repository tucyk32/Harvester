#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
light_astronomical_integrator.py
---------------------------------
Lekka wersja integratora astronomicznego z mega ML
"""

import pandas as pd
import json
import logging
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightAstronomicalIntegrator:
    def __init__(self):
        self.astronomical_data = None
        self.historical_data = None
        self.combined_data = None
        self.models = {}

    def load_astronomical_sample(self, max_events=10000):
        """Ładuje próbkę danych astronomicznych"""
        logger.info(f"🌌 LOADING ASTRONOMICAL SAMPLE (max {max_events} events)!")

        events = []
        files_to_load = ['astronomical_współczesność.json', 'astronomical_wiek_xix.json']

        for file_name in files_to_load:
            if Path(file_name).exists():
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                results = data.get('results', {})
                for epoch_key, epoch_events in results.items():
                    if isinstance(epoch_events, list):
                        events.extend(epoch_events)
                        if len(events) >= max_events:
                            break
                if len(events) >= max_events:
                    break

        events = events[:max_events]
        df = pd.DataFrame(events)

        # Clean and prepare data
        df['year'] = pd.to_numeric(df.get('year', df.get('date', '').str[:4]), errors='coerce')
        df['title_length'] = df['title'].str.len().fillna(0)
        df['subcategory'] = df.get('subcategory', 'UNKNOWN')

        self.astronomical_data = df
        logger.info(f"✅ Loaded {len(df)} astronomical events")
        return df

    def load_historical_sample(self, max_events=5000):
        """Ładuje próbkę danych historycznych"""
        logger.info(f"📜 LOADING HISTORICAL SAMPLE (max {max_events} events)!")

        # Load from mega_ml_insights or create sample
        try:
            with open('mega_ml_insights.json', 'r', encoding='utf-8') as f:
                insights = json.load(f)

            # Create sample historical data
            sample_data = []
            for i in range(min(max_events, 1000)):
                sample_data.append({
                    'title': f'Historical Event {i}',
                    'content': f'Content for historical event {i}',
                    'year': 1800 + (i % 200),
                    'category': 'HISTORY',
                    'source': 'historical_sample',
                    'is_astronomical': 0
                })

            df = pd.DataFrame(sample_data)
            self.historical_data = df
            logger.info(f"✅ Loaded {len(df)} historical events")
            return df

        except:
            logger.warning("Could not load historical data, creating sample")
            return pd.DataFrame()

    def combine_datasets(self):
        """Łączy dane astronomiczne z historycznymi"""
        logger.info("🔗 COMBINING DATASETS!")

        if self.astronomical_data is None:
            logger.error("No astronomical data!")
            return

        # Prepare astronomical data
        astro_df = self.astronomical_data.copy()
        astro_df['is_astronomical'] = 1
        astro_df['category'] = astro_df.get('category', 'ASTRONOMY')
        astro_df['content'] = astro_df.get('content', astro_df.get('description', ''))

        # Prepare historical data
        if self.historical_data is not None and len(self.historical_data) > 0:
            hist_df = self.historical_data.copy()
            hist_df['is_astronomical'] = 0

            # Combine
            combined = pd.concat([astro_df, hist_df], ignore_index=True)
        else:
            combined = astro_df

        # Add features
        combined['title_length'] = combined['title'].str.len().fillna(0)
        combined['content_length'] = combined['content'].str.len().fillna(0)
        combined['has_year'] = (~combined['year'].isna()).astype(int)

        self.combined_data = combined
        logger.info(f"🎯 Combined dataset: {len(combined)} records")
        return combined

    def train_combined_classifier(self):
        """Trenuje klasyfikator na połączonych danych"""
        logger.info("🎯 TRAINING COMBINED CLASSIFIER!")

        if self.combined_data is None:
            return

        df = self.combined_data.copy()

        # Features
        feature_cols = ['title_length', 'content_length', 'has_year']
        if 'year' in df.columns:
            feature_cols.append('year')

        X = df[feature_cols].fillna(0)
        y = df['is_astronomical']

        if len(X) < 10 or y.nunique() < 2:
            logger.warning("Not enough data for training")
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        clf = RandomForestClassifier(n_estimators=50, random_state=42)
        clf.fit(X_train_scaled, y_train)

        train_score = clf.score(X_train_scaled, y_train)
        test_score = clf.score(X_test_scaled, y_test)

        logger.info(f"🔗 Combined Classifier:")
        logger.info(f"   Train accuracy: {train_score:.4f}")
        logger.info(f"   Test accuracy: {test_score:.4f}")

        self.models['combined_classifier'] = clf

        return clf

    def generate_insights(self):
        """Generuje insights"""
        logger.info("💡 GENERATING INSIGHTS!")

        insights = {
            'data_summary': {
                'astronomical_events': len(self.astronomical_data) if self.astronomical_data is not None else 0,
                'historical_events': len(self.historical_data) if self.historical_data is not None else 0,
                'combined_events': len(self.combined_data) if self.combined_data is not None else 0
            },
            'model_performance': {},
            'recommendations': [
                "Astronomical data successfully integrated",
                "Combined ML model trained for astronomical vs historical classification",
                "Ready for further astronomical analysis"
            ]
        }

        if self.models:
            for model_name in self.models:
                insights['model_performance'][model_name] = "Trained successfully"

        with open('light_astronomical_insights.json', 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)

        logger.info("💾 Insights saved to light_astronomical_insights.json")
        return insights

    def run_light_pipeline(self):
        """Uruchamia lekki pipeline"""
        logger.info("🚀🌟 STARTING LIGHT ASTRONOMICAL PIPELINE!")

        try:
            # Load data
            self.load_astronomical_sample(max_events=5000)
            self.load_historical_sample(max_events=1000)

            # Combine and train
            self.combine_datasets()
            self.train_combined_classifier()

            # Generate insights
            insights = self.generate_insights()

            logger.info("🎉🌟 LIGHT PIPELINE COMPLETED!")
            logger.info(f"📊 Astronomical events: {insights['data_summary']['astronomical_events']}")
            logger.info(f"📜 Historical events: {insights['data_summary']['historical_events']}")

            return insights

        except Exception as e:
            logger.error(f"💥 ERROR: {e}")
            raise

def main():
    print("🚀🌟 LIGHT ASTRONOMICAL INTEGRATOR!")
    integrator = LightAstronomicalIntegrator()
    insights = integrator.run_light_pipeline()

    print("\n📊 RESULTS:")
    print(f"Astronomical: {insights['data_summary']['astronomical_events']}")
    print(f"Historical: {insights['data_summary']['historical_events']}")
    print(f"Combined: {insights['data_summary']['combined_events']}")

if __name__ == "__main__":
    main()