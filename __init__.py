import logging
import logging.handlers

LOGS_DIR = '/home/wwwlogs'

access_logger = logging.getLogger('werp_access')
access_logger.setLevel(logging.DEBUG)
access_logger_fh = logging.handlers.TimedRotatingFileHandler(LOGS_DIR + '/werp_access.log', when='midnight')
access_logger_fh.setLevel(logging.DEBUG)
access_logger_formatter = logging.Formatter('[%(asctime)s] %(message)s')
access_logger_fh.setFormatter(access_logger_formatter)
access_logger.addHandler(access_logger_fh)

error_logger = logging.getLogger('werp_error')
error_logger.setLevel(logging.DEBUG)
error_logger_fh = logging.handlers.TimedRotatingFileHandler(LOGS_DIR + '/werp_error.log', when='midnight')
error_logger_fh.setLevel(logging.DEBUG)
error_logger_formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s %(message)s')
error_logger_fh.setFormatter(error_logger_formatter)
error_logger.addHandler(error_logger_fh)

from . import spider

app = spider.wsgi()




error_logger.info('Yo!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')