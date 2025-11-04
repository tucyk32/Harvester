#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
astronomical_ml_integrator.py
-----------------------------
Integruje dane astronomiczne z MEGA_WORLD_CHRONOLOGY do modelu ML
Dodaje 60,869 wydarzeń astronomicznych do systemu ML!
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AstronomicalMLIntegrator:
    def __init__(self):
        self.astronomical_data = []
        self.df_astronomical = None
        self.models = {}
        self.encoders = {}
        self.scalers = {}

    def load_all_astronomical_data(self):
        """Ładuje wszystkie dane astronomiczne z plików JSON"""
        logger.info("🌟 ŁADOWANIE DANYCH ASTRONOMICZNYCH DO ML!")

        astronomical_files = [
            'astronomical_prehistoria.json',
            'astronomical_antyk_wczesny.json',
            'astronomical_antyk_późny.json',
            'astronomical_wczesne_średniowiecze.json',
            'astronomical_wysokie_średniowiecze.json',
            'astronomical_nowożytność.json',
            'astronomical_wiek_xix.json',
            'astronomical_współczesność.json'
        ]

        total_events = 0

        for file_name in astronomical_files:
            file_path = Path(file_name)
            if file_path.exists():
                try:
                    logger.info(f"📖 Ładowanie: {file_name}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Wyciągnij wydarzenia z różnych struktur
                    events = []
                    if 'results' in data:
                        for epoch_key, epoch_events in data['results'].items():
                            events.extend(epoch_events)
                    elif isinstance(data, list):
                        events = data
                    else:
                        # Sprawdź inne możliwe struktury
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 0:
                                if isinstance(value[0], dict) and 'id' in value[0]:
                                    events.extend(value)

                    self.astronomical_data.extend(events)
                    logger.info(f"✅ {file_name}: {len(events)} wydarzeń")
                    total_events += len(events)

                except Exception as e:
                    logger.error(f"❌ Błąd ładowania {file_name}: {e}")
            else:
                logger.warning(f"⚠️ Plik nie istnieje: {file_name}")

        logger.info(f"🎯 Łącznie załadowano: {total_events} wydarzeń astronomicznych")
        return total_events

    def convert_to_dataframe(self):
        """Konwertuje dane astronomiczne na DataFrame pandas"""
        logger.info("🔄 Konwersja danych astronomicznych na DataFrame...")

        records = []
        for event in self.astronomical_data:
            record = {
                'id': event.get('id', ''),
                'title': event.get('title', ''),
                'date': event.get('date', ''),
                'time': event.get('time', '00:00:00'),
                'category': event.get('category', 'ASTRONOMY'),
                'subcategory': event.get('subcategory', ''),
                'source': event.get('source', ''),
                'content': event.get('content', ''),
                'epoch': event.get('epoch', ''),
                'epoch_period': event.get('epoch_period', ''),
                'julian_day': event.get('julian_day', 0),
            }

            # Dodaj metadane
            metadata = event.get('metadata', {})
            for key, value in metadata.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    record[f'meta_{key}'] = value
                elif isinstance(value, str):
                    record[f'meta_{key}'] = value

            records.append(record)

        self.df_astronomical = pd.DataFrame(records)
        logger.info(f"✅ DataFrame utworzony: {len(self.df_astronomical)} wierszy, {len(self.df_astronomical.columns)} kolumn")
        return self.df_astronomical

    def preprocess_data(self):
        """Przetwarza dane do formatu ML"""
        logger.info("🔧 Przetwarzanie danych dla ML...")

        df = self.df_astronomical.copy()

        # Konwersja dat
        df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
        df['year'] = df['date_parsed'].dt.year
        df['month'] = df['date_parsed'].dt.month
        df['day'] = df['date_parsed'].dt.day

        # Kodowanie kategorii
        self.encoders['subcategory'] = LabelEncoder()
        df['subcategory_encoded'] = self.encoders['subcategory'].fit_transform(df['subcategory'].fillna('UNKNOWN'))

        self.encoders['source'] = LabelEncoder()
        df['source_encoded'] = self.encoders['source'].fit_transform(df['source'].fillna('UNKNOWN'))

        # Numeryczne cechy
        numeric_features = ['julian_day', 'year', 'month', 'day']
        meta_numeric_cols = [col for col in df.columns if col.startswith('meta_') and df[col].dtype in ['int64', 'float64']]
        numeric_features.extend(meta_numeric_cols)

        # Skalowanie cech numerycznych
        self.scalers['features'] = StandardScaler()
        df_numeric = df[numeric_features].fillna(0)
        df_scaled = pd.DataFrame(
            self.scalers['features'].fit_transform(df_numeric),
            columns=[f'{col}_scaled' for col in numeric_features]
        )

        # Połącz dane
        df_processed = pd.concat([df, df_scaled], axis=1)

        logger.info(f"✅ Dane przetworzone: {len(df_processed)} rekordów")
        logger.info(f"📊 Kategorie: {len(df['subcategory'].unique())}")
        logger.info(f"📡 Źródła: {len(df['source'].unique())}")

        return df_processed

    def train_astronomical_models(self):
        """Trenuje modele ML na danych astronomicznych"""
        logger.info("🤖 Trening modeli ML na danych astronomicznych...")

        df = self.preprocess_data()

        # Przygotuj dane do klasyfikacji podkategorii
        features = [col for col in df.columns if col.endswith('_scaled')]
        X = df[features].fillna(0)
        y_subcategory = df['subcategory_encoded']

        # Podziel na train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y_subcategory, test_size=0.2, random_state=42)

        # Model klasyfikacji podkategorii
        logger.info("🎯 Trening klasyfikatora podkategorii...")
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        # Predykcja i ocena
        y_pred = clf.predict(X_test)
        try:
            report = classification_report(y_test, y_pred, target_names=self.encoders['subcategory'].classes_, output_dict=True)
        except ValueError:
            # Jeśli klasy się nie zgadzają, użyj domyślnych nazw
            report = classification_report(y_test, y_pred, output_dict=True)

        self.models['subcategory_classifier'] = {
            'model': clf,
            'accuracy': clf.score(X_test, y_test),
            'classification_report': report
        }

        logger.info(f"🎯 Dokładność klasyfikatora: {clf.score(X_test, y_test):.2f}")
        logger.info(f"📊 Najważniejsze cechy: {clf.feature_importances_[:5]}")

        # Clustering wydarzeń
        logger.info("🎪 Trening modelu klasteryzacji...")
        n_clusters = min(8, len(df) // 100)  # Maksymalnie 8 klastrów
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)

        silhouette = silhouette_score(X, clusters)

        self.models['clustering'] = {
            'model': kmeans,
            'n_clusters': n_clusters,
            'silhouette_score': silhouette,
            'cluster_labels': clusters
        }

        logger.info(f"🎪 Klasteryzacja zakończona: {n_clusters} klastrów, ocena: {silhouette:.3f}")
        # Analiza tekstowa tytułów
        logger.info("📝 Analiza tekstowa tytułów...")
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        title_features = vectorizer.fit_transform(df['title'].fillna(''))

        self.models['text_analysis'] = {
            'vectorizer': vectorizer,
            'title_features': title_features,
            'feature_names': vectorizer.get_feature_names_out()
        }

        logger.info("✅ Modele ML wytrenowane!")
        return self.models

    def generate_insights(self):
        """Generuje insights z danych astronomicznych"""
        logger.info("🔍 Generowanie insights z danych astronomicznych...")

        df = self.df_astronomical.copy()
        
        # Dodaj kolumny dat jeśli nie istnieją
        if 'date_parsed' not in df.columns:
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
        if 'year' not in df.columns:
            df['year'] = df['date_parsed'].dt.year
        if 'month' not in df.columns:
            df['month'] = df['date_parsed'].dt.month
        if 'day' not in df.columns:
            df['day'] = df['date_parsed'].dt.day

        insights = {
            'data_summary': {
                'total_events': len(df),
                'categories': df['category'].value_counts().to_dict(),
                'subcategories': df['subcategory'].value_counts().to_dict(),
                'sources': df['source'].value_counts().to_dict(),
                'epochs': df['epoch'].value_counts().to_dict()
            },
            'temporal_analysis': {
                'year_range': {
                    'min': int(df['year'].min()),
                    'max': int(df['year'].max())
                },
                'events_per_year': df.groupby('year').size().to_dict(),
                'peak_years': df['year'].value_counts().head(10).to_dict()
            },
            'astronomical_patterns': {
                'meteor_showers': len(df[df['subcategory'] == 'METEOR_SHOWER']),
                'solar_events': len(df[df['subcategory'] == 'SOLAR_EVENT']),
                'lunar_phases': len(df[df['subcategory'] == 'LUNAR_PHASE']),
                'comets': len(df[df['subcategory'] == 'COMET'])
            },
            'ml_performance': {
                'subcategory_accuracy': self.models['subcategory_classifier']['accuracy'],
                'clustering_silhouette': self.models['clustering']['silhouette_score'],
                'n_clusters': self.models['clustering']['n_clusters']
            }
        }

        # Zapisz insights
        with open('astronomical_ml_insights.json', 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)

        logger.info("💾 Insights zapisane do astronomical_ml_insights.json")
        return insights

    def create_visualizations(self):
        """Tworzy wizualizacje danych astronomicznych"""
        logger.info("📊 Tworzenie wizualizacji...")

        df = self.df_astronomical.copy()
        
        # Dodaj kolumny dat jeśli nie istnieją
        if 'date_parsed' not in df.columns:
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
        if 'year' not in df.columns:
            df['year'] = df['date_parsed'].dt.year

        # Wykres kategorii
        plt.figure(figsize=(12, 6))
        df['subcategory'].value_counts().head(10).plot(kind='bar')
        plt.title('Top 10 Podkategorii Wydarzeń Astronomicznych')
        plt.xlabel('Podkategoria')
        plt.ylabel('Liczba wydarzeń')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('astronomical_categories.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Wykres temporalny
        plt.figure(figsize=(14, 6))
        yearly_counts = df.groupby('year').size()
        yearly_counts.plot()
        plt.title('Wydarzenia Astronomiczne w Czasie')
        plt.xlabel('Rok')
        plt.ylabel('Liczba wydarzeń')
        plt.tight_layout()
        plt.savefig('astronomical_timeline.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Wykres źródeł
        plt.figure(figsize=(10, 6))
        df['source'].value_counts().head(10).plot(kind='pie', autopct='%1.1f%%')
        plt.title('Rozkład Źródeł Danych Astronomicznych')
        plt.tight_layout()
        plt.savefig('astronomical_sources.png', dpi=300, bbox_inches='tight')
        plt.close()

        logger.info("✅ Wizualizacje utworzone!")

    def run_full_integration(self):
        """Uruchamia pełną integrację danych astronomicznych z ML"""
        logger.info("🚀 ROZPOCZYNAM PEŁNĄ INTEGRACJĘ DANYCH ASTRONOMICZNYCH Z ML!")
        logger.info("=" * 80)

        # 1. Załaduj dane
        total_events = self.load_all_astronomical_data()

        # 2. Konwertuj na DataFrame
        self.convert_to_dataframe()

        # 3. Przetwórz dane
        self.preprocess_data()

        # 4. Trenuj modele
        self.train_astronomical_models()

        # 5. Generuj insights
        insights = self.generate_insights()

        # 6. Utwórz wizualizacje
        self.create_visualizations()

        logger.info("🎯 INTEGRACJA DANYCH ASTRONOMICZNYCH Z ML ZAKOŃCZONA!")
        logger.info(f"💎 {total_events} wydarzeń astronomicznych dodanych do systemu ML")
        logger.info("📁 Pliki wyjściowe:")
        logger.info("   • astronomical_ml_insights.json")
        logger.info("   • astronomical_categories.png")
        logger.info("   • astronomical_timeline.png")
        logger.info("   • astronomical_sources.png")

        return insights

def main():
    """Główna funkcja"""
    integrator = AstronomicalMLIntegrator()
    insights = integrator.run_full_integration()

    # Wyświetl podsumowanie
    print("\n" + "="*80)
    print("🎯 PODSUMOWANIE INTEGRACJI DANYCH ASTRONOMICZNYCH Z ML")
    print("="*80)
    print(f"📊 Wydarzenia: {insights['data_summary']['total_events']:,}")
    print(f"🎯 Dokładność klasyfikacji: {insights['ml_performance']['subcategory_accuracy']:.1%}")
    print(f"🎪 Liczba klastrów: {insights['ml_performance']['n_clusters']}")
    print(f"⭐ Ocena klasteryzacji: {insights['ml_performance']['clustering_silhouette']:.3f}")
    print("\n🏆 TOP PODKATEGORIE:")
    for cat, count in list(insights['data_summary']['subcategories'].items())[:5]:
        print(f"   • {cat}: {count:,}")

if __name__ == "__main__":
    main()