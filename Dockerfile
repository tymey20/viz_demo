# Apex Analytics — Cloud Run ready container.
#
# Build:    docker build -t apex-analytics .
# Run:      docker run -p 8000:8000 -e PORT=8000 apex-analytics
# Cloud Run deploy (one-time):
#   gcloud run deploy apex-analytics \
#       --source . \
#       --region <region> \
#       --service-account <sa-with-bigquery.dataViewer> \
#       --allow-unauthenticated   # (or use IAP / IAM-based access)
#
# Cloud Run injects $PORT — uvicorn reads it via server.py's __main__ block,
# but the recommended entrypoint is the CMD below which honors $PORT directly.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install deps first for layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app source. .dockerignore keeps cruft out.
COPY server.py ./
COPY lib/ ./lib/
COPY dashboards/ ./dashboards/
COPY queries/ ./queries/

EXPOSE 8000

# Cloud Run sets PORT (default 8080). Locally we default to 8000.
CMD exec uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}
