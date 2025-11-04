import json

with open('astronomical_antyk_wczesny.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data.get('results', {}).get('epoch_ANTYK WCZESNY', [])
jesus_events = []
for event in events:
    date = event.get('date', '')
    if date.startswith(('0030-', '0031-', '0032-', '0033-')):
        jesus_events.append(event)

print(f'Znaleziono {len(jesus_events)} wydarzeń dla lat 30-33 AD w wczesnym antyku')
if jesus_events:
    for i, event in enumerate(jesus_events[:5]):
        print(f'{i+1}. {event["date"]} - {event["title"]} ({event["subcategory"]})')
else:
    print('Brak wydarzeń dla tego okresu')

# Sprawdź zakres dat w tym pliku
all_dates = set()
for event in events[:100]:  # sprawdź pierwsze 100 wydarzeń
    date = event.get('date', '')
    if date:
        year = date[:4]
        all_dates.add(year)

print(f'\nZakres lat w pliku wczesnego antyku: {sorted(all_dates)}')