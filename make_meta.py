import json
from datetime import datetime, timezone

count = 0
try:
    count = len(json.load(open('history.json')))
except:
    pass

meta = {
    'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'count': count
}
json.dump(meta, open('meta.json', 'w'))
print('meta:', meta)
