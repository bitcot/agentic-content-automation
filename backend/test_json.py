import sqlite3
import json

conn = sqlite3.connect('/Users/apple/inbound_lead/backend/memory_layer.db')
cur = conn.cursor()
cur.execute('SELECT id, content FROM content_logs ORDER BY id DESC LIMIT 1')
content = cur.fetchone()[1]

try:
    data = json.loads(content)
    print("Success")
except Exception as e:
    print("Failed:", str(e))
