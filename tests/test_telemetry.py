import json
import pytest
from src.telemetry import TelemetryWriter


@pytest.fixture
def writer(tmp_path):
    return TelemetryWriter(str(tmp_path / "test_telemetry.jsonl"))


def _sample_snapshot():
    return {
        "timestamp": "2026-01-01T00:00:00+00:00",
        "nodes": [{"node": "pve1", "status": "online", "cpu_pct": 45, "memory_pct": 50, "vms": [], "containers": []}],
    }


class TestTelemetryWriter:
    def test_write_creates_file(self, writer):
        writer.write(_sample_snapshot(), [])
        assert writer.path.exists()

    def test_write_appends_jsonl(self, writer):
        writer.write(_sample_snapshot(), [])
        writer.write(_sample_snapshot(), [{"severity": "WARNING", "node": "pve1", "alert_type": "cpu_high", "message": "test"}])
        lines = writer.path.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_read_last(self, writer):
        for i in range(5):
            snap = _sample_snapshot()
            snap["timestamp"] = f"2026-01-0{i+1}T00:00:00+00:00"
            writer.write(snap, [])
        records = writer.read_last(3)
        assert len(records) == 3
        assert records[0]["timestamp"] == "2026-01-03T00:00:00+00:00"

    def test_read_last_empty(self, writer):
        assert writer.read_last() == []

    def test_record_structure(self, writer):
        writer.write(_sample_snapshot(), [])
        record = writer.read_last(1)[0]
        assert "node_count" in record
        assert "nodes_summary" in record
        assert "alert_count" in record
