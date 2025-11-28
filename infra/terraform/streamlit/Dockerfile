FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    cmake \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock* README.md .python-version ./

RUN uv sync --no-dev

COPY data/ ./data
COPY src/streamlit ./src

EXPOSE 8080

CMD ["uv", "run", "streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
