#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jd_zero_ml_learner.py
---------------------
Model ML uczący się od dnia JD 0 - pełnej ery astronomicznej
Analizuje wzorce astronomiczne od początku czasu Julianskiego
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, silhouette_score, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JDZeroMLLearner:
    """
    Model ML uczący się od dnia JD 0 - pełnej ery astronomicznej
    """

    def __init__(self):
        self.astronomical_data = []
        self.df_astronomical = None
        self.models = {}
        self.encoders = {}
        self.scalers = {}
        self.jd_range = {'min': float('inf'), 'max': float('-inf')}

    def load_complete_astronomical_history(self):
        """Ładuje kompletną historię astronomiczną od JD 0"""
        logger.info("🌟 ŁADOWANIE KOMPLETNEJ HISTORII ASTRONOMICZNEJ OD JD 0!")

        astronomical_files = [
            'astronomical_prehistoria.json',           # JD 0 - początek ery
            'astronomical_antyk_wczesny.json',         # Starożytność wczesna
            'astronomical_antyk_późny.json',           # Starożytność późna
            'astronomical_wczesne_średniowiecze.json', # Wczesne średniowiecze
            'astronomical_wysokie_średniowiecze.json', # Wysokie średniowiecze
            'astronomical_nowożytność.json',           # Nowożytność
            'astronomical_wiek_xix.json',              # XIX wiek
            'astronomical_współczesność.json',         # Współczesność
            # Dodatkowe pliki miesięczne dla pełniejszego pokrycia
            'astronomical_events_sierpień_2024.json',
            'astronomical_events_wrzesień_2024.json',
            'astronomical_events_październik_2024.json',
            'astronomical_events_listopad_2024.json'
        ]

        total_events = 0

        for file_name in astronomical_files:
            file_path = Path(file_name)
            if file_path.exists():
                try:
                    logger.info(f"📖 Ładowanie od JD 0: {file_name}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Wyciągnij wydarzenia z różnych struktur
                    events = []
                    if 'results' in data:
                        for epoch_key, epoch_events in data['results'].items():
                            if isinstance(epoch_events, list):
                                events.extend(epoch_events)
                    elif isinstance(data, list):
                        events = data

                    # Aktualizuj zakres JD
                    for event in events:
                        if 'julian_day' in event:
                            jd = event['julian_day']
                            self.jd_range['min'] = min(self.jd_range['min'], jd)
                            self.jd_range['max'] = max(self.jd_range['max'], jd)

                    self.astronomical_data.extend(events)
                    logger.info(f"✅ {file_name}: {len(events)} wydarzeń (JD: {min([e.get('julian_day', 0) for e in events]):.0f} - {max([e.get('julian_day', 0) for e in events]):.0f})")
                    total_events += len(events)

                except Exception as e:
                    logger.error(f"❌ Błąd ładowania {file_name}: {e}")
            else:
                logger.warning(f"⚠️ Plik nie istnieje: {file_name}")

        logger.info(f"🎯 Łącznie załadowano: {total_events} wydarzeń astronomicznych")
        logger.info(f"📅 Zakres JD: {self.jd_range['min']:.0f} - {self.jd_range['max']:.0f} ({self.jd_range['max'] - self.jd_range['min']:.0f} dni ery astronomicznej)")
        return total_events

    def convert_to_jd_centric_dataframe(self):
        """Konwertuje dane na DataFrame skupiający się na JD"""
        logger.info("🔄 Konwersja na DataFrame z naciskiem na JD...")

        records = []
        for event in self.astronomical_data:
            jd = event.get('julian_day', 0)

            record = {
                'id': event.get('id', ''),
                'title': event.get('title', ''),
                'date': event.get('date', ''),
                'julian_day': jd,
                'category': event.get('category', 'ASTRONOMY'),
                'subcategory': event.get('subcategory', ''),
                'source': event.get('source', ''),
                'content': event.get('content', ''),
                'epoch': event.get('epoch', ''),
                'epoch_period': event.get('epoch_period', ''),
            }

            # Dodaj metadane astronomiczne
            metadata = event.get('metadata', {})
            for key, value in metadata.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    record[f'meta_{key}'] = value
                elif isinstance(value, str):
                    record[f'meta_{key}'] = value

            # Dodaj cechy czasowe oparte na JD
            record.update({
                'jd_millennia': jd / 365250,  # JD w tysiącleciach
                'jd_centuries': jd / 36525,   # JD w wiekach
                'jd_years': jd / 365.25,      # JD w latach
                'jd_cycle_19y': jd % (19 * 365.25),  # Cykl Metona (19 lat)
                'jd_cycle_18y': jd % (18.61 * 365.25),  # Cykl Saros (18.6 lat)
                'jd_seasonal': jd % 365.25,   # Cykl sezonowy
                'jd_lunar': jd % 29.53,       # Cykl księżycowy
            })

            records.append(record)

        self.df_astronomical = pd.DataFrame(records)
        logger.info(f"✅ JD-centric DataFrame utworzony: {len(self.df_astronomical)} wierszy")
        logger.info(f"📊 Zakres JD: {self.df_astronomical['julian_day'].min():.0f} - {self.df_astronomical['julian_day'].max():.0f}")
        return self.df_astronomical

    def preprocess_jd_data(self):
        """Przetwarza dane z naciskiem na cykle JD"""
        logger.info("🔧 Przetwarzanie danych z cyklami JD...")

        df = self.df_astronomical.copy()

        # Konwersja dat (jeśli dostępne)
        df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
        df['year'] = df['date_parsed'].dt.year.fillna(0).astype(int)
        df['month'] = df['date_parsed'].dt.month.fillna(1).astype(int)
        df['day'] = df['date_parsed'].dt.day.fillna(1).astype(int)

        # Kodowanie kategorii
        self.encoders['subcategory'] = LabelEncoder()
        df['subcategory_encoded'] = self.encoders['subcategory'].fit_transform(df['subcategory'].fillna('UNKNOWN'))

        self.encoders['source'] = LabelEncoder()
        df['source_encoded'] = self.encoders['source'].fit_transform(df['source'].fillna('UNKNOWN'))

        self.encoders['epoch'] = LabelEncoder()
        df['epoch_encoded'] = self.encoders['epoch'].fit_transform(df['epoch'].fillna('UNKNOWN'))

        # Cechy numeryczne skupiające się na JD
        jd_features = [
            'julian_day', 'jd_millennia', 'jd_centuries', 'jd_years',
            'jd_cycle_19y', 'jd_cycle_18y', 'jd_seasonal', 'jd_lunar'
        ]

        # Metadane numeryczne
        meta_numeric_cols = [col for col in df.columns if col.startswith('meta_') and df[col].dtype in ['int64', 'float64']]
        jd_features.extend(meta_numeric_cols)

        # Skalowanie cech JD
        self.scalers['jd_features'] = StandardScaler()
        df_jd = df[jd_features].fillna(0)
        df_jd_scaled = pd.DataFrame(
            self.scalers['jd_features'].fit_transform(df_jd),
            columns=[f'{col}_scaled' for col in jd_features]
        )

        # Połącz dane
        df_processed = pd.concat([df, df_jd_scaled], axis=1)

        logger.info(f"✅ Dane JD przetworzone: {len(df_processed)} rekordów")
        logger.info(f"📊 Kategorie: {len(df['subcategory'].unique())}")
        logger.info(f"📅 Epoki: {len(df['epoch'].unique())}")
        logger.info(f"📡 Źródła: {len(df['source'].unique())}")

        return df_processed

    def train_jd_centric_models(self):
        """Trenuje modele ML skupiające się na cyklach JD"""
        logger.info("🤖 Trening modeli ML skupiających się na cyklach JD...")

        df = self.preprocess_jd_data()

        # Cechy skupiające się na JD
        jd_features = [col for col in df.columns if col.endswith('_scaled') and 'jd_' in col]

        # 1. Klasyfikacja podkategorii na podstawie cykli JD
        logger.info("🎯 Trening klasyfikatora podkategorii (JD-centric)...")
        X = df[jd_features].fillna(0)
        y_subcategory = df['subcategory_encoded']

        X_train, X_test, y_train, y_test = train_test_split(X, y_subcategory, test_size=0.2, random_state=42)

        clf = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=20)
        clf.fit(X_train, y_train)

        accuracy = clf.score(X_test, y_test)
        y_pred = clf.predict(X_test)

        try:
            report = classification_report(y_test, y_pred, target_names=self.encoders['subcategory'].classes_, output_dict=True)
        except:
            report = classification_report(y_test, y_pred, output_dict=True)

        self.models['jd_subcategory_classifier'] = {
            'model': clf,
            'accuracy': accuracy,
            'classification_report': report,
            'feature_importance': dict(zip(jd_features, clf.feature_importances_))
        }

        logger.info(f"🎯 Dokładność klasyfikatora JD: {accuracy:.4f}")

        # 2. Predykcja epoki na podstawie JD
        logger.info("📅 Trening predyktora epoki na podstawie JD...")
        y_epoch = df['epoch_encoded']
        X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(X, y_epoch, test_size=0.2, random_state=42)

        epoch_clf = RandomForestClassifier(n_estimators=150, random_state=42)
        epoch_clf.fit(X_train_e, y_train_e)

        epoch_accuracy = epoch_clf.score(X_test_e, y_test_e)

        self.models['jd_epoch_predictor'] = {
            'model': epoch_clf,
            'accuracy': epoch_accuracy
        }

        logger.info(f"📅 Dokładność predyktora epoki: {epoch_accuracy:.4f}")

        # 3. Klasteryzacja wydarzeń w przestrzeni JD
        logger.info("🎪 Klasteryzacja w przestrzeni JD...")
        n_clusters = min(12, len(df) // 500)  # Więcej klastrów dla dłuższej historii
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)

        silhouette = silhouette_score(X, clusters)

        self.models['jd_clustering'] = {
            'model': kmeans,
            'n_clusters': n_clusters,
            'silhouette_score': silhouette,
            'cluster_labels': clusters,
            'cluster_centers_jd': kmeans.cluster_centers_[:, 0]  # JD coordinates of centers
        }

        logger.info(f"🎪 Klasteryzacja JD: {n_clusters} klastrów, ocena: {silhouette:.4f}")

        # 4. Analiza cykli astronomicznych
        logger.info("🔄 Analiza cykli astronomicznych...")
        cycle_features = ['jd_cycle_19y_scaled', 'jd_cycle_18y_scaled', 'jd_seasonal_scaled', 'jd_lunar_scaled']

        if all(col in df.columns for col in cycle_features):
            X_cycles = df[cycle_features].fillna(0)

            # Predykcja typu wydarzenia na podstawie cyklu
            cycle_clf = RandomForestClassifier(n_estimators=100, random_state=42)
            cycle_clf.fit(X_train, y_subcategory)

            self.models['cycle_predictor'] = {
                'model': cycle_clf,
                'cycle_accuracy': cycle_clf.score(X_test, y_subcategory),
                'cycle_features': cycle_features
            }

            logger.info(f"🔄 Dokładność predyktora cykli: {cycle_clf.score(X_test, y_subcategory):.4f}")

        logger.info("✅ Modele JD-centric wytrenowane!")
        return self.models

    def generate_jd_insights(self):
        """Generuje insights skupiające się na pełnej historii JD"""
        logger.info("🔍 Generowanie insights z pełnej historii JD...")

        df = self.df_astronomical.copy()

        # Analiza rozkładu wydarzeń w czasie JD
        jd_bins = pd.cut(df['julian_day'],
                        bins=[0, 100000, 500000, 1000000, 1500000, 2000000, float('inf')],
                        labels=['Prehistory', 'Ancient', 'Medieval', 'Renaissance', 'Modern', 'Contemporary'])

        insights = {
            'jd_range': {
                'min_jd': float(self.jd_range['min']),
                'max_jd': float(self.jd_range['max']),
                'span_days': float(self.jd_range['max'] - self.jd_range['min']),
                'span_years': float((self.jd_range['max'] - self.jd_range['min']) / 365.25),
                'span_millennia': float((self.jd_range['max'] - self.jd_range['min']) / 365250)
            },
            'data_summary': {
                'total_events': len(df),
                'categories': df['category'].value_counts().to_dict(),
                'subcategories': df['subcategory'].value_counts().to_dict(),
                'sources': df['source'].value_counts().to_dict(),
                'epochs': df['epoch'].value_counts().to_dict()
            },
            'temporal_distribution': {
                'events_by_jd_period': jd_bins.value_counts().to_dict(),
                'peak_jd_periods': jd_bins.value_counts().head(3).to_dict()
            },
            'astronomical_cycles': {
                'lunar_cycles_covered': float(self.jd_range['max'] - self.jd_range['min']) / 29.53,
                'solar_cycles_covered': float(self.jd_range['max'] - self.jd_range['min']) / 365.25,
                'metonic_cycles_covered': float(self.jd_range['max'] - self.jd_range['min']) / (19 * 365.25),
                'saros_cycles_covered': float(self.jd_range['max'] - self.jd_range['min']) / (18.61 * 365.25)
            },
            'ml_performance': {
                'jd_subcategory_accuracy': self.models['jd_subcategory_classifier']['accuracy'],
                'jd_epoch_accuracy': self.models['jd_epoch_predictor']['accuracy'],
                'jd_clustering_silhouette': self.models['jd_clustering']['silhouette_score'],
                'jd_n_clusters': self.models['jd_clustering']['n_clusters']
            }
        }

        # Zapisz insights
        with open('jd_zero_ml_insights.json', 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)

        logger.info("💾 JD insights zapisane do jd_zero_ml_insights.json")
        return insights

    def create_jd_visualizations(self):
        """Tworzy wizualizacje skupiające się na JD"""
        logger.info("📊 Tworzenie wizualizacji JD...")

        df = self.df_astronomical.copy()

        # Wykres wydarzeń w czasie JD
        plt.figure(figsize=(16, 8))
        plt.scatter(df['julian_day'], range(len(df)), alpha=0.6, s=2)
        plt.title('Wydarzenia Astronomiczne w Pełnej Skali Czasu JD (od JD 0)', fontsize=14)
        plt.xlabel('Dzień Julianski (JD)')
        plt.ylabel('Indeks Wydarzenia')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('jd_zero_timeline.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Wykres gęstości wydarzeń w JD
        plt.figure(figsize=(14, 6))
        plt.hist(df['julian_day'], bins=50, alpha=0.7, edgecolor='black')
        plt.title('Rozkład Wydarzeń Astronomicznych w Czasie JD', fontsize=14)
        plt.xlabel('Dzień Julianski (JD)')
        plt.ylabel('Liczba Wydarzeń')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('jd_zero_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()

        # Wykres cykli astronomicznych
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Cykle Astronomiczne w Pełnej Historii JD', fontsize=16)

        # Cykl Metona (19 lat)
        axes[0,0].scatter(df['jd_cycle_19y'], df['julian_day'], alpha=0.5, s=1)
        axes[0,0].set_title('Cykl Metona (19 lat)')
        axes[0,0].set_xlabel('Pozycja w cyklu (dni)')
        axes[0,0].set_ylabel('JD')

        # Cykl Saros (18.6 lat)
        axes[0,1].scatter(df['jd_cycle_18y'], df['julian_day'], alpha=0.5, s=1)
        axes[0,1].set_title('Cykl Saros (18.6 lat)')
        axes[0,1].set_xlabel('Pozycja w cyklu (dni)')
        axes[0,1].set_ylabel('JD')

        # Cykl sezonowy
        axes[1,0].scatter(df['jd_seasonal'], df['julian_day'], alpha=0.5, s=1)
        axes[1,0].set_title('Cykl Sezonowy (365.25 dni)')
        axes[1,0].set_xlabel('Pozycja w cyklu (dni)')
        axes[1,0].set_ylabel('JD')

        # Cykl księżycowy
        axes[1,1].scatter(df['jd_lunar'], df['julian_day'], alpha=0.5, s=1)
        axes[1,1].set_title('Cykl Księżycowy (29.53 dni)')
        axes[1,1].set_xlabel('Pozycja w cyklu (dni)')
        axes[1,1].set_ylabel('JD')

        plt.tight_layout()
        plt.savefig('jd_zero_cycles.png', dpi=300, bbox_inches='tight')
        plt.close()

        logger.info("✅ Wizualizacje JD utworzone!")

    def run_jd_zero_learning(self):
        """Uruchamia pełne uczenie się od JD 0"""
        logger.info("🚀 ROZPOCZYNAM UCZENIE SIĘ OD DNIA JD 0!")
        logger.info("=" * 80)
        logger.info("🤖 Model będzie się uczył wzorców astronomicznych")
        logger.info("📅 od samego początku ery Julianskiej")
        logger.info("=" * 80)

        # 1. Załaduj kompletną historię
        total_events = self.load_complete_astronomical_history()

        # 2. Konwertuj na JD-centric DataFrame
        self.convert_to_jd_centric_dataframe()

        # 3. Przetwórz dane z naciskiem na JD
        self.preprocess_jd_data()

        # 4. Trenuj JD-centric modele
        self.train_jd_centric_models()

        # 5. Generuj JD insights
        insights = self.generate_jd_insights()

        # 6. Utwórz JD wizualizacje
        self.create_jd_visualizations()

        logger.info("🎯 UCZENIE SIĘ OD JD 0 ZAKOŃCZONE!")
        logger.info(f"💎 {total_events} wydarzeń od początku ery astronomicznej")
        logger.info(f"📅 Zakres JD: {self.jd_range['min']:.0f} - {self.jd_range['max']:.0f}")
        logger.info("📁 Pliki wyjściowe:")
        logger.info("   • jd_zero_ml_insights.json")
        logger.info("   • jd_zero_timeline.png")
        logger.info("   • jd_zero_distribution.png")
        logger.info("   • jd_zero_cycles.png")

        return insights

def main():
    """Główna funkcja"""
    learner = JDZeroMLLearner()
    insights = learner.run_jd_zero_learning()

    # Wyświetl podsumowanie
    print("\n" + "="*80)
    print("🎯 PODSUMOWANIE UCZENIA SIĘ OD JD 0")
    print("="*80)
    print(f"📊 Wydarzenia: {insights['data_summary']['total_events']:,}")
    print(f"📅 Zakres JD: {insights['jd_range']['min_jd']:,.0f} - {insights['jd_range']['max_jd']:,.0f}")
    print(f"⏰ Czas trwania: {insights['jd_range']['span_years']:,.0f} lat ({insights['jd_range']['span_millennia']:.1f} tysiącleci)")
    print(f"🎯 Dokładność klasyfikacji: {insights['ml_performance']['jd_subcategory_accuracy']:.4f}")
    print(f"📅 Dokładność epoki: {insights['ml_performance']['jd_epoch_accuracy']:.4f}")
    print(f"🎪 Klasteryzacja: {insights['ml_performance']['jd_n_clusters']} klastrów (ocena: {insights['ml_performance']['jd_clustering_silhouette']:.4f})")

    print("\n🔄 Pokryte cykle astronomiczne:")
    print(f"   • Księżycowe: {insights['astronomical_cycles']['lunar_cycles_covered']:,.0f} cykli")
    print(f"   • Słoneczne: {insights['astronomical_cycles']['solar_cycles_covered']:,.0f} cykli")
    print(f"   • Metonic: {insights['astronomical_cycles']['metonic_cycles_covered']:.1f} cykli")
    print(f"   • Saros: {insights['astronomical_cycles']['saros_cycles_covered']:.1f} cykli")

if __name__ == "__main__":
    main()