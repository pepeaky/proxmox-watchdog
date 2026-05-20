"""Threshold-based alert evaluation."""

from __future__ import annotations
import logging

from src.config import get_thresholds

logger = logging.getLogger("watchdog.alerts")


def evaluate(snapshot: dict, thresholds: dict | None = None) -> list[dict]:
    th = thresholds or get_thresholds()
    alerts = []

    for node in snapshot.get("nodes", []):
        name = node["node"]

        if node.get("status") != "online":
            alerts.append(_alert("CRITICAL", name, "node_offline", f"Node {name} is {node.get('status')}"))
            continue

        if node["cpu_pct"] >= th["cpu"]:
            alerts.append(_alert("WARNING", name, "cpu_high", f"CPU at {node['cpu_pct']}% (threshold {th['cpu']}%)"))

        if node["memory_pct"] >= th["memory"]:
            alerts.append(_alert("WARNING", name, "memory_high", f"Memory at {node['memory_pct']}% (threshold {th['memory']}%)"))

        for s in node.get("storage", []):
            if s["used_pct"] is not None and s["used_pct"] >= th["disk"]:
                alerts.append(_alert("WARNING", name, "disk_high", f"Storage '{s['name']}' at {s['used_pct']}% (threshold {th['disk']}%)"))

    for a in alerts:
        logger.warning("[%s] %s — %s: %s", a["severity"], a["node"], a["alert_type"], a["message"])

    return alerts


def _alert(severity: str, node: str, alert_type: str, message: str) -> dict:
    return {"severity": severity, "node": node, "alert_type": alert_type, "message": message}
