FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
COPY app ./app
COPY workers ./workers
ARG DOCURAG_INSTALL_REAL_OCR=false
ARG DOCURAG_INSTALL_REDIS=false
ARG DOCURAG_INSTALL_NATS=false
RUN extras="dev"; \
    if [ "$DOCURAG_INSTALL_REAL_OCR" = "true" ]; then \
      pip install --no-cache-dir "paddlepaddle-gpu==3.3.0" -i https://www.paddlepaddle.org.cn/packages/stable/cu129/ && \
      extras="$extras,real-ocr"; \
    fi; \
    if [ "$DOCURAG_INSTALL_REDIS" = "true" ]; then \
      extras="$extras,redis"; \
    fi; \
    if [ "$DOCURAG_INSTALL_NATS" = "true" ]; then \
      extras="$extras,nats"; \
    fi; \
    pip install --no-cache-dir ".[${extras}]"

COPY tests ./tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
