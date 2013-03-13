from cherrypy.process import servers, plugins
from cherrypy import wsgiserver
import cherrypy
import os
import os.path
import datetime
import logging
import logging.handlers


from . import spider


LOGS_DIR = 'logs'

if not os.path.isdir(LOGS_DIR):
    os.mkdir(LOGS_DIR)

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

def log_access():
    headers = str(cherrypy.request.headers) if cherrypy.request.headers is not None else '[No headers]'
    domain = str(cherrypy.request.base) if cherrypy.request.base is not None else '[No domain]'
    request_line = str(cherrypy.request.request_line) if cherrypy.request.request_line is not None else '[No request line]'
    status = str(cherrypy.response.status) if cherrypy.response.status is not None else '[No status]'
    access_logger.info('%s "%s" %s %s', domain, request_line, status, headers)

cherrypy.tools.werp_access_log = cherrypy.Tool('on_end_resource', log_access)

def fake_wait_for_occupied_port(host, port): return
servers.wait_for_occupied_port = fake_wait_for_occupied_port

cherrypy.config.update({
    'tools.sessions.on': False,
    'tools.encode.on': True,
    'tools.encode.encoding': 'utf-8',
    'tools.encode.text_only': False,
    'tools.gzip.on': True,
    'tools.werp_access_log.on': True,
    #'server.thread_pool': 111,
    #'server.socket_queue_size': 33,
    'log.access_file': LOGS_DIR + '/cherrypy_access.log',
    'log.error_file':  LOGS_DIR + '/cherrypy_error.log'})

wsgis = []
wsgis.append(spider.wsgi())

cherrypy.server.unsubscribe()

for wsgi in wsgis:
    numthreads = 10
    request_queue_size = 5
    if hasattr(wsgi, 'numthreads') and wsgi.numthreads > 0:
        numthreads = wsgi.numthreads
    if hasattr(wsgi, 'request_queue_size') and wsgi.request_queue_size > 0:
        request_queue_size = wsgi.request_queue_size
    s = cherrypy.wsgiserver.CherryPyWSGIServer(wsgi.bind_address, wsgi, numthreads=numthreads,
        request_queue_size=request_queue_size)
    sa = servers.ServerAdapter(cherrypy.engine, s)
    sa.subscribe()

plugins.Daemonizer(cherrypy.engine).subscribe()

cherrypy.engine.start()