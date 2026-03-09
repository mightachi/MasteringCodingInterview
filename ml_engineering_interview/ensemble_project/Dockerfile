# Multi-stage: build not required for pure Python; use slim image for smaller size
FROM python:3.11-slim

WORKDIR /app

# Install dependencies only (no dev deps)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config.yaml .
COPY train.py .
COPY api/ api/
COPY src/ src/

# Train at build time so image is self-contained (optional; alternative: mount model at runtime)
RUN python train.py

# Default: run server; override CMD to run train only
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
