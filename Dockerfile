# Production Dockerfile for Manga OCR FastAPI Microservice
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for OpenCV and MeCab
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml README.md ./
COPY manga_ocr/ manga_ocr/
COPY assets/ assets/

# Install dependencies including FastAPI, Uvicorn, and torchvision
RUN uv pip install --system -e ".[dev]" fastapi uvicorn torchvision

# Expose microservice port
EXPOSE 8000

# Healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start Uvicorn server
CMD ["python", "-m", "manga_ocr.server"]
