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

