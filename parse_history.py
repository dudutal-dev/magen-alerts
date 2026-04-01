import json, subprocess, sys

def fetch_url(url):
    r = subprocess.run([
        'curl', '-s', '-f', '--max-time', '20',
        '-A', 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)',
        '-H', 'Accept: application/json, text/plain, */*',
        '-H', 'Accept-Language: he-IL,he;q=0.9',
        url
    ], capture_output=True, text=True)
    return r.stdout

SOURCES = [
    'https://api.tzevaadom.co.il/alerts-history/',
    'https://www.oref.org.il/WarningMessages/alert/History/AlertsHistory.json',
]

def extract_cities(raw):
    if isinstance(raw, list):
        result = []
        for c in raw:
            if isinstance(c, str) and c.strip():
                result.append(c.strip())
            elif isinstance(c, dict):
                name = c.get('name') or c.get('city') or c.get('label') or ''
                if name:
                    result.append(str(name))
        return result
    if isinstance(raw, str):
        return [x.strip() for x in raw.split(',') if x.strip()]
    return []

for url in SOURCES:
    try:
        raw = fetch_url(url).strip().lstrip('\xef\xbb\xbf')
        if not raw:
            print(f'Empty response from {url}')
            continue
        data = json.loads(raw)
        if not isinstance(data, list):
            print(f'Not a list from {url}: {type(data)}')
            continue
        print(f'Got {len(data)} entries from {url}')
        if len(data) == 0:
            continue
        # Show first entry for debugging
        print(f'First entry keys: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0])}')
        print(f'First entry: {json.dumps(data[0], ensure_ascii=False)[:200]}')
        
        normalized = []
        for h in data:
            if not isinstance(h, dict):
                continue
            date = (h.get('alertDate') or h.get('time') or h.get('alerttime') or 
                    h.get('date') or h.get('startTime') or '')
            if isinstance(date, (int, float)):
                from datetime import datetime, timezone
                date = datetime.fromtimestamp(date, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            cat = str(h.get('category') or h.get('cat') or '1')
            cities = extract_cities(h.get('cities') or h.get('data') or h.get('areas') or [])
            if cities:
                normalized.append({'alertDate': str(date), 'category': cat, 'data': cities})
        
        print(f'Normalized: {len(normalized)} entries with cities')
        if normalized:
            json.dump(normalized, open('history.json', 'w'), ensure_ascii=False)
            print(f'Saved to history.json')
            sys.exit(0)
    except Exception as e:
        print(f'Error from {url}: {e}')

print('All sources failed')
