#!/usr/bin/env python
'''
A simple, lightweight, WSGI-compatible web framework.
'''

__author__ = 'SLZ'

# import build-in modules
import os
import sys
import time
import datetime
import threading
import logging
import traceback
import hashlib
import functools
import json
from io import StringIO
# import custom modules
from .common import Dict
from .errors import notfound, HttpError, RedirectError
from .request import Request
from .response import Response
from .template import Template, Jinja2TemplateEngine
from .router import Router
from .apis import APIError

# thread local object for storing request and response:
ctx = threading.local()

class digwebs(object):
    def __init__(
        self,
        root_path = None,
        template_folder = 'views',
        middlewares_folder= 'middlewares',
        controller_folder = 'controllers',
        is_develop_mode = True):
        '''
        Init a digwebs.

        Args:
          root_path: root path.
        '''

        self.root_path = root_path if root_path else os.path.abspath(os.path.dirname(sys.argv[0]))
        self.middleware = []
        self.template_folder = template_folder
        self.middlewares_folder = middlewares_folder
        self.controller_folder = controller_folder
        self.is_develop_mode = is_develop_mode
        self.template_callbacks = set()
        self.router = None
    
    def init_all(self):
        if self.template_folder:
            self._init_template_engine(os.path.join(self.root_path, self.template_folder))
        
        self.router = Router(self.is_develop_mode)
        self.middleware.append(self.router.create_controller(self.root_path,self.controller_folder,))
        if self.middlewares_folder:
            self._init_middlewares(os.path.join(self.root_path, self.middlewares_folder))

    def _init_template_engine(self,template_path):
        def datetime_filter(t):
            delta = int(time.time() - t)
            if delta < 60:
                return u'1分钟前'
            if delta < 3600:
                return u'%s分钟前' % (delta // 60)
            if delta < 86400:
                return u'%s小时前' % (delta // 3600)
            if delta < 604800:
                return u'%s天前' % (delta // 86400)
            dt = datetime.datetime.fromtimestamp(t)
            return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

        self.template_engine = Jinja2TemplateEngine(template_path)
        self.template_engine.add_filter('datetime', datetime_filter)

    def _init_middlewares(self,middlewares_path):
        for f in os.listdir(middlewares_path):
            if f.endswith('.py'):
                import_module = f.replace(".py", "")
                m = __import__(self.middlewares_folder, globals(), locals(),
                               [import_module])
                s_m = getattr(m, import_module)
                fn = getattr(s_m, import_module, None)
                if fn is not None and callable(
                        fn) and not import_module.endswith('__'):
                    self.middleware.append(fn())

        def take_second(elem):
            return elem[1]

        self.middleware.sort(key=take_second)

    def run(self, port=9999, host='127.0.0.1'):
        from wsgiref.simple_server import make_server
        logging.info('application (%s) will start at %s:%s...' %
                     (self.root_path, host, port))
        server = make_server(host, port, self.get_wsgi_application())
        server.serve_forever()

    def get_wsgi_application(self):
        _application = Dict(document_root=self.root_path)

        def fn_route():
            def route_entry(context, next):
                def dispatch(i):
                    fn = self.middleware[i][0]
                    if i == len(self.middleware):
                        fn = next
                    return fn(context, lambda: dispatch(i + 1))

                return dispatch(0)

            return route_entry

        fn_exec = fn_route()

        def wsgi(env, start_response):
            ctx.application = _application
            ctx.request = Request(env)
            response = ctx.response = Response()
            try:
                r = fn_exec(ctx, None)
                if isinstance(r, Template):
                    tmp = []
                    for cbf in self.template_callbacks:
                        r.model.update(cbf())
                    r.model['ctx'] = ctx
                    tmp.append(self.template_engine(r.template_name, r.model))
                    r = tmp
                if isinstance(r, str):
                    tmp = []
                    tmp.append(r.encode('utf-8'))
                    r = tmp
                if r is None:
                    r = []
                start_response(response.status, response.headers)
                return r
            except RedirectError as e:
                response.set_header('Location', e.location)
                start_response(e.status, response.headers)
                return []
            except HttpError as e:
                start_response(e.status, response.headers)
                return ['<html><body><h1>', e.status, '</h1></body></html>']
            except Exception as e:
                logging.exception(e)
                '''
                if not configs.get('debug',False):
                    start_response('500 Internal Server Error', [])
                    return ['<html><body><h1>500 Internal Server Error</h1></body></html>']
                '''
                exc_type, exc_value, exc_traceback = sys.exc_info()
                fp = StringIO()
                traceback.print_exception(
                    exc_type, exc_value, exc_traceback, file=fp)
                stacks = fp.getvalue()
                fp.close()
                start_response('500 Internal Server Error', [])
                return [
                    r'''<html><body><h1>500 Internal Server Error</h1><div style="font-family:Monaco, Menlo, Consolas, 'Courier New', monospace;"><pre>''',
                    stacks.replace('<', '&lt;').replace('>', '&gt;'),
                    '</pre></div></body></html>'
                ]
            finally:
                del ctx.application
                del ctx.request
                del ctx.response

        return wsgi

    def register_template_callback(self,cb):
        self.template_callbacks.add(cb)
    
    def unregister_template_callback(self,cb):
        self.template_callbacks.remove(cb)
    
    @property
    def static_resource_url(self):
        return self.template_engine.get_globals('static_file_prefix')

    @static_resource_url.setter
    def static_resource_url(self, value):
        self.template_engine.set_globals('static_file_prefix',value)

    def get(self, path):
        '''
        A @get decorator.

        @get('/:id')
        def index(id):
            pass

        >>> @get('/test/:id')
        ... def test():
        ...     return 'ok'
        ...
        >>> test.__web_route__
        '/test/:id'
        >>> test.__web_method__
        'GET'
        >>> test()
        'ok'
        '''

        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'GET'
            return func

        return _decorator

    def post(self, path):
        '''
        A @post decorator.

        >>> @post('/post/:id')
        ... def testpost():
        ...     return '200'
        ...
        >>> testpost.__web_route__
        '/post/:id'
        >>> testpost.__web_method__
        'POST'
        >>> testpost()
        '200'
        '''

        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'POST'
            return func

        return _decorator

    def put(self, path):
        '''
        A @put decorator.
        '''

        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'PUT'
            return func

        return _decorator

    def delete(self, path):
        '''
        A @delete decorator.
        '''

        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'DELETE'
            return func

        return _decorator

    def view(self, path):
        '''
        A view decorator that render a view by dict.

        >>> @view('test/view.html')
        ... def hello():
        ...     return dict(name='Bob')
        >>> t = hello()
        >>> isinstance(t, Template)
        True
        >>> t.template_name
        'test/view.html'
        >>> @view('test/view.html')
        ... def hello2():
        ...     return ['a list']
        >>> t = hello2()
        Traceback (most recent call last):
        ...
        ValueError: Expect return a dict when using @view() decorator.
        '''

        def _decorator(func):
            @functools.wraps(func)
            def _wrapper(*args, **kw):
                r = func(*args, **kw)
                if isinstance(r, dict):
                    logging.info('return Template')
                    return Template(path, **r)
                raise ValueError(
                    'Expect return a dict when using @view() decorator.')

            return _wrapper

        return _decorator
    
    def dynamic_view(self, pathfn):
        def _decorator(func):
            @functools.wraps(func)
            def _wrapper(*args, **kw):
                r = func(*args, **kw)
                if isinstance(r, dict):
                    logging.info('return Template')
                    return Template(pathfn(), **r)
                raise ValueError('Expect return a dict when using @view() decorator.')
            return _wrapper
        return _decorator

    def api(self,func):
        '''
        A decorator that makes a function to json api, makes the return value as json.

        @app.route('/api/test')
        @api
        def api_test():
            return dict(result='123', items=[])
        '''
        @functools.wraps(func)
        def _wrapper(*args, **kw):
            try:
                r = json.dumps(func(*args, **kw))
            except APIError as e:
                r = json.dumps(dict(error=e.error, data=e.data, message=e.message))
            except Exception as e:
                logging.exception(e)
                r = json.dumps(dict(error='internalerror', data=e.__class__.__name__, message=str(e)))
            ctx.response.content_type = 'application/json'
            return r
        return _wrapper

current_app = None
def get_app(config_ins):
    global current_app
    if current_app is None:
        current_app = digwebs(**config_ins)
    return current_app

if __name__ == '__main__':
    sys.path.append('.')
    import doctest
    doctest.testmod()
