# Alpha Innotec Prometheus Exporter

[![Docker Image](https://img.shields.io/badge/Docker-GHCR-blue?logo=docker)](https://github.com/aracloud/alpha-innotec-exporter/pkgs/container/alpha-innotec-exporter)
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Alpine Linux](https://img.shields.io/badge/Base-Alpine_Linux-0D597F?logo=alpinelinux)
![Prometheus](https://img.shields.io/badge/Metrics-Prometheus-E6522C?logo=prometheus)

A lightweight, Docker-ready **Prometheus exporter** for an **Alpha Innotec LW251** heat pump with a compatible **Luxtronik WebSocket interface**. It reads operational data from the heat pump and exposes metrics for **Prometheus** and **Grafana**.

> [!NOTE]
> Developed and tested against an Alpha Innotec LW251 exposing the `Lux_WS` WebSocket subprotocol on TCP port `8214`, with **German-language** menu and metric labels. Compatibility with other models, controllers, firmware versions, and languages is not guaranteed.

## Features

- Alpine Linux-based Python container
- Read-only telemetry collection via Luxtronik WebSocket (`Lux_WS`)
- Prometheus text metrics at `/metrics`
- Heating and hot-water temperatures
- Compressor, pump, valve, and auxiliary heater states
- Compressor starts, operating hours, and average runtime
- Scrape success and duration diagnostics
- Runtime configuration using Docker Compose environment variables (no `.env` file required)
- Suitable for GitHub Container Registry (GHCR) deployment

## Architecture

```text
Alpha Innotec LW251
  192.168.x.x:8214 (Lux_WS)
          |
          v
   LW251 Exporter (Docker)
       :8888/metrics
          |
          v
      Prometheus
          |
          v
        Grafana
```

## Quick start (Docker Compose)

Create a `compose.yaml`:

```yaml
services:
  lw251-exporter:
    image: ghcr.io/aracloud/alpha-innotec-exporter:latest
    container_name: lw251-exporter
    restart: unless-stopped
    ports:
      - "8888:8888"
    environment:
      SERVER_HOST: "0.0.0.0"
      SERVER_PORT: "8888"
      HEATPUMP_HOST: "192.168.1.100"  # Replace with your heat pump's IP
      HEATPUMP_PORT: "8214"
```

Start the exporter:

```bash
docker compose up -d
```

Check its logs and metrics:

```bash
docker compose logs --tail=50 lw251-exporter
curl -fsS http://127.0.0.1:8888/metrics
```

A healthy scrape should include:

```text
heat_pump_scrape_success 1
```

> [!IMPORTANT]
> The GHCR image must have been built and published before `docker compose up -d` can pull it. If the package is private, authenticate to GHCR first. The heat pump must be reachable from the Docker host over TCP port `8214`.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `HEATPUMP_HOST` | Empty | IP address or hostname of the heat pump; **required** for successful collection |
| `HEATPUMP_PORT` | `8214` | Luxtronik WebSocket port |
| `SERVER_HOST` | `0.0.0.0` | Exporter listen address |
| `SERVER_PORT` | `8888` | Exporter listen port |

All configuration can be supplied directly in `compose.yaml`. No separate `.env` file is necessary.

## Build locally

```bash
git clone https://github.com/aracloud/alpha-innotec-exporter.git
cd alpha-innotec-exporter
docker build -t lw251-exporter:local .
```

Run the locally built image:

```bash
docker run --rm -p 8888:8888 \
  -e HEATPUMP_HOST=192.168.1.100 \
  -e HEATPUMP_PORT=8214 \
  lw251-exporter:local
```

## Prometheus integration

Add the following job to the existing `scrape_configs` section of `prometheus.yml`:

```yaml
  - job_name: "alpha-innotec-lw251"
    scrape_interval: 60s
    scrape_timeout: 20s
    metrics_path: /metrics
    static_configs:
      - targets: ["DOCKER_HOST_IP:8888"]
```

Replace `DOCKER_HOST_IP` with the reachable IP or DNS name of the host running the exporter. Do not use `localhost` when Prometheus runs in a separate container or on another machine unless the network configuration explicitly makes that address valid.

> [!CAUTION]
> Every request to `/metrics` triggers communication with the heat pump. Use a conservative scrape interval such as **60 seconds**, and avoid extra frequent health checks or parallel monitoring systems that repeatedly query the controller.

## Grafana / PromQL examples

| Panel | PromQL |
|---|---|
| Outdoor temperature | `heat_pump_ambient_temperature` |
| Flow temperature | `heat_pump_flow_temperature` |
| Return temperature | `heat_pump_return_temperature` |
| Target return temperature | `heat_pump_target_return_temperature` |
| Hot water actual | `heat_pump_actual_service_water_temperature` |
| Hot water target | `heat_pump_target_service_water_temperature` |
| Compressor 1 status | `heat_pump_compressor_status` |
| Compressor 1 starts (24 h) | `increase(heat_pump_compressor_1_starts_total[24h])` |
| Compressor 1 operating hours (24 h) | `increase(heat_pump_compressor_1_operating_hours[24h])` |
| Scrape status | `heat_pump_scrape_success` |
| Scrape duration | `heat_pump_scrape_duration_seconds` |

**Notes:** Start counters may be sampled as integers, so Prometheus `increase()` can return fractional estimates. Operating-hour counters may only update in full-hour increments. Accurate COP or seasonal performance factor calculations require appropriate thermal-energy and electrical-energy measurements; the temperature and status metrics alone are not sufficient.

## Available telemetry

The tested controller exposes these categories:

- **Temperatures:** flow, return, target return, external return, hot gas, outdoor and average temperature, domestic hot water actual/target, heat source inlet/outlet, mixing circuit, and other controller-reported sensors.
- **Outputs:** compressor(s), pumps, defrost valve, mixer, auxiliary heaters, ventilation, and analog outputs.
- **Operating hours:** compressor operating hours, compressor start counters, average runtime, total heat-pump hours, heating hours, and hot-water hours.
- **Diagnostics:** `heat_pump_scrape_success` and `heat_pump_scrape_duration_seconds`.

Some reported sensors may be unused or return placeholder values depending on the heat pump's configuration. Do not interpret every reported temperature as a physically installed sensor.

## Troubleshooting

**The exporter responds on `/` but does not show metrics:** Use `/metrics`, not `/`.

**`/metrics` is empty or collection fails:** Check the container logs, `HEATPUMP_HOST`, TCP connectivity to port `8214`, and controller compatibility. The WebSocket connection uses the `Lux_WS` subprotocol and begins with `LOGIN;0`.

**Menu lookup fails:** The current metric mapping is designed for **German** Luxtronik labels such as `Temperaturen`, `Ausgänge`, and `Betriebsstunden`. Other controller languages may require a different mapping.

**Prometheus target is DOWN:** Check whether Prometheus can reach `DOCKER_HOST_IP:8888`, whether Docker published port `8888`, and whether firewall rules allow access.

**Scrape returns HTTP 200 but no usable samples:** Review the exporter logs and the response body. A successful HTTP response alone does not prove that telemetry was collected.

## Security

The exporter is intended for trusted local networks. Its metrics endpoint has no built-in authentication; do **not** expose port `8888` directly to the public internet. Restrict access to Prometheus and other authorized monitoring clients. Do not expose the heat pump's TCP port `8214` publicly.

## Upstream project and attribution

This project is adapted from [gerarddejong/heat-pump-telemetry-exporter](https://github.com/gerarddejong/heat-pump-telemetry-exporter) by Gerard Diederik de Jong, with modifications for the German-language Luxtronik interface and deployment via Docker/Prometheus.

**Before publishing:** Review the upstream repository's license and comply with its attribution and redistribution requirements. Do not claim an unverified license for the derivative project.

## License

License information is pending verification of the upstream project's license and applicable reuse terms.
