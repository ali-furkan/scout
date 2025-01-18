FROM python:3.13-slim

WORKDIR /app

COPY apps/scraper/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY apps/scraper/src/ /app/

ENV PYTHONPATH=/app/src
ENV SCOUT_ENV=production
ENV SCRAPER_HOST=0.0.0.0
ENV SCRAPER_PORT=8000

ENV SCRAPER_CACHE_TTL=3600
ENV SCRAPER_CACHE_ENABLED=true
ENV SCRAPER_CACHE_FILE=""
COPY .cache/cache.json /app/cache.json

ENV SCRAPER_BASE_API=""
ENV SCRAPER_DB_URI=""
ENV SCRAPER_JOBS_DB_URI=""
EXPOSE 8000

ENV GUNICORN_CMD_ARGS="-w 1 -b ${SCRAPER_HOST}:${SCRAPER_PORT}"

CMD ["gunicorn", "prod:flask_app"]