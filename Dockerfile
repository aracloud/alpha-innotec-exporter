FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py config.py ./

RUN useradd --system --uid 10001 exporter
USER exporter

EXPOSE 8888

CMD ["python", "-u", "main.py"]

