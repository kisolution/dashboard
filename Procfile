web: gunicorn alfa.wsgi --timeout 120 --log-file -
worker: python manage.py process_tasks --queue=default