#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analiza_znakow_jezusa.py
-------------------------
ANALIZA ASTRONOMICZNYCH ZNAKÓW PODCZAS ŚMIERCI JEZUSA
Zaćmienia słoneczne i krwawy księżyc
"""

import json
from datetime import datetime

def analyze_astronomical_signs():
    """Analizuje znaki astronomiczne podczas śmierci Jezusa"""

    print("🔭 ANALIZA ZNAKÓW ASTRONOMICZNYCH PODCZAS ŚMIERCI JEZUSA")
    print("☀️ Zaćmienia słoneczne i 🌙 krwawy księżyc")
    print("=" * 80)

    try:
        # Wczytaj dane astronomiczne
        with open('astronomical_antyk_późny.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        events = data.get('results', {}).get('epoch_ANTYK PÓŹNY', [])

        # Filtruj wydarzenia z lat 30-33 AD
        jesus_events = []
        for event in events:
            date = event.get('date', '')
            if date.startswith(('0030-', '0031-', '0032-', '0033-')):
                jesus_events.append(event)

        print(f"📊 Wczytano {len(jesus_events)} wydarzeń astronomicznych z lat 30-33 AD")

        # Szukaj zaćmień słonecznych i księżycowych
        solar_eclipses = []
        lunar_eclipses = []
        blood_moons = []

        for event in jesus_events:
            title = event.get('title', '').lower()
            content = event.get('content', '').lower()
            subcategory = event.get('subcategory', '')

            # Zaćmienia słoneczne
            if ('zaćmienie' in title or 'zaćmienie' in content or
                'eclipse' in title or 'solar' in subcategory):
                if ('słońca' in title or 'solar' in title or 'sun' in content):
                    solar_eclipses.append(event)

            # Zaćmienia księżycowe (krwawy księżyc)
            if ('zaćmienie' in title or 'zaćmienie' in content or
                'eclipse' in title or 'lunar' in subcategory):
                if ('księżyca' in title or 'lunar' in title or 'moon' in content or
                    'blood' in content):
                    lunar_eclipses.append(event)
                    if ('blood' in content or 'krwawy' in content or 'czerwony' in content):
                        blood_moons.append(event)

        print(f"\n☀️ Zaćmienia słoneczne znalezione: {len(solar_eclipses)}")
        for eclipse in solar_eclipses:
            print(f"   📅 {eclipse['date']} - {eclipse['title']}")
            if eclipse.get('content'):
                print(f"      📝 {eclipse['content']}")

        print(f"\n🌙 Zaćmienia księżycowe znalezione: {len(lunar_eclipses)}")
        for eclipse in lunar_eclipses:
            print(f"   📅 {eclipse['date']} - {eclipse['title']}")
            if eclipse.get('content'):
                print(f"      📝 {eclipse['content']}")

        print(f"\n🩸 Krwawe księżyce znalezione: {len(blood_moons)}")
        for blood_moon in blood_moons:
            print(f"   📅 {blood_moon['date']} - {blood_moon['title']}")
            if blood_moon.get('content'):
                print(f"      📝 {blood_moon['content']}")

        # Sprawdź konkretną datę ukrzyżowania: 15 kwietnia 33 AD
        crucifixion_date = '0033-04-15'
        crucifixion_events = [e for e in jesus_events if e['date'] == crucifixion_date]

        print(f"\n✝️ WYDARZENIA ASTRONOMICZNE DNIA UKRZYŻOWANIA (15 kwietnia 33 AD):")
        print(f"   📊 Znaleziono wydarzeń: {len(crucifixion_events)}")

        for event in crucifixion_events:
            print(f"   🔭 {event['title']}")
            if event.get('content'):
                print(f"      📝 {event['content']}")

        # Sprawdź dni wokół ukrzyżowania (zaćmienie mogło być dzień wcześniej lub później)
        print(f"\n🔍 SPRAWDZENIE OKRESU WOKÓŁ UKRZYŻOWANIA (12-18 kwietnia 33 AD):")

        dates_to_check = [
            '0033-04-12', '0033-04-13', '0033-04-14', '0033-04-15',
            '0033-04-16', '0033-04-17', '0033-04-18'
        ]

        for check_date in dates_to_check:
            day_events = [e for e in jesus_events if e['date'] == check_date]
            eclipse_events = [e for e in day_events if
                            'zaćmienie' in e.get('title', '').lower() or
                            'eclipse' in e.get('title', '').lower()]

            if eclipse_events:
                print(f"\n   📅 {check_date}:")
                for eclipse in eclipse_events:
                    print(f"      ⚠️ {eclipse['title']}")
                    if eclipse.get('content'):
                        print(f"         📝 {eclipse['content']}")

        # Analiza biblijna
        print(f"\n📖 PORÓWNANIE Z PISMEM ŚWIĘTYM:")
        print("=" * 80)

        print("📜 EWANGELIE (Mateusz 27:45, Marek 15:33, Łukasz 23:44-45):")
        print("   'Od godziny szóstej aż do godziny dziewiątej była ciemność'")
        print("   'zaćmienie słońca'")

        print("\n📜 KSIĘGA JOELA 2:31:")
        print("   'Słońce zamieni się w ciemność, a księżyc w krew,'")
        print("   'zanim nadejdzie dzień Pana, wielki i straszny.'")

        print("\n📜 DZIEJE APOSTOLSKIE 2:20:")
        print("   'Słońce zamieni się w ciemność, a księżyc w krew,'")
        print("   'zanim nadejdzie dzień Pana, wielki i straszny.'")

        print("\n📜 KSIĘGA IZAJASZA 13:10:")
        print("   'Słońce i księżyc się zaćmią, a gwiazdy wstrzymają blask swój.'")

        # Wnioski
        print(f"\n🎯 WNIOSKI:")
        print("=" * 80)

        if solar_eclipses:
            print("✅ ZNALEZIONO ZAĆMIENIA SŁONECZNE w okresie śmierci Jezusa!")
            for eclipse in solar_eclipses:
                print(f"   ☀️ {eclipse['date']} - {eclipse['title']}")
        else:
            print("❌ NIE ZNALEZIONO ZAĆMIEŃ SŁONECZNYCH w danych astronomicznych")

        if blood_moons:
            print("✅ ZNALEZIONO KRWAWE KSIĘŻYCE w okresie śmierci Jezusa!")
            for blood_moon in blood_moons:
                print(f"   🩸 {blood_moon['date']} - {blood_moon['title']}")
        else:
            print("❌ NIE ZNALEZIONO KRWAWYCH KSIĘŻYCÓW w danych astronomicznych")

        print(f"\n🔬 PODSUMOWANIE:")
        print(f"   📊 Analiza oparta na {len(jesus_events)} wydarzeniach astronomicznych")
        print(f"   📅 Okres: lata 30-33 AD")
        print(f"   🔭 Źródła: astropy, ephem, skyfield")
        print(f"   📚 Metoda: Prawdziwe obliczenia astronomiczne")

        return {
            'solar_eclipses': len(solar_eclipses),
            'lunar_eclipses': len(lunar_eclipses),
            'blood_moons': len(blood_moons),
            'crucifixion_date': '0033-04-15',
            'total_events': len(jesus_events)
        }

    except Exception as e:
        print(f"❌ Błąd podczas analizy: {e}")
        return None

if __name__ == "__main__":
    analyze_astronomical_signs()