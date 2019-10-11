web: daphne centralperk.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: celery -A centralperk worker -l info -E -P gevent -c 25 -n worker1@centralperk
worker: python manage.py runworker channels -v2