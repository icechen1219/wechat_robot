# coding=utf-8

import logging
import logging.config

logging.config.fileConfig("logger.conf")


def logmessage():
    logger = logging.getLogger("msgLogger")
    logger.warning("There is a error in this file")


def logdebug():
    logger = logging.getLogger("debugLogger")
    logger.debug("There is a debug in this file")


logdebug()


def fun():
    print("test")
    logmessage()


fun()
