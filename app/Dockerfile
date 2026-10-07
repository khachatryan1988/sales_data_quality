# Use a lightweight Python base image.
FROM python:3.12-slim

# All application files live under /app.
WORKDIR /app

# Install Python dependencies first to improve Docker layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code, SQL files, tests, and data directories.
COPY src ./src
COPY sql ./sql
COPY tests ./tests
COPY data ./data

# Run the full analytics pipeline by default.
CMD ["python", "src/run_pipeline.py"]
