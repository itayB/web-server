ARG PYTHON_VERSION=3.14.0

FROM python:${PYTHON_VERSION}-slim-trixie
WORKDIR /
# hadolint ignore=DL3008,DL4006
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     curl \
  && curl -LsSf https://astral.sh/uv/install.sh | sh \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY web_server /web_server
RUN /root/.local/bin/uv pip install . --system --no-cache-dir

# hadolint ignore=DL3008
CMD ["python", "-m", "web_server"]
