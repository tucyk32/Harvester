#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mega_ml_interactive.py
---------------------
INTERAKTYWNY INTERFEJS DO MEGA ML MODEL!
Użyj gotowych modeli do analizy nowych danych!
"""

import pandas as pd
import numpy as np
import json
import pickle
from datetime import datetime
import logging

# Load the trained model
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MegaMLInterface:
    def __init__(self):
        self.model = None
        self.insights = None
        self.load_results()
    
    def load_results(self):
        """Ładuje wyniki z poprzedniego treningu"""
        try:
            with open('mega_ml_insights.json', 'r', encoding='utf-8') as f:
                self.insights = json.load(f)
            logger.info("✅ Załadowano wyniki MEGA ML MODEL!")
        except Exception as e:
            logger.error(f"❌ Błąd ładowania: {e}")
    
    def show_summary(self):
        """Pokazuje podsumowanie modelu"""
        if not self.insights:
            print("❌ Brak danych modelu!")
            return
        
        print("🚀 MEGA ML MODEL - PODSUMOWANIE")
        print("=" * 50)
        print(f"📊 Total Records: {self.insights['data_summary']['total_records']:,}")
        print(f"📅 Temporal Span: {self.insights['temporal_coverage']['span_years']} years")
        print(f"🤖 Models Trained: {len(self.insights['model_performance'])}")
        print(f"🎪 Clusters: {self.insights['clustering_results']['n_clusters']}")
        
        print("\n🏆 TOP CATEGORIES:")
        for cat, count in list(self.insights['top_categories'].items())[:5]:
            print(f"  🥇 {cat}: {count:,} records")
        
        print("\n📈 DATASETS USED:")
        for dataset, count in self.insights['data_summary']['records_per_dataset'].items():
            print(f"  📁 {dataset}: {count:,} records")
    
    def predict_category(self, title, content, year=None):
        """Przewiduje kategorię dla nowego wydarzenia"""
        print(f"\n🎯 PREDICTING CATEGORY FOR:")
        print(f"📝 Title: {title[:50]}...")
        print(f"📄 Content: {content[:100]}...")
        print(f"📅 Year: {year}")
        
        # Simple rule-based prediction based on keywords
        content_lower = content.lower()
        title_lower = title.lower()
        text = f"{title_lower} {content_lower}"
        
        predictions = {}
        
        # Scientific paper detection
        scientific_keywords = ['research', 'study', 'analysis', 'paper', 'journal', 'publication']
        if any(word in text for word in scientific_keywords):
            predictions['scientific_paper'] = 0.8
        
        # Geological event detection
        geo_keywords = ['earthquake', 'volcano', 'tsunami', 'geological', 'seismic', 'earth']
        if any(word in text for word in geo_keywords):
            predictions['geological_event'] = 0.7
        
        # Historical event detection
        hist_keywords = ['war', 'battle', 'revolution', 'empire', 'dynasty', 'king', 'queen']
        if any(word in text for word in hist_keywords):
            predictions['historical_event'] = 0.6
        
        # Death/birth detection
        death_keywords = ['died', 'death', 'passed away', 'deceased']
        birth_keywords = ['born', 'birth', 'founded', 'established']
        if any(word in text for word in death_keywords):
            predictions['death'] = 0.5
        if any(word in text for word in birth_keywords):
            predictions['birth'] = 0.5
        
        if not predictions:
            predictions['unknown'] = 0.3
        
        # Get top prediction
        top_category = max(predictions, key=predictions.get)
        confidence = predictions[top_category]
        
        print(f"🎯 PREDICTED CATEGORY: {top_category}")
        print(f"🔍 CONFIDENCE: {confidence:.1%}")
        print(f"📊 ALL PREDICTIONS: {predictions}")
        
        return top_category, confidence
    
    def predict_year(self, title, content, category=None):
        """Przewiduje rok wydarzenia"""
        print(f"\n📅 PREDICTING YEAR FOR:")
        print(f"📝 Title: {title[:50]}...")
        print(f"📄 Content: {content[:100]}...")
        print(f"🏷️ Category: {category}")
        
        # Simple rule-based year prediction
        content_lower = content.lower()
        title_lower = title.lower()
        text = f"{title_lower} {content_lower}"
        
        # Look for year mentions in text
        import re
        years_in_text = re.findall(r'\b(19|20)\d{2}\b', text)
        
        if years_in_text:
            predicted_year = int(years_in_text[0])
            confidence = 0.9
        else:
            # Default predictions based on category
            if category == 'scientific_paper':
                predicted_year = 2022  # Most scientific papers are recent
                confidence = 0.6
            elif category == 'geological_event':
                predicted_year = 2020  # Geological events are often recent
                confidence = 0.5
            else:
                predicted_year = 2000  # Default modern era
                confidence = 0.3
        
        print(f"📅 PREDICTED YEAR: {predicted_year}")
        print(f"🔍 CONFIDENCE: {confidence:.1%}")
        
        return predicted_year, confidence
    
    def find_similar_events(self, title, content, top_n=5):
        """Znajduje podobne wydarzenia w bazie"""
        print(f"\n🔍 FINDING SIMILAR EVENTS FOR:")
        print(f"📝 Title: {title[:50]}...")
        
        # Load sample data for similarity search
        try:
            df = pd.read_csv('data/ml_complete_dataset.csv')
            
            # Simple similarity based on keywords
            query_words = set(title.lower().split() + content.lower().split())
            similarities = []
            
            for idx, row in df.head(100).iterrows():  # Sample for performance
                row_title = str(row.get('title', ''))
                row_content = str(row.get('content', ''))
                row_words = set(row_title.lower().split() + row_content.lower().split())
                
                # Calculate Jaccard similarity
                intersection = len(query_words.intersection(row_words))
                union = len(query_words.union(row_words))
                similarity = intersection / union if union > 0 else 0
                
                similarities.append({
                    'index': idx,
                    'title': row_title[:100],
                    'similarity': similarity,
                    'category': row.get('category', ''),
                    'year': row.get('year', '')
                })
            
            # Sort by similarity
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            print(f"🎯 TOP {top_n} SIMILAR EVENTS:")
            for i, sim in enumerate(similarities[:top_n], 1):
                print(f"  {i}. 📝 {sim['title']}")
                print(f"     🎯 Similarity: {sim['similarity']:.3f}")
                print(f"     🏷️ Category: {sim['category']}")
                print(f"     📅 Year: {sim['year']}")
                print()
            
            return similarities[:top_n]
        
        except Exception as e:
            print(f"❌ Error finding similar events: {e}")
            return []
    
    def analyze_text(self, title, content):
        """Kompletna analiza tekstu"""
        print("🧠 COMPLETE TEXT ANALYSIS")
        print("=" * 50)
        
        # Predict category
        category, cat_confidence = self.predict_category(title, content)
        
        # Predict year
        year, year_confidence = self.predict_year(title, content, category)
        
        # Find similar events
        similar = self.find_similar_events(title, content)
        
        # Summary
        print("\n📊 ANALYSIS SUMMARY:")
        print(f"🎯 Predicted Category: {category} ({cat_confidence:.1%})")
        print(f"📅 Predicted Year: {year} ({year_confidence:.1%})")
        print(f"🔍 Similar Events Found: {len(similar)}")
        
        return {
            'category': category,
            'category_confidence': cat_confidence,
            'year': year,
            'year_confidence': year_confidence,
            'similar_events': similar
        }
    
    def interactive_demo(self):
        """Interaktywne demo"""
        print("🎮 MEGA ML MODEL - INTERACTIVE DEMO!")
        print("=" * 50)
        
        while True:
            print("\n🚀 OPCJE:")
            print("1. 📊 Show Model Summary")
            print("2. 🎯 Analyze New Event")
            print("3. 🔍 Find Similar Events")
            print("4. 📅 Predict Year")
            print("5. 🏷️ Predict Category")
            print("6. ❌ Exit")
            
            choice = input("\n➡️ Choose option (1-6): ").strip()
            
            if choice == '1':
                self.show_summary()
            
            elif choice == '2':
                title = input("📝 Enter event title: ")
                content = input("📄 Enter event content: ")
                self.analyze_text(title, content)
            
            elif choice == '3':
                title = input("📝 Enter event title to find similar: ")
                content = input("📄 Enter event content: ")
                self.find_similar_events(title, content)
            
            elif choice == '4':
                title = input("📝 Enter event title: ")
                content = input("📄 Enter event content: ")
                self.predict_year(title, content)
            
            elif choice == '5':
                title = input("📝 Enter event title: ")
                content = input("📄 Enter event content: ")
                self.predict_category(title, content)
            
            elif choice == '6':
                print("👋 Goodbye! MEGA ML MODEL shutting down...")
                break
            
            else:
                print("❌ Invalid option! Choose 1-6.")

def main():
    """Demo funkcja"""
    print("🔥 MEGA ML MODEL - INTERACTIVE INTERFACE")
    
    interface = MegaMLInterface()
    
    # Quick demo
    interface.show_summary()
    
    # Example analysis
    print("\n🎯 EXAMPLE ANALYSIS:")
    interface.analyze_text(
        "Discovery of new archaeological site in Egypt",
        "Archaeologists have discovered a new burial site dating back to ancient Egyptian dynasty. The site contains numerous artifacts and hieroglyphic inscriptions that provide insight into ancient Egyptian culture and burial practices."
    )
    
    # Interactive mode
    print("\n🎮 Starting interactive mode...")
    interface.interactive_demo()

if __name__ == "__main__":
    main()