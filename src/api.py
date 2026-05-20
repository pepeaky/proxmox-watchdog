"""Proxmox VE API client — read-only monitoring endpoints."""

from __future__ import annotations
import requests
import urllib3

from src.config import get_proxmox_config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ProxmoxClient:
    def __init__(self, config: dict | None = None):
        cfg = config or get_proxmox_config()
        self.base_url = cfg["host"].rstrip("/") + "/api2/json"
        self.session = requests.Session()
        self.session.headers["Authorization"] = (
            f"PVEAPIToken={cfg['user']}!{cfg['token_name']}={cfg['token_value']}"
        )
        self.session.verify = cfg["verify_ssl"]

    def _get(self, path: str) -> dict:
        resp = self.session.get(f"{self.base_url}{path}", timeout=10)
        resp.raise_for_status()
        return resp.json()["data"]

    def get_nodes(self) -> list[dict]:
        return self._get("/nodes")

    def get_node_status(self, node: str) -> dict:
        return self._get(f"/nodes/{node}/status")

    def get_vms(self, node: str) -> list[dict]:
        return self._get(f"/nodes/{node}/qemu")

    def get_containers(self, node: str) -> list[dict]:
        return self._get(f"/nodes/{node}/lxc")

    def get_storage(self, node: str) -> list[dict]:
        return self._get(f"/nodes/{node}/storage")

    def get_storage_status(self, node: str, storage: str) -> dict:
        return self._get(f"/nodes/{node}/storage/{storage}/status")
