FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
ARG PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir --extra-index-url ${PIP_EXTRA_INDEX_URL} -r /app/backend/requirements.txt

COPY backend /app/backend
COPY ml /app/ml
COPY models /app/models

ENV PYTHONPATH=/app:/app/backend \
    AEGIS_API_HOST=0.0.0.0 \
    AEGIS_API_PORT=8001

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "backend.anomaly_api.main:app", "--host", "0.0.0.0", "--port", "8001"]
