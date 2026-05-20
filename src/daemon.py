"""Watchdog daemon — polling loop with graceful shutdown."""

from __future__ import annotations
import logging
import signal
import sys
import time

import schedule

from src.api import ProxmoxClient
from src.collector import collect_cluster_snapshot
from src.alerts import evaluate
from src.telemetry import TelemetryWriter
from src.config import get_daemon_config

logger = logging.getLogger("watchdog")


class Watchdog:
    def __init__(self):
        self._running = False
        self._client = ProxmoxClient()
        self._telemetry = TelemetryWriter()
        self._cfg = get_daemon_config()

    def _setup_logging(self) -> None:
        from pathlib import Path
        log_path = Path(self._cfg["log_file"])
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self._cfg["log_level"]),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout),
            ],
        )

    def _tick(self) -> None:
        try:
            snapshot = collect_cluster_snapshot(self._client)
            alerts = evaluate(snapshot)
            self._telemetry.write(snapshot, alerts)

            node_names = [n["node"] for n in snapshot["nodes"]]
            logger.info("Polled %d node(s): %s | %d alert(s)", len(node_names), ", ".join(node_names), len(alerts))
        except Exception:
            logger.exception("Error during poll cycle")

    def _handle_signal(self, signum, frame) -> None:
        logger.info("Received signal %d — shutting down", signum)
        self._running = False

    def run(self) -> None:
        self._setup_logging()
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        logger.info("Watchdog started — polling every %ds", self._cfg["poll_interval"])
        self._running = True

        schedule.every(self._cfg["poll_interval"]).seconds.do(self._tick)
        self._tick()

        while self._running:
            schedule.run_pending()
            time.sleep(1)

        logger.info("Watchdog stopped")
