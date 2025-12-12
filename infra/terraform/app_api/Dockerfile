FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

# Install the project into `/app`
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install dependencies using uv
ENV UV_SYSTEM_PYTHON=1
RUN uv sync --locked --no-dev

# Install the project as a package
RUN uv pip install -e .

# Run the ETL process
CMD ["goats-elt", "api", "start", "--reload"]
