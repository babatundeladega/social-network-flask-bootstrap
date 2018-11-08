import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from flask import g

import app as application

logging.basicConfig()
logger = logging.getLogger(application.__name__)


class LoggerAPIRefContextFilter(logging.Filter):

    def filter(self, record):
        try:
            record.api_ref = getattr(g, 'api_ref', 'NO-API-REF')
        except RuntimeError:
            record.api_ref = 'NO-API-REF'
        return True


def safe_mkdir(dir_):
    if not os.path.exists(dir_):
        os.mkdir(dir_)


def _setup_log_path(log_filename):
    # create directory for logging file if it doesn't exist
    if '/' in log_filename:
        log_dir = log_filename.rsplit('/', 1)[0]

        try:
            safe_mkdir(log_dir)
        except Exception as e:
            print('Logging setup failed! Terminating... Error:', e)
            sys.exit(1)

    print('Logs directory: "%s"' % os.path.abspath(log_filename))


def _remove_logger_default_handlers(logger_):
    del logger_.handlers[:]


def _configure_app_logger(app, log_filename):
    file_handler = TimedRotatingFileHandler(
        log_filename,
        when=app.config.get('LOG_ROTATION_WHEN', 'midnight'),
        interval=app.config.get('LOG_ROTATION_INTERVAL', 1),
        backupCount=app.config.get('LOG_BACKUP_COUNT', 60))
    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s|%(levelname)-5s [%(api_ref)-20s] %(message)s')
    logger_filter = LoggerAPIRefContextFilter()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    file_handler.setLevel(app.config.get('FILE_LOG_LEVEL', logging.DEBUG))
    console_handler.setLevel(app.config.get('CONSOLE_LOG_LEVEL', logging.DEBUG))

    _remove_logger_default_handlers(app.logger)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addFilter(logger_filter)


def setup_logging(app):
    """Set up a logger for the application."""
    global logger

    log_filename = app.config.get('LOG_FILENAME', 'logs/application.log')
    _setup_log_path(log_filename)

    _configure_app_logger(app, log_filename)
    logger = app.logger
