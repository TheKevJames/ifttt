import logging
import os
import sys

from pythonjsonlogger import jsonlogger


LOG_FORMAT = '%(levelname) %(name)s %(lineno) %(message)'


class JsonFormatter(jsonlogger.JsonFormatter):
    def __init__(self, fmt=LOG_FORMAT, *args, **kwargs):
        jsonlogger.JsonFormatter.__init__(self, fmt=fmt, *args, **kwargs)

    def process_log_record(self, log_record):
        # stackdriver uses "severity" instead of "levelname"
        log_record['severity'] = log_record['levelname']
        del log_record['levelname']

        return super(JsonFormatter, self).process_log_record(log_record)


def configure():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logging.getLogger().addHandler(handler)

    if os.environ.get('DEBUG', '').lower() == 'true':
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('asyncio').setLevel(logging.INFO)
        logging.getLogger('google').setLevel(logging.INFO)
        logging.getLogger('urllib3').setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.INFO)
