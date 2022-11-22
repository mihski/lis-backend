import os

bind = f":{os.getenv('SERVER_BIND_PORT', 8000)}"
workers = os.getenv("GUNICORN_WORKERS", 1)
timeout = 30
reload = True
worker_class = "uvicorn.workers.UvicornWorker"