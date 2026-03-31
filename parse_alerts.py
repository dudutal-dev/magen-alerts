import json

try:
    raw = open('alerts_raw.txt', encoding='utf-8-sig').read().strip()
    d = json.loads(raw)
    json.dump(d, open('alerts.json', 'w'), ensure_ascii=False)
    print('alerts ok:', type(d))
except Exception as e:
    print('alerts error:', e)
    open('alerts.json', 'w').write('{}')
