FROM python:3.14-slim AS deps
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.14-slim
WORKDIR /srv

COPY --from=deps /install /usr/local
COPY app/ app/
COPY scripts/ scripts/
COPY static/ static/
COPY feeds.json feeds_world.json feeds_gbfs.json ./
COPY docs/status.json docs/deep_check.json docs/

# Run as a dedicated non-root user; only /srv/data is writable.
RUN useradd --system --uid 10001 --no-create-home transit \
    && mkdir -p /srv/data && chown 10001:10001 /srv/data
USER 10001

VOLUME /srv/data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=4)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
