# gunicorn configuration for production
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
timeout = 120
keepalive = 5
errorlog = "-"
accesslog = "-"
capture_output = True
