import cherrypy
import json
import os.path
import urllib.request
import urllib.parse
import logging
import threading


from . import graber
from .uatrains import orm
from .uatrains.layout import layout
from .uatrains import notifier
    

class spider(object):
    @cherrypy.expose
    def index(self):
        gth = threading.Thread(name='uatr_spider', target=graber.grab)
        gth.setDaemon(True)
        gth.start()
    @cherrypy.expose
    def get_railway_timetable(self, rwid):
        lng = 'RU'
        conn = orm.q_engine.connect()
        ses = orm.sescls(bind=conn)
        rw = None
        l = ''
        try:
            rw = ses.query(orm.Railway).\
                options(orm.joinedload_all(orm.Railway.routes, orm.Route.route_trains, orm.RouteTrain.train,
                orm.E.t_ss)).\
                filter(orm.Railway.id == int(rwid)).\
                all()
        except:
            notifier.notify('Uatrains error', 'Can\'t find railway by rwid = ' + str(rwid) + '\n' +\
                traceback.format_exc())
        if rw is not None:
            if rw[0].routes is None or (rw[0].routes is not None and len(rw[0].routes) == 0):
                notifier.notify('Uatrains error', 'No routes were found for rwid = ' + str(rwid))
            l = layout.getRailwayTimetable(rw[0], lng)
        ses.close()
        conn.close()
        return l
    

def error_page_default(status, message, traceback, version):
    logging.error(traceback)    
    d = urllib.parse.urlencode({'status': status, 'message': message, 'traceback': traceback, 'version': version,
        'data': json.dumps({'subject': 'Uatrains spider error',
            'base': cherrypy.request.base, 'request_line': cherrypy.request.request_line})})
    d = d.encode('utf-8')
    req = urllib.request.Request('http://localhost:18404/sendmail')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')
    res = urllib.request.urlopen(req, d)
    return res.read().decode()

def wsgi():
    conf = os.path.join(os.path.dirname(__file__), "spider.conf")
    tree = cherrypy._cptree.Tree()
    app = tree.mount(spider(), config=conf)
    app.config.update({'/': {'error_page.default': error_page_default}})
    tree.bind_address = (app.config['global']['server.socket_host'], app.config['global']['server.socket_port'])
    return tree