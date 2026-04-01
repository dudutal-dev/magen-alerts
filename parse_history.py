import json, subprocess
from datetime import datetime, timezone

def fetch(url):
    r = subprocess.run([
        'curl', '-s', '-f', '--max-time', '20',
        '-A', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)',
        '-H', 'Accept: application/json',
        url
    ], capture_output=True, text=True)
    return r.stdout.strip().lstrip('\xef\xbb\xbf')

# Load existing history
try:
    existing = json.load(open('history.json'))
    if not isinstance(existing, list):
        existing = []
except:
    existing = []

print(f'Existing history: {len(existing)} entries')

# Check current alerts.json — if active alert, add to history
try:
    current = json.load(open('alerts.json'))
    cities = current.get('data', [])
    if cities and isinstance(cities, list) and len(cities) > 0:
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        cat = str(current.get('cat') or current.get('category') or '1')
        new_entry = {'alertDate': now, 'category': cat, 'data': cities}
        # Add only if not duplicate of last entry
        if not existing or existing[0].get('data') != cities:
            existing.insert(0, new_entry)
            print(f'Added current alert: {cities[:3]}')
except Exception as e:
    print(f'alerts.json check: {e}')

# Try to get real history from oref (may work sometimes)
urls = [
    'https://www.oref.org.il/WarningMessages/alert/History/AlertsHistory.json',
    'https://api.tzevaadom.co.il/alerts-history/',
]

for url in urls:
    try:
        raw = fetch(url)
        if not raw:
            print(f'Empty: {url}')
            continue
        data = json.loads(raw)
        if not isinstance(data, list) or not data:
            print(f'Bad data from {url}')
            continue
        
        # Normalize
        normalized = []
        for h in data:
            if not isinstance(h, dict):
                continue
            date = (h.get('alertDate') or h.get('time') or '')
            if isinstance(date, (int,float)):
                date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            cat = str(h.get('category') or h.get('cat') or '1')
            raw_cities = h.get('cities') or h.get('data') or []
            if isinstance(raw_cities, str):
                cities = [x.strip() for x in raw_cities.split(',') if x.strip()]
            elif isinstance(raw_cities, list):
                cities = [c.get('name', '') if isinstance(c, dict) else str(c) for c in raw_cities]
                cities = [c for c in cities if c]
            else:
                cities = []
            if cities:
                normalized.append({'alertDate': str(date), 'category': cat, 'data': cities})
        
        if normalized:
            print(f'Got {len(normalized)} from {url}')
            # Merge with existing
            existing_dates = {e.get('alertDate') for e in existing}
            for e in normalized:
                if e['alertDate'] not in existing_dates:
                    existing.append(e)
            existing.sort(key=lambda x: x.get('alertDate',''), reverse=True)
            break
        else:
            print(f'No valid entries from {url}')
    except Exception as e:
        print(f'Error {url}: {e}')

# Keep max 500 entries
existing = existing[:500]
json.dump(existing, open('history.json', 'w'), ensure_ascii=False)
print(f'Saved {len(existing)} entries to history.json')
