"""Append-only JSONL telemetry writer."""

from __future__ import annotations
import json
from pathlib import Path

from src.config import get_daemon_config


class TelemetryWriter:
    def __init__(self, path: str | None = None):
        self.path = Path(path or get_daemon_config()["telemetry_file"])
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, snapshot: dict, alerts: list[dict]) -> None:
        record = {
            "timestamp": snapshot["timestamp"],
            "node_count": len(snapshot["nodes"]),
            "nodes_summary": [
                {
                    "node": n["node"],
                    "status": n["status"],
                    "cpu_pct": n["cpu_pct"],
                    "memory_pct": n["memory_pct"],
                    "vm_count": len(n.get("vms", [])),
                    "ct_count": len(n.get("containers", [])),
                }
                for n in snapshot["nodes"]
            ],
            "alert_count": len(alerts),
            "alerts": alerts,
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def read_last(self, n: int = 10) -> list[dict]:
        if not self.path.exists():
            return []
        lines = self.path.read_text().strip().split("\n")
        return [json.loads(line) for line in lines[-n:]]
