"""Collects and normalizes telemetry from all Proxmox nodes."""

from __future__ import annotations
from datetime import datetime, timezone

from src.api import ProxmoxClient


def collect_cluster_snapshot(client: ProxmoxClient) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    nodes_raw = client.get_nodes()
    nodes = []

    for n in nodes_raw:
        node_name = n["node"]
        status = client.get_node_status(node_name)

        cpu_pct = round(status.get("cpu", 0) * 100, 2)
        mem = status.get("memory", {})
        mem_pct = round(mem.get("used", 0) / max(mem.get("total", 1), 1) * 100, 2)

        storages = []
        for s in client.get_storage(node_name):
            sid = s["storage"]
            try:
                ss = client.get_storage_status(node_name, sid)
                disk_pct = round(ss.get("used", 0) / max(ss.get("total", 1), 1) * 100, 2)
            except Exception:
                disk_pct = None
            storages.append({"name": sid, "used_pct": disk_pct})

        vms = _summarize_guests(client.get_vms(node_name))
        cts = _summarize_guests(client.get_containers(node_name))

        nodes.append({
            "node": node_name,
            "status": n.get("status", "unknown"),
            "uptime_s": status.get("uptime", 0),
            "cpu_pct": cpu_pct,
            "memory_pct": mem_pct,
            "memory_used_bytes": mem.get("used", 0),
            "memory_total_bytes": mem.get("total", 0),
            "storage": storages,
            "vms": vms,
            "containers": cts,
        })

    return {"timestamp": timestamp, "nodes": nodes}


def _summarize_guests(guests: list[dict]) -> list[dict]:
    return [
        {
            "id": g.get("vmid"),
            "name": g.get("name", ""),
            "status": g.get("status", "unknown"),
            "cpu_pct": round(g.get("cpu", 0) * 100, 2),
            "memory_used": g.get("mem", 0),
            "memory_max": g.get("maxmem", 0),
        }
        for g in guests
    ]
