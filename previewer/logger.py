import logging

from . import __name__ as app

logger = logging.getLogger(app)

logging.basicConfig(format="%(message)s", level=logging.DEBUG)


DEBUG = logger.debug
INFO = logger.info
WARNING = logger.warning
