bind = "unix:/tmp/dev.oknesset.sock"
workers = 1
debug = True
daemon = True
pidfile = "/tmp/dev.oknesset.gunicorn.pid"
log_file = "/var/log/dev.oknesset/gunicorn.log"
log_level = "debug"
name = "dev.oknesset.gunicorn"
