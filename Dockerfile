FROM ghcr.io/astral-sh/uv@sha256:04d046b13e60d6bcec73cbc5e1cad25d680dea90c8573340950a0ac2d1aef424 AS uv
FROM library/python@sha256:2325bb286ec344af3e5898cc224b5844e2707ac6e26b1632516fd3edc84a5e26 AS base
COPY --from=uv /uv /uvx /usr/local/bin/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_NO_SYNC=1 UV_NO_DEV=1 PATH=/opt/venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --uid 1000 --create-home app && mkdir -p /opt/venv /var/lib/celery && chown -R app:app /opt/venv /var/lib/celery /app
COPY --chown=app:app pyproject.toml uv.lock .python-version ./
USER app
RUN uv sync --frozen --no-dev --no-install-project
COPY --chown=app:app . .
FROM base AS development
CMD ["uv", "run", "--frozen", "uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
FROM base AS checks
ENV UV_NO_DEV=0
RUN uv sync --frozen --group dev --no-install-project
FROM checks AS e2e
USER root
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
RUN uv run --frozen playwright install --with-deps chromium && chmod -R a+rX /opt/playwright
USER app

FROM library/node@sha256:4196d66a565c6f195728d9952f161f4adfe2ad753052a08b7ec7f1c5a6bda42b AS assets
WORKDIR /assets
COPY package.json package-lock.json ./
RUN npm ci
COPY static/src ./static/src
COPY templates ./templates
RUN npm run build:css && npm run check:js
FROM base AS static-build
COPY --from=assets --chown=app:app /assets/static/dist /app/static/dist
RUN uv run --frozen python manage.py collectstatic --noinput --settings=config.settings.build --ignore=src/styles.css
FROM base AS production
COPY --from=static-build --chown=app:app /app/staticfiles /app/staticfiles
ENV DJANGO_SETTINGS_MODULE=config.settings.production
CMD ["uv", "run", "--frozen", "uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
