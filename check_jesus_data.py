import json

with open('astronomical_wczesne_średniowiecze.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data.get('results', {}).get('epoch_WCZESNE ŚREDNIOWIECZE', [])
jesus_events = []
for event in events:
    date = event.get('date', '')
    if date.startswith(('0030-', '0031-', '0032-', '0033-')):
        jesus_events.append(event)

print(f'Znaleziono {len(jesus_events)} wydarzeń dla lat 30-33 AD')
print('Przykładowe wydarzenia:')
for i, event in enumerate(jesus_events[:10]):
    print(f'{i+1}. {event["date"]} - {event["title"]} ({event["subcategory"]})')

# Sprawdź unikalne kategorie
categories = set()
for event in jesus_events:
    categories.add(event.get('subcategory', 'UNKNOWN'))

print(f'\nUnikalne kategorie wydarzeń: {sorted(categories)}')