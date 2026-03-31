import json, subprocess

def normalize_entry(h):
    """Convert any alert format to standard: {alertDate, category, data:[cities]}"""
    # Get date
    date = h.get('alertDate') or h.get('time') or h.get('alerttime') or ''
    # Get category
    cat = h.get('category') or h.get('cat') or 1
    # Get cities - handle objects, strings, or arrays
    raw_cities = h.get('cities') or h.get('data') or []
    if isinstance(raw_cities, str):
        cities = [c.strip() for c in raw_cities.split(',') if c.strip()]
    elif isinstance(raw_cities, list):
        cities = []
        for c in raw_cities:
            if isinstance(c, str):
                cities.append(c)
            elif isinstance(c, dict):
                # Tzofar format: {"name": "תל אביב", ...}
                name = c.get('name') or c.get('city') or c.get('area') or ''
                if name:
                    cities.append(name)
    else:
        cities = []
    return {'alertDate': date, 'category': int(cat), 'data': cities}

def try_tzofar():
    raw = open('hist_raw.txt', encoding='utf-8-sig').read().strip()
    d = json.loads(raw)
    assert isinstance(d, list), f'not a list: {type(d)}'
    normalized = [normalize_entry(h) for h in d]
    normalized = [h for h in normalized if h['data']]  # filter empty
    json.dump(normalized, open('history.json', 'w'), ensure_ascii=False)
    print(f'Tzofar history ok: {len(normalized)} entries')
    return True

def try_oref():
    r = subprocess.run([
        'curl', '-s', '--max-time', '15',
        '-H', 'Referer: https://www.oref.org.il/',
        '-H', 'X-Requested-With: XMLHttpRequest',
        '-H', 'User-Agent: Mozilla/5.0',
        'https://www.oref.org.il/WarningMessages/alert/History/AlertsHistory.json'
    ], capture_output=True, text=True)
    raw = r.stdout.strip('\xef\xbb\xbf')
    d = json.loads(raw)
    assert isinstance(d, list)
    normalized = [normalize_entry(h) for h in d]
    normalized = [h for h in normalized if h['data']]
    json.dump(normalized, open('history.json', 'w'), ensure_ascii=False)
    print(f'oref history ok: {len(normalized)} entries')
    return True

try:
    try_tzofar()
except Exception as e1:
    print(f'Tzofar failed: {e1}')
    try:
        try_oref()
    except Exception as e2:
        print(f'oref also failed: {e2}')
        print('keeping existing history.json')
