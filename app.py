import os
import sqlite3

import requests

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)

DB_FILE = "data/app.db"

PIHOLE_URL = os.getenv("PIHOLE_URL")
PIHOLE_PASSWORD = os.getenv("PIHOLE_PASSWORD")

PIHOLE_SID = None


def db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def get_domains(service_id):

    conn = db()

    rows = conn.execute(
        """
        select domain
        from service_domains
        where service_id = ?
        order by domain
        """,
        (service_id,)
    ).fetchall()

    conn.close()

    return [x["domain"] for x in rows]


def pihole_login():

    r = requests.post(
        f"{PIHOLE_URL}/api/auth",
        json={
            "password": PIHOLE_PASSWORD
        },
        timeout=15
    )

    r.raise_for_status()

    data = r.json()

    return data["session"]["sid"]


def get_sid():

    global PIHOLE_SID

    if PIHOLE_SID:
        return PIHOLE_SID

    PIHOLE_SID = pihole_login()

    return PIHOLE_SID


def reset_sid():

    global PIHOLE_SID

    PIHOLE_SID = None


@app.get("/")
async def index(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/api/services")
async def services():

    conn = db()

    rows = conn.execute(
        """
        select

            s.id,
            s.name,
            s.category,

            count(sd.domain) as domain_count,

            coalesce(st.enabled,0) as enabled

        from services s

        left join service_domains sd
            on sd.service_id = s.id

        left join state st
            on st.service_id = s.id

        group by
            s.id,
            s.name,
            s.category,
            st.enabled

        order by
            s.category,
            s.name
        """
    ).fetchall()

    stats = conn.execute(
        """
        select
            (select count(*) from services) as services,
            (select count(*) from service_domains) as domains,
            (select count(*) from state) as enabled
        """
    ).fetchone()

    conn.close()

    return JSONResponse(
        {
            "stats": dict(stats),
            "services": [dict(x) for x in rows]
        }
    )


@app.post("/api/toggle/{service_id}")
async def toggle(service_id: str):

    conn = db()

    try:

        state = conn.execute(
            """
            select enabled
            from state
            where service_id = ?
            """,
            (service_id,)
        ).fetchone()

        enabled = bool(state["enabled"]) if state else False

        domains = get_domains(service_id)

        groups = conn.execute(
            """
            select group_id
            from service_groups
            where service_id = ?
            order by group_id
            """,
            (service_id,)
        ).fetchall()

        groups = [
            row["group_id"]
            for row in groups
        ]

        if not groups:
            groups = [0]


        sid = get_sid()

        headers = {
            "X-FTL-SID": sid
        }

        if enabled:

            conn.execute(
                """
                delete
                from state
                where service_id = ?
                """,
                (service_id,)
            )

            for domain in domains:

                r = requests.delete(
                    f"{PIHOLE_URL}/api/domains/deny/exact/{domain}",
                    headers=headers,
                    timeout=15
                )

                if r.status_code in (401, 403):

                    reset_sid()
                    sid = get_sid()

                    headers = {
                        "X-FTL-SID": sid
                    }

                    requests.delete(
                        f"{PIHOLE_URL}/api/domains/deny/exact/{domain}",
                        headers=headers,
                        timeout=15
                    )

            new_state = False

        else:

            conn.execute(
                """
                insert into state(service_id,enabled)
                values(?,1)

                on conflict(service_id)
                do update set enabled=1
                """,
                (service_id,)
            )

            for domain in domains:

                r = requests.post(
                    f"{PIHOLE_URL}/api/domains/deny/exact",
                    headers=headers,
                    json={
                        "domain": domain,
                            "groups": groups,

                        "comment": "Service Manager V3"
                    },
                    timeout=15
                )

                if r.status_code in (401, 403):

                    reset_sid()
                    sid = get_sid()

                    headers = {
                        "X-FTL-SID": sid
                    }

                    requests.post(
                        f"{PIHOLE_URL}/api/domains/deny/exact",
                        headers=headers,
                        json={
                            "domain": domain,
                            "groups": groups,

                            "comment": "Service Manager V3"
                        },
                        timeout=15
                    )

            new_state = True

        conn.commit()

        return JSONResponse(
            {
                "success": True,
                "service_id": service_id,
                "enabled": new_state,
                "domain_count": len(domains)
            }
        )

    except Exception as ex:

        conn.rollback()

        return JSONResponse(
            {
                "success": False,
                "error": str(ex)
            },
            status_code=500
        )

    finally:

        conn.close()


import subprocess

@app.post("/api/catalog/update")
async def catalog_update():

    try:

        result = subprocess.run(
            [
                "python3",
                "catalog_update.py"
            ],
            cwd="/app",
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:

            return JSONResponse(
                {
                    "success": False,
                    "error": result.stderr
                },
                status_code=500
            )

        conn = db()

        meta = {
            row["key"]: row["value"]
            for row in conn.execute(
                """
                select key,value
                from catalog_meta
                """
            ).fetchall()
        }

        conn.close()

        return JSONResponse(
            {
                "success": True,
                "services": meta.get(
                    "services_count",
                    "0"
                ),
                "domains": meta.get(
                    "domains_count",
                    "0"
                ),
                "last_update": meta.get(
                    "last_update",
                    "unknown"
                ),
                "message":
                    f"Catalog updated successfully. "
                    f"{meta.get('services_count','0')} services, "
                    f"{meta.get('domains_count','0')} domains."
            }
        )

    except Exception as ex:

        return JSONResponse(
            {
                "success": False,
                "error": str(ex)
            },
            status_code=500
        )


@app.get("/api/groups")
async def groups():

    sid = get_sid()

    headers = {
        "X-FTL-SID": sid
    }

    r = requests.get(
        f"{PIHOLE_URL}/api/groups",
        headers=headers,
        timeout=15
    )

    if r.status_code in (401,403):

        reset_sid()

        sid = get_sid()

        headers = {
            "X-FTL-SID": sid
        }

        r = requests.get(
            f"{PIHOLE_URL}/api/groups",
            headers=headers,
            timeout=15
        )

    r.raise_for_status()

    return JSONResponse(
        r.json()
    )


@app.get("/api/service/{service_id}/groups")
async def service_groups(service_id: str):

    conn = db()

    rows = conn.execute(
        """
        select group_id
        from service_groups
        where service_id = ?
        order by group_id
        """,
        (service_id,)
    ).fetchall()

    conn.close()

    return JSONResponse(
        {
            "service_id": service_id,
            "groups": [
                row["group_id"]
                for row in rows
            ]
        }
    )


@app.post("/api/service/{service_id}/groups")
async def save_service_groups(
    service_id: str,
    request: Request
):

    data = await request.json()

    groups = data.get(
        "groups",
        []
    )

    conn = db()

    try:

        conn.execute(
            """
            delete
            from service_groups
            where service_id = ?
            """,
            (service_id,)
        )

        for group_id in groups:

            conn.execute(
                """
                insert into service_groups(
                    service_id,
                    group_id
                )
                values(?,?)
                """,
                (
                    service_id,
                    int(group_id)
                )
            )

        conn.commit()

        return JSONResponse(
            {
                "success": True,
                "service_id": service_id,
                "groups": groups
            }
        )

    except Exception as ex:

        conn.rollback()

        return JSONResponse(
            {
                "success": False,
                "error": str(ex)
            },
            status_code=500
        )

    finally:

        conn.close()

