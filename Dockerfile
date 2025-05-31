# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local
WORKDIR /app

# Copy project files
COPY . .

# Optional: Expose port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
