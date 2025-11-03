FROM python:3.12-slim-bookworm

ARG BOT_NAME="satsuki"

# set environment variables
ENV TZ='Asia/Tokyo'

# uv environment variables
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT='/usr/local/'
ENV UV_SYSTEM_PYTHON=1

WORKDIR /usr/src/${BOT_NAME}/
COPY ./ ./

RUN apt update && \
    apt upgrade -y && \
    apt install -y git build-essential nano curl tzdata

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# install dependencies
RUN uv sync --frozen --no-dev --no-cache

CMD ["uv","run","main.py"]