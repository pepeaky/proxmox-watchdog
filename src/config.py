import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_proxmox_config() -> dict:
    return {
        "host": os.getenv("PROXMOX_HOST", "https://localhost:8006"),
        "user": os.getenv("PROXMOX_USER", "root@pam"),
        "token_name": os.getenv("PROXMOX_TOKEN_NAME", "watchdog"),
        "token_value": os.getenv("PROXMOX_TOKEN_VALUE", ""),
        "verify_ssl": os.getenv("PROXMOX_VERIFY_SSL", "false").lower() == "true",
    }


def get_thresholds() -> dict:
    return {
        "cpu": float(os.getenv("ALERT_CPU_THRESHOLD", "90")),
        "memory": float(os.getenv("ALERT_MEMORY_THRESHOLD", "85")),
        "disk": float(os.getenv("ALERT_DISK_THRESHOLD", "90")),
    }


def get_daemon_config() -> dict:
    return {
        "poll_interval": int(os.getenv("POLL_INTERVAL_SECONDS", "30")),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "log_file": os.getenv("LOG_FILE", "logs/watchdog.log"),
        "telemetry_file": os.getenv("TELEMETRY_FILE", "logs/telemetry.jsonl"),
    }
