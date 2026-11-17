import os
import sqlite3

db = sqlite3.connect("data/app.db")

icons = {
    f[:-4].lower()
    for f in os.listdir(
        "tmp/simple-icons/icons"
    )
    if f.endswith(".svg")
}

rows = db.execute(
    """
    select id,name
    from services
    order by name
    """
)

for service_id, name in rows:

    candidates = [
        service_id.lower(),
        service_id.replace("_", "").lower(),
        name.replace(" ", "").replace("+","plus").lower()
    ]

    for c in candidates:
        if c in icons:
            print(
                f"{service_id}|{c}"
            )
            break
