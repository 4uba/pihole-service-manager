import os
import sqlite3

ICONS_DIR = "tmp/simple-icons/icons"

icons = {
    filename[:-4].lower()
    for filename in os.listdir(ICONS_DIR)
    if filename.endswith(".svg")
}

conn = sqlite3.connect("data/app.db")

rows = conn.execute(
    """
    select id, name
    from services
    order by name
    """
).fetchall()

conn.close()

for service_id, name in rows:

    candidates = [
        service_id.lower(),
        service_id.replace("_", "").lower(),
        name.replace(" ", "").replace("+", "plus").lower()
    ]

    for candidate in candidates:
        if candidate in icons:
            print(f"{service_id}|{candidate}")
            break
