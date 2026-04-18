# 1. Base image (Python 3.11 slim - light and fast)
FROM python:3.11-slim

# 2. Install essential system dependencies for Postgres/psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Work directory set karo
WORKDIR /app

# 4. Copy requirements and install (No-cache to save space)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your whole project
COPY . .

# 6. Start command (Render's dynamic port use karega)
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT