FROM python:3.10-slim

WORKDIR /app

COPY services/ ./services/
RUN pip install --no-cache-dir docker tensorflow redis

CMD ["python", "services/coordinator.py"]

