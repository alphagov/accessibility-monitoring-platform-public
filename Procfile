web: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py recache_statuses && waitress-serve --port=$PORT accessibility_monitoring_platform.wsgi:application
