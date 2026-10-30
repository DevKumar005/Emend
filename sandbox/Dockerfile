# Architecture-neutral base for macOS (Apple Silicon arm64) and Linux (amd64)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /sandbox

# Install pytest and report extensions
RUN pip install --no-cache-dir \
    pytest>=8.0.0 \
    pytest-json-report>=1.5.0 \
    pytest-timeout>=2.3.0

# Run as non-root user for security
RUN useradd -m sandboxuser
USER sandboxuser

CMD ["pytest", "--json-report", "--json-report-file=.report.json"]