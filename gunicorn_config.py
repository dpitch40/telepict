import multiprocessing

bind = "0.0.0.0:443"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = '/var/log/telepict/gunicorn-access.log'
errorlog = '/var/log/telepict/gunicorn-error.log'
keyfile = '/etc/letsencrypt/live/www.telephone-pictionary.net/privkey.pem'
certfile = '/etc/letsencrypt/live/www.telephone-pictionary.net/fullchain.pem'
