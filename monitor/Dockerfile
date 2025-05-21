FROM python:3.11-slim

WORKDIR /app

COPY ../ /app/

RUN pip install requests docker

CMD ["python", "/app/monitor/health_monitor.py"]