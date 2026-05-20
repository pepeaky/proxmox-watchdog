import pytest
from unittest.mock import MagicMock
from src.collector import collect_cluster_snapshot, _summarize_guests


class TestCollector:
    def _mock_client(self):
        client = MagicMock()
        client.get_nodes.return_value = [{"node": "pve1", "status": "online"}]
        client.get_node_status.return_value = {
            "cpu": 0.45,
            "memory": {"used": 8_000_000_000, "total": 16_000_000_000},
            "uptime": 86400,
        }
        client.get_storage.return_value = [{"storage": "local"}]
        client.get_storage_status.return_value = {"used": 50_000_000_000, "total": 100_000_000_000}
        client.get_vms.return_value = [
            {"vmid": 100, "name": "web-server", "status": "running", "cpu": 0.3, "mem": 2_000_000_000, "maxmem": 4_000_000_000}
        ]
        client.get_containers.return_value = []
        return client

    def test_snapshot_structure(self):
        snap = collect_cluster_snapshot(self._mock_client())
        assert "timestamp" in snap
        assert len(snap["nodes"]) == 1

    def test_cpu_percentage(self):
        snap = collect_cluster_snapshot(self._mock_client())
        assert snap["nodes"][0]["cpu_pct"] == 45.0

    def test_memory_percentage(self):
        snap = collect_cluster_snapshot(self._mock_client())
        assert snap["nodes"][0]["memory_pct"] == 50.0

    def test_storage_percentage(self):
        snap = collect_cluster_snapshot(self._mock_client())
        assert snap["nodes"][0]["storage"][0]["used_pct"] == 50.0

    def test_vms_collected(self):
        snap = collect_cluster_snapshot(self._mock_client())
        assert len(snap["nodes"][0]["vms"]) == 1
        assert snap["nodes"][0]["vms"][0]["name"] == "web-server"

    def test_storage_error_returns_none(self):
        client = self._mock_client()
        client.get_storage_status.side_effect = Exception("timeout")
        snap = collect_cluster_snapshot(client)
        assert snap["nodes"][0]["storage"][0]["used_pct"] is None


class TestSummarizeGuests:
    def test_empty_list(self):
        assert _summarize_guests([]) == []

    def test_guest_fields(self):
        guests = [{"vmid": 100, "name": "vm1", "status": "running", "cpu": 0.5, "mem": 1024, "maxmem": 2048}]
        result = _summarize_guests(guests)
        assert result[0]["id"] == 100
        assert result[0]["cpu_pct"] == 50.0
