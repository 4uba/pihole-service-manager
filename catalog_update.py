#!/usr/bin/env python3

import html
import os
import sqlite3
from datetime import datetime

import requests

DB_FILE = "data/app.db"

URL = "https://adguardteam.github.io/HostlistsRegistry/assets/services.json"

ICONS_DIR = "static/icons"

os.makedirs(ICONS_DIR, exist_ok=True)

print("Downloading services.json...")

r = requests.get(
    URL,
    timeout=60
)

r.raise_for_status()

data = r.json()

services = data.get(
    "blocked_services",
    []
)

print(
    f"Found {len(services)} services"
)

conn = sqlite3.connect(DB_FILE)

cur = conn.cursor()

#
# Preserve state table
#
cur.execute(
    "delete from services"
)

cur.execute(
    "delete from service_domains"
)

service_count = 0
domain_count = 0

for svc in services:

    service_id = (
        svc.get("id", "")
        .strip()
        .lower()
    )

    if not service_id:
        continue

    name = (
        svc.get("name")
        or service_id
    )

    category = (
        svc.get("group")
        or "software"
    )

    cur.execute(
        """
        insert into services(
            id,
            name,
            category
        )
        values(?,?,?)
        """,
        (
            service_id,
            name,
            category
        )
    )

    service_count += 1

    for rule in svc.get("rules", []):

        rule = str(rule).strip()

        if not rule.startswith("||"):
            continue

        domain = (
            rule
            .replace("||", "", 1)
            .split("^")[0]
            .strip()
        )

        if not domain:
            continue

        cur.execute(
            """
            insert into service_domains(
                service_id,
                domain
            )
            values(?,?)
            """,
            (
                service_id,
                domain
            )
        )

        domain_count += 1

    svg = svc.get("icon_svg")

    if svg:

        svg = html.unescape(svg)

        with open(
            os.path.join(
                ICONS_DIR,
                f"{service_id}.svg"
            ),
            "w",
            encoding="utf-8"
        ) as f:
            f.write(svg)

cur.execute("""
insert into catalog_meta(
    key,
    value
)
values(
    'source',
    'HostlistsRegistry'
)
on conflict(key)
do update set value=excluded.value
""")

cur.execute("""
insert into catalog_meta(
    key,
    value
)
values(
    'last_update',
    ?
)
on conflict(key)
do update set value=excluded.value
""",
(
    datetime.utcnow().isoformat()
,)
)

cur.execute("""
insert into catalog_meta(
    key,
    value
)
values(
    'services_count',
    ?
)
on conflict(key)
do update set value=excluded.value
""",
(
    str(service_count),
)
)

cur.execute("""
insert into catalog_meta(
    key,
    value
)
values(
    'domains_count',
    ?
)
on conflict(key)
do update set value=excluded.value
""",
(
    str(domain_count),
)
)

conn.commit()

conn.close()

print()
print("Catalog updated successfully")
print(
    f"Services : {service_count}"
)
print(
    f"Domains  : {domain_count}"
)
print(
    f"Icons    : {service_count}"
)
