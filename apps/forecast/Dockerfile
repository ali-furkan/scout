FROM python:3.13-slim

WORKDIR /app

COPY apps/forecast/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libgomp1

COPY apps/forecast/src/ /app/src

ENV PYTHONPATH=/app/src
ENV SCOUT_ENV=production
ENV FORECAST_HOST=0.0.0.0
ENV FORECAST_PORT=8001

COPY .cache/.models/ /app/.models/

ENV FORECAST_MODEL_PATH=/app/.models/
ENV FORECAST_MODEL_TAG=model_latest

EXPOSE 8001

ENV GUNICORN_CMD_ARGS="-w 1 -b ${FORECAST_HOST}:${FORECAST_PORT}"

CMD ["gunicorn", "api:app"]
