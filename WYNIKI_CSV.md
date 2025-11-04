# WIKIHARVESTER - Zebrane dane historyczne

## 📁 **Struktura systemu po reorganizacji:**

```
WIKIHARVESTER/
├── harvesters/              # 4 GŁÓWNE HARVESTERY
│   ├── advanced_data_harvester.py     # 6,147+ records
│   ├── real_data_harvester.py         # 443 records  
│   ├── scientific_archives_harvester.py # 60 JSON papers
│   └── ssl_fixed_harvester.py         # 32 backup records
│
├── data/                    # WSZYSTKIE ZEBRANE DANE
│   ├── cache/harvested_data.csv        # 6,147 lines - główny harvester
│   ├── unified_output/                 # ML datasets (534 complete)
│   ├── scientific_cache/               # 60 structured papers  
│   ├── real_data_complete.csv          # 443 lines academic data
│   └── real_harvested_data.csv
│
├── analyze_harvested_data.py      # Analiza wszystkich danych
├── historical_ml_analyzer.py      # ML + NLP + clustering
├── unified_data_pipeline.py       # ML datasets generator
└── enhanced_timeline_viewer.py    # HTML timeline viewer
```

## 🔥 **Zebrane dane - ponad 7,000 rekordów:**

### **Advanced Data Harvester (6,147+ records):**
- **Wikipedia wielojęzyczna**: Wydarzenia PL/EN/DE/FR (1,000+ events)
- **arXiv papers**: 372 artykuły naukowe (1986-2025)
- **USGS geological**: 499 trzęsień ziemi (2022-2025) 
- **Julian Day range**: -6500 do 2025 CE
- **Confidence avg**: 85.2%

### **Real Data Harvester (443 records):**
- **arXiv ML papers**: "Lecture Notes: Optimization for Machine Learning" (Elad Hazan, 2019)
- **PubMed medical**: Medical research papers z abstracts
- **Crossref academic**: Peer-reviewed publications
- **Wikipedia events**: Multi-language historical events

### **Scientific Archives (60 JSON papers):**
- **Computer Science timeline**: Structured metadata
- **AI/ML evolution**: Key papers z authors + years
- **JSON format**: Ready for timeline analysis

### **SSL Fixed Harvester (32 records):**
- **Backup data**: Dla problemowych źródeł
- **arXiv historical**: "Symbols and astrological terms in ancient arabic inscriptions" (2019)

## 🤖 **ML-Ready Datasets (data/unified_output/):**

### **ml_complete_dataset.csv (534 records):**
- **Complete dataset**: Wszystkie zweryfikowane dane
- **Features**: JD, AM_day, confidence, source_type
- **Categories**: Historical events, scientific papers, geological data

### **ml_high_confidence_dataset.csv (300 records):**
- **High confidence**: Tylko dane z confidence > 80%
- **Premium quality**: Najlepsze dane do ML analysis

### **ml_timeseries_dataset.csv (223 records):**
- **Time series**: Dane z prawidłowymi datami
- **Temporal analysis**: Gotowe do trend analysis

### **ml_features_dataset.csv (534 records):**
- **ML features**: Extracted features dla machine learning
- **NLP ready**: Text features + metadata

## 📊 **Kluczowe statystyki:**

### **Zakres temporalny:**
- **Najstarsze**: -6500 (prehistoria)
- **Najnowsze**: 2025 CE
- **Span**: Ponad 8,500 lat danych historycznych

### **Języki:**
- **Polski**: Wydarzenia, urodziny, zgony
- **Angielski**: Events, births, deaths  
- **Niemiecki**: Historische Ereignisse
- **Francuski**: Événements historiques

### **Źródła danych:**
- **Wikipedia**: 6 języków
- **arXiv.org**: 372+ papers
- **PubMed**: Medical research
- **USGS**: Geological data
- **Crossref**: Academic papers

### **Formaty:**
- **CSV**: UTF-8, comma-separated, pandas-ready
- **SQLite**: Relational databases w cache folderach
- **JSON**: Structured scientific papers
- **ML datasets**: Feature-engineered, confidence-scored

## 🎯 **Julian Day + AM Day integracja:**

### **Prawidłowe JD calculation:**
- **Algorithm**: Fliegla–Van Flanderna
- **Auto-switching**: Julian < 1582-10-15, Gregorian ≥ 1582-10-15
- **AM_day = JD - 1721668.5**: Ready for AM system integration

### **Astronomiczne lata (poprawione BCE):**
- **1 BCE = 0**: Poprawne astronomiczne numerowanie
- **2 BCE = -1**: Wszystkie daty p.n.e. fixed
- **Historical accuracy**: Verified against astronomical sources

## 🚀 **Usage Examples:**

```python
# Analiza wszystkich zebranych danych
python analyze_harvested_data.py

# ML analysis z NLP
python historical_ml_analyzer.py

# Timeline HTML viewer
python enhanced_timeline_viewer.py

# Unifikacja w ML datasets
python unified_data_pipeline.py
```

## 📈 **Data Quality Metrics:**

- **Total verified records**: 7,000+
- **Average confidence**: 85.2%
- **Temporal coverage**: 8,500+ years
- **Multi-language**: 6 languages
- **Multi-source**: 6 different APIs/sources
- **ML-ready**: 534 engineered features

---
*WIKIHARVESTER - Complete Historical Data Pipeline*
*Ostatnia aktualizacja: 4 listopada 2025*