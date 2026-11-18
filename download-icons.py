#!/usr/bin/env python3

import os
import sqlite3

import requests

DB = "data/app.db"
OUT = "static/icons"

os.makedirs(OUT, exist_ok=True)

DEFAULT_SVG = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="12" fill="#eef2f7"/>
<text x="32" y="42" text-anchor="middle"
font-size="24"
font-family="Arial"
fill="#64748b">?</text>
</svg>
'''.strip()

with open(f"{OUT}/default.svg", "w", encoding="utf-8") as f:
    f.write(DEFAULT_SVG)

ICON_MAP = {
    # AI
    "chatgpt": "openai",
    "claude": "anthropic",
    "copilot": "microsoft",
    "gemini": "google",
    "deepseek": "deepseek",
    "perplexity": "perplexity",
    "meta_ai": "meta",
    "qwen": "alibabacloud",
    "grok": "x",

    # Social
    "facebook": "facebook",
    "instagram": "instagram",
    "reddit": "reddit",
    "linkedin": "linkedin",
    "pinterest": "pinterest",
    "discord": "discord",
    "telegram": "telegram",
    "whatsapp": "whatsapp",
    "tiktok": "tiktok",
    "snapchat": "snapchat",
    "mastodon": "mastodon",
    "bluesky": "bluesky",
    "tumblr": "tumblr",
    "vk": "vk",
    "line": "line",
    "imgur": "imgur",
    "flickr": "flickr",
    "onlyfans": "onlyfans",
    "twitter": "x",

    # Streaming
    "youtube": "youtube",
    "netflix": "netflix",
    "spotify": "spotify",
    "twitch": "twitch",
    "soundcloud": "soundcloud",
    "vimeo": "vimeo",
    "deezer": "deezer",
    "tidal": "tidal",
    "plex": "plex",
    "crunchyroll": "crunchyroll",
    "disneyplus": "disneyplus",
    "bilibili": "bilibili",
    "hulu": "hulu",
    "iqiyi": "iqiyi",

    # Gaming
    "steam": "steam",
    "epic_games": "epicgames",
    "riot_games": "riotgames",
    "leagueoflegends": "leagueoflegends",
    "playstation": "playstation",
    "nintendo": "nintendo",
    "roblox": "roblox",
    "minecraft": "minecraft",
    "ubisoft": "ubisoft",
    "valorant": "valorant",
    "rockstar_games": "rockstargames",
    "gog": "gogdotcom",
    "xboxlive": "xbox",

    # Messenger
    "slack": "slack",
    "signal": "signal",
    "skype": "skype",
    "microsoft_teams": "microsoftteams",
    "wechat": "wechat",
    "viber": "viber",
    "kakaotalk": "kakaotalk",

    # Shopping
    "amazon": "amazon",
    "ebay": "ebay",
    "aliexpress": "aliexpress",
    "shopee": "shopee",
    "temu": "temu",
    "shein": "shein",
    "lazada": "lazada",
    "mercado_libre": "mercadolibre",

    # Privacy / Hosting
    "cloudflare": "cloudflare",
    "dropbox": "dropbox",
    "box": "box",
    "proton": "proton",

    # Dating
    "tinder": "tinder",
    "grindr": "grindr",

    # Gambling
    "betfair": "betfair",

    # Software
    "nvidia": "nvidia",
    "playstore": "googleplay"
}

BASE = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons"

conn = sqlite3.connect(DB)

service_ids = [
    row[0]
    for row in conn.execute("select id from services order by id")
]

conn.close()

ok = 0
missing = 0

for service_id in service_ids:

    slug = ICON_MAP.get(service_id)

    if not slug:
        missing += 1
        print(f"NO MAP   {service_id}")
        continue

    try:
        r = requests.get(f"{BASE}/{slug}.svg", timeout=20)

        if r.status_code != 200:
            missing += 1
            print(f"MISS     {service_id} -> {slug}")
            continue

        with open(f"{OUT}/{service_id}.svg", "wb") as f:
            f.write(r.content)

    except (requests.RequestException, OSError) as e:
        missing += 1
        print(f"ERROR    {service_id}: {e}")
        continue

    ok += 1
    print(f"OK       {service_id}")

print()
print(f"Downloaded : {ok}")
print(f"Missing    : {missing}")
print()
print(f"Icons path : {OUT}")
