#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jd_zero_light_learner.py
-------------------------
Lekki model ML uczący się od dnia JD 0 - wzorców astronomicznych
Optymalizowany dla pełnej ery Julianskiej z szybszym treningiem
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JDZeroLightLearner:
    """
    Lekki model ML uczący się od dnia JD 0 z optymalizacją wydajności
    """

    def __init__(self):
        self.astronomical_data = []
        self.df_astronomical = None
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.jd_range = {'min': float('inf'), 'max': float('-inf')}

    def load_jd_history_sample(self):
        """Ładuje próbkę historii astronomicznej od JD 0 z optymalizacją"""
        logger.info("🌟 ŁADOWANIE HISTORII ASTRONOMICZNEJ OD JD 0 (OPTymalizowane)!")

        astronomical_files = [
            'astronomical_prehistoria.json',           # JD 0 - początek ery
            'astronomical_antyk_wczesny.json',         # Starożytność wczesna
            'astronomical_antyk_późny.json',           # Starożytność późna
            'astronomical_wczesne_średniowiecze.json', # Wczesne średniowiecze
            'astronomical_wysokie_średniowiecze.json', # Wysokie średniowiecze
            'astronomical_nowożytność.json',           # Nowożytność
            'astronomical_wiek_xix.json',              # XIX wiek
            'astronomical_współczesność.json'          # Współczesność
        ]

        total_events = 0
        max_per_epoch = 2000  # Limit wydarzeń na epokę dla optymalizacji

        for file_name in astronomical_files:
            file_path = Path(file_name)
            if file_path.exists():
                try:
                    logger.info(f"📖 Ładowanie: {file_name}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    events = []
                    if 'results' in data:
                        for epoch_key, epoch_events in data['results'].items():
                            if isinstance(epoch_events, list):
                                # Ogranicz liczbę wydarzeń na epokę dla optymalizacji
                                limited_events = epoch_events[:max_per_epoch] if len(epoch_events) > max_per_epoch else epoch_events
                                events.extend(limited_events)

                    # Aktualizuj zakres JD
                    for event in events:
                        if 'julian_day' in event:
                            jd = event['julian_day']
                            self.jd_range['min'] = min(self.jd_range['min'], jd)
                            self.jd_range['max'] = max(self.jd_range['max'], jd)

                    self.astronomical_data.extend(events)
                    logger.info(f"✅ {file_name}: {len(events)} wydarzeń (limit: {max_per_epoch})")
                    total_events += len(events)

                except Exception as e:
                    logger.error(f"❌ Błąd ładowania {file_name}: {e}")
            else:
                logger.warning(f"⚠️ Plik nie istnieje: {file_name}")

        logger.info(f"🎯 Łącznie załadowano: {total_events} wydarzeń astronomicznych")
        logger.info(f"📅 Zakres JD: {self.jd_range['min']:.0f} - {self.jd_range['max']:.0f}")
        return total_events

    def create_jd_dataframe(self):
        """Tworzy DataFrame skupiający się na JD"""
        logger.info("🔄 Tworzenie DataFrame JD...")

        records = []
        for event in self.astronomical_data:
            jd = event.get('julian_day', 0)

            record = {
                'julian_day': jd,
                'subcategory': event.get('subcategory', ''),
                'source': event.get('source', ''),
                'epoch': event.get('epoch', ''),
                # Cechy cyklu astronomicznego
                'jd_years': jd / 365.25,
                'jd_cycle_solar': jd % 365.25,      # Cykl słoneczny
                'jd_cycle_lunar': jd % 29.53,       # Cykl księżycowy
                'jd_cycle_metonic': jd % (19 * 365.25),  # Cykl Metona
                'jd_millennia': jd / 365250,        # W tysiącleciach
            }

            records.append(record)

        self.df_astronomical = pd.DataFrame(records)
        logger.info(f"✅ DataFrame JD utworzony: {len(self.df_astronomical)} wierszy")
        return self.df_astronomical

    def preprocess_jd_data_light(self):
        """Lekkie przetwarzanie danych JD"""
        logger.info("🔧 Lekkie przetwarzanie danych JD...")

        df = self.df_astronomical.copy()

        # Kodowanie kategorii
        self.encoders['subcategory'] = LabelEncoder()
        df['subcategory_encoded'] = self.encoders['subcategory'].fit_transform(df['subcategory'].fillna('UNKNOWN'))

        self.encoders['source'] = LabelEncoder()
        df['source_encoded'] = self.encoders['source'].fit_transform(df['source'].fillna('UNKNOWN'))

        # Skalowanie cech JD
        jd_features = ['julian_day', 'jd_years', 'jd_cycle_solar', 'jd_cycle_lunar', 'jd_cycle_metonic', 'jd_millennia']
        self.scalers['jd_features'] = StandardScaler()
        df_jd_scaled = pd.DataFrame(
            self.scalers['jd_features'].fit_transform(df[jd_features]),
            columns=[f'{col}_scaled' for col in jd_features]
        )

        df_processed = pd.concat([df, df_jd_scaled], axis=1)

        logger.info(f"✅ Dane przetworzone: {len(df_processed)} rekordów")
        logger.info(f"📊 Kategorie: {len(df['subcategory'].unique())}")
        logger.info(f"📡 Źródła: {len(df['source'].unique())}")

        return df_processed

    def train_light_jd_models(self):
        """Trenuje lekkie modele JD z optymalizacją"""
        logger.info("🤖 Trening lekkich modeli JD...")

        df = self.preprocess_jd_data_light()
        jd_features = [col for col in df.columns if col.endswith('_scaled')]

        # Podziel dane na mniejsze partie dla treningu
        sample_size = min(10000, len(df))  # Maksymalnie 10k próbek
        df_sample = df.sample(n=sample_size, random_state=42)

        X = df_sample[jd_features]
        y_subcategory = df_sample['subcategory_encoded']

        # Podział na train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y_subcategory, test_size=0.3, random_state=42)

        # Lekki klasyfikator
        logger.info("🎯 Trening lekkiego klasyfikatora...")
        clf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
        clf.fit(X_train, y_train)

        accuracy = clf.score(X_test, y_test)
        logger.info(f"🎯 Dokładność klasyfikatora: {accuracy:.4f}")

        # Lekka klasteryzacja
        logger.info("🎪 Lekka klasteryzacja...")
        n_clusters = 6  # Mniej klastrów dla optymalizacji
        kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=1000)
        clusters = kmeans.fit_predict(X)

        silhouette = silhouette_score(X, clusters)
        logger.info(f"🎪 Klasteryzacja: {n_clusters} klastrów, ocena: {silhouette:.4f}")

        self.models = {
            'jd_classifier': {
                'model': clf,
                'accuracy': accuracy,
                'feature_importance': dict(zip(jd_features, clf.feature_importances_))
            },
            'jd_clustering': {
                'model': kmeans,
                'n_clusters': n_clusters,
                'silhouette_score': silhouette,
                'cluster_labels': clusters
            }
        }

        logger.info("✅ Lekkie modele JD wytrenowane!")
        return self.models

    def generate_jd_insights_light(self):
        """Generuje lekkie insights JD"""
        logger.info("🔍 Generowanie insights JD...")

        df = self.df_astronomical.copy()

        insights = {
            'jd_range': {
                'min_jd': float(self.jd_range['min']),
                'max_jd': float(self.jd_range['max']),
                'span_days': float(self.jd_range['max'] - self.jd_range['min']),
                'span_years': float((self.jd_range['max'] - self.jd_range['min']) / 365.25)
            },
            'data_summary': {
                'total_events': len(df),
                'subcategories': df['subcategory'].value_counts().to_dict(),
                'sources': df['source'].value_counts().to_dict(),
                'epochs': df['epoch'].value_counts().to_dict()
            },
            'astronomical_cycles': {
                'solar_cycles': float(self.jd_range['max'] - self.jd_range['min']) / 365.25,
                'lunar_cycles': float(self.jd_range['max'] - self.jd_range['min']) / 29.53,
                'metonic_cycles': float(self.jd_range['max'] - self.jd_range['min']) / (19 * 365.25)
            },
            'ml_performance': {
                'classifier_accuracy': self.models['jd_classifier']['accuracy'],
                'clustering_silhouette': self.models['jd_clustering']['silhouette_score'],
                'n_clusters': self.models['jd_clustering']['n_clusters']
            }
        }

        with open('jd_zero_light_insights.json', 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)

        logger.info("💾 Insights zapisane do jd_zero_light_insights.json")
        return insights

    def create_jd_visualizations_light(self):
        """Tworzy lekkie wizualizacje JD"""
        logger.info("📊 Tworzenie wizualizacji JD...")

        df = self.df_astronomical.copy()

        # Wykres rozkładu wydarzeń w JD
        plt.figure(figsize=(12, 6))
        plt.hist(df['julian_day'], bins=30, alpha=0.7, edgecolor='black')
        plt.title('Rozkład Wydarzeń Astronomicznych od JD 0', fontsize=14)
        plt.xlabel('Dzień Julianski (JD)')
        plt.ylabel('Liczba Wydarzeń')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('jd_zero_light_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Wykres cykli
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle('Cykle Astronomiczne od JD 0', fontsize=16)

        axes[0].scatter(df['jd_cycle_solar'], df['julian_day'], alpha=0.3, s=1)
        axes[0].set_title('Cykl Słoneczny (365.25 dni)')
        axes[0].set_xlabel('Pozycja w cyklu')
        axes[0].set_ylabel('JD')

        axes[1].scatter(df['jd_cycle_lunar'], df['julian_day'], alpha=0.3, s=1)
        axes[1].set_title('Cykl Księżycowy (29.53 dni)')
        axes[1].set_xlabel('Pozycja w cyklu')
        axes[1].set_ylabel('JD')

        axes[2].scatter(df['jd_cycle_metonic'], df['julian_day'], alpha=0.3, s=1)
        axes[2].set_title('Cykl Metona (19 lat)')
        axes[2].set_xlabel('Pozycja w cyklu')
        axes[2].set_ylabel('JD')

        plt.tight_layout()
        plt.savefig('jd_zero_light_cycles.png', dpi=300, bbox_inches='tight')
        plt.close()

        logger.info("✅ Wizualizacje JD utworzone!")

    def run_light_jd_learning(self):
        """Uruchamia lekkie uczenie się od JD 0"""
        logger.info("🚀 ROZPOCZYNAM LEKKIE UCZENIE SIĘ OD JD 0!")
        logger.info("=" * 80)

        # 1. Załaduj historię z optymalizacją
        total_events = self.load_jd_history_sample()

        # 2. Utwórz DataFrame JD
        self.create_jd_dataframe()

        # 3. Przetwórz dane lekko
        self.preprocess_jd_data_light()

        # 4. Trenuj lekkie modele
        self.train_light_jd_models()

        # 5. Generuj insights
        insights = self.generate_jd_insights_light()

        # 6. Utwórz wizualizacje
        self.create_jd_visualizations_light()

        logger.info("🎯 LEKKIE UCZENIE SIĘ OD JD 0 ZAKOŃCZONE!")
        logger.info(f"💎 {total_events} wydarzeń od początku ery astronomicznej")
        logger.info(f"📅 Zakres JD: {self.jd_range['min']:.0f} - {self.jd_range['max']:.0f}")
        logger.info("📁 Pliki wyjściowe:")
        logger.info("   • jd_zero_light_insights.json")
        logger.info("   • jd_zero_light_distribution.png")
        logger.info("   • jd_zero_light_cycles.png")

        return insights

def main():
    """Główna funkcja"""
    learner = JDZeroLightLearner()
    insights = learner.run_light_jd_learning()

    print("\n" + "="*80)
    print("🎯 PODSUMOWANIE LEKKIEGO UCZENIA SIĘ OD JD 0")
    print("="*80)
    print(f"📊 Wydarzenia: {insights['data_summary']['total_events']:,}")
    print(f"📅 Zakres JD: {insights['jd_range']['min_jd']:,.0f} - {insights['jd_range']['max_jd']:,.0f}")
    print(f"⏰ Czas trwania: {insights['jd_range']['span_years']:,.0f} lat")
    print(f"🎯 Dokładność klasyfikatora: {insights['ml_performance']['classifier_accuracy']:.4f}")
    print(f"🎪 Klasteryzacja: {insights['ml_performance']['n_clusters']} klastrów (ocena: {insights['ml_performance']['clustering_silhouette']:.4f})")

    print("\n🔄 Pokryte cykle astronomiczne:")
    print(f"   • Słoneczne: {insights['astronomical_cycles']['solar_cycles']:,.0f} cykli")
    print(f"   • Księżycowe: {insights['astronomical_cycles']['lunar_cycles']:,.0f} cykli")
    print(f"   • Metonic: {insights['astronomical_cycles']['metonic_cycles']:.1f} cykli")

if __name__ == "__main__":
    main()