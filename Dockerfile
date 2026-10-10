FROM python:3.13-alpine

LABEL org.opencontainers.image.title="Alpha Innotec Exporter"
LABEL org.opencontainers.image.description="Prometheus exporter for Alpha Innotec heat pumps"
LABEL org.opencontainers.image.source="https://github.com/aracloud/alpha-innotec-exporter"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && addgroup -S exporter \
    && adduser -S -G exporter exporter

COPY --chown=exporter:exporter main.py config.py ./

USER exporter

EXPOSE 8888

CMD ["python", "-u", "main.py"]

