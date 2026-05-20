import pytest
from src.alerts import evaluate

THRESHOLDS = {"cpu": 90, "memory": 85, "disk": 90}


def _make_snapshot(cpu=50, mem=60, disk=70, status="online"):
    return {
        "timestamp": "2026-01-01T00:00:00+00:00",
        "nodes": [
            {
                "node": "pve1",
                "status": status,
                "cpu_pct": cpu,
                "memory_pct": mem,
                "storage": [{"name": "local", "used_pct": disk}],
            }
        ],
    }


class TestAlertEvaluation:
    def test_no_alerts_when_healthy(self):
        alerts = evaluate(_make_snapshot(), THRESHOLDS)
        assert alerts == []

    def test_cpu_alert(self):
        alerts = evaluate(_make_snapshot(cpu=95), THRESHOLDS)
        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "cpu_high"
        assert alerts[0]["severity"] == "WARNING"

    def test_memory_alert(self):
        alerts = evaluate(_make_snapshot(mem=88), THRESHOLDS)
        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "memory_high"

    def test_disk_alert(self):
        alerts = evaluate(_make_snapshot(disk=95), THRESHOLDS)
        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "disk_high"

    def test_multiple_alerts(self):
        alerts = evaluate(_make_snapshot(cpu=92, mem=90, disk=95), THRESHOLDS)
        assert len(alerts) == 3

    def test_offline_node_critical(self):
        alerts = evaluate(_make_snapshot(status="offline"), THRESHOLDS)
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "CRITICAL"
        assert alerts[0]["alert_type"] == "node_offline"

    def test_threshold_boundary_triggers(self):
        alerts = evaluate(_make_snapshot(cpu=90), THRESHOLDS)
        assert len(alerts) == 1

    def test_below_threshold_no_alert(self):
        alerts = evaluate(_make_snapshot(cpu=89.99), THRESHOLDS)
        assert alerts == []

    def test_null_disk_usage_ignored(self):
        snap = _make_snapshot()
        snap["nodes"][0]["storage"] = [{"name": "nfs", "used_pct": None}]
        alerts = evaluate(snap, THRESHOLDS)
        assert alerts == []
