# coding=utf-8

import logging
from logging.handlers import TimedRotatingFileHandler

logHandler = TimedRotatingFileHandler("messages.log", when="D")
logFormatter = logging.Formatter('#%(asctime)s %(name)s %(levelname)-8s# %(message)s', "%m/%d/%Y %H:%M:%S")
logHandler.setFormatter(logFormatter)
logHandler.setLevel(logging.WARNING)
logger = logging.getLogger('')
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

for k in range(5):
    logger.debug("Line %d" % k)
