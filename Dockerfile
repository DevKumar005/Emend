# Multi-stage Dockerfile for Emend (Fix it. Prove it.)
# Compatible with Hugging Face Docker Spaces, local deployment, and cloud hosts

# Stage 1: Build the React + TypeScript frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend serving API and built frontend
FROM python:3.11-slim AS runner
WORKDIR /app

# Install system dependencies including git for deterministic diffs
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt backend/
COPY backend/requirements-core.txt backend/
COPY backend/requirements-api.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application source code
COPY contracts/ contracts/
COPY backend/ backend/
COPY demo_repos/ demo_repos/

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Setup environment variables
ENV PYTHONPATH="/app/backend:/app"
ENV PORT=7860
ENV RUN_MODE="hosted"
EXPOSE 7860

# Non-root user for security sandbox compliance
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["sh", "-c", "exec uvicorn emend.api.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
