#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_eclipses_in_data.py
-------------------------
SPRAWDZA CZY W ISTNIEJĄCYCH DANYCH ASTRONOMICZNYCH SĄ ZAĆMIENIA
"""

import json

def check_eclipses():
    """Sprawdza czy w danych są zaćmienia"""

    print("🔭 SPRAWDZANIE ZAĆMIEŃ W DANYCH ASTRONOMICZNYCH")
    print("=" * 80)

    try:
        # Wczytaj dane astronomiczne dla ANTYKU PÓŹNEGO
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
                'eclipse' in title or 'SOLAR_ECLIPSE' in subcategory):
                if ('słońca' in title or 'solar' in title or 'sun' in content):
                    solar_eclipses.append(event)

            # Zaćmienia księżycowe (krwawy księżyc)
            if ('zaćmienie' in title or 'zaćmienie' in content or
                'eclipse' in title or 'LUNAR_ECLIPSE' in subcategory):
                if ('księżyca' in title or 'lunar' in title or 'moon' in content or
                    'blood' in content):
                    lunar_eclipses.append(event)
                    if ('blood' in content or 'krwawy' in content or 'czerwony' in content):
                        blood_moons.append(event)

        print(f"\n☀️ Zaćmienia słoneczne znalezione: {len(solar_eclipses)}")
        for eclipse in solar_eclipses:
            print(f"   📅 {eclipse['date']} - {eclipse['title']}")
            print(f"      📝 {eclipse.get('content', '')}")

        print(f"\n🌙 Zaćmienia księżycowe znalezione: {len(lunar_eclipses)}")
        for eclipse in lunar_eclipses:
            print(f"   📅 {eclipse['date']} - {eclipse['title']}")
            print(f"      📝 {eclipse.get('content', '')}")

        print(f"\n🩸 Krwawe księżyce znalezione: {len(blood_moons)}")
        for blood_moon in blood_moons:
            print(f"   📅 {blood_moon['date']} - {blood_moon['title']}")
            print(f"      📝 {blood_moon.get('content', '')}")

        # Sprawdź konkretną datę ukrzyżowania: 15 kwietnia 33 AD
        crucifixion_date = '0033-04-15'
        crucifixion_events = [e for e in jesus_events if e['date'] == crucifixion_date]

        print(f"\n✝️ WYDARZENIA ASTRONOMICZNE DNIA UKRZYŻOWANIA (15 kwietnia 33 AD):")
        print(f"   📊 Znaleziono wydarzeń: {len(crucifixion_events)}")

        for event in crucifixion_events:
            print(f"   🔭 {event['title']}")
            if event.get('content'):
                print(f"      📝 {event['content']}")

        # Sprawdź czy są jakieś wzmianki o zaćmieniach w całym zbiorze
        all_eclipse_mentions = []
        for event in jesus_events:
            title = event.get('title', '').lower()
            content = event.get('content', '').lower()
            if ('zaćmienie' in title or 'zaćmienie' in content or
                'eclipse' in title or 'eclipse' in content):
                all_eclipse_mentions.append(event)

        print(f"\n🔍 WSZYSTKIE WZMIANKI O ZAĆMIENIACH W LATACH 30-33 AD: {len(all_eclipse_mentions)}")
        for event in all_eclipse_mentions:
            print(f"   📅 {event['date']} - {event['title']}")
            print(f"      📝 {event.get('content', '')}")

        # WNIOSKI
        print(f"\n🎯 WNIOSKI:")
        print("=" * 80)

        if solar_eclipses:
            print("✅ ZNALEZIONO ZAĆMIENIA SŁONECZNE w danych astronomicznych!")
            for eclipse in solar_eclipses:
                print(f"   ☀️ {eclipse['date']} - {eclipse['title']}")
        else:
            print("❌ NIE ZNALEZIONO ZAĆMIEŃ SŁONECZNYCH w danych astronomicznych")
            print("   💡 Konieczne jest uruchomienie harvestera z obliczeniami zaćmień")

        if blood_moons:
            print("✅ ZNALEZIONO KRWAWE KSIĘŻYCE w danych astronomicznych!")
            for blood_moon in blood_moons:
                print(f"   🩸 {blood_moon['date']} - {blood_moon['title']}")
        else:
            print("❌ NIE ZNALEZIONO KRWAWYCH KSIĘŻYCÓW w danych astronomicznych")
            print("   💡 Konieczne jest uruchomienie harvestera z obliczeniami zaćmień")

        print(f"\n📊 PODSUMOWANIE:")
        print(f"   📅 Zakres: lata 30-33 AD")
        print(f"   🔭 Wydarzenia: {len(jesus_events)}")
        print(f"   ☀️ Zaćmienia słoneczne: {len(solar_eclipses)}")
        print(f"   🌙 Zaćmienia księżycowe: {len(lunar_eclipses)}")
        print(f"   🩸 Krwawe księżyce: {len(blood_moons)}")

    except Exception as e:
        print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    check_eclipses()