# 🚀 MEGA ML MODEL - JAK UŻYWAĆ?

## ⚡ 3 SPOSOBY UŻYCIA MODELU

### 1. 🎯 PODSTAWOWE URUCHOMIENIE
```bash
# Trenuj model z wszystkich danych
python mega_ml_model.py
```
**Wynik:** Model analizuje 4,666 rekordów i generuje insights

---

### 2. 🎮 INTERAKTYWNY TRYB
```bash
# Uruchom przykłady i demo
python mega_ml_examples.py
```
**Możliwości:**
- ✅ Zobacz podsumowanie modelu
- ✅ Testuj predykcje na przykładach
- ✅ Interaktywny klasyfikator wydarzeń

---

### 3. 💻 PROGRAMOWE UŻYCIE

#### 🔍 Analiza Nowego Wydarzenia:
```python
from mega_ml_examples import predict_event_category

# Przewiduj kategorię
category, confidence = predict_event_category(
    "Nowe odkrycie archeologiczne w Egipcie",
    "Archeolodzy odkryli grobowiec faraona..."
)
print(f"Kategoria: {category} ({confidence:.1%})")
```

#### 📊 Załaduj Wyniki Modelu:
```python
import json

# Załaduj insights
with open('mega_ml_insights.json', 'r') as f:
    insights = json.load(f)

print(f"Total records: {insights['data_summary']['total_records']}")
print(f"Top category: {list(insights['top_categories'].keys())[0]}")
```

---

## 🎯 CO MOŻE ROBIĆ MODEL?

### ✅ **KLASYFIKACJA WYDARZEŃ** (92.6% accuracy)
- scientific_paper ← badania naukowe
- geological_event ← trzęsienia ziemi, tsunami
- historical_event ← wojny, bitwy
- death/birth ← zgony, urodzenia

### ✅ **PRZEWIDYWANIE DAT** (±2.4 lat RMSE)
- Szacuje rok wydarzenia na podstawie treści
- Wykorzystuje słowa kluczowe i kontekst

### ✅ **CLUSTERING WYDARZEŃ** (8 klastrów)
- Grupuje podobne wydarzenia
- Identyfikuje wzorce w danych

### ✅ **ANALIZA TRENDÓW CZASOWYCH**
- Wydarzenia według dekad
- Trendy kategorii w czasie

---

## 📋 WYNIKI ANALIZY

### 📊 **STATYSTYKI:**
- **4,666 rekordów** z 8 harvesterów
- **39 lat** danych (1986-2025)
- **2,159 publikacji naukowych** (46%)
- **499 wydarzeń geologicznych** (11%)

### 🎪 **KLASTRY:**
- Klaster 1: 1,370 wydarzeń (geological_event, events)
- Klaster 0: 1,360 wydarzeń (scientific_paper, urodzenia)
- Klaster 7: 820 wydarzeń (archaeological_find)

### 📈 **NAJAKTYWNIEJSZA DEKADA:** 2020s (1,669 wydarzeń)

---

## 🛠️ PRAKTYCZNE ZASTOSOWANIA

### 1. **AUTOMATYCZNA KATEGORIZACJA**
```python
# Nowy artykuł/wydarzenie → automatyczna kategoria
category = predict_event_category(title, content)
```

### 2. **SZACOWANIE DAT**
```python
# Wydarzenie bez daty → przewidywany rok
year = predict_year(title, content, category)
```

### 3. **WYSZUKIWANIE PODOBNYCH**
```python
# Znajdź podobne wydarzenia w bazie danych
similar = find_similar_events(title, content)
```

### 4. **ANALIZA WZORCÓW**
```python
# Trendy, clustering, insights
insights = load_model_results()
```

---

## 🎮 DEMO W AKCJI

```bash
python mega_ml_examples.py
```

**Przykład sesji:**
```
📝 Tytuł: "Trzęsienie ziemi w Japonii"
📄 Opis: "Silne trzęsienie magnitude 7.2..."

🎯 PREDICTED: geological_event
🔍 CONFIDENCE: 90.0%
```

---

## 📄 PLIKI WYNIKOWE

- **`mega_ml_insights.json`** - szczegółowe wyniki analizy
- **`MEGA_ML_RAPORT.md`** - pełny raport z wizualizacjami
- **`mega_ml_model.py`** - główny model ML
- **`mega_ml_examples.py`** - przykłady użycia

---

## 🎯 GOTOWE DO UŻYCIA!

**Model jest w pełni funkcjonalny i gotowy do:**
- 🔮 Przewidywania kategorii nowych wydarzeń
- 📅 Szacowania dat nieznanych wydarzeń  
- 🎪 Grupowania podobnych wydarzeń
- 📊 Analizy trendów historycznych

### ⚡ Quick Start:
```bash
python mega_ml_examples.py
```

**🏆 MEGA ML MODEL = HISTORICAL DOMINATION! 🏆**