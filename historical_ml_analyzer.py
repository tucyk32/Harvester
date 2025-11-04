#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
historical_ml_analyzer.py
-------------------------
Zaawansowane narzędzie do analizy danych historycznych z użyciem uczenia maszynowego.
Integruje:
- Wikipedia data (już mamy)
- Archiwa naukowe (arXiv, PubMed, JSTOR)
- Dane geologiczne/archeologiczne
- ML do pattern recognition, prediction, correlation analysis

Funkcje ML:
1. NLP - ekstrakcja dat, miejsc, osób z tekstów
2. Time Series Analysis - trendy historyczne
3. Network Analysis - powiązania między wydarzeniami/osobami
4. Clustering - grupowanie podobnych wydarzeń
5. Prediction - przewidywanie na podstawie wzorców historycznych
"""

import pandas as pd
import numpy as np
import requests
import json
import re
from datetime import datetime, timedelta
import time
from pathlib import Path

# ML Libraries
try:
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.neural_network import MLPClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    ML_AVAILABLE = True
except ImportError:
    print("⚠️ Scikit-learn not available. Install with: pip install scikit-learn")
    ML_AVAILABLE = False

try:
    import spacy
    NLP_AVAILABLE = True
except ImportError:
    print("⚠️ SpaCy not available. Install with: pip install spacy")
    NLP_AVAILABLE = False

try:
    import networkx as nx
    NETWORK_AVAILABLE = True
except ImportError:
    print("⚠️ NetworkX not available. Install with: pip install networkx")
    NETWORK_AVAILABLE = False

# Stałe
AM_EPOCH_OFFSET = 1738164.0

class HistoricalMLAnalyzer:
    def __init__(self, data_path: str = None):
        self.data = None
        self.ml_models = {}
        self.nlp_model = None
        self.network = None
        
        if data_path:
            self.load_data(data_path)
        
        self.init_nlp()
    
    def load_data(self, path: str):
        """Ładuje dane z CSV lub JSON"""
        print(f"📊 Ładowanie danych z {path}...")
        
        if path.endswith('.csv'):
            self.data = pd.read_csv(path)
        elif path.endswith('.json'):
            with open(path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                if 'events' in json_data:
                    self.data = pd.DataFrame(json_data['events'])
                else:
                    self.data = pd.DataFrame(json_data)
        
        print(f"✅ Załadowano {len(self.data)} rekordów")
        return self.data
    
    def init_nlp(self):
        """Inicjalizuje model NLP"""
        if not NLP_AVAILABLE:
            return
        
        try:
            # Próba załadowania polskiego modelu
            self.nlp_model = spacy.load("pl_core_news_sm")
            print("✅ Załadowano polski model NLP")
        except OSError:
            try:
                # Fallback na angielski
                self.nlp_model = spacy.load("en_core_web_sm")
                print("✅ Załadowano angielski model NLP")
            except OSError:
                print("⚠️ Brak modeli NLP. Zainstaluj: python -m spacy download pl_core_news_sm")
                self.nlp_model = None
    
    def extract_scientific_papers(self, query: str, source: str = "arxiv", limit: int = 100):
        """Pobiera papers z archiwów naukowych"""
        print(f"🔬 Pobieranie papers z {source}: '{query}'")
        
        papers = []
        
        if source == "arxiv":
            papers = self._fetch_arxiv_papers(query, limit)
        elif source == "pubmed":
            papers = self._fetch_pubmed_papers(query, limit)
        
        # Konwertuj na format timeline
        events = []
        for paper in papers:
            if 'published' in paper:
                try:
                    pub_date = datetime.fromisoformat(paper['published'].replace('Z', ''))
                    jd = self._date_to_jd(pub_date.year, pub_date.month, pub_date.day)
                    am_day = jd - AM_EPOCH_OFFSET
                    
                    events.append({
                        'start_jd': jd,
                        'am_day': am_day,
                        'category': 'SCIENTIFIC',
                        'subcategory': 'publication',
                        'title': paper.get('title', 'Unknown Paper'),
                        'description': paper.get('summary', ''),
                        'authors': paper.get('authors', []),
                        'source': source,
                        'source_url': paper.get('url', ''),
                        'reliability': 5,
                        'year': pub_date.year,
                        'month': pub_date.month,
                        'day': pub_date.day
                    })
                except:
                    continue
        
        print(f"✅ Znaleziono {len(events)} publikacji")
        return events
    
    def _fetch_arxiv_papers(self, query: str, limit: int):
        """Pobiera papers z arXiv"""
        base_url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': limit,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response (simplified)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            papers = []
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace):
                title = entry.find('atom:title', namespace)
                summary = entry.find('atom:summary', namespace)
                published = entry.find('atom:published', namespace)
                
                authors = []
                for author in entry.findall('atom:author', namespace):
                    name = author.find('atom:name', namespace)
                    if name is not None:
                        authors.append(name.text)
                
                papers.append({
                    'title': title.text if title is not None else '',
                    'summary': summary.text if summary is not None else '',
                    'published': published.text if published is not None else '',
                    'authors': authors,
                    'url': f"https://arxiv.org/abs/{entry.find('atom:id', namespace).text.split('/')[-1]}"
                })
            
            return papers
            
        except Exception as e:
            print(f"❌ Błąd arXiv: {e}")
            return []
    
    def _fetch_pubmed_papers(self, query: str, limit: int):
        """Pobiera papers z PubMed (placeholder - wymaga API key)"""
        print("⚠️ PubMed integration wymaga API key")
        return []
    
    def nlp_extract_entities(self, text_column: str = 'text'):
        """Ekstraktuje nazwane jednostki z tekstów"""
        if not self.nlp_model or self.data is None:
            print("❌ Brak modelu NLP lub danych")
            return
        
        # Sprawdź dostępne kolumny tekstowe
        available_text_cols = [col for col in ['text', 'title'] if col in self.data.columns]
        if text_column not in self.data.columns:
            if available_text_cols:
                text_column = available_text_cols[0]
                print(f"⚠️ Używam kolumny '{text_column}' zamiast domyślnej")
            else:
                print("❌ Brak kolumn tekstowych do analizy NLP")
                return
        
        print(f"🧠 Analizuję teksty NLP w kolumnie '{text_column}'...")
        
        entities_data = []
        
        for idx, row in self.data.iterrows():
            text = str(row.get(text_column, ''))
            if len(text) < 10:
                continue
                
            doc = self.nlp_model(text[:1000])  # Limit dla wydajności
            
            entities = {
                'index': idx,
                'persons': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
                'places': [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']],
                'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
                'organizations': [ent.text for ent in doc.ents if ent.label_ == 'ORG']
            }
            entities_data.append(entities)
        
        entities_df = pd.DataFrame(entities_data)
        print(f"✅ Wyekstraktowano jednostki z {len(entities_df)} tekstów")
        
        return entities_df
    
    def cluster_events(self, feature_columns: list = None, n_clusters: int = 10):
        """Grupuje wydarzenia używając ML clustering"""
        if not ML_AVAILABLE or self.data is None:
            print("❌ Brak scikit-learn lub danych")
            return
        
        print(f"🎯 Grupowanie wydarzeń na {n_clusters} klastrów...")
        
        if feature_columns is None:
            # Używaj kolumn które faktycznie istnieją
            available_columns = ['year_abs', 'month', 'day', 'section']
            feature_columns = [col for col in available_columns if col in self.data.columns]
        
        if not feature_columns:
            print("❌ Brak odpowiednich kolumn do clusteringu")
            return
        
        print(f"📊 Używane kolumny: {feature_columns}")
        
        # Przygotuj dane do clusteringu
        data_for_clustering = self.data[feature_columns].copy()
        
        # Encode categorical variables
        for col in data_for_clustering.columns:
            if data_for_clustering[col].dtype == 'object':
                data_for_clustering[col] = pd.Categorical(data_for_clustering[col]).codes
        
        # Handle missing values
        data_for_clustering = data_for_clustering.fillna(-1)
        
        # Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(data_for_clustering)
        
        self.data['cluster'] = clusters
        
        # Analiza klastrów
        cluster_analysis = {}
        for i in range(n_clusters):
            cluster_data = self.data[self.data['cluster'] == i]
            
            # Użyj year_abs jeśli dostępne
            time_col = 'year_abs' if 'year_abs' in cluster_data.columns else 'year'
            time_range = 'N/A'
            if time_col in cluster_data.columns and not cluster_data[time_col].isna().all():
                time_range = f"{cluster_data[time_col].min()}-{cluster_data[time_col].max()}"
            
            cluster_analysis[i] = {
                'size': len(cluster_data),
                'sections': cluster_data['section'].value_counts().to_dict() if 'section' in cluster_data else {},
                'time_range': time_range,
                'sample_titles': cluster_data['title'].head(3).tolist() if 'title' in cluster_data else []
            }
        
        print("✅ Clustering completed!")
        for i, analysis in cluster_analysis.items():
            print(f"Klaster {i}: {analysis['size']} wydarzeń, {analysis['time_range']}")
        
        return cluster_analysis
    
    def time_series_analysis(self, time_column: str = 'year_abs', value_column: str = None):
        """Analiza szeregów czasowych"""
        if self.data is None:
            print("❌ Brak danych")
            return
        
        print(f"📈 Analiza szeregów czasowych: {time_column}")
        
        # Sprawdź czy kolumna istnieje
        if time_column not in self.data.columns:
            print(f"❌ Kolumna {time_column} nie istnieje. Dostępne: {list(self.data.columns)}")
            return
        
        # Usuń wartości NaN z kolumny czasowej
        clean_data = self.data.dropna(subset=[time_column])
        
        # Grupuj po czasie
        if value_column and value_column in clean_data.columns:
            time_series = clean_data.groupby(time_column)[value_column].sum()
        else:
            time_series = clean_data.groupby(time_column).size()
        
        # Podstawowe statystyki
        stats = {
            'mean': time_series.mean(),
            'std': time_series.std(),
            'trend': 'increasing' if time_series.iloc[-1] > time_series.iloc[0] else 'decreasing',
            'peak_year': time_series.idxmax(),
            'peak_value': time_series.max(),
            'total_events': time_series.sum()
        }
        
        print(f"📊 Statystyki szeregu czasowego:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return time_series, stats
    
    def build_network(self, connection_type: str = 'temporal'):
        """Buduje sieć powiązań między wydarzeniami"""
        if not NETWORK_AVAILABLE or self.data is None:
            print("❌ Brak NetworkX lub danych")
            return
        
        print(f"🕸️ Budowanie sieci powiązań: {connection_type}")
        
        self.network = nx.Graph()
        
        # Dodaj węzły (wydarzenia)
        for idx, row in self.data.iterrows():
            self.network.add_node(idx, 
                                title=row.get('title', ''),
                                section=row.get('section', ''),
                                year=row.get('year_abs', 0))
        
        # Dodaj krawędzie na podstawie kryteriów
        if connection_type == 'temporal':
            # Połącz wydarzenia bliskie czasowo
            self._add_temporal_edges(threshold_years=10)
        elif connection_type == 'categorical':
            # Połącz wydarzenia z tej samej sekcji
            self._add_categorical_edges()
        elif connection_type == 'textual':
            # Połącz na podstawie podobieństwa tekstowego
            self._add_textual_edges()
        
        print(f"✅ Sieć zbudowana: {self.network.number_of_nodes()} węzłów, {self.network.number_of_edges()} krawędzi")
        
        # Podstawowe metryki sieci
        if self.network.number_of_edges() > 0:
            metrics = {
                'density': nx.density(self.network),
                'avg_clustering': nx.average_clustering(self.network),
                'connected_components': nx.number_connected_components(self.network)
            }
            print(f"📊 Metryki sieci: {metrics}")
            return metrics
        
        return {}
    
    def _add_temporal_edges(self, threshold_years: int = 10):
        """Dodaje krawędzie między wydarzeniami bliskimi czasowo"""
        year_col = 'year_abs' if 'year_abs' in self.data.columns else 'year'
        
        for i in range(len(self.data)):
            for j in range(i+1, len(self.data)):
                year_i = self.data.iloc[i].get(year_col, 0)
                year_j = self.data.iloc[j].get(year_col, 0)
                
                if abs(year_i - year_j) <= threshold_years:
                    self.network.add_edge(i, j, weight=1.0/(abs(year_i - year_j) + 1))
    
    def _add_categorical_edges(self):
        """Dodaje krawędzie między wydarzeniami z tej samej sekcji"""
        category_col = 'section' if 'section' in self.data.columns else 'category'
        
        if category_col not in self.data.columns:
            print(f"❌ Brak kolumny {category_col} do grupowania")
            return
            
        categories = self.data.groupby(category_col).groups
        
        for category, indices in categories.items():
            indices = list(indices)
            for i in range(len(indices)):
                for j in range(i+1, len(indices)):
                    self.network.add_edge(indices[i], indices[j], weight=1.0)
    
    def _add_textual_edges(self):
        """Dodaje krawędzie na podstawie podobieństwa tekstowego"""
        if not ML_AVAILABLE:
            return
        
        text_col = 'text' if 'text' in self.data.columns else 'title'
        
        # TF-IDF vectorization
        texts = self.data[text_col].fillna('').astype(str)
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Oblicz podobieństwo cosine
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Dodaj krawędzie dla podobnych tekstów
        threshold = 0.3
        for i in range(len(similarity_matrix)):
            for j in range(i+1, len(similarity_matrix)):
                if similarity_matrix[i][j] > threshold:
                    self.network.add_edge(i, j, weight=similarity_matrix[i][j])
    
    def predict_patterns(self, target_column: str = 'section', features: list = None):
        """Przewiduje wzorce używając ML"""
        if not ML_AVAILABLE or self.data is None:
            print("❌ Brak scikit-learn lub danych")
            return
        
        print(f"🔮 Przewidywanie wzorców dla: {target_column}")
        
        if target_column not in self.data.columns:
            print(f"❌ Kolumna {target_column} nie istnieje")
            return
        
        if features is None:
            available_features = ['year_abs', 'month', 'day']
            features = [f for f in available_features if f in self.data.columns]
        
        if not features:
            print("❌ Brak odpowiednich cech do predykcji")
            return
        
        print(f"📊 Używane cechy: {features}")
        
        # Przygotuj dane
        X = self.data[features].copy()
        y = self.data[target_column].copy()
        
        # Handle missing values
        X = X.fillna(0)
        y = y.fillna('UNKNOWN')
        
        # Encode target if categorical
        if y.dtype == 'object':
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            y = le.fit_transform(y)
            self.ml_models['label_encoder'] = le
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model accuracy: {accuracy:.3f}")
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(features, model.feature_importances_))
            print("📊 Feature importance:")
            for feature, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                print(f"  {feature}: {imp:.3f}")
        
        self.ml_models['predictor'] = model
        return model, accuracy
    
    def _date_to_jd(self, year: int, month: int, day: int) -> float:
        """Konwertuje datę na Julian Day"""
        if month <= 2:
            year -= 1
            month += 12
        
        a = year // 100
        if year >= 1583 or (year == 1582 and month >= 10 and day >= 15):
            b = 2 - a + a // 4
        else:
            b = 0
        
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        return jd
    
    def generate_report(self, output_file: str = "ml_analysis_report.json"):
        """Generuje raport z analizy ML"""
        if self.data is None:
            print("❌ Brak danych do analizy")
            return
        
        print(f"📋 Generuję raport analizy ML...")
        
        report = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_events': len(self.data),
                'ml_available': ML_AVAILABLE,
                'nlp_available': NLP_AVAILABLE and self.nlp_model is not None,
                'network_available': NETWORK_AVAILABLE
            },
            'data_summary': {
                'sections': self.data['section'].value_counts().to_dict() if 'section' in self.data else {},
                'time_range': f"{self.data['year_abs'].min()}-{self.data['year_abs'].max()}" if 'year_abs' in self.data else 'N/A',
                'languages': self.data['lang'].value_counts().to_dict() if 'lang' in self.data else {}
            },
            'analyses_performed': []
        }
        
        # Dodaj wyniki analiz jeśli zostały wykonane
        if 'cluster' in self.data.columns:
            report['analyses_performed'].append('clustering')
            report['clustering_results'] = self.data['cluster'].value_counts().to_dict()
        
        if self.network:
            report['analyses_performed'].append('network_analysis')
            report['network_metrics'] = {
                'nodes': self.network.number_of_nodes(),
                'edges': self.network.number_of_edges(),
                'density': nx.density(self.network) if self.network.number_of_edges() > 0 else 0
            }
        
        if self.ml_models:
            report['analyses_performed'].append('machine_learning')
            report['ml_models'] = list(self.ml_models.keys())
        
        # Zapisz raport
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Raport zapisany: {output_file}")
        return report

def main():
    """Demonstracja możliwości systemu"""
    print("🚀 Historical ML Analyzer - Demo")
    print("=" * 50)
    
    # Inicjalizacja
    analyzer = HistoricalMLAnalyzer()
    
    # Załaduj dane z unified pipeline
    unified_file = "unified_output/ml_complete_dataset.csv"
    if Path(unified_file).exists():
        analyzer.load_data(unified_file)
        
        print(f"\n📊 Załadowano {len(analyzer.data)} rekordów z unified pipeline")
        
        # Podstawowa analiza
        print("\n1️⃣ Time Series Analysis:")
        ts_data, ts_stats = analyzer.time_series_analysis()
        
        print("\n2️⃣ Event Clustering:")
        cluster_results = analyzer.cluster_events(n_clusters=5)
        
        print("\n3️⃣ Network Analysis:")
        network_metrics = analyzer.build_network('categorical')
        
        print("\n4️⃣ Pattern Prediction:")
        prediction_result = analyzer.predict_patterns()
        if prediction_result:
            model, accuracy = prediction_result
        
        print("\n5️⃣ NLP Entity Extraction:")
        entities = analyzer.nlp_extract_entities()
        
        # Generuj raport
        print("\n📋 Generating Report:")
        report = analyzer.generate_report()
        
    else:
        # Fallback to original data
        wiki_file = "out/caly_rok_pl_fixed_updated.csv"
        if Path(wiki_file).exists():
            analyzer.load_data(wiki_file)
            
            # Użyj próbki dla szybkiego testowania
            print(f"\n📊 Używam próbki 1000 rekordów z {len(analyzer.data)} dostępnych")
            analyzer.data = analyzer.data.sample(n=min(1000, len(analyzer.data)), random_state=42)
            
            # Podstawowa analiza
            print("\n1️⃣ Time Series Analysis:")
            ts_data, ts_stats = analyzer.time_series_analysis()
            
            print("\n2️⃣ Event Clustering:")
            cluster_results = analyzer.cluster_events(n_clusters=5)
            
            print("\n3️⃣ Network Analysis:")
            network_metrics = analyzer.build_network('categorical')
            
            print("\n4️⃣ Pattern Prediction:")
            prediction_result = analyzer.predict_patterns()
            if prediction_result:
                model, accuracy = prediction_result
            
            print("\n5️⃣ NLP Entity Extraction:")
            entities = analyzer.nlp_extract_entities()
            
            # Generuj raport
            print("\n📋 Generating Report:")
            report = analyzer.generate_report()
        else:
            print(f"❌ Nie znaleziono plików danych")
            return
    
    # Test integracji z arXiv
    print("\n6️⃣ Scientific Papers Integration:")
    papers = analyzer.extract_scientific_papers("machine learning history", "arxiv", 10)
    if papers:
        print(f"✅ Znaleziono {len(papers)} publikacji naukowych")

if __name__ == "__main__":
    main()