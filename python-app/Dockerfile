# syntax=docker/dockerfile:1

############################################
# Stage 1 — Builder
############################################

# Use the full official Python image for building.
FROM python:3.11 AS builder

# Set the working directory inside the image.
WORKDIR /app

# Copy dependency manifest first to maximize layer caching.
COPY requirements.txt .

# Install dependencies into a dedicated prefix directory we can copy later.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Copy the application source code after dependencies (better caching).
COPY app.py .

############################################
# Stage 2 — Runtime (Production)
############################################

# Use a smaller Python runtime image.
FROM python:3.11-slim AS runtime

# Set the working directory inside the runtime image.
WORKDIR /app

# Create a non-root user (least privilege).
RUN adduser --disabled-password --gecos "" appuser

# Copy only installed dependencies from the builder stage.
COPY --from=builder /install /usr/local

# Copy only the application code needed to run.
COPY --from=builder /app/app.py /app/app.py

# Set environment variables for production defaults.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    APP_NAME=python-app \
    LOG_LEVEL=INFO \
    LOG_DIR=/var/log/python-app

# Create a logs directory (useful with a named volume).
RUN mkdir -p "${LOG_DIR}" && chown -R appuser:appuser "${LOG_DIR}"

# Expose the container port (documentation + tooling).
EXPOSE 5000

# Define a health check using Python itself (no curl needed).
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT','5000') + '/health', timeout=2).read()" || exit 1

# Switch to the non-root user.
USER appuser

# Entrypoint defines the executable; CMD provides default args.
ENTRYPOINT ["python"]
CMD ["app.py"]

