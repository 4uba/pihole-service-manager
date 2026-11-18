# Pi-hole Service Manager

A service-oriented management layer for Pi-hole.

Pi-hole Service Manager allows administrators to manage online services instead of individual domains. Services such as YouTube, TikTok, Discord, Netflix, Twitch, Reddit, Telegram, and Facebook can be blocked or allowed through a simple web interface.

## Why?

Pi-hole is excellent at domain-level filtering, but managing large collections of domains can become difficult over time.

Service Manager introduces a higher-level abstraction:

Service
→ Managed Domains
→ Pi-hole Rules
→ Assigned Device Groups

This enables service-based policy management while continuing to use standard Pi-hole functionality.

## Features

- Service-based blocking and unblocking
- Native Pi-hole API integration
- Dynamic Pi-hole Group discovery
- Per-group service assignment
- Automatic catalog updates
- Category-based service organization
- Full-text service search
- SQLite-backed configuration storage
- FastAPI backend
- Responsive web interface

## Pi-hole Group Support

Service Manager supports native Pi-hole Groups and allows services to be assigned to specific device groups.

Examples:

- Discord → Kids
- TikTok → Default, TV3
- Netflix → TV1, TV2, TV3
- YouTube → Kids, TV1

When a service is enabled, Service Manager automatically creates the corresponding Pi-hole rules using the selected groups.

## Architecture

Service Manager UI

↓

FastAPI Backend

↓

SQLite Configuration

↓

Pi-hole API

↓

Pi-hole DNS Engine

No direct modification of Pi-hole databases is required.

## Service Catalog

The service catalog is automatically generated from:

- AdGuard HostlistsRegistry

Catalog updates preserve service configuration and group assignments.

## Installation

### Requirements

- Pi-hole 6.x
- Docker
- Docker Compose
- Git

### Clone Repository

git clone https://github.com/4uba/pihole-service-manager.git

cd pihole-service-manager

### Configure Environment

Create a .env file:

PIHOLE_URL=http://YOUR_PIHOLE_IP

PIHOLE_PASSWORD=YOUR_PIHOLE_PASSWORD

Example:

PIHOLE_URL=http://192.168.1.10

PIHOLE_PASSWORD=your_password

### Start Application

docker compose up -d

### Verify Operation

Open:

http://SERVER_IP:8081

The application should display the Service Manager dashboard and automatically connect to Pi-hole.

### Updating the Service Catalog

Use the Update Catalog button in the web interface.

### Upgrading

git pull

docker compose build

docker compose up -d

### Supported Pi-hole Versions

- Pi-hole 6.x

### Security Notes

Service Manager uses the official Pi-hole API and does not modify Pi-hole databases directly.

All service assignments and group mappings are stored locally in SQLite.

## Technology Stack

- FastAPI
- SQLite
- Vanilla JavaScript
- Pi-hole API
- Docker
- AdGuard HostlistsRegistry

## Current Status

### v3.2.0-alpha1

Implemented:

- Service catalog management
- Dynamic catalog updates
- Category filtering
- Service search
- Pi-hole API integration
- Dynamic Pi-hole Group discovery
- Group-aware service blocking
- Persistent group assignments
- Web-based management interface

## Project Goals

- Simplify service-based content management for Pi-hole
- Reduce the need to manage domains manually
- Leverage native Pi-hole capabilities instead of replacing them
- Remain compatible with standard Pi-hole installations and upgrades

## License

MIT License
