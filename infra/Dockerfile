# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Install the project into `/app`
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire project
COPY . /app

# Install dependencies using uv
# Using --system flag since we're in an isolated container
ENV UV_SYSTEM_PYTHON=1
# RUN uv pip install -r requirements.txt
RUN uv sync --locked --no-dev

# Install the project as a package
RUN uv pip install -e .

# Run the ETL process
CMD ["uv", "run", "goats-elt"]