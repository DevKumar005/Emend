
# Stage 1: Build React Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Runtime Environment
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend:/app

WORKDIR /app

# Install system utilities & git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt backend/requirements-core.txt backend/requirements-api.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code, contracts, and demo repos
COPY backend/ backend/
COPY contracts/ contracts/
COPY demo_repos/ demo_repos/

# Copy built frontend assets
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist /app/backend/emend/api/static

# Initialize git tracking inside demo_repos so working tree resets function properly
RUN git config --global user.email "emend-agent@hackathon.local" && \
    git config --global user.name "Emend Agent" && \
    git init /app && \
    git add demo_repos/ && \
    git commit -m "init demo repos"

# Non-root user for security sandbox compliance
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Bind to Railway's dynamic PORT (fallback to 7860 locally)
CMD ["sh", "-c", "exec uvicorn emend.api.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
