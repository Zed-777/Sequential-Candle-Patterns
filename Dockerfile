FROM python:3.12-slim

# Lightweight image for running the CLI or dashboard
WORKDIR /app

# Prevents creation of __pycache__ with a different owner
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml requirements.txt dev-requirements.txt ./
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir .

COPY src/ ./src

# Default entrypoint runs the CLI module
ENTRYPOINT ["python", "-m", "candle_patterns.cli"]
CMD ["--help"]
