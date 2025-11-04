#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGA HARVESTER CHRONOLOGII ŚWIATA
Od JD 0 (4713 BC) do dziś - pełna historia ludzkości
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'harvesters'))

from scientific_archives_harvester import ScientificArchivesHarvester
from datetime import datetime, timedelta
import time
import math

def julian_day_to_date(jd):
    """Konwersja Julian Day na datę"""
    a = jd + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    
    return year, month, day

def date_to_julian_day(year, month, day):
    """Konwersja daty na Julian Day"""
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

def generate_astronomical_data_for_epoch(jd_start, jd_end, epoch_name, period, harvester):
    """Generuj dane astronomiczne dla całej epoki używając bibliotek naukowych"""
    events = []
    
    # Oblicz liczbę dni w epoce
    days_in_epoch = jd_end - jd_start
    
    # PRECYZJA GODZINNA dla WSZYSTKICH EPOK - co godzinę dla całego zakresu
    step_days = 1/24  # Co godzinę dla CAŁEJ chronologii świata
    precision = "hourly"
    
    print(f"📊 Epoka {epoch_name}: {days_in_epoch:,} dni, krok {step_days} dni (co godzinę), precyzja {precision}")
    
    # Generuj dane dla całej epoki
    current_jd = jd_start
    event_count = 0
    
    iterations = 0
    while current_jd <= jd_end:
        iterations += 1
        # Usunięto limit debugowania - pełna generacja
        
        try:
            # Konwertuj JD na datę i czas (uwzględniając godziny)
            year, month, day = julian_day_to_date(current_jd)
            
            # Oblicz czas z ułamkowej części dnia
            fractional_day = current_jd - int(current_jd)
            hours = int(fractional_day * 24)
            minutes = int((fractional_day * 24 - hours) * 60)
            seconds = int(((fractional_day * 24 - hours) * 60 - minutes) * 60)
            
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            date_str = f"{abs(int(year)):04d}-{int(month):02d}-{int(day):02d}"
            
            # 1. POZYCJA SŁOŃCA (astropy)
            try:
                from astropy.time import Time
                from astropy.coordinates import get_sun, EarthLocation, AltAz
                
                # Dla dat przed 1900 rokiem pomiń transformację do horyzontu (problemy z IERS)
                use_horizon = current_year >= 1900
                
                # Czas astronomiczny
                time_utc = Time(date_str)
                location = EarthLocation.of_site('greenwich')
                
                # Pozycja Słońca
                sun = get_sun(time_utc)
                
                # Współrzędne ekliptyczne zawsze
                ra_deg = sun.ra.degree
                dec_deg = sun.dec.degree
                
                # Pozycja w horyzoncie tylko dla dat po 1900 roku
                if use_horizon:
                    altaz_frame = AltAz(obstime=time_utc, location=location)
                    sun_altaz = sun.transform_to(altaz_frame)
                    azimuth_deg = sun_altaz.az.degree
                    altitude_deg = sun_altaz.alt.degree
                else:
                    azimuth_deg = 0.0  # Placeholder
                    altitude_deg = 0.0  # Placeholder
                
                solar_event = {
                    'id': f"sun_{epoch_name.lower()}_{current_jd:.3f}",
                    'title': f"Pozycja Słońca - {date_str} {time_str}",
                    'date': date_str,
                    'time': time_str,
                    'category': 'ASTRONOMY',
                    'subcategory': 'SOLAR_POSITION',
                    'source': 'astropy_library',
                    'content': f"Słońce: Azymut {azimuth_deg:.1f}°, Wysokość {altitude_deg:.1f}°, RA {ra_deg:.1f}°, Dec {dec_deg:.1f}°",
                    'epoch': epoch_name,
                    'epoch_period': period,
                    'julian_day': current_jd,
                    'metadata': {
                        'celestial_object': 'Sun',
                        'azimuth_deg': azimuth_deg,
                        'altitude_deg': altitude_deg,
                        'ra_deg': ra_deg,
                        'dec_deg': dec_deg,
                        'timestamp_jd': current_jd,
                        'precision': precision,
                        'library': 'astropy',
                        'horizon_coords': use_horizon
                    }
                }
                events.append(solar_event)
                event_count += 1
                
            except Exception as e:
                # Jeśli astropy nie działa dla tej daty, pomiń
                pass
            
            # 2. FAZA KSIĘŻYCA (ephem)
            try:
                import ephem
                
                # Obserwator w Greenwich
                observer = ephem.Observer()
                observer.lat = '51.5'
                observer.lon = '0.0'
                observer.date = date_str
                
                moon = ephem.Moon()
                moon.compute(observer)
                
                phase = moon.moon_phase
                if phase < 0.1:
                    phase_name = "Nów Księżyca"
                elif phase < 0.4:
                    phase_name = "Pierwsza Kwadra"
                elif phase < 0.6:
                    phase_name = "Pełnia Księżyca"
                elif phase < 0.9:
                    phase_name = "Ostatnia Kwadra"
                else:
                    phase_name = "Nów Księżyca"
                
                lunar_event = {
                    'id': f"moon_{epoch_name.lower()}_{current_jd:.3f}",
                    'title': f"{phase_name} - {date_str} {time_str}",
                    'date': date_str,
                    'time': time_str,
                    'category': 'ASTRONOMY',
                    'subcategory': 'LUNAR_PHASE',
                    'source': 'ephem_library',
                    'content': f"Księżyc: {phase_name}, Faza: {phase:.3f}",
                    'epoch': epoch_name,
                    'epoch_period': period,
                    'julian_day': current_jd,
                    'metadata': {
                        'celestial_object': 'Moon',
                        'phase_name': phase_name,
                        'phase_value': phase,
                        'altitude_deg': float(moon.alt) * 180.0 / 3.14159,
                        'azimuth_deg': float(moon.az) * 180.0 / 3.14159,
                        'timestamp_jd': current_jd,
                        'precision': precision,
                        'library': 'ephem'
                    }
                }
                events.append(lunar_event)
                event_count += 1
                
            except Exception as e:
                # Jeśli ephem nie działa dla tej daty, pomiń
                pass
            
            # 3. WSCHODY/ZACHODY SŁOŃCA (ephem) - co godzinę dla pełnej precyzji
            try:
                import ephem
                
                observer = ephem.Observer()
                observer.lat = '51.5'
                observer.lon = '0.0'
                observer.date = date_str
                
                sun = ephem.Sun()
                
                # Wschód słońca
                try:
                    sunrise = observer.next_rising(sun)
                    sunrise_dt = ephem.Date(sunrise).datetime()
                    sunrise_str = sunrise_dt.strftime('%H:%M:%S')
                    
                    sunrise_event = {
                        'id': f"sunrise_{epoch_name.lower()}_{current_jd:.3f}",
                        'title': f"Wschód Słońca - {date_str} {time_str}",
                        'date': date_str,
                        'time': sunrise_str,
                        'category': 'ASTRONOMY',
                        'subcategory': 'SOLAR_EVENT',
                        'source': 'ephem_library',
                        'content': f"Wschód Słońca o {sunrise_str} UTC",
                        'epoch': epoch_name,
                        'epoch_period': period,
                        'julian_day': current_jd,
                        'metadata': {
                            'event_type': 'sunrise',
                            'timestamp_jd': current_jd,
                            'location': 'Greenwich',
                            'precision': 'minute',
                            'library': 'ephem'
                        }
                    }
                    events.append(sunrise_event)
                    event_count += 1
                    
                except:
                    pass
                
                # Zachód słońca
                try:
                    sunset = observer.next_setting(sun)
                    sunset_dt = ephem.Date(sunset).datetime()
                    sunset_str = sunset_dt.strftime('%H:%M:%S')
                    
                    sunset_event = {
                        'id': f"sunset_{epoch_name.lower()}_{current_jd:.3f}",
                        'title': f"Zachód Słońca - {date_str} {time_str}",
                        'date': date_str,
                        'time': sunset_str,
                        'category': 'ASTRONOMY',
                        'subcategory': 'SOLAR_EVENT',
                        'source': 'ephem_library',
                        'content': f"Zachód Słońca o {sunset_str} UTC",
                        'epoch': epoch_name,
                        'epoch_period': period,
                        'julian_day': current_jd,
                        'metadata': {
                            'event_type': 'sunset',
                            'timestamp_jd': current_jd,
                            'location': 'Greenwich',
                            'precision': 'minute',
                            'library': 'ephem'
                        }
                    }
                    events.append(sunset_event)
                    event_count += 1
                    
                except:
                    pass
                
            except Exception as e:
                # Jeśli ephem nie działa dla tej daty, pomiń
                pass
            
            # 4. ZAĆMIENIA SŁONECZNE I KSIĘŻYCOWE (skyfield) - tylko dla epok po 1900 roku
            if current_year >= 1900:  # Skyfield tylko dla współczesnych dat
                try:
                    import skyfield.api as skyfield_api
                    from skyfield import almanac

                    # Ładuj dane efemeryd
                    ts = skyfield_api.load.timescale()
                    eph = skyfield_api.load('de421.bsp')

                    # Funkcje do sprawdzania zaćmień
                    def solar_eclipses_at(t):
                        """Sprawdź zaćmienia słoneczne"""
                        return almanac.solar_eclipse_function(eph, eph['earth'])(t)

                    def lunar_eclipses_at(t):
                        """Sprawdź zaćmienia księżycowe"""
                        return almanac.lunar_eclipse_function(eph, eph['earth'])(t)

                    # Sprawdź zaćmienia dla tej godziny
                    t = ts.utc(current_year, current_month, current_day, hours, minutes, seconds)

                    # Zaćmienie słoneczne
                    solar_eclipse_value = solar_eclipses_at(t)
                    if solar_eclipse_value > 0.9:  # Prawie całkowite zaćmienie
                        eclipse_type = "zaćmienie słoneczne"
                        if solar_eclipse_value > 0.99:
                            eclipse_type = "zaćmienie słoneczne całkowite"
                        elif solar_eclipse_value > 0.95:
                            eclipse_type = "zaćmienie słoneczne częściowe"

                        solar_eclipse_event = {
                            'id': f"solar_eclipse_{epoch_name.lower()}_{current_jd:.3f}",
                            'title': f"Zaćmienie Słońca - {date_str} {time_str}",
                            'date': date_str,
                            'time': time_str,
                            'category': 'ASTRONOMY',
                            'subcategory': 'SOLAR_ECLIPSE',
                            'source': 'skyfield_library',
                            'content': f"{eclipse_type.capitalize()} widoczne z Ziemi, magnituda: {solar_eclipse_value:.3f}",
                            'epoch': epoch_name,
                            'epoch_period': period,
                            'julian_day': current_jd,
                            'metadata': {
                                'eclipse_type': 'solar',
                                'magnitude': solar_eclipse_value,
                                'visibility': 'global' if solar_eclipse_value > 0.95 else 'partial',
                                'timestamp_jd': current_jd,
                                'precision': 'hour',
                                'library': 'skyfield'
                            }
                        }
                        events.append(solar_eclipse_event)
                        event_count += 1

                    # Zaćmienie księżycowe
                    lunar_eclipse_value = lunar_eclipses_at(t)
                    if lunar_eclipse_value > 0.9:  # Widoczne zaćmienie
                        eclipse_type = "zaćmienie księżycowe"
                        if lunar_eclipse_value > 0.99:
                            eclipse_type = "zaćmienie księżycowe całkowite"
                        elif lunar_eclipse_value > 0.95:
                            eclipse_type = "zaćmienie księżycowe częściowe"

                        lunar_eclipse_event = {
                            'id': f"lunar_eclipse_{epoch_name.lower()}_{current_jd:.3f}",
                            'title': f"Zaćmienie Księżyca - {date_str} {time_str}",
                            'date': date_str,
                            'time': time_str,
                            'category': 'ASTRONOMY',
                            'subcategory': 'LUNAR_ECLIPSE',
                            'source': 'skyfield_library',
                            'content': f"{eclipse_type.capitalize()}, Księżyc staje się czerwony (krwawy księżyc), magnituda: {lunar_eclipse_value:.3f}",
                            'epoch': epoch_name,
                            'epoch_period': period,
                            'julian_day': current_jd,
                            'metadata': {
                                'eclipse_type': 'lunar',
                                'magnitude': lunar_eclipse_value,
                                'blood_moon': True if lunar_eclipse_value > 0.95 else False,
                                'color': 'red' if lunar_eclipse_value > 0.9 else 'normal',
                                'timestamp_jd': current_jd,
                                'precision': 'hour',
                                'library': 'skyfield'
                            }
                        }
                        events.append(lunar_eclipse_event)
                        event_count += 1

                except Exception as e:
                    # Jeśli skyfield nie działa, pomiń
                    pass

            # 5. KOMETY - kometa Halleya i inne ważne komety
            try:
                # Kometa Halleya - okres około 76 lat
                # Znane pojawienia: 1986, 2061, 2134, etc.
                halley_appearances = [
                    (date_to_julian_day(1986, 2, 9), "Pojawienie się komety Halleya 1986"),
                    (date_to_julian_day(2061, 7, 28), "Pojawienie się komety Halleya 2061"),
                    (date_to_julian_day(2134, 11, 27), "Pojawienie się komety Halleya 2134"),
                    # Historyczne pojawienia
                    (date_to_julian_day(1066, 3, 20), "Pojawienie się komety Halleya 1066 (Bitwa pod Hastings)"),
                    (date_to_julian_day(1456, 6, 8), "Pojawienie się komety Halleya 1456"),
                    (date_to_julian_day(1531, 8, 26), "Pojawienie się komety Halleya 1531"),
                    (date_to_julian_day(1607, 10, 27), "Pojawienie się komety Halleya 1607"),
                    (date_to_julian_day(1682, 9, 15), "Pojawienie się komety Halleya 1682 (odkrycie Edmunda Halleya)"),
                    (date_to_julian_day(1758, 12, 25), "Pojawienie się komety Halleya 1758"),
                    (date_to_julian_day(1835, 11, 5), "Pojawienie się komety Halleya 1835"),
                    (date_to_julian_day(1910, 5, 20), "Pojawienie się komety Halleya 1910"),
                ]

                for halley_jd, description in halley_appearances:
                    if jd_start <= halley_jd <= jd_end:
                        halley_year, halley_month, halley_day = julian_day_to_date(halley_jd)
                        halley_date_str = f"{abs(int(halley_year)):04d}-{int(halley_month):02d}-{int(halley_day):02d}"

                        halley_event = {
                            'id': f"halley_comet_{halley_year}_{epoch_name.lower()}_{halley_jd:.0f}",
                            'title': f"{description} - {halley_date_str}",
                            'date': halley_date_str,
                            'time': "00:00:00",
                            'category': 'ASTRONOMY',
                            'subcategory': 'COMET',
                            'source': 'historical_astronomical_records',
                            'content': f"Kometa Halleya widoczna z Ziemi, okres orbitalny około 76 lat. {description}",
                            'epoch': epoch_name,
                            'epoch_period': period,
                            'julian_day': halley_jd,
                            'metadata': {
                                'comet_name': 'Halley',
                                'orbital_period_years': 76,
                                'visibility': 'naked_eye',
                                'historical_significance': 'regular_comet',
                                'description': description,
                                'timestamp_jd': halley_jd,
                                'precision': 'day',
                                'library': 'historical'
                            }
                        }
                        events.append(halley_event)
                        event_count += 1

            except Exception as e:
                # Jeśli obliczenia komety nie działają, pomiń
                pass

            # 6. KONIUNKCJE PLANETARNE - bliskie spotkania planet
            try:
                # Sprawdź koniunkcje planet dla ważnych wydarzeń
                # Lista ważnych koniunkcji historycznych
                planetary_conjunctions = [
                    # Wielka koniunkcja Jowisz-Saturn 2020
                    (date_to_julian_day(2020, 12, 21), "Wielka koniunkcja Jowisza i Saturna", "Jupiter-Saturn"),
                    # Inne historyczne koniunkcje
                    (date_to_julian_day(1961, 2, 4), "Koniunkcja Merkurego i Jowisza", "Mercury-Jupiter"),
                    (date_to_julian_day(2000, 5, 5), "Koniunkcja Wenus i Jowisza", "Venus-Jupiter"),
                ]

                for conj_jd, description, planets in planetary_conjunctions:
                    if jd_start <= conj_jd <= jd_end:
                        try:
                            conj_year, conj_month, conj_day = julian_day_to_date(conj_jd)
                            conj_date_str = f"{abs(conj_year):04d}-{conj_month:02d}-{conj_day:02d}"

                            conjunction_event = {
                                'id': f"planetary_conjunction_{epoch_name.lower()}_{conj_jd:.0f}",
                                'title': f"Koniunkcja planetarna: {planets} - {conj_date_str}",
                                'date': conj_date_str,
                                'time': "00:00:00",
                                'category': 'ASTRONOMY',
                                'subcategory': 'PLANETARY_CONJUNCTION',
                                'source': 'astronomical_calculations',
                                'content': f"{description}, planety widoczne blisko siebie na niebie",
                                'epoch': epoch_name,
                                'epoch_period': period,
                                'julian_day': conj_jd,
                                'metadata': {
                                    'conjunction_type': 'planetary',
                                    'planets': planets,
                                    'description': description,
                                    'visibility': 'naked_eye',
                                    'timestamp_jd': conj_jd,
                                    'precision': 'day',
                                    'library': 'astronomical'
                                }
                            }
                            events.append(conjunction_event)
                            event_count += 1
                        except:
                            pass

            except Exception as e:
                # Jeśli koniunkcje nie działają, pomiń
                pass

            # 7. ROJE METEORÓW - coroczne zjawiska
            try:
                # Lista ważnych rojów meteorów
                meteor_showers = [
                    ("Leonidy", "Listopad", "Radiant w Lwie", "Kometa Tempel-Tuttle", 17),
                    ("Geminidy", "Grudzień", "Radiant w Bliźniętach", "Asteroida 3200 Phaethon", 13),
                    ("Kwadranci", "Styczeń", "Radiant w Wolarzu", "Kometa nieznana", 3),
                    ("Lirydy", "Kwiecień", "Radiant w Lutni", "Kometa Thatcher", 18),
                    ("Perseidy", "Sierpień", "Radiant w Perseuszu", "Kometa Swift-Tuttle", 12),
                    ("Orionidy", "Październik", "Radiant w Orionie", "Kometa Halleya", 21),
                ]

                # Dla każdej epoki, dodaj coroczne roje meteorów
                for shower_name, month_name, radiant, parent, peak_day in meteor_showers:
                    # Oblicz daty dla tej epoki (co roku)
                    if days_in_epoch > 365:  # Tylko dla dłuższych epok
                        years_in_epoch = int(days_in_epoch / 365.25)
                        for year_offset in range(years_in_epoch):
                            try:
                                # Szacunkowa data w tej epoce
                                if year >= 0:  # AD
                                    meteor_year = year + year_offset
                                    if meteor_year > 2025:  # Nie przekraczaj współczesności
                                        break
                                else:  # BC
                                    meteor_year = year - year_offset
                                    if meteor_year < -4000:  # Nie sięgaj zbyt daleko w przeszłość
                                        break

                                # Miesiąc na podstawie nazwy
                                month_map = {
                                    "Styczeń": 1, "Luty": 2, "Marzec": 3, "Kwiecień": 4,
                                    "Maj": 5, "Czerwiec": 6, "Lipiec": 7, "Sierpień": 8,
                                    "Wrzesień": 9, "Październik": 10, "Listopad": 11, "Grudzień": 12
                                }
                                meteor_month = month_map.get(month_name, 1)

                                meteor_jd = date_to_julian_day(meteor_year, meteor_month, peak_day)
                                if jd_start <= meteor_jd <= jd_end:
                                    meteor_date_str = f"{abs(int(meteor_year)):04d}-{meteor_month:02d}-{peak_day:02d}"

                                    meteor_event = {
                                        'id': f"meteor_shower_{shower_name.lower()}_{epoch_name.lower()}_{meteor_jd:.0f}",
                                        'title': f"Rój meteorów {shower_name} - {meteor_date_str}",
                                        'date': meteor_date_str,
                                        'time': "00:00:00",
                                        'category': 'ASTRONOMY',
                                        'subcategory': 'METEOR_SHOWER',
                                        'source': 'astronomical_records',
                                        'content': f"Rój {shower_name}, radiant {radiant}, maksimum {peak_day} {month_name}",
                                        'epoch': epoch_name,
                                        'epoch_period': period,
                                        'julian_day': meteor_jd,
                                        'metadata': {
                                            'shower_name': shower_name,
                                            'radiant': radiant,
                                            'parent_body': parent,
                                            'peak_date': f"{peak_day} {month_name}",
                                            'frequency': 'annual',
                                            'timestamp_jd': meteor_jd,
                                            'precision': 'day',
                                            'library': 'astronomical'
                                        }
                                    }
                                    events.append(meteor_event)
                                    event_count += 1

                            except:
                                continue

            except Exception as e:
                # Jeśli meteory nie działają, pomiń
                pass

            # 8. SUPERNOWE I GWIAZDY ZMIENNE - historyczne wydarzenia
            try:
                # Lista ważnych supernowych i gwiazd zmiennych
                stellar_events = [
                    (date_to_julian_day(1054, 7, 4), "Supernowa 1054", "Mgławica Kraba", "Crab Nebula"),
                    (date_to_julian_day(1604, 10, 9), "Supernowa Keplera", "Gwiazdozbiór Wężownika", "Kepler's Supernova"),
                    (date_to_julian_day(1987, 2, 23), "Supernowa 1987A", "Wielki Obłok Magellana", "SN 1987A"),
                ]

                for stellar_jd, event_name, location, description in stellar_events:
                    if jd_start <= stellar_jd <= jd_end:
                        try:
                            stellar_year, stellar_month, stellar_day = julian_day_to_date(stellar_jd)
                            stellar_date_str = f"{abs(stellar_year):04d}-{stellar_month:02d}-{stellar_day:02d}"

                            stellar_event = {
                                'id': f"stellar_event_{event_name.lower().replace(' ', '_')}_{epoch_name.lower()}_{stellar_jd:.0f}",
                                'title': f"{event_name} - {stellar_date_str}",
                                'date': stellar_date_str,
                                'time': "00:00:00",
                                'category': 'ASTRONOMY',
                                'subcategory': 'STELLAR_EVENT',
                                'source': 'historical_astronomical_records',
                                'content': f"{event_name} w {location} - {description}",
                                'epoch': epoch_name,
                                'epoch_period': period,
                                'julian_day': stellar_jd,
                                'metadata': {
                                    'event_type': 'supernova' if 'supernowa' in event_name.lower() else 'variable_star',
                                    'location': location,
                                    'description': description,
                                    'visibility': 'naked_eye',
                                    'historical_significance': 'major_astronomical_event',
                                    'timestamp_jd': stellar_jd,
                                    'precision': 'day',
                                    'library': 'historical'
                                }
                            }
                            events.append(stellar_event)
                            event_count += 1
                        except:
                            pass

            except Exception as e:
                # Jeśli wydarzenia gwiazdowe nie działają, pomiń
                pass
            
            # Progress co 1000 wydarzeń
            if event_count % 1000 == 0 and event_count > 0:
                print(f"  🔭 Wygenerowano {event_count:,} wydarzeń... (JD: {current_jd:.0f})")
            
        except Exception as e:
            # Jeśli data jest nieprawidłowa, pomiń
            pass
        
        # Następny krok
        current_jd += step_days
    
    print(f"✅ Łącznie wydarzeń dla {epoch_name}: {event_count:,}")
    return events

