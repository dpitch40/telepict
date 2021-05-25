import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '/var/log/telepict/gunicorn-access.log'
errorlog = '/var/log/telepict/gunicorn-error.log'
