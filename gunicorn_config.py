"""
Gunicorn configuration file for HeyReach exports
Sets timeout to 30 minutes to handle large exports
"""

import os

# Server socket - use PORT from environment (Render requirement)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

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

# Startup hook to confirm config is loaded
def on_starting(server):
    print("=" * 60)
    print("🚀 GUNICORN CONFIG LOADED")
    print(f"   Port: {port}")
    print(f"   Timeout: {timeout} seconds ({timeout/60:.1f} minutes)")
    print(f"   Workers: {workers}")
    print(f"   Threads: {threads}")
    print("=" * 60)

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