def run_mega_world_chronology_harvester():
    """MEGA HARVESTER - cała chronologia świata od JD 0 używając bibliotek astronomicznych"""
    print("🌍 MEGA HARVESTER CHRONOLOGII ŚWIATA")
    print("🕐 Od JD 0 (4713 BC) do dziś - BIBLIOTEKI ASTRONOMICZNE")
    print("=" * 80)
    
    harvester = ScientificArchivesHarvester(rate_limit=1.0)
    
    # Sprawdź biblioteki
    from harvesters.scientific_archives_harvester import ASTRO_LIBS_AVAILABLE
    
    if not ASTRO_LIBS_AVAILABLE:
        print("❌ Biblioteki astronomiczne niedostępne!")
        return
    
    print("✅ Biblioteki astronomiczne dostępne - rozpoczynam zbieranie")
    print(f"🕐 Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Julian Day 0 = 1 stycznia 4713 BC
    jd_start = 0
    jd_today = date_to_julian_day(2025, 11, 4)  # Dzisiaj
    
    print(f"📅 JD START: {jd_start} (4713 BC)")
    print(f"📅 JD TODAY: {jd_today} (2025-11-04)")
    print(f"📊 ŁĄCZNIE DNI: {jd_today - jd_start:,} dni = {(jd_today - jd_start)/365.25:.0f} lat")
    
    # Podziel na epoki historyczne dla zarządzania danymi
    epochs = [
        (0, 1000000, "PREHISTORIA", "4713 BC - 1440 BC"),
        (1000000, 1500000, "ANTYK WCZESNY", "1440 BC - 72 BC"), 
        (1500000, 1721426, "ANTYK PÓŹNY", "72 BC - 1 AD"),
        (1721426, 2000000, "WCZESNE ŚREDNIOWIECZE", "1 AD - 763 AD"),
        (2000000, 2300000, "WYSOKIE ŚREDNIOWIECZE", "763 AD - 1584 AD"),
        (2300000, 2400000, "NOWOŻYTNOŚĆ", "1584 AD - 1858 AD"),
        (2400000, 2450000, "WIEK XIX", "1858 AD - 1995 AD"),
        (2450000, jd_today, "WSPÓŁCZESNOŚĆ", "1995 AD - DZIŚ")
    ]
    
    print(f"\n📚 EPOKI DO ZBADANIA: {len(epochs)}")
    for i, (jd_start_epoch, jd_end_epoch, name, period) in enumerate(epochs, 1):
        days = jd_end_epoch - jd_start_epoch
        years = days / 365.25
        print(f"  {i}. {name}: JD {jd_start_epoch:,} - {jd_end_epoch:,} ({days:,} dni, {years:.0f} lat) - {period}")
    
    all_events = []
    total_events = 0
    
    for epoch_num, (jd_start_epoch, jd_end_epoch, epoch_name, period) in enumerate(epochs, 1):
        print(f"\n🏛️ EPOKA {epoch_num}/{len(epochs)}: {epoch_name}")
        print(f"📅 {period}")
        print(f"🕐 Start zbierania: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 60)
        
        # Konwertuj JD na daty
        start_year, start_month, start_day = julian_day_to_date(jd_start_epoch)
        end_year, end_month, end_day = julian_day_to_date(jd_end_epoch)
        
        # Generuj dane astronomiczne używając bibliotek naukowych dla CAŁEJ epoki
        print(f"🔭 Generuję dane astronomiczne z bibliotek naukowych dla {epoch_name}")
        
        try:
            # Zbieraj dane astronomiczne dla całej epoki używając bibliotek
            astronomical_events = generate_astronomical_data_for_epoch(
                jd_start_epoch, jd_end_epoch, epoch_name, period, harvester
            )
            
            print(f"✅ Wygenerowano {len(astronomical_events):,} wydarzeń astronomicznych dla {epoch_name}")
            all_events.extend(astronomical_events)
            total_events += len(astronomical_events)
            
            # Zapisz dane epoki
            epoch_filename = f"astronomical_{epoch_name.lower().replace(' ', '_')}.json"
            harvester.save_results({f'epoch_{epoch_name}': astronomical_events}, epoch_filename)
            
            # Statystyki epoki
            if astronomical_events:
                print(f"📋 PRÓBKA Z {epoch_name}:")
                for j, event in enumerate(astronomical_events[:3], 1):
                    title = event.get('title', 'Nieznany')[:60]
                    source = event.get('source', 'N/A')
                    date = event.get('date', 'N/A')
                    print(f"  {j}. {title}")
                    print(f"     📅 {date} | 📡 {source}")
            
            # Kategorie w epoce
            categories = {}
            sources = {}
            for event in astronomical_events:
                cat = event.get('subcategory', 'UNKNOWN')
                src = event.get('source', 'UNKNOWN')
                categories[cat] = categories.get(cat, 0) + 1
                sources[src] = sources.get(src, 0) + 1
            
            print(f"📊 KATEGORIE W {epoch_name}:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {cat}: {count}")
            
            print(f"📡 ŹRÓDŁA W {epoch_name}:")
            for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"   {src}: {count}")
            
            print(f"💾 Zapisano: {epoch_filename}")
            print(f"📈 Łącznie zebranych wydarzeń: {total_events:,}")
            
        except Exception as e:
            print(f"❌ Błąd dla {epoch_name}: {e}")
        
        # Przejście do następnej epoki bez przerwy
        if epoch_num < len(epochs):
            print(f"\n🚀 Przechodzę natychmiast do następnej epoki...")
    
    # FINALNE ZAPISANIE MEGA CHRONOLOGII
    print(f"\n🌍 FINALNE ZAPISANIE MEGA CHRONOLOGII ŚWIATA")
    print(f"🕐 Koniec zbierania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Zapisz wszystko jako mega plik
    harvester.save_results({'mega_world_chronology': all_events}, 'MEGA_WORLD_CHRONOLOGY.json')
    
    print(f"\n🎯 MEGA HARVESTING CHRONOLOGII ŚWIATA UKOŃCZONY!")
    print(f"💎 {len(all_events):,} wydarzeń z {(jd_today)/365.25:.0f} lat historii")
    print(f"🔬 Źródła: astropy, ephem, skyfield, astroquery - ŻADNYCH API!")

if __name__ == "__main__":
    run_mega_world_chronology_harvester()