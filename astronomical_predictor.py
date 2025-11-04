#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
astronomical_predictor.py
-------------------------
Model predykcyjny dla zdarzeń astronomicznych
Przewiduje przyszłe pozycje Słońca, fazy Księżyca, meteory itp.
"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AstronomicalPredictor:
    def __init__(self):
        self.data = None
        self.models = {}
        self.scalers = {}
        self.encoders = {}

    def load_astronomical_data(self):
        """Ładuje dane astronomiczne do predykcji"""
        logger.info("🌌 LOADING ASTRONOMICAL DATA FOR PREDICTION!")

        events = []

        # Load from available files
        files_to_check = [
            'astronomical_współczesność.json',
            'astronomical_wiek_xix.json',
            'astronomical_nowożytność.json'
        ]

        for file_name in files_to_check:
            if Path(file_name).exists():
                try:
                    with open(file_name, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    results = data.get('results', {})
                    for epoch_key, epoch_events in results.items():
                        if isinstance(epoch_events, list):
                            events.extend(epoch_events[:2000])  # Limit per file

                    logger.info(f"✅ {file_name}: {len(epoch_events) if 'epoch_events' in locals() else 0} events")
                except Exception as e:
                    logger.error(f"❌ Error loading {file_name}: {e}")

        df = pd.DataFrame(events)
        logger.info(f"📊 Total events loaded: {len(df)}")

        # Prepare for prediction
        df['year'] = pd.to_numeric(df.get('year'), errors='coerce')
        df['jd'] = pd.to_numeric(df.get('jd'), errors='coerce')
        df['date'] = pd.to_datetime(df.get('date'), errors='coerce')

        # Extract temporal features
        if 'date' in df.columns:
            df['month'] = df['date'].dt.month
            df['day'] = df['date'].dt.day
            df['day_of_year'] = df['date'].dt.dayofyear

        self.data = df
        return df

    def prepare_features_for_prediction(self):
        """Przygotowuje features do predykcji"""
        logger.info("🧠 PREPARING PREDICTION FEATURES!")

        if self.data is None:
            return

        df = self.data.copy()

        # Basic features
        df['title_length'] = df['title'].str.len().fillna(0)
        df['has_coordinates'] = pd.Series(df.get('coordinates')).notna().astype('int64')
        df['has_magnitude'] = pd.Series(df.get('magnitude')).notna().astype('int64')

        # Encode categorical features
        if 'subcategory' in df.columns:
            le_subcat = LabelEncoder()
            df['subcategory_encoded'] = le_subcat.fit_transform(df['subcategory'].fillna('UNKNOWN'))
            self.encoders['subcategory'] = le_subcat

        if 'source' in df.columns:
            le_source = LabelEncoder()
            df['source_encoded'] = le_source.fit_transform(df['source'].fillna('UNKNOWN'))
            self.encoders['source'] = le_source

        # Temporal patterns
        df['is_summer'] = df.get('month', 0).isin([6, 7, 8]).astype(int)
        df['is_winter'] = df.get('month', 0).isin([12, 1, 2]).astype(int)

        self.data = df
        return df

    def train_temporal_predictor(self):
        """Trenuje model predykcji temporalnej"""
        logger.info("⏰ TRAINING TEMPORAL PREDICTOR!")

        if self.data is None or 'day_of_year' not in self.data.columns:
            logger.warning("No temporal data for prediction")
            return

        df = self.data.dropna(subset=['day_of_year', 'year']).copy()

        if len(df) < 100:
            logger.warning("Not enough temporal data")
            return

        # Features for predicting day of year
        feature_cols = ['year', 'month', 'title_length', 'has_coordinates']
        if 'subcategory_encoded' in df.columns:
            feature_cols.append('subcategory_encoded')

        X = df[feature_cols].fillna(0)
        y = df['day_of_year']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        regressor.fit(X_train_scaled, y_train)

        train_pred = regressor.predict(X_train_scaled)
        test_pred = regressor.predict(X_test_scaled)

        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))

        logger.info(f"📅 Temporal Predictor:")
        logger.info(f"   Train RMSE: {train_rmse:.2f} days")
        logger.info(f"   Test RMSE: {test_rmse:.2f} days")

        self.models['temporal_predictor'] = regressor
        self.scalers['temporal'] = scaler

        return regressor

    def train_subcategory_predictor(self):
        """Trenuje model predykcji podkategorii"""
        logger.info("🎯 TRAINING SUBCATEGORY PREDICTOR!")

        if self.data is None or 'subcategory' not in self.data.columns:
            return

        df = self.data.copy()

        # Features
        feature_cols = ['title_length', 'has_coordinates', 'has_magnitude', 'is_summer', 'is_winter']
        if 'month' in df.columns:
            feature_cols.append('month')
        if 'source_encoded' in df.columns:
            feature_cols.append('source_encoded')

        X = df[feature_cols].fillna(0)
        y = df['subcategory_encoded']

        if y.nunique() < 2:
            logger.warning("Not enough subcategory variation")
            return

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        classifier.fit(X_train_scaled, y_train)

        train_acc = classifier.score(X_train_scaled, y_train)
        test_acc = classifier.score(X_test_scaled, y_test)

        logger.info(f"🏷️  Subcategory Predictor:")
        logger.info(f"   Train accuracy: {train_acc:.4f}")
        logger.info(f"   Test accuracy: {test_acc:.4f}")

        self.models['subcategory_predictor'] = classifier
        self.scalers['subcategory'] = scaler

        return classifier

    def predict_future_events(self, future_years=5):
        """Przewiduje przyszłe zdarzenia astronomiczne"""
        logger.info(f"🔮 PREDICTING FUTURE EVENTS ({future_years} years ahead)!")

        if not self.models:
            logger.warning("No trained models for prediction")
            return []

        predictions = []

        # Generate future dates
        current_year = datetime.now().year
        future_dates = []

        for year in range(current_year + 1, current_year + future_years + 1):
            for month in range(1, 13):
                # Predict key astronomical dates
                if month in [1, 7]:  # Winter/summer solstice approximation
                    future_dates.append((year, month, 15))
                elif month in [4, 10]:  # Equinox approximation
                    future_dates.append((year, month, 20))

        # Make predictions for each future date
        for year, month, day in future_dates:
            try:
                # Temporal prediction
                if 'temporal_predictor' in self.models:
                    temporal_features = [[year, month, 50, 1, 0]]  # Sample features
                    temporal_scaled = self.scalers['temporal'].transform(temporal_features)
                    predicted_day = self.models['temporal_predictor'].predict(temporal_scaled)[0]

                    # Subcategory prediction
                    subcategory = "SOLAR_POSITION"  # Default
                    if 'subcategory_predictor' in self.models:
                        subcat_features = [[50, 1, 0, month in [6,7,8], month in [12,1,2], month, 0]]
                        subcat_scaled = self.scalers['subcategory'].transform(subcat_features)
                        predicted_subcat_encoded = self.models['subcategory_predictor'].predict(subcat_scaled)[0]

                        if 'subcategory' in self.encoders:
                            subcategory = self.encoders['subcategory'].inverse_transform([predicted_subcat_encoded])[0]

                    prediction = {
                        'year': year,
                        'month': month,
                        'predicted_day': int(predicted_day),
                        'subcategory': subcategory,
                        'confidence': 0.8,
                        'type': 'predicted'
                    }

                    predictions.append(prediction)

            except Exception as e:
                logger.warning(f"Error predicting for {year}-{month}: {e}")

        logger.info(f"🔮 Generated {len(predictions)} future predictions")
        return predictions

    def generate_prediction_report(self, predictions):
        """Generuje raport z predykcji"""
        logger.info("📋 GENERATING PREDICTION REPORT!")

        report = {
            'generated_at': datetime.now().isoformat(),
            'model_info': {
                'temporal_predictor': 'trained' if 'temporal_predictor' in self.models else 'not_available',
                'subcategory_predictor': 'trained' if 'subcategory_predictor' in self.models else 'not_available'
            },
            'predictions': predictions,
            'summary': {
                'total_predictions': len(predictions),
                'categories_predicted': list(set(p['subcategory'] for p in predictions)),
                'year_range': f"{min(p['year'] for p in predictions)} - {max(p['year'] for p in predictions)}" if predictions else "N/A"
            },
            'insights': [
                "Predictions based on historical astronomical patterns",
                "Focus on solar positions and seasonal astronomical events",
                "Predictions are probabilistic and should be verified with astronomical calculations",
                "Model accuracy depends on quality and quantity of training data"
            ]
        }

        with open('astronomical_predictions.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info("💾 Predictions saved to astronomical_predictions.json")
        return report

    def run_prediction_pipeline(self):
        """Uruchamia kompletny pipeline predykcyjny"""
        logger.info("🚀🔮 STARTING ASTRONOMICAL PREDICTION PIPELINE!")

        try:
            # Load and prepare data
            self.load_astronomical_data()
            self.prepare_features_for_prediction()

            # Train models
            self.train_temporal_predictor()
            self.train_subcategory_predictor()

            # Make predictions
            predictions = self.predict_future_events(future_years=3)

            # Generate report
            report = self.generate_prediction_report(predictions)

            logger.info("🎉🔮 PREDICTION PIPELINE COMPLETED!")
            logger.info(f"📊 Predictions generated: {len(predictions)}")

            return report

        except Exception as e:
            logger.error(f"💥 ERROR in prediction pipeline: {e}")
            raise

def main():
    print("🚀🔮 ASTRONOMICAL PREDICTOR!")
    print("Przewidywanie przyszłych zdarzeń astronomicznych")

    predictor = AstronomicalPredictor()
    report = predictor.run_prediction_pipeline()

    print("\n📊 PREDICTION RESULTS:")
    print(f"Total predictions: {report['summary']['total_predictions']}")
    print(f"Categories: {', '.join(report['summary']['categories_predicted'])}")
    print(f"Year range: {report['summary']['year_range']}")

    print("\n🔮 SAMPLE PREDICTIONS:")
    for pred in report['predictions'][:5]:
        print(f"  {pred['year']}-{pred['month']:02d}-{pred['predicted_day']:02d}: {pred['subcategory']}")

    print(f"\n💾 Full predictions saved to: astronomical_predictions.json")

if __name__ == "__main__":
    main()