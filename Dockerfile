FROM python:3.10-slim

WORKDIR /app

COPY services/ ./services/
RUN pip install --no-cache-dir tensorflow redis simpy

CMD ["python", "services/coordinator.py"]

