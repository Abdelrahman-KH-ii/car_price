FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# collectstatic needs SECRET_KEY even if DEBUG=False
RUN SECRET_KEY=collectstatic-dummy-key \
    DEBUG=False \
    DB_ENGINE=sqlite \
    python manage.py collectstatic --noinput

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# PORT env var injected by Render/Railway automatically
CMD sh -c "python manage.py migrate --noinput && \
           gunicorn carprice.wsgi:application \
           --bind 0.0.0.0:${PORT:-8000} \
           --workers 2 \
           --threads 2 \
           --timeout 120 \
           --access-logfile - \
           --error-logfile -"
