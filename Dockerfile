# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
RUN pip install --no-cache-dir uv

# Install Node.js and pnpm for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY package.json ./
COPY pnpm-lock.yaml* ./

# Install Python dependencies
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -e .

# Install Node.js dependencies
RUN pnpm install --frozen-lockfile

# Copy project files
COPY . .

# Build frontend assets
RUN pnpm run build

# Create staticfiles directory and collect static files
RUN mkdir -p staticfiles
RUN uv run python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run the application
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]