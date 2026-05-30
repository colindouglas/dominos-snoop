FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY tracker.py ./

ENV DATA_DIR=/data
VOLUME /data

CMD ["uv", "run", "dominos-snoop"]
