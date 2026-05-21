FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
COPY app ./app
ARG DOCURAG_INSTALL_REAL_OCR=false
RUN if [ "$DOCURAG_INSTALL_REAL_OCR" = "true" ]; then \
      pip install --no-cache-dir ".[dev,real-ocr]"; \
    else \
      pip install --no-cache-dir ".[dev]"; \
    fi

COPY tests ./tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
