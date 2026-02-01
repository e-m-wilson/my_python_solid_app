# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Set work directory
WORKDIR /app

# Install dependencies for building poetry packages
RUN apt-get update && apt-get install -y curl build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml poetry.lock /app/

# disable venv creation
RUN poetry config virtualenvs.create false 

# Install project dependencies without dev packages
RUN poetry install --without dev --no-interaction --no-ansi

# Ensure Poetry bin dir is on PATH
ENV PATH="/usr/local/bin:/root/.local/bin:$PATH"

# Copy the rest of the source code / alembic
COPY src /app/src
COPY src/repl.py /app/repl.py
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

# Stage 2: Run stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /app /app
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH="/usr/local/bin:/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Command to run
CMD ["sh", "-c", "poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000"]