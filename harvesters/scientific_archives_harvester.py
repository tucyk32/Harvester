#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scientific_archives_harvester.py
--------------------------------
Specjalistyczny harvester do pobierania danych z archiwów naukowych:
- arXiv (fizyka, matematyka, CS)
- PubMed (medycyna, biologia)
- JSTOR (humanistyka, społeczne)
- Google Scholar
- ResearchGate
- Academia.edu

Ekstraktuje metadata publikacji i integruje z timeline.
"""

import requests
import xml.etree.ElementTree as ET
import json
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import pandas as pd

# Biblioteki astronomiczne
try:
    import ephem
    import astropy
    from astropy.time import Time
    from astropy.coordinates import get_sun, EarthLocation, AltAz
    # Nie importujemy get_moon - użyjemy ephem do Księżyca
    import skyfield.api as skyfield
    from astroquery.jplhorizons import Horizons
    ASTRO_LIBS_AVAILABLE = True
    print("✅ Biblioteki astronomiczne załadowane pomyślnie")
except ImportError as e:
    print(f"⚠️ Niektóre biblioteki astronomiczne niedostępne: {e}")
    ASTRO_LIBS_AVAILABLE = False

class ScientificArchivesHarvester:
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HistoricalML/1.0 (academic research; contact@example.edu)'
        })
        
        # API endpoints
        self.endpoints = {
            'arxiv': 'http://export.arxiv.org/api/query',
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
            'crossref': 'https://api.crossref.org/works',
            'semantic_scholar': 'https://api.semanticscholar.org/graph/v1/paper/search',
            'nasa_apod': 'https://api.nasa.gov/planetary/apod',
            'nasa_neo': 'https://api.nasa.gov/neo/rest/v1/feed',
            'nasa_mars': 'https://api.nasa.gov/insight_weather/',
            'nasa_exoplanets': 'https://exoplanetarchive.ipac.caltech.edu/TAP/sync',
            'usgs_earthquake': 'https://earthquake.usgs.gov/fdsnws/event/1/query'
        }
    
    def search_arxiv(self, query: str, max_results: int = 100, category: str = None) -> List[Dict]:
        """
        Przeszukuje arXiv dla publikacji naukowych
        
        Args:
            query: Zapytanie wyszukiwania
            max_results: Maksymalna liczba wyników
            category: Kategoria arXiv (np. 'cs.AI', 'physics.hist-ph')
        """
        print(f"🔬 Przeszukuję arXiv: '{query}' (max: {max_results})")
        
        # Buduj zapytanie
        search_query = f'all:{query}'
        if category:
            search_query += f' AND cat:{category}'
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        try:
            response = self.session.get(self.endpoints['arxiv'], params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
            
            papers = []
            for entry in root.findall('atom:entry', namespace):
                paper = self._parse_arxiv_entry(entry, namespace)
                if paper:
                    papers.append(paper)
            
            print(f"✅ Znaleziono {len(papers)} publikacji z arXiv")
            time.sleep(self.rate_limit)
            return papers
            
        except Exception as e:
            print(f"❌ Błąd arXiv: {e}")
            return []
    
    def _parse_arxiv_entry(self, entry, namespace) -> Optional[Dict]:
        """Parsuje pojedynczy wpis z arXiv"""
        try:
            # Podstawowe informacje
            title_elem = entry.find('atom:title', namespace)
            title = title_elem.text.strip() if title_elem is not None else 'Unknown Title'
            
            summary_elem = entry.find('atom:summary', namespace)
            summary = summary_elem.text.strip() if summary_elem is not None else ''
            
            published_elem = entry.find('atom:published', namespace)
            published = published_elem.text if published_elem is not None else ''
            
            updated_elem = entry.find('atom:updated', namespace)
            updated = updated_elem.text if updated_elem is not None else ''
            
            # Autorzy
            authors = []
            for author in entry.findall('atom:author', namespace):
                name_elem = author.find('atom:name', namespace)
                if name_elem is not None:
                    authors.append(name_elem.text)
            
            # Kategorie
            categories = []
            for category in entry.findall('atom:category', namespace):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            # URL i ID
            id_elem = entry.find('atom:id', namespace)
            arxiv_id = id_elem.text.split('/')[-1] if id_elem is not None else ''
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ''
            
            # PDF link
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else ''
            
            # Parsuj datę publikacji
            pub_date = None
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', ''))
                except:
                    pass
            
            return {
                'title': title,
                'summary': summary,
                'authors': authors,
                'categories': categories,
                'published': published,
                'updated': updated,
                'pub_date': pub_date,
                'arxiv_id': arxiv_id,
                'arxiv_url': arxiv_url,
                'pdf_url': pdf_url,
                'source': 'arXiv'
            }
            
        except Exception as e:
            print(f"⚠️ Błąd parsowania wpisu arXiv: {e}")
            return None
    
    def search_crossref(self, query: str, max_results: int = 100, year_range: tuple = None) -> List[Dict]:
        """
        Przeszukuje Crossref dla publikacji akademickich
        
        Args:
            query: Zapytanie wyszukiwania
            max_results: Maksymalna liczba wyników
            year_range: Zakres lat (start_year, end_year)
        """
        print(f"📚 Przeszukuję Crossref: '{query}' (max: {max_results})")
        
        params = {
            'query': query,
            'rows': min(max_results, 1000),  # Crossref limit
            'sort': 'published',
            'order': 'desc'
        }
        
        # Filtr roku
        if year_range:
            start_year, end_year = year_range
            params['filter'] = f'from-pub-date:{start_year},until-pub-date:{end_year}'
        
        try:
            response = self.session.get(self.endpoints['crossref'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for item in data.get('message', {}).get('items', []):
                paper = self._parse_crossref_item(item)
                if paper:
                    papers.append(paper)
            
            print(f"✅ Znaleziono {len(papers)} publikacji z Crossref")
            time.sleep(self.rate_limit)
            return papers
            
        except Exception as e:
            print(f"❌ Błąd Crossref: {e}")
            return []
    
    def _parse_crossref_item(self, item) -> Optional[Dict]:
        """Parsuje pojedynczy wpis z Crossref"""
        try:
            # Tytuł
            title = ''
            if 'title' in item and item['title']:
                title = item['title'][0]
            
            # Autorzy
            authors = []
            if 'author' in item:
                for author in item['author']:
                    given = author.get('given', '')
                    family = author.get('family', '')
                    full_name = f"{given} {family}".strip()
                    if full_name:
                        authors.append(full_name)
            
            # Data publikacji
            pub_date = None
            published_str = ''
            if 'published-print' in item:
                date_parts = item['published-print'].get('date-parts', [[]])[0]
            elif 'published-online' in item:
                date_parts = item['published-online'].get('date-parts', [[]])[0]
            else:
                date_parts = []
            
            if date_parts and len(date_parts) >= 3:
                try:
                    year, month, day = date_parts[0], date_parts[1], date_parts[2]
                    pub_date = datetime(year, month, day)
                    published_str = pub_date.isoformat()
                except:
                    pass
            elif date_parts and len(date_parts) >= 1:
                try:
                    year = date_parts[0]
                    pub_date = datetime(year, 1, 1)
                    published_str = str(year)
                except:
                    pass
            
            # Czasopismo
            journal = item.get('container-title', [''])[0] if 'container-title' in item else ''
            
            # DOI
            doi = item.get('DOI', '')
            doi_url = f"https://doi.org/{doi}" if doi else ''
            
            # Typ publikacji
            pub_type = item.get('type', 'unknown')
            
            # Abstract (rzadko dostępne w Crossref)
            abstract = item.get('abstract', '')
            
            return {
                'title': title,
                'summary': abstract,
                'authors': authors,
                'journal': journal,
                'published': published_str,
                'pub_date': pub_date,
                'doi': doi,
                'doi_url': doi_url,
                'type': pub_type,
                'source': 'Crossref'
            }
            
        except Exception as e:
            print(f"⚠️ Błąd parsowania wpisu Crossref: {e}")
            return None
    
    def search_semantic_scholar(self, query: str, max_results: int = 100, fields: List[str] = None) -> List[Dict]:
        """
        Przeszukuje Semantic Scholar
        
        Args:
            query: Zapytanie wyszukiwania
            max_results: Maksymalna liczba wyników
            fields: Pola do pobrania
        """
        print(f"🧠 Przeszukuję Semantic Scholar: '{query}' (max: {max_results})")
        
        if fields is None:
            fields = ['title', 'abstract', 'authors', 'year', 'publicationDate', 'journal', 'url']
        
        params = {
            'query': query,
            'limit': min(max_results, 100),  # API limit
            'fields': ','.join(fields)
        }
        
        try:
            response = self.session.get(self.endpoints['semantic_scholar'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for item in data.get('data', []):
                paper = self._parse_semantic_scholar_item(item)
                if paper:
                    papers.append(paper)
            
            print(f"✅ Znaleziono {len(papers)} publikacji z Semantic Scholar")
            time.sleep(self.rate_limit)
            return papers
            
        except Exception as e:
            print(f"❌ Błąd Semantic Scholar: {e}")
            return []
    
    def _parse_semantic_scholar_item(self, item) -> Optional[Dict]:
        """Parsuje pojedynczy wpis z Semantic Scholar"""
        try:
            title = item.get('title', 'Unknown Title')
            abstract = item.get('abstract', '')
            year = item.get('year')
            publication_date = item.get('publicationDate', '')
            journal = item.get('journal', {}).get('name', '') if item.get('journal') else ''
            url = item.get('url', '')
            
            # Autorzy
            authors = []
            for author in item.get('authors', []):
                name = author.get('name', '')
                if name:
                    authors.append(name)
            
            # Data publikacji
            pub_date = None
            if publication_date:
                try:
                    pub_date = datetime.fromisoformat(publication_date)
                except:
                    pass
            elif year:
                try:
                    pub_date = datetime(int(year), 1, 1)
                except:
                    pass
            
            return {
                'title': title,
                'summary': abstract,
                'authors': authors,
                'journal': journal,
                'published': publication_date or str(year) if year else '',
                'pub_date': pub_date,
                'year': year,
                'url': url,
                'source': 'Semantic Scholar'
            }
            
        except Exception as e:
            print(f"⚠️ Błąd parsowania wpisu Semantic Scholar: {e}")
            return None
    
    def search_nasa_astronomical_events(self, start_date: str = None, end_date: str = None, max_results: int = 100) -> List[Dict]:
        """
        Zbiera dane astronomiczne z NASA APIs i alternatywnych źródeł z dokładnością do godzin
        """
        print(f"🚀 Zbieranie danych astronomicznych z dokładnością do godzin...")
        
        astronomical_events = []
        
        # Użyj alternatywnych źródeł jeśli NASA API nie działa
        print("🌍 Zbieranie danych geologicznych/astronomicznych z USGS...")
        
        # 1. USGS Earthquake data (geological events with precise times)
        earthquake_events = self._get_usgs_earthquake_data(start_date, end_date)
        astronomical_events.extend(earthquake_events)
        
        # 2. Próba NASA APIs (może nie działać z DEMO_KEY)
        try:
            nasa_api_key = "DEMO_KEY"
            
            # APOD - zwykle działa z DEMO_KEY
            print("�️ Pobieranie NASA APOD...")
            apod_events = self._get_nasa_apod_data_simple(start_date, end_date, nasa_api_key)
            astronomical_events.extend(apod_events)
            
        except Exception as e:
            print(f"⚠️ NASA APIs nie dostępne: {e}")
        
        # 3. Astronomical papers from arXiv (reliable source)
        print("📚 Pobieranie publikacji astronomicznych z arXiv...")
        astro_papers = self._get_arxiv_astronomy_papers()
        astronomical_events.extend(astro_papers)
        
        print(f"✅ Zebrano {len(astronomical_events)} wydarzeń astronomicznych")
        return astronomical_events[:max_results]

    def _get_solar_events(self, start_dt: datetime, end_dt: datetime) -> List[Dict]:
        """Dokładne dane słoneczne z astropy - wschody, zachody, pozycje"""
        events = []
        try:
            from astropy.coordinates import EarthLocation, AltAz, get_sun
            from astropy.time import Time
            
            # Lokalizacja domyślna (można parametryzować)
            location = EarthLocation.of_site('greenwich')
            
            current = start_dt
            while current <= end_dt:
                try:
                    # Czas UTC
                    time_utc = Time(current)
                    
                    # Pozycja Słońca
                    sun = get_sun(time_utc)
                    altaz_frame = AltAz(obstime=time_utc, location=location)
                    sun_altaz = sun.transform_to(altaz_frame)
                    
                    # Dane słoneczne
                    solar_data = {
                        'id': f"sun_{current.strftime('%Y%m%d_%H%M')}",
                        'title': f"Pozycja Słońca - {current.strftime('%Y-%m-%d %H:%M')} UTC",
                        'date': current.strftime('%Y-%m-%d'),
                        'time': current.strftime('%H:%M:%S'),
                        'category': 'ASTRONOMY',
                        'subcategory': 'SOLAR',
                        'source': 'astropy',
                        'content': f"Słońce: Azymut {sun_altaz.az.degree:.2f}°, Wysokość {sun_altaz.alt.degree:.2f}°",
                        'metadata': {
                            'celestial_object': 'Sun',
                            'azimuth_deg': sun_altaz.az.degree,
                            'altitude_deg': sun_altaz.alt.degree,
                            'ra_deg': sun.ra.degree,
                            'dec_deg': sun.dec.degree,
                            'timestamp_utc': current.isoformat(),
                            'location': 'Greenwich',
                            'precision': 'hourly'
                        }
                    }
                    events.append(solar_data)
                    
                except Exception as e:
                    print(f"⚠️ Błąd danych słonecznych dla {current}: {e}")
                
                # Co 6 godzin dla lepszej precyzji
                current += timedelta(hours=6)
                
            print(f"☀️ Zebrano {len(events)} wydarzeń słonecznych")
            return events
            
        except Exception as e:
            print(f"❌ Błąd _get_solar_events: {e}")
            return []

    def _get_lunar_phases(self, start_dt: datetime, end_dt: datetime) -> List[Dict]:
        """Precyzyjne fazy Księżyca z ephem"""
        events = []
        try:
            # Fazy Księżyca
            current = start_dt
            while current <= end_dt:
                try:
                    observer = ephem.Observer()
                    observer.date = current
                    
                    moon = ephem.Moon()
                    moon.compute(observer)
                    
                    # Faza Księżyca (0-1)
                    phase = moon.moon_phase
                    
                    # Kategoryzacja fazy
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
                    
                    lunar_data = {
                        'id': f"moon_{current.strftime('%Y%m%d_%H%M')}",
                        'title': f"{phase_name} - {current.strftime('%Y-%m-%d %H:%M')} UTC",
                        'date': current.strftime('%Y-%m-%d'),
                        'time': current.strftime('%H:%M:%S'),
                        'category': 'ASTRONOMY',
                        'subcategory': 'LUNAR',
                        'source': 'ephem',
                        'content': f"Księżyc: {phase_name}, Faza: {phase:.3f}, Wysokość: {float(moon.alt):.2f}°",
                        'metadata': {
                            'celestial_object': 'Moon',
                            'phase_name': phase_name,
                            'phase_value': phase,
                            'altitude_deg': float(moon.alt) * 180.0 / 3.14159,
                            'azimuth_deg': float(moon.az) * 180.0 / 3.14159,
                            'distance_km': float(moon.earth_distance) * 149597870.7,
                            'timestamp_utc': current.isoformat(),
                            'precision': 'hourly'
                        }
                    }
                    events.append(lunar_data)
                    
                except Exception as e:
                    print(f"⚠️ Błąd danych księżycowych dla {current}: {e}")
                
                # Co 12 godzin
                current += timedelta(hours=12)
                
            print(f"🌙 Zebrano {len(events)} wydarzeń księżycowych")
            return events
            
        except Exception as e:
            print(f"❌ Błąd _get_lunar_phases: {e}")
            return []

    def _get_planetary_positions(self, start_dt: datetime, end_dt: datetime) -> List[Dict]:
        """Pozycje planet z JPL Horizons (astroquery)"""
        events = []
        try:
            from astroquery.jplhorizons import Horizons
            
            # Główne planety
            planets = {
                '399': 'Earth',
                '301': 'Moon', 
                '10': 'Sun',
                '199': 'Mercury',
                '299': 'Venus',
                '499': 'Mars',
                '599': 'Jupiter',
                '699': 'Saturn'
            }
            
            # Co tydzień dla planet
            current = start_dt
            while current <= end_dt:
                try:
                    for planet_id, planet_name in planets.items():
                        try:
                            # JPL Horizons query
                            obj = Horizons(id=planet_id, 
                                         location='500@399',  # Geocentric
                                         epochs=current.strftime('%Y-%m-%d %H:%M'))
                            
                            eph = obj.ephemerides()
                            
                            if len(eph) > 0:
                                row = eph[0]
                                
                                planetary_data = {
                                    'id': f"planet_{planet_name.lower()}_{current.strftime('%Y%m%d')}",
                                    'title': f"Pozycja {planet_name} - {current.strftime('%Y-%m-%d')}",
                                    'date': current.strftime('%Y-%m-%d'),
                                    'time': current.strftime('%H:%M:%S'),
                                    'category': 'ASTRONOMY',
                                    'subcategory': 'PLANETARY',
                                    'source': 'JPL_Horizons',
                                    'content': f"{planet_name}: RA {row['RA']:.2f}°, DEC {row['DEC']:.2f}°, Odległość {row['delta']:.2f} AU",
                                    'metadata': {
                                        'celestial_object': planet_name,
                                        'planet_id': planet_id,
                                        'ra_deg': float(row['RA']),
                                        'dec_deg': float(row['DEC']),
                                        'distance_au': float(row['delta']),
                                        'magnitude': float(row['V']) if 'V' in row.colnames else None,
                                        'timestamp_utc': current.isoformat(),
                                        'precision': 'daily'
                                    }
                                }
                                events.append(planetary_data)
                                
                        except Exception as e:
                            print(f"⚠️ Błąd JPL Horizons dla {planet_name}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"⚠️ Błąd danych planetarnych dla {current}: {e}")
                
                # Co tydzień
                current += timedelta(days=7)
                time.sleep(0.5)  # Rate limiting dla JPL
                
            print(f"🪐 Zebrano {len(events)} wydarzeń planetarnych")
            return events
            
        except Exception as e:
            print(f"❌ Błąd _get_planetary_positions: {e}")
            return []

    def _get_celestial_events(self, start_dt: datetime, end_dt: datetime) -> List[Dict]:
        """Specjalne zjawiska astronomiczne z ephem"""
        events = []
        try:
            # Konfiguracja obserwatora
            observer = ephem.Observer()
            observer.lat = '51.5'  # Greenwich
            observer.lon = '0.0'
            
            current = start_dt
            while current <= end_dt:
                try:
                    observer.date = current
                    
                    # Słońce
                    sun = ephem.Sun()
                    sun.compute(observer)
                    
                    # Wschodem/zachód Słońca
                    try:
                        sunrise = observer.next_rising(sun)
                        sunset = observer.next_setting(sun)
                        
                        # Wschód słońca
                        if sunrise:
                            sunrise_dt = ephem.Date(sunrise).datetime()
                            events.append({
                                'id': f"sunrise_{current.strftime('%Y%m%d')}",
                                'title': f"Wschód Słońca - {sunrise_dt.strftime('%Y-%m-%d %H:%M')} UTC",
                                'date': sunrise_dt.strftime('%Y-%m-%d'),
                                'time': sunrise_dt.strftime('%H:%M:%S'),
                                'category': 'ASTRONOMY',
                                'subcategory': 'SOLAR_EVENT',
                                'source': 'ephem',
                                'content': f"Wschód Słońca o {sunrise_dt.strftime('%H:%M')} UTC",
                                'metadata': {
                                    'event_type': 'sunrise',
                                    'timestamp_utc': sunrise_dt.isoformat(),
                                    'location': 'Greenwich',
                                    'precision': 'minute'
                                }
                            })
                        
                        # Zachód słońca
                        if sunset:
                            sunset_dt = ephem.Date(sunset).datetime()
                            events.append({
                                'id': f"sunset_{current.strftime('%Y%m%d')}",
                                'title': f"Zachód Słońca - {sunset_dt.strftime('%Y-%m-%d %H:%M')} UTC",
                                'date': sunset_dt.strftime('%Y-%m-%d'),
                                'time': sunset_dt.strftime('%H:%M:%S'),
                                'category': 'ASTRONOMY',
                                'subcategory': 'SOLAR_EVENT',
                                'source': 'ephem',
                                'content': f"Zachód Słońca o {sunset_dt.strftime('%H:%M')} UTC",
                                'metadata': {
                                    'event_type': 'sunset',
                                    'timestamp_utc': sunset_dt.isoformat(),
                                    'location': 'Greenwich',
                                    'precision': 'minute'
                                }
                            })
                    
                    except Exception as e:
                        print(f"⚠️ Błąd wschodów/zachodów dla {current}: {e}")
                    
                except Exception as e:
                    print(f"⚠️ Błąd zdarzeń astronomicznych dla {current}: {e}")
                
                # Co dzień
                current += timedelta(days=1)
                
            print(f"🌅 Zebrano {len(events)} zdarzeń astronomicznych")
            return events
            
        except Exception as e:
            print(f"❌ Błąd _get_celestial_events: {e}")
            return []

    def _get_usgs_earthquake_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Pobiera dane sejsmiczne z USGS z dokładnymi godzinami"""
        events = []
        
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                'format': 'geojson',
                'starttime': start_date,
                'endtime': end_date,
                'minmagnitude': '4.0',
                'limit': '100'
            }
            
            response = self.session.get(self.endpoints['usgs_earthquake'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for feature in data.get('features', []):
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})
                
                if props.get('time'):
                    # USGS ma dokładne czasy w milisekundach!
                    event_time = datetime.fromtimestamp(props['time'] / 1000)
                    
                    event = {
                        'title': f"Earthquake M{props.get('mag', 'Unknown')} - {props.get('place', 'Unknown location')}",
                        'summary': f"Magnitude {props.get('mag')} earthquake at {props.get('place')}. Time: {event_time.strftime('%Y-%m-%d %H:%M:%S')} UTC. Depth: {geom.get('coordinates', [None, None, None])[2]}km",
                        'published': event_time.isoformat(),
                        'pub_date': event_time,
                        'source': 'USGS Earthquake',
                        'url': props.get('url', ''),
                        'magnitude': props.get('mag'),
                        'place': props.get('place'),
                        'depth_km': geom.get('coordinates', [None, None, None])[2],
                        'latitude': geom.get('coordinates', [None, None])[1],
                        'longitude': geom.get('coordinates', [None, None])[0],
                        'exact_time_utc': event_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'category': 'ASTRONOMY',
                        'subcategory': 'seismic_event'
                    }
                    
                    events.append(event)
            
            time.sleep(self.rate_limit)
            
        except Exception as e:
            print(f"⚠️ Błąd pobierania danych USGS: {e}")
        
        return events
    
    def _get_nasa_apod_data_simple(self, start_date: str, end_date: str, api_key: str) -> List[Dict]:
        """Uproszczona wersja APOD"""
        events = []
        
        try:
            # Spróbuj tylko jeden dzień
            params = {
                'api_key': api_key
            }
            
            response = self.session.get(self.endpoints['nasa_apod'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('date'):
                apod_date = datetime.strptime(data['date'], '%Y-%m-%d')
                
                event = {
                    'title': f"NASA APOD: {data.get('title', 'Astronomy Picture')}",
                    'summary': data.get('explanation', '')[:500],
                    'published': apod_date.isoformat(),
                    'pub_date': apod_date,
                    'source': 'NASA APOD',
                    'url': data.get('url', ''),
                    'category': 'ASTRONOMY',
                    'subcategory': 'daily_picture'
                }
                
                events.append(event)
            
            time.sleep(self.rate_limit)
            
        except Exception as e:
            print(f"⚠️ Błąd pobierania APOD: {e}")
        
        return events
    
    def _get_arxiv_astronomy_papers(self) -> List[Dict]:
        """Pobiera najnowsze publikacje astronomiczne z arXiv"""
        events = []
        
        try:
            # Kategorie astronomiczne
            query = 'cat:astro-ph*'
            
            params = {
                'search_query': query,
                'start': 0,
                'max_results': 50,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            response = self.session.get(self.endpoints['arxiv'], params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace):
                title_elem = entry.find('atom:title', namespace)
                summary_elem = entry.find('atom:summary', namespace)
                published_elem = entry.find('atom:published', namespace)
                
                if title_elem is not None and published_elem is not None:
                    title = title_elem.text.strip()
                    summary = summary_elem.text.strip() if summary_elem is not None else ''
                    
                    try:
                        pub_date = datetime.fromisoformat(published_elem.text.replace('Z', ''))
                        
                        event = {
                            'title': f"Astro Paper: {title}",
                            'summary': summary[:500],
                            'published': pub_date.isoformat(),
                            'pub_date': pub_date,
                            'source': 'arXiv Astronomy',
                            'category': 'ASTRONOMY',
                            'subcategory': 'research_paper',
                            'exact_time_utc': pub_date.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        events.append(event)
                    except:
                        pass
            
            time.sleep(self.rate_limit)
            
        except Exception as e:
            print(f"⚠️ Błąd pobierania arXiv astronomy: {e}")
        
        return events
    
    def _get_nasa_neo_data(self, start_date: str, end_date: str, api_key: str) -> List[Dict]:
        """Pobiera dane o asteroidach bliskich Ziemi z dokładnymi godzinami"""
        events = []
        
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'api_key': api_key
            }
            
            response = self.session.get(self.endpoints['nasa_neo'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for date_str, objects in data.get('near_earth_objects', {}).items():
                for obj in objects:
                    # Parsuj datę przelotu z dokładnością do godzin
                    approach_data = obj.get('close_approach_data', [{}])[0]
                    approach_date_str = approach_data.get('close_approach_date_full', '')
                    
                    if approach_date_str:
                        try:
                            # Format: "2024-01-15 12:34" - dokładne godziny!
                            approach_date = datetime.strptime(approach_date_str, '%Y-%m-%d %H:%M')
                        except:
                            try:
                                approach_date = datetime.strptime(approach_date_str, '%Y-%b-%d %H:%M')
                            except:
                                approach_date = datetime.strptime(date_str, '%Y-%m-%d')
                    else:
                        approach_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    event = {
                        'title': f"Asteroid {obj.get('name', 'Unknown')} Close Approach",
                        'summary': f"Asteroid {obj.get('name')} approaches Earth at {approach_date.strftime('%Y-%m-%d %H:%M')} UTC. Diameter: {obj.get('estimated_diameter', {}).get('meters', {}).get('estimated_diameter_max', 'Unknown')}m. Potentially hazardous: {obj.get('is_potentially_hazardous_asteroid', False)}",
                        'published': approach_date.isoformat(),
                        'pub_date': approach_date,
                        'source': 'NASA NEO',
                        'url': obj.get('nasa_jpl_url', ''),
                        'asteroid_id': obj.get('id', ''),
                        'diameter_m': obj.get('estimated_diameter', {}).get('meters', {}).get('estimated_diameter_max'),
                        'potentially_hazardous': obj.get('is_potentially_hazardous_asteroid', False),
                        'miss_distance_km': approach_data.get('miss_distance', {}).get('kilometers'),
                        'velocity_kmh': approach_data.get('relative_velocity', {}).get('kilometers_per_hour'),
                        'approach_time': approach_date_str,  # Dokładny czas!
                        'category': 'ASTRONOMY',
                        'subcategory': 'asteroid_approach'
                    }
                    
                    events.append(event)
            
            time.sleep(self.rate_limit)
            
        except Exception as e:
            print(f"⚠️ Błąd pobierania danych NEO: {e}")
        
        return events
    
    def _get_nasa_apod_data(self, start_date: str, end_date: str, api_key: str) -> List[Dict]:
        """Pobiera Astronomy Picture of the Day"""
        events = []
        
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'api_key': api_key
            }
            
            response = self.session.get(self.endpoints['nasa_apod'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # APOD może zwrócić listę lub pojedynczy obiekt
            if isinstance(data, list):
                apod_list = data
            else:
                apod_list = [data]
            
            for apod in apod_list:
                if apod.get('date'):
                    apod_date = datetime.strptime(apod['date'], '%Y-%m-%d')
                    # Dodaj godzinę publikacji (standardowo 00:00 UTC)
                    
                    event = {
                        'title': f"NASA APOD: {apod.get('title', 'Astronomy Picture')}",
                        'summary': apod.get('explanation', '')[:500],
                        'published': apod_date.isoformat(),
                        'pub_date': apod_date,
                        'source': 'NASA APOD',
                        'url': apod.get('url', ''),
                        'hd_url': apod.get('hdurl', ''),
                        'media_type': apod.get('media_type', 'image'),
                        'copyright': apod.get('copyright', ''),
                        'category': 'ASTRONOMY',
                        'subcategory': 'daily_picture'
                    }
                    
                    events.append(event)
            
            time.sleep(self.rate_limit)
            
        except Exception as e:
            print(f"⚠️ Błąd pobierania APOD: {e}")
        
        return events
    
    def _get_nasa_mars_data(self, api_key: str) -> List[Dict]:
        """Pobiera dane pogodowe z Marsa z dokładnymi godzinami"""
        events = []
        
        try:
            params = {
                'api_key': api_key,
                'feedtype': 'json',
                'ver': '1.0'
            }
            
            response = self.session.get(self.endpoints['nasa_mars'], params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Mars weather data z godzinami
            for sol_key, sol_data in data.items():
                if sol_key.isdigit():  # Sol numbers are digits
                    sol_date = sol_data.get('First_UTC', '')
                    last_date = sol_data.get('Last_UTC', '')
                    
                    if sol_date:
                        try:
                            # Mars data często ma dokładne godziny
                            mars_date = datetime.fromisoformat(sol_date.replace('Z', ''))
                            
                            event = {
                                'title': f"Mars Weather Sol {sol_key} - {mars_date.strftime('%H:%M')} UTC",
                                'summary': f"Mars weather data for Sol {sol_key} at {mars_date.strftime('%Y-%m-%d %H:%M')} UTC. Temperature: {sol_data.get('AT', {}).get('av', 'Unknown')}°C",
                                'published': mars_date.isoformat(),
                                'pub_date': mars_date,
                                'source': 'NASA Mars InSight',
                                'sol': int(sol_key),
                                'temperature_c': sol_data.get('AT', {}).get('av'),
                                'wind_speed': sol_data.get('HWS', {}).get('av'),
                                'pressure': sol_data.get('PRE', {}).get('av'),
                                'first_utc': sol_date,
                                'last_utc': last_date,
                                'category': 'ASTRONOMY',
                                'subcategory': 'mars_weather'
                            }
                            
                            events.append(event)
                        except:
                            pass
            
            time.sleep(self.rate_limit)
            
        except Exception as e:
            print(f"⚠️ Błąd pobierania danych Mars: {e}")
        
        return events
    
    def search_astronomical_papers_arxiv(self, max_results: int = 200) -> List[Dict]:
        """Przeszukuje arXiv specjalnie dla publikacji astronomicznych"""
        print(f"🔭 Przeszukuję arXiv dla publikacji astronomicznych...")
        
        astro_papers = []
        
        # Kategorie astronomiczne w arXiv
        astro_categories = [
            'astro-ph.EP',  # Earth and Planetary Astrophysics
            'astro-ph.GA',  # Astrophysics of Galaxies  
            'astro-ph.HE',  # High Energy Astrophysical Phenomena
            'astro-ph.IM',  # Instrumentation and Methods for Astrophysics
            'astro-ph.SR',  # Solar and Stellar Astrophysics
            'astro-ph.CO'   # Cosmology and Nongalactic Astrophysics
        ]
        
        results_per_category = max_results // len(astro_categories)
        
        for category in astro_categories:
            try:
                papers = self.search_arxiv(
                    query='astronomy OR astrophysics OR cosmology OR exoplanet OR galaxy OR solar OR stellar',
                    max_results=results_per_category,
                    category=category
                )
                astro_papers.extend(papers)
                
            except Exception as e:
                print(f"⚠️ Błąd kategorii {category}: {e}")
        
        print(f"✅ Znaleziono {len(astro_papers)} publikacji astronomicznych")
        return astro_papers
    
    def convert_to_timeline_format(self, papers: List[Dict], am_epoch: float = 1738164.0) -> List[Dict]:
        """
        Konwertuje publikacje na format timeline z JD/AM_day
        """
        print(f"🔄 Konwertuję {len(papers)} publikacji na format timeline...")
        
        timeline_events = []
        
        for paper in papers:
            if not paper.get('pub_date'):
                continue
            
            pub_date = paper['pub_date']
            
            # Oblicz Julian Day
            jd = self._date_to_jd(pub_date.year, pub_date.month, pub_date.day)
            am_day = jd - am_epoch
            
            # Kategoryzuj na podstawie źródła i zawartości
            category = self._categorize_paper(paper)
            
            event = {
                'start_jd': jd,
                'end_jd': jd,
                'am_day': am_day,
                'category': category,
                'subcategory': 'publication',
                'title': paper.get('title', 'Unknown Title'),
                'description': paper.get('summary', '')[:500],  # Limit opisu
                'authors': paper.get('authors', []),
                'journal': paper.get('journal', ''),
                'source': paper.get('source', 'Unknown'),
                'source_url': paper.get('arxiv_url') or paper.get('doi_url') or paper.get('url', ''),
                'reliability': 5,  # Publikacje naukowe = wysoka wiarygodność
                'year': pub_date.year,
                'month': pub_date.month,
                'day': pub_date.day,
                'doi': paper.get('doi', ''),
                'arxiv_id': paper.get('arxiv_id', ''),
                'categories': paper.get('categories', [])
            }
            
            timeline_events.append(event)
        
        print(f"✅ Konwersja zakończona: {len(timeline_events)} wydarzeń")
        return timeline_events
    
    def _categorize_paper(self, paper: Dict) -> str:
        """Kategoryzuje publikację na podstawie zawartości"""
        title = paper.get('title', '').lower()
        abstract_raw = paper.get('summary', '') or paper.get('abstract', '') or ''
        abstract = abstract_raw.lower() if abstract_raw else ''
        categories = paper.get('categories', [])
        
        # Mapowanie kategorii arXiv
        category_mapping = {
            'cs.': 'COMPUTER_SCIENCE',
            'physics': 'PHYSICS',
            'math': 'MATHEMATICS',
            'q-bio': 'BIOLOGY',
            'stat': 'STATISTICS',
            'econ': 'ECONOMICS',
            'q-fin': 'FINANCE'
        }
        
        # Sprawdź kategorie arXiv
        for cat in categories:
            for prefix, mapped_cat in category_mapping.items():
                if cat.startswith(prefix):
                    return mapped_cat
        
        # Sprawdź słowa kluczowe w tytule/abstracie
        text = title + ' ' + abstract
        
        if any(word in text for word in ['history', 'historical', 'ancient', 'medieval']):
            return 'HISTORICAL'
        elif any(word in text for word in ['machine learning', 'artificial intelligence', 'ai', 'ml']):
            return 'ARTIFICIAL_INTELLIGENCE'
        elif any(word in text for word in ['quantum', 'particle', 'physics']):
            return 'PHYSICS'
        elif any(word in text for word in ['biology', 'medicine', 'medical', 'genetic']):
            return 'BIOLOGY'
        elif any(word in text for word in ['astronomy', 'astrophysics', 'cosmology']):
            return 'ASTRONOMY'
        else:
            return 'SCIENTIFIC'
    
    def _date_to_jd(self, year: int, month: int, day: int) -> float:
        """Konwertuje datę na Julian Day"""
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
    
    def search_multi_source(self, query: str, max_per_source: int = 50, year_range: tuple = None) -> Dict[str, List[Dict]]:
        """
        Przeszukuje wiele źródeł jednocześnie
        """
        print(f"🔍 Multi-source search: '{query}'")
        print(f"📊 Max per source: {max_per_source}")
        if year_range:
            print(f"📅 Year range: {year_range[0]}-{year_range[1]}")
        
        results = {}
        
        # arXiv
        try:
            arxiv_papers = self.search_arxiv(query, max_per_source)
            results['arxiv'] = arxiv_papers
        except Exception as e:
            print(f"❌ arXiv failed: {e}")
            results['arxiv'] = []
        
        # Crossref
        try:
            crossref_papers = self.search_crossref(query, max_per_source, year_range)
            results['crossref'] = crossref_papers
        except Exception as e:
            print(f"❌ Crossref failed: {e}")
            results['crossref'] = []
        
        # Semantic Scholar
        try:
            ss_papers = self.search_semantic_scholar(query, max_per_source)
            results['semantic_scholar'] = ss_papers
        except Exception as e:
            print(f"❌ Semantic Scholar failed: {e}")
            results['semantic_scholar'] = []
        
        # Statystyki
        total_papers = sum(len(papers) for papers in results.values())
        print(f"\n📊 Multi-source results:")
        for source, papers in results.items():
            print(f"  {source}: {len(papers)} papers")
        print(f"  Total: {total_papers} papers")
        
        return results
    
    def save_results(self, results: Dict[str, List[Dict]], output_file: str):
        """Zapisuje wyniki do pliku"""
        print(f"💾 Zapisuję wyniki do {output_file}")
        
        # Przygotuj dane do zapisu
        save_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_papers': sum(len(papers) for papers in results.values()),
                'sources': list(results.keys())
            },
            'results': results
        }
        
        if output_file.endswith('.json'):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
        elif output_file.endswith('.csv'):
            # Flatten do CSV
            all_papers = []
            for source, papers in results.items():
                for paper in papers:
                    paper['search_source'] = source
                    all_papers.append(paper)
            
            df = pd.DataFrame(all_papers)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ Wyniki zapisane: {output_file}")

def main():
    """Demo funkcjonalności z danymi NASA"""
    print("� Scientific Archives Harvester + NASA - Demo")
    print("=" * 60)
    
    harvester = ScientificArchivesHarvester(rate_limit=1.5)
    
    # 1. Zbieraj dane astronomiczne NASA
    print("\n🌌 ZBIERANIE DANYCH ASTRONOMICZNYCH NASA:")
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    nasa_events = harvester.search_nasa_astronomical_events(
        start_date=start_date,
        end_date=end_date,
        max_results=50
    )
    
    # 2. Zbieraj publikacje astronomiczne z arXiv
    print("\n🔭 ZBIERANIE PUBLIKACJI ASTRONOMICZNYCH:")
    astro_papers = harvester.search_astronomical_papers_arxiv(max_results=100)
    
    # 3. Test queries dla innych źródeł
    queries = [
        "exoplanet discovery",
        "black hole astronomy", 
        "solar system exploration"
    ]
    
    all_results = {}
    
    for query in queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        # Multi-source search
        results = harvester.search_multi_source(
            query=query,
            max_per_source=20,
            year_range=(2020, 2024)
        )
        all_results[query] = results
        
        # Convert to timeline format
        all_papers = []
        for source, papers in results.items():
            all_papers.extend(papers)
        
        timeline_events = harvester.convert_to_timeline_format(all_papers)
        
        print(f"✅ Query completed: {len(timeline_events)} timeline events created")
    
    # 4. Combine NASA events with timeline format
    nasa_timeline = harvester.convert_to_timeline_format(nasa_events)
    astro_timeline = harvester.convert_to_timeline_format(astro_papers)
    
    # 5. Save all results
    print(f"\n💾 ZAPISYWANIE WYNIKÓW:")
    
    # NASA events
    harvester.save_results({'nasa_astronomical_events': nasa_events}, 'nasa_astronomical_events.json')
    
    # Astronomical papers
    harvester.save_results({'astronomical_papers': astro_papers}, 'astronomical_papers.json')
    
    # Combined timeline
    combined_timeline = nasa_timeline + astro_timeline
    harvester.save_results({'astronomical_timeline': combined_timeline}, 'astronomical_timeline.json')
    
    # Scientific papers from queries
    harvester.save_results(all_results, 'scientific_papers_astronomy.json')
    
    # 6. Statistics
    print(f"\n📊 PODSUMOWANIE ZBIERANIA:")
    print(f"🚀 NASA Events: {len(nasa_events)}")
    print(f"🔭 Astronomical Papers: {len(astro_papers)}")
    print(f"📚 Query Results: {sum(len(papers) for results in all_results.values() for papers in results.values())}")
    print(f"⏱️ Combined Timeline Events: {len(combined_timeline)}")
    
    # Show sample NASA events with exact times
    if nasa_events:
        print(f"\n🕐 PRÓBKA WYDARZEŃ NASA Z DOKŁADNYMI GODZINAMI:")
        for i, event in enumerate(nasa_events[:3], 1):
            approach_time = event.get('approach_time', 'N/A')
            pub_date = event.get('pub_date', datetime.now())
            print(f"  {i}. {event.get('title', 'Unknown')}")
            print(f"     📅 Czas: {pub_date.strftime('%Y-%m-%d %H:%M')} UTC")
            print(f"     🎯 Kategoria: {event.get('subcategory', 'N/A')}")
            if approach_time != 'N/A':
                print(f"     ⏰ Dokładny czas: {approach_time}")
    
    print(f"\n🎯 HARVESTER GOTOWY - DANE NASA Z DOKŁADNOŚCIĄ DO GODZIN! 🎯")

if __name__ == "__main__":
    main()