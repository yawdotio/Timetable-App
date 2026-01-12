# ==========================================
# Stage 1: Builder (Heavy lifting)
# ==========================================
FROM python:3.11-slim as builder

# Install build dependencies (GCC, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a virtual environment to isolate dependencies
RUN python -m venv /opt/venv
# Enable venv for the upcoming pip install
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ==========================================
# Stage 2: Runner (Lightweight / Production)
# ==========================================
FROM python:3.11-slim as runner

# Install ONLY runtime libraries (libpq) needed for Postgres
# We do NOT install gcc or g++ here
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Enable the venv in this stage too
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY ./app ./app
# Do NOT copy .env.example to .env (See "Secrets" below)
COPY ./init_db.py .

# Create uploads directory (optional when using GCS)
# Used as fallback for local development or when USE_GCS=false
RUN mkdir -p uploads

# Cloud Run usage:
# We use the $PORT environment variable.
# Workers: Keep it low (1-2) for Free Tier instances which usually have 1 vCPU.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
