# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

# Set shell to bash for better error handling
SHELL ["/bin/bash", "-c"]

# Fix apt sources and install with retry logic
RUN echo "deb http://deb.debian.org/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update -qq --fix-missing || apt-get update -qq --fix-missing || apt-get update -qq --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libopenblas-dev \
        gfortran \
        liblapack-dev \
        libatlas-base-dev \
        libjpeg-dev \
        zlib1g-dev \
        poppler-utils \
        ffmpeg \
        tesseract-ocr && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.11-slim

# Set shell to bash for better error handling
SHELL ["/bin/bash", "-c"]

# Fix apt sources and install runtime dependencies with retry logic
RUN echo "deb http://deb.debian.org/debian bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update -qq --fix-missing || apt-get update -qq --fix-missing || apt-get update -qq --fix-missing && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        libopenblas0 \
        liblapack3 \
        libatlas3-base \
        libjpeg62-turbo \
        poppler-utils \
        ffmpeg \
        tesseract-ocr && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy backend application and modules from root context
COPY backend/ /app/
COPY modules/ /app/modules/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080', timeout=5)" || exit 1

# Expose port
EXPOSE 8080

# Run FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
