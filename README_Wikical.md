# Wikipedia Historical Data Harvester

## 🔥 Kompletny system zbierania danych historycznych

### 🏗️ **Architektura systemu:**

```
WIKIHARVESTER/
├── harvesters/              # 4 GŁÓWNE HARVESTERY
│   ├── advanced_data_harvester.py     # Wikipedia + arXiv + USGS geological
│   ├── real_data_harvester.py         # Academic papers (arXiv, PubMed, Crossref) 
│   ├── scientific_archives_harvester.py # Structured JSON scientific data
│   └── ssl_fixed_harvester.py         # SSL-fixed backup harvester
│
├── data/                    # WSZYSTKIE ZEBRANE DANE
│   ├── cache/              # Główny harvester (6,147+ records)
│   ├── unified_output/     # ML-ready datasets (534 records)
│   ├── scientific_cache/   # Scientific papers (60 JSON papers)
│   ├── real_data_complete.csv  # Real academic data (443 records)
│   └── real_harvested_data.csv
│
├── analyze_harvested_data.py      # Analiza wszystkich zebranych danych
├── historical_ml_analyzer.py      # ML analysis, NLP, clustering
├── unified_data_pipeline.py       # Unifikacja danych w ML datasets
└── enhanced_timeline_viewer.py    # HTML timeline viewer
```

## 🚀 **Quick Start**

### Instalacja:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements_wikical.txt
pip install -r requirements_ml.txt
```

### Uruchomienie harvesterów:
```bash
# Advanced Data Harvester (Wikipedia multilang + arXiv + geological)
python harvesters/advanced_data_harvester.py

# Real Data Harvester (academic papers)
python harvesters/real_data_harvester.py

# Scientific Archives (structured JSON)
python harvesters/scientific_archives_harvester.py

# Analiza wszystkich zebranych danych
python analyze_harvested_data.py
```

## 📊 **Zebrane dane:**

### **6,147+ rekordów z Advanced Data Harvester:**
- **Wikipedia wielojęzyczna**: Wydarzenia historyczne (PL, EN, DE, FR)
- **arXiv papers**: 372 artykuły naukowe (1986-2025)
- **USGS geological**: 499 trzęsień ziemi (2022-2025)
- **Format**: JD + AM_day + confidence scoring

### **443 rekordów z Real Data Harvester:**
- **arXiv ML papers**: Machine learning research
- **PubMed medical**: Publikacje medyczne
- **Crossref academic**: Peer-reviewed papers
- **Format**: Structured metadata + abstracts

### **60 papers z Scientific Archives:**
- **JSON structured**: Computer Science, AI, ML timeline
- **Metadata**: Authors, years, abstracts, DOIs
- **Format**: Timeline events z JD conversion

## 🤖 **ML Analysis Features:**

- **Named Entity Recognition**: Automatyczne wykrywanie miejsc, osób, dat
- **Clustering**: Grupowanie podobnych wydarzeń
- **Time Series Analysis**: Analiza trendów czasowych
- **Network Analysis**: Powiązania między wydarzeniami
- **Confidence Scoring**: Ocena wiarygodności danych (85.2% średnia)

## 📈 **Integracja z AM-JD:**

### **Julian Day (JD) + AM Day:**
- **Automatyczny**: Fliegla–Van Flanderna algorithm
- **Auto-switching**: Julian < 1582-10-15, Gregorian ≥ 1582-10-15
- **AM_day = JD - 1721668.5**: Gotowe do integracji
- **Zakres**: Od -6500 do 2025 CE

### **Astronomiczne lata:**
- **1 BCE = rok 0**, **2 BCE = rok -1**
- **Poprawne BCE handling**: Wszystkie daty p.n.e. prawidłowo przeliczone

## 🔍 **Analiza i wizualizacja:**

```bash
# Kompletna analiza wszystkich danych
python analyze_harvested_data.py

# ML analysis z clusteringiem i NLP
python historical_ml_analyzer.py

# Unifikacja w ML datasets
python unified_data_pipeline.py

# HTML timeline viewer
python enhanced_timeline_viewer.py
```

## 📁 **Formaty danych:**

- **CSV**: UTF-8, comma-separated
- **SQLite**: Relacyjne bazy danych
- **JSON**: Structured metadata
- **ML datasets**: Pandas-ready, confidence-scored

## 🌍 **Źródła danych:**

- **Wikipedia**: 6 języków (PL, EN, DE, FR, ES, IT)
- **arXiv.org**: Preprints naukowe
- **PubMed**: Publikacje medyczne  
- **Crossref**: Peer-reviewed papers
- **USGS**: Dane geologiczne
- **Multiple APIs**: SSL-fixed, rate-limited

---
*System WIKIHARVESTER - Complete Historical Data Pipeline*
