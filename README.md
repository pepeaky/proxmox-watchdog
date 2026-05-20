# Proxmox Watchdog

A Python daemon that monitors Proxmox VE clusters via the REST API, collects system telemetry, and raises threshold-based alerts for CPU, memory, and disk usage.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Proxmox VE Cluster                  │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐            │
│  │  Node 1  │   │  Node 2  │   │  Node N  │            │
│  │ VMs/CTs  │   │ VMs/CTs  │   │ VMs/CTs  │            │
│  └─────────┘   └─────────┘   └─────────┘            │
└──────────────────────┬───────────────────────────────┘
                       │ REST API (token auth)
                       ▼
              ┌─────────────────┐
              │   ProxmoxClient  │  src/api.py
              │   (read-only)    │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │    Collector     │  src/collector.py
              │ (normalize data) │
              └────────┬────────┘
                       │ snapshot dict
              ┌────────┼────────┐
              │                 │
     ┌────────▼──────┐  ┌──────▼────────┐
     │  Alert Engine  │  │   Telemetry    │
     │  (thresholds)  │  │  (JSONL log)   │
     │  src/alerts.py │  │ src/telemetry  │
     └───────────────┘  └───────────────┘
              │
     ┌────────▼────────┐
     │  Daemon Loop     │  src/daemon.py
     │  (schedule +     │
     │   signal handler)│
     └─────────────────┘
```

## Features

- **Token-based auth** — no password storage, uses Proxmox API tokens
- **Per-node metrics** — CPU %, memory %, disk % per storage, VM/CT counts
- **Threshold alerts** — configurable via `.env`, WARNING for resources, CRITICAL for offline nodes
- **JSONL telemetry** — append-only log for time-series analysis
- **Graceful shutdown** — handles SIGINT/SIGTERM cleanly
- **Zero dependencies on Proxmox SDK** — pure REST via `requests`

## Quick Start

```bash
git clone <repo-url> && cd 02-proxmox-watchdog
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configure Proxmox credentials & thresholds

python main.py run           # start daemon
python main.py history       # view recent telemetry
```

## Configuration (.env)

| Variable | Default | Description |
|---|---|---|
| `PROXMOX_HOST` | `https://localhost:8006` | Proxmox API URL |
| `PROXMOX_TOKEN_NAME` | `watchdog` | API token name |
| `POLL_INTERVAL_SECONDS` | `30` | Seconds between polls |
| `ALERT_CPU_THRESHOLD` | `90` | CPU alert threshold (%) |
| `ALERT_MEMORY_THRESHOLD` | `85` | Memory alert threshold (%) |
| `ALERT_DISK_THRESHOLD` | `90` | Disk alert threshold (%) |

## Testing

```bash
pytest -v
```

**22 tests** — all run without a Proxmox instance (mocked API client).

## Project Structure

```
├── main.py               # CLI: run, history
├── src/
│   ├── config.py          # .env loader
│   ├── api.py             # Proxmox REST client (read-only)
│   ├── collector.py       # Normalize raw API → snapshot dict
│   ├── alerts.py          # Threshold evaluation engine
│   ├── telemetry.py       # JSONL writer/reader
│   └── daemon.py          # Polling loop + signal handling
└── tests/
    ├── test_alerts.py     # 9 tests — threshold logic, boundaries, edge cases
    ├── test_collector.py  # 8 tests — data normalization, error handling
    └── test_telemetry.py  # 5 tests — JSONL write/read, file creation
```
