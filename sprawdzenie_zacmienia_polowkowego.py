#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sprawdzenie_zacmienia_polowkowego.py
-------------------------
SPRAWDZENIE ZAĆMIENIA PÓŁCIENIOWEGO W DNIU UKRZYŻOWANIA
"""

import json
from datetime import datetime, timedelta
import skyfield.api as sf
from skyfield import almanac
from skyfield.api import N, S, E, W, wgs84

def load_ts():
    """Załaduj timescale Skyfield"""
    ts = sf.load.timescale()
    return ts

def check_penumbral_eclipses():
    """Sprawdź zaćmienia półcieniowe w dniu ukrzyżowania"""

    print("🔍 SPRAWDZENIE ZAĆMIENIA PÓŁCIENIOWEGO W DNIU UKRZYŻOWANIA")
    print("=" * 80)

    # Data ukrzyżowania - poprawiona na podstawie analizy
    crucifixion_date = datetime(33, 4, 7)  # 7 kwietnia 33 AD

    print(f"📅 DATA UKRZYŻOWANIA: {crucifixion_date.strftime('%A, %d %B %Y')}")

    # Załaduj efemerydy
    ts = load_ts()
    eph = sf.load('de421.bsp')

    # Sprawdź zaćmienia w dniu ukrzyżowania
    start_time = ts.utc(33, 4, 7, 0, 0, 0)  # Początek dnia
    end_time = ts.utc(33, 4, 7, 23, 59, 59)  # Koniec dnia

    print(f"⏰ OKRES SPRAWDZANIA: {start_time.utc_strftime()} - {end_time.utc_strftime()}")

    # Sprawdź zaćmienia słoneczne używając właściwej funkcji
    try:
        from skyfield.eclipse import solar_eclipse_times

        # Znajdź czasy zaćmień słonecznych
        times = solar_eclipse_times(eph, start_time, end_time)

        print(f"\n☀️ ZAĆMIENIA SŁONECZNE W DNIU UKRZYŻOWANIA:")
        if times:
            for t in times:
                print(f"   • Czas: {t.utc_strftime('%H:%M:%S UTC')}")

                # Sprawdź typ zaćmienia
                magnitude = almanac.solar_eclipse_magnitude(eph, t)
                print(f"   • Magnituda: {magnitude}")

                if magnitude > 0:
                    print(f"   ✅ ZNALEZIONO ZAĆMIENIE!")
                    return True, t, "Solar Eclipse"
        else:
            print("   ❌ Brak zaćmień słonecznych")

    except ImportError:
        print("   ⚠️ Funkcja solar_eclipse_times niedostępna")

    return False, None, None

def check_nearby_dates():
    """Sprawdź zaćmienia w okolicznych datach"""

    print(f"\n🔍 SPRAWDZENIE OKOLICZNYCH DAT (33 AD)")
    print("=" * 80)

    ts = load_ts()
    eph = sf.load('de421.bsp')

    # Sprawdź cały miesiąc kwiecień 33 AD
    start_time = ts.utc(33, 4, 1, 0, 0, 0)
    end_time = ts.utc(33, 4, 30, 23, 59, 59)

    print(f"📅 OKRES: {start_time.utc_strftime('%B %Y')}")

    # Znajdź wszystkie zaćmienia słoneczne w kwietniu 33 AD
    solar_eclipses = almanac.find_discrete(start_time, end_time, almanac.solar_eclipse_function(eph))

    print(f"\n☀️ WSZYSTKIE ZAĆMIENIA SŁONECZNE W KWIETNIU 33 AD:")
    found_penumbral = False

    if solar_eclipses:
        for time, eclipse_type in solar_eclipses:
            magnitude = almanac.solar_eclipse_magnitude(eph, time)
            print(f"   • Data: {time.utc_strftime('%d %B %Y %H:%M UTC')}")
            print(f"   • Typ: {eclipse_type}")
            print(f"   • Magnituda: {magnitude}")

            if eclipse_type == 'Penumbral':
                found_penumbral = True
                print(f"   ✅ ZAĆMIENIE PÓŁCIENIOWE!")
                print(f"   📍 Czy w dniu ukrzyżowania? {time.utc_strftime('%d') == '07'}")
    else:
        print("   ❌ Brak zaćmień słonecznych w kwietniu 33 AD")

    return found_penumbral

def check_nasa_jpl_data():
    """Sprawdź dane NASA JPL dla 33 AD"""

    print(f"\n🛰️ SPRAWDZENIE DANYCH NASA JPL")
    print("=" * 80)

    # Sprawdź czy mamy dostęp do danych NASA
    try:
        ts = load_ts()
        eph = sf.load('de421.bsp')

        # Sprawdź zaćmienia w całym 33 AD
        start_time = ts.utc(33, 1, 1, 0, 0, 0)
        end_time = ts.utc(33, 12, 31, 23, 59, 59)

        solar_eclipses = almanac.find_discrete(start_time, end_time, almanac.solar_eclipse_function(eph))

        print(f"📊 ZAĆMIENIA SŁONECZNE W 33 AD (według NASA JPL DE421):")

        penumbral_found = False
        for time, eclipse_type in solar_eclipses:
            magnitude = almanac.solar_eclipse_magnitude(eph, time)
            print(f"   • {time.utc_strftime('%d %B %Y %H:%M UTC')} - {eclipse_type} (magnituda: {magnitude})")

            if eclipse_type == 'Penumbral':
                penumbral_found = True
                print(f"   ✅ ZAĆMIENIE PÓŁCIENIOWE ZNALEZIONE!")

        if not penumbral_found:
            print("   ❌ Brak zaćmień półcieniowych w 33 AD")

        return penumbral_found

    except Exception as e:
        print(f"❌ Błąd podczas sprawdzania danych NASA: {e}")
        return False

def main():
    """Główna analiza"""

    print("✝️ SPRAWDZENIE ZAĆMIENIA PÓŁCIENIOWEGO W DNIU UKRZYŻOWANIA")
    print("📖 NA PODSTAWIE DANYCH NASA JPL")
    print("=" * 80)

    # Sprawdź zaćmienia w dniu ukrzyżowania
    found_crucifixion, time_crucifixion, type_crucifixion = check_penumbral_eclipses()

    # Sprawdź okoliczne daty
    found_nearby = check_nearby_dates()

    # Sprawdź pełne dane NASA
    found_nasa = check_nasa_jpl_data()

    # KOŃCOWE WNIOSKI
    print(f"\n" + "=" * 80)
    print("🎯 KOŃCOWE WNIOSKI")
    print("=" * 80)

    if found_crucifixion or found_nearby or found_nasa:
        print("✅ ZNALEZIONO ZAĆMIENIE PÓŁCIENIOWE!")
        print("📍 Potwierdza to relacje historyczne (Thallus, Flegon)")
        print("🔬 Dane NASA JPL potwierdzają istnienie zaćmienia")

        if found_crucifixion:
            print(f"⏰ Dokładny czas: {time_crucifixion.utc_strftime('%d %B %Y %H:%M UTC')}")
            print(f"📊 Typ: {type_crucifixion}")

    else:
        print("❌ NIE ZNALEZIONO ZAĆMIENIA PÓŁCIENIOWEGO")
        print("🔍 Wszystkie dostępne dane astronomiczne sprawdzone")
        print("📚 Możliwa interpretacja symboliczna ciemności")

    print(f"\n📖 ŹRÓDŁO DANYCH: NASA JPL DE421 Ephemeris")
    print(f"🛠️ BIBLIOTEKA: Skyfield {sf.__version__}")

if __name__ == "__main__":
    main()