web: gunicorn alfa.wsgi --log-file -
worker: celery -A alfa worker --loglevel=info -P solo