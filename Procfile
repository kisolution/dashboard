web: export PYTHONPATH=$PYTHONPATH:$PWD && gunicorn alfa.wsgi --timeout 120 --log-file -
worker: export PYTHONPATH=$PYTHONPATH:$PWD && python manage.py process_tasks