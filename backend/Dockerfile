FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
COPY app ./app
ARG DOCURAG_INSTALL_REAL_OCR=false
ARG DOCURAG_INSTALL_REDIS=false
RUN if [ "$DOCURAG_INSTALL_REAL_OCR" = "true" ] && [ "$DOCURAG_INSTALL_REDIS" = "true" ]; then \
      pip install --no-cache-dir "paddlepaddle-gpu==3.3.0" -i https://www.paddlepaddle.org.cn/packages/stable/cu129/ && \
      pip install --no-cache-dir ".[dev,real-ocr,redis]"; \
    elif [ "$DOCURAG_INSTALL_REAL_OCR" = "true" ]; then \
      pip install --no-cache-dir "paddlepaddle-gpu==3.3.0" -i https://www.paddlepaddle.org.cn/packages/stable/cu129/ && \
      pip install --no-cache-dir ".[dev,real-ocr]"; \
    elif [ "$DOCURAG_INSTALL_REDIS" = "true" ]; then \
      pip install --no-cache-dir ".[dev,redis]"; \
    else \
      pip install --no-cache-dir ".[dev]"; \
    fi

COPY tests ./tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
