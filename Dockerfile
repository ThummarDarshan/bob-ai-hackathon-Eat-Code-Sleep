# GridPulse AI — Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY seeds/ ./seeds/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create __init__.py files for package resolution
RUN touch src/__init__.py src/app/__init__.py src/app/core/__init__.py \
    src/app/models/__init__.py src/app/schemas/__init__.py \
    src/app/services/__init__.py src/app/routes/__init__.py \
    src/app/database/__init__.py

EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
