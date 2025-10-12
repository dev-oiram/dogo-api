# ---------- 1. Base image ----------
FROM python:3.12-slim

# ---------- 2. Environment variables ----------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- 3. Working directory ----------
WORKDIR /app

# ---------- 4. System dependencies ----------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# ---------- 5. Copy project files ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ---------- 6. Expose port ----------
EXPOSE 8000

# For production (using Gunicorn):
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
