# coding=utf-8

import logging
import logging.config

logging.config.fileConfig("logger.conf")


def logmessage(chat_from, chat_msg):
    logger = logging.getLogger("msgLogger")
    logger.warning("%s-%s", chat_from, chat_msg)


def debug(debug_info):
    logger = logging.getLogger("debugLogger")
    logger.debug(debug_info)


def info(common_info):
    logger = logging.getLogger("debugLogger")
    logger.info(common_info)
