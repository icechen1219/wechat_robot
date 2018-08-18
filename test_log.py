#################################################################################################
import logging
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
# 基本的日志系统配置
# logging.basicConfig(filename='wechat.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
# 定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大2M
# logging.basicConfig()
Rthandler = RotatingFileHandler('event.log', maxBytes=2 * 1024 * 1024, backupCount=5)
Rthandler.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
Rthandler.setFormatter(formatter)
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
logger.addHandler(Rthandler)
################################################################################################

logging.debug('debug msg')
logging.info('info msg')
logging.warning('warn msg')
logging.error('error msg')
logging.fatal('fatal msg')
logging.debug('end msg')

print(u'this is a test')
