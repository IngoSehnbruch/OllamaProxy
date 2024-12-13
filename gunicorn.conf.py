# Number of worker processes (adjust based on the number of CPU cores)
workers = 2

# Bind to a specific address and port
bind = "0.0.0.0:9434"

# Worker timeout in seconds (default is 30)
timeout = 300

# Log level
loglevel = "info"

# Optional: Access log and error log files
accesslog = "-"  # "-" outputs access logs to stdout
errorlog = "-"   # "-" outputs error logs to stderr