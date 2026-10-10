#!/usr/bin/env python3
"""Read-only Luxtronik WebSocket -> Prometheus exporter for Alpha Innotec LW251."""
import logging
import re
import time
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer

import websocket
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def parse_value(value):
    value = value.strip()
    if value.lower() in ("ein", "on"):
        return 1
    if value.lower() in ("aus", "off"):
        return 0
    if re.fullmatch(r"\d+:\d{2}", value):
        h, m = map(int, value.split(":"))
        if m >= 60:
            raise ValueError("invalid time")
        return h * 60 + m
    match = re.search(r"[-+]?(?:\d+(?:[.,]\d*)?|[.,]\d+)", value)
    if not match:
        raise ValueError(f"cannot parse value: {value!r}")
    return float(match.group().replace(",", "."))


def get_metrics():
    ws = websocket.create_connection(
        f"ws://{config.heatPumpHost}:{config.heatPumpPort}/",
        subprotocols=["Lux_WS"], timeout=10,
    )
    try:
        ws.send("LOGIN;0")
        root = ET.fromstring(ws.recv())
        menu = {}
        for item in root.findall(".//item[@id]"):
            name = item.findtext("name")
            if name:
                menu[name] = item.attrib["id"]
        output = []
        for group, definitions in config.metrics.items():
            if group not in menu:
                logging.warning("Group missing: %s", group)
                continue
            ws.send(f"GET;{menu[group]}")
            response = ET.fromstring(ws.recv())
            values = {}
            for item in response.findall(".//item"):
                name, value = item.findtext("name"), item.findtext("value")
                if name is not None and value is not None:
                    values[name] = value
            for definition in definitions:
                raw = values.get(definition["name"])
                if raw is None:
                    logging.warning("Metric missing: %s / %s", group, definition["name"])
                    continue
                try:
                    value = parse_value(raw)
                except ValueError as exc:
                    logging.warning("Metric invalid: %s: %s", definition["name"], exc)
                    continue
                name = definition["variable"]
                help_text = definition["help"].replace("\\", "\\\\").replace("\n", "\\n")
                output.extend((f"# HELP {name} {help_text}", f"# TYPE {name} {definition['type']}", f"{name} {value:g}"))
        return "\n".join(output) + "\n"
    finally:
        ws.close()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?", 1)[0] != "/metrics":
            self.send_error(404, "Use /metrics")
            return
        start = time.monotonic()
        try:
            metrics = get_metrics()
            success = 1
        except Exception:
            logging.exception("Luxtronik scrape failed")
            metrics = ""
            success = 0
        elapsed = time.monotonic() - start
        metrics += ("# HELP heat_pump_scrape_success Whether the last heat pump read succeeded.\n"
                    "# TYPE heat_pump_scrape_success gauge\n"
                    f"heat_pump_scrape_success {success}\n"
                    "# HELP heat_pump_scrape_duration_seconds Heat pump read duration in seconds.\n"
                    "# TYPE heat_pump_scrape_duration_seconds gauge\n"
                    f"heat_pump_scrape_duration_seconds {elapsed:.3f}\n")
        body = metrics.encode("utf-8")
        self.send_response(200 if success else 503)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer((config.serverHost, config.serverPort), Handler)
    logging.info("LW251 exporter listening on %s:%s", config.serverHost, config.serverPort)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
