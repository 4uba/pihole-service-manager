# Pi-hole Service Manager

Pi-hole Service Manager adds service-based control to Pi-hole.

Block or allow services such as TikTok, Discord, Netflix, YouTube, Reddit, Twitch, Telegram and many others without manually managing domain lists.

## Features

- Service-based blocking
- Pi-hole API integration
- Dynamic Pi-hole Group discovery
- Per-group blocking
- FastAPI backend
- SQLite database
- Automatic catalog updates
- HostlistsRegistry integration

## Example

TikTok:
- Default ✅
- TV3 ✅

Discord:
- Kids ✅

The application automatically creates Pi-hole rules using the selected groups.

## Status

Current release: v3.2.0-alpha1
