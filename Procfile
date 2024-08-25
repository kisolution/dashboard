web: python patch_background_tasks.py && gunicorn alfa.wsgi --timeout 120 --log-file -
worker: python patch_background_tasks.py && python manage.py process_tasks