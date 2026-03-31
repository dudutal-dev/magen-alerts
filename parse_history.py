import json, subprocess

def try_tzofar():
    raw = open('hist_raw.txt', encoding='utf-8-sig').read().strip()
    d = json.loads(raw)
    assert isinstance(d, list), 'not a list'
    json.dump(d, open('history.json', 'w'), ensure_ascii=False)
    print('history from Tzofar:', len(d), 'entries')
    return True

def try_oref():
    r = subprocess.run([
        'curl', '-s', '--max-time', '15',
        '-H', 'Referer: https://www.oref.org.il/',
        '-H', 'X-Requested-With: XMLHttpRequest',
        '-H', 'User-Agent: Mozilla/5.0',
        'https://www.oref.org.il/WarningMessages/alert/History/AlertsHistory.json'
    ], capture_output=True, text=True)
    d = json.loads(r.stdout.strip('\xef\xbb\xbf'))
    assert isinstance(d, list)
    json.dump(d, open('history.json', 'w'), ensure_ascii=False)
    print('history from oref:', len(d), 'entries')
    return True

try:
    try_tzofar()
except Exception as e1:
    print('Tzofar failed:', e1)
    try:
        try_oref()
    except Exception as e2:
        print('oref also failed:', e2)
        print('keeping existing history.json')
