"""
Gunicorn configuration file for HeyReach exports
Sets timeout to 30 minutes to handle large exports
"""

# Server socket
bind = "0.0.0.0:10000"

# Worker processes
workers = 2
worker_class = "sync"
threads = 4

# Timeout - 30 minutes for large exports
timeout = 1800
graceful_timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "link-tracker"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (disabled for Render)
keyfile = None
certfile = None
