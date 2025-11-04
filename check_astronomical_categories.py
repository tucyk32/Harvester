#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_astronomical_categories.py
---------------------------------
SPRAWDZA JAKIE KATEGORIE WYDARZEŃ ASTRONOMICZNYCH ZOSTAŁY ZEBRANE
"""

import json

def check_categories():
    """Sprawdza kategorie wydarzeń astronomicznych"""

    print("📊 KATEGORIE WYDARZEŃ ASTRONOMICZNYCH (30-33 AD)")
    print("=" * 60)

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

        print(f"Wczytano {len(jesus_events)} wydarzeń astronomicznych z lat 30-33 AD")

        categories = {}
        subcategories = {}

        for event in jesus_events:
            cat = event.get('category', 'UNKNOWN')
            subcat = event.get('subcategory', 'UNKNOWN')

            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

            if subcat not in subcategories:
                subcategories[subcat] = 0
            subcategories[subcat] += 1

        print("\nKATEGORIE:")
        for cat, count in sorted(categories.items()):
            print(f"   {cat}: {count} wydarzeń")

        print("\nPODKATEGORIE:")
        for subcat, count in sorted(subcategories.items()):
            print(f"   {subcat}: {count} wydarzeń")

        print("\n🔍 PRZYKŁADOWE WYDARZENIA:")
        for i, event in enumerate(jesus_events[:15]):
            print(f"   {i+1}. {event['date']} - {event['title']}")
            print(f"      Kategoria: {event.get('category', 'N/A')}")
            print(f"      Podkategoria: {event.get('subcategory', 'N/A')}")
            if event.get('content'):
                print(f"      Treść: {event['content'][:100]}...")
            print()

        # Sprawdź czy są jakieś wzmianki o zaćmieniach w treści
        eclipse_mentions = []
        for event in jesus_events:
            title = event.get('title', '').lower()
            content = event.get('content', '').lower()
            if ('zaćmienie' in title or 'zaćmienie' in content or
                'eclipse' in title or 'eclipse' in content):
                eclipse_mentions.append(event)

        print(f"🔍 WZMIANKI O ZAĆMIENIACH W TEKŚCIE: {len(eclipse_mentions)}")
        for event in eclipse_mentions:
            print(f"   📅 {event['date']} - {event['title']}")
            if event.get('content'):
                print(f"      📝 {event['content']}")

    except Exception as e:
        print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    check_categories()