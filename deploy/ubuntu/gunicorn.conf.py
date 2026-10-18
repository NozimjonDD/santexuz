"""systemd owns fd 3; no public TCP port and no autoreload in production."""
import os

bind = "fd://3"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_class = "gthread"
timeout = 60
graceful_timeout = 45
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = False
worker_tmp_dir = "/dev/shm"
accesslog = "-"
errorlog = "-"
# Do not include query strings (Telegram init data or other personal data).
access_log_format = '%(t)s "%(m)s %(U)s %(H)s" %(s)s %(b)s %(L)s'
capture_output = True
