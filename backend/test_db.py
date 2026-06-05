import sqlite3
import json
conn = sqlite3.connect('memory_layer.db')
c = conn.cursor()
c.execute("SELECT id, content FROM content_logs ORDER BY id DESC LIMIT 1")
row = c.fetchone()
if row:
    print("ID:", row[0])
    draft = json.loads(row[1])
    print("Blog Image URL:", draft.get("blog", {}).get("image_url"))
    print("LinkedIn Image URL:", draft.get("linkedin", {}).get("image_url"))
