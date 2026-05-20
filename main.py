"""Entry point for the Proxmox Watchdog daemon."""

import argparse
import json

from src.daemon import Watchdog
from src.telemetry import TelemetryWriter


def cmd_run(args):
    Watchdog().run()


def cmd_history(args):
    writer = TelemetryWriter()
    records = writer.read_last(args.count)
    if not records:
        print("No telemetry data yet.")
        return
    for r in records:
        ts = r["timestamp"]
        nodes = ", ".join(n["node"] for n in r["nodes_summary"])
        alerts = r["alert_count"]
        print(f"[{ts}] nodes: {nodes} | alerts: {alerts}")


def main():
    parser = argparse.ArgumentParser(description="Proxmox/Linux Watchdog Daemon")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("run", help="Start the watchdog daemon")

    p_hist = sub.add_parser("history", help="Show recent telemetry")
    p_hist.add_argument("--count", type=int, default=10)

    args = parser.parse_args()
    {"run": cmd_run, "history": cmd_history}[args.command](args)


if __name__ == "__main__":
    main()
