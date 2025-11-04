#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pełny harvester astronomiczny - kilka godzin zbierania
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'harvesters'))

from scientific_archives_harvester import ScientificArchivesHarvester
from datetime import datetime, timedelta
import time

def run_full_astronomical_harvester():
    """Pełny harvester astronomiczny na kilka godzin"""
    print("🚀 PEŁNY HARVESTER ASTRONOMICZNY - KILKA GODZIN ZBIERANIA")
    print("=" * 70)
    
    harvester = ScientificArchivesHarvester(rate_limit=2.0)  # Wolniejsze dla stabilności
    
    # Sprawdź biblioteki
    from harvesters.scientific_archives_harvester import ASTRO_LIBS_AVAILABLE
    
    if not ASTRO_LIBS_AVAILABLE:
        print("❌ Biblioteki astronomiczne niedostępne!")
        return
    
    print("✅ Biblioteki astronomiczne dostępne - rozpoczynam zbieranie")
    print(f"🕐 Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Okresy zbierania - ostatnie 3 miesiące + przyszły miesiąc
    periods = [
        ("2024-08-01", "2024-08-31", "Sierpień 2024"),
        ("2024-09-01", "2024-09-30", "Wrzesień 2024"), 
        ("2024-10-01", "2024-10-31", "Październik 2024"),
        ("2024-11-01", "2024-11-30", "Listopad 2024"),
        ("2024-12-01", "2024-12-31", "Grudzień 2024"),
    ]
    
    all_events = []
    total_events = 0
    
    for i, (start_date, end_date, period_name) in enumerate(periods, 1):
        print(f"\n📅 OKRES {i}/{len(periods)}: {period_name}")
        print(f"🕐 Czas: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        try:
            # Zbieraj dane astronomiczne
            events = harvester.search_nasa_astronomical_events(
                start_date=start_date,
                end_date=end_date,
                max_results=500  # Więcej danych
            )
            
            print(f"✅ Zebrano {len(events)} wydarzeń dla {period_name}")
            all_events.extend(events)
            total_events += len(events)
            
            # Zapisz okresowe wyniki
            period_filename = f"astronomical_events_{period_name.lower().replace(' ', '_')}.json"
            harvester.save_results({f'events_{period_name}': events}, period_filename)
            
            # Pokazuj próbki danych
            if events:
                print(f"📋 PRÓBKA DANYCH Z {period_name}:")
                for j, event in enumerate(events[:3], 1):
                    title = event.get('title', 'Nieznany')[:50]
                    category = event.get('subcategory', 'N/A')
                    source = event.get('source', 'N/A')
                    timestamp = event.get('metadata', {}).get('timestamp_utc', 'N/A')
                    print(f"  {j}. {title}")
                    print(f"     📂 {category} | 📡 {source} | 🕐 {timestamp}")
            
            # Statystyki po kategorii
            categories = {}
            for event in events:
                cat = event.get('subcategory', 'UNKNOWN')
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"📊 KATEGORIE W {period_name}:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   {cat}: {count} wydarzeń")
            
            print(f"💾 Zapisano: {period_filename}")
            print(f"📈 Łącznie zebranych wydarzeń: {total_events}")
            
        except Exception as e:
            print(f"❌ Błąd dla {period_name}: {e}")
        
        # Czas między okresami
        if i < len(periods):
            print(f"\n⏳ Przerwa 30 sekund przed następnym okresem...")
            time.sleep(30)
    
    # Finalne zapisanie wszystkich danych
    print(f"\n💾 FINALNE ZAPISYWANIE DANYCH:")
    print(f"🕐 Czas: {datetime.now().strftime('%H:%M:%S')}")
    
    # Wszystkie wydarzenia
    harvester.save_results({'all_astronomical_events': all_events}, 'full_astronomical_harvest.json')
    
    # Timeline format
    timeline_events = harvester.convert_to_timeline_format(all_events)
    harvester.save_results({'astronomical_timeline': timeline_events}, 'full_astronomical_timeline.json')
    
    # Finalne statystyki
    print(f"\n📊 FINALNE STATYSTYKI:")
    print(f"📅 Okresy: {len(periods)}")
    print(f"🔭 Łącznie wydarzeń: {len(all_events)}")
    print(f"⏱️ Timeline events: {len(timeline_events)}")
    
    # Statystyki źródeł
    sources = {}
    categories = {}
    for event in all_events:
        src = event.get('source', 'UNKNOWN')
        cat = event.get('subcategory', 'UNKNOWN')
        sources[src] = sources.get(src, 0) + 1
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📡 ŹRÓDŁA DANYCH:")
    for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"   {src}: {count} wydarzeń")
    
    print(f"\n📂 KATEGORIE:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count} wydarzeń")
    
    # Próbka najlepszych danych
    print(f"\n🌟 TOP 10 NAJCIEKAWSZYCH WYDARZEŃ:")
    # Sortuj według precyzji i ważności
    sorted_events = sorted(all_events, key=lambda x: (
        x.get('metadata', {}).get('precision', 'unknown') == 'minute',
        x.get('metadata', {}).get('precision', 'unknown') == 'hourly',
        len(x.get('content', ''))
    ), reverse=True)
    
    for i, event in enumerate(sorted_events[:10], 1):
        title = event.get('title', 'Nieznany')[:60]
        precision = event.get('metadata', {}).get('precision', 'N/A')
        timestamp = event.get('metadata', {}).get('timestamp_utc', 'N/A')
        obj = event.get('metadata', {}).get('celestial_object', 'N/A')
        print(f"  {i:2d}. {title}")
        print(f"      🎯 {precision} | 🌟 {obj} | 🕐 {timestamp}")
    
    print(f"\n✅ HARVESTING UKOŃCZONY!")
    print(f"🕐 Koniec: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💎 Zebrano {len(all_events)} precyzyjnych wydarzeń astronomicznych")
    print(f"🔬 Źródła: astropy, ephem, JPL Horizons, arXiv")

if __name__ == "__main__":
    run_full_astronomical_harvester()