#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKRYPT DO OBLICZEŃ ZAĆMIEŃ DLA OKRESU ŚMIERCI JEZUSA
Specjalnie dla lat 30-33 AD z obsługą błędów
"""

import sys
import os
import json
from datetime import datetime, timedelta

def calculate_eclipses_for_jesus_period():
    """Oblicz zaćmienia dla okresu śmierci Jezusa (30-33 AD)"""

    print("🔭 OBLICZENIA ZAĆMIEŃ DLA OKRESU ŚMIERCI JEZUSA")
    print("=" * 60)

    try:
        # Import bibliotek astronomicznych
        from skyfield.api import load, Topos
        from skyfield import almanac
        import numpy as np

        print("✅ Ładowanie efemeryd Skyfield...")

        # Załaduj efemerydy
        eph = load('de421.bsp')
        ts = load.timescale()

        print("✅ Efemerydy załadowane")

        # Okres analizy: 30-33 AD
        start_date = ts.utc(30, 1, 1)
        end_date = ts.utc(33, 12, 31)

        print(f"📅 Analizowany okres: {start_date.utc_strftime('%Y-%m-%d')} do {end_date.utc_strftime('%Y-%m-%d')}")

        # Funkcje zaćmień
        def solar_eclipses_at(t):
            try:
                return almanac.solar_eclipse_function(eph, eph['earth'])(t)
            except:
                return 0.0

        def lunar_eclipses_at(t):
            try:
                return almanac.lunar_eclipse_function(eph, eph['earth'])(t)
            except:
                return 0.0

        # Skanuj dzień po dniu
        solar_eclipses_found = []
        lunar_eclipses_found = []

        current_time = start_date
        days_checked = 0

        print("🔍 Skanowanie zaćmień dzień po dniu...")

        while current_time.tt < end_date.tt:
            try:
                # Sprawdź zaćmienia słoneczne
                solar_value = solar_eclipses_at(current_time)
                if solar_value > 0.8:  # Widoczne zaćmienie
                    eclipse_info = {
                        'date': current_time.utc_strftime('%Y-%m-%d'),
                        'magnitude': float(solar_value),
                        'type': 'solar',
                        'description': f'Zaćmienie słoneczne, magnituda: {solar_value:.3f}'
                    }
                    solar_eclipses_found.append(eclipse_info)
                    print(f"☀️ ZNALEZIONE ZAĆMIENIE SŁONECZNE: {eclipse_info['date']} (magnituda: {solar_value:.3f})")

                # Sprawdź zaćmienia księżycowe
                lunar_value = lunar_eclipses_at(current_time)
                if lunar_value > 0.8:  # Widoczne zaćmienie
                    eclipse_info = {
                        'date': current_time.utc_strftime('%Y-%m-%d'),
                        'magnitude': float(lunar_value),
                        'type': 'lunar',
                        'description': f'Zaćmienie księżycowe, magnituda: {lunar_value:.3f}'
                    }
                    lunar_eclipses_found.append(eclipse_info)
                    print(f"🌙 ZNALEZIONE ZAĆMIENIE KSIĘŻYCOWE: {eclipse_info['date']} (magnituda: {lunar_value:.3f})")

                days_checked += 1

                # Progress co 100 dni
                if days_checked % 100 == 0:
                    print(f"📊 Sprawdzono {days_checked} dni...")

            except Exception as e:
                print(f"⚠️ Błąd dla dnia {current_time.utc_strftime('%Y-%m-%d')}: {str(e)}")
                pass

            # Następny dzień
            current_time = ts.tt_jd(current_time.tt + 1)

        print("\n📊 PODSUMOWANIE OBLICZEŃ:")
        print(f"☀️ Zaćmienia słoneczne znalezione: {len(solar_eclipses_found)}")
        print(f"🌙 Zaćmienia księżycowe znalezione: {len(lunar_eclipses_found)}")
        print(f"📅 Dni sprawdzone: {days_checked}")

        # Szczegóły zaćmień słonecznych
        if solar_eclipses_found:
            print("\n☀️ SZCZEGÓŁY ZAĆMIEŃ SŁONECZNYCH:")
            for eclipse in solar_eclipses_found:
                print(f"  📅 {eclipse['date']}: {eclipse['description']}")

        # Szczegóły zaćmień księżycowych
        if lunar_eclipses_found:
            print("\n🌙 SZCZEGÓŁY ZAĆMIEŃ KSIĘŻYCOWYCH:")
            for eclipse in lunar_eclipses_found:
                print(f"  📅 {eclipse['date']}: {eclipse['description']}")

        # Sprawdź okolice ukrzyżowania
        crucifixion_date = ts.utc(33, 4, 15)  # 15 kwietnia 33 AD
        print("\n✝️ SPRAWDZENIE OKOLIC UKRZYŻOWANIA (15 kwietnia 33 AD):")
        print(f"📅 Data ukrzyżowania: {crucifixion_date.utc_strftime('%Y-%m-%d')}")

        # Sprawdź ±7 dni od ukrzyżowania
        for days_offset in range(-7, 8):
            check_date = ts.tt_jd(crucifixion_date.tt + days_offset)
            solar_val = solar_eclipses_at(check_date)
            lunar_val = lunar_eclipses_at(check_date)

            if solar_val > 0.5 or lunar_val > 0.5:
                print(f"  📅 {check_date.utc_strftime('%Y-%m-%d')} (dzień {days_offset:+d}):")
                if solar_val > 0.5:
                    print(f"    ☀️ Zaćmienie słoneczne: magnituda {solar_val:.3f}")
                if lunar_val > 0.5:
                    print(f"    🌙 Zaćmienie księżycowe: magnituda {lunar_val:.3f}")

        # Zapisz wyniki do pliku
        results = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'period': '30-33 AD',
                'method': 'Skyfield DE421',
                'crucifixion_date': '33-04-15'
            },
            'solar_eclipses': solar_eclipses_found,
            'lunar_eclipses': lunar_eclipses_found,
            'statistics': {
                'days_checked': days_checked,
                'solar_eclipses_count': len(solar_eclipses_found),
                'lunar_eclipses_count': len(lunar_eclipses_found)
            }
        }

        with open('eclipses_jesus_period.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n💾 Wyniki zapisane do: eclipses_jesus_period.json")
        return results

    except Exception as e:
        print(f"❌ BŁĄD: {str(e)}")
        return None

if __name__ == "__main__":
    calculate_eclipses_for_jesus_period()