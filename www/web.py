#!/usr/bin/env python

'''
A simple, lightweight, WSGI-compatible web framework.
'''

__author__ = 'SLZ'

import os, re, sys, time, datetime, threading, logging, traceback, hashlib
from io import StringIO

# thread local object for storing request and response:
ctx = threading.local()

from .common import Dict
from .errors import notfound, HttpError, RedirectError
from .request import Request
from .response import Response

def make_signed_cookie(id, email, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [id, expires, hashlib.md5('{id}-{email}-{expires}-{secret}'.format(id=id,email=email,expires=expires,secret=configs.session.secret).encode('utf-8')).hexdigest()]
    return '-'.join(L)

class Template(object):

    def __init__(self, template_name, **kw):
        '''
        Init a template object with template name, model as dict, and additional kw that will append to model.

        >>> t = Template('hello.html', title='Hello', copyright='@2012')
        >>> t.model['title']
        'Hello'
        >>> t.model['copyright']
        '@2012'
        >>> t = Template('test.html', abc=u'ABC', xyz=u'XYZ')
        >>> t.model['abc']
        u'ABC'
        '''
        self.template_name = template_name
        self.model = dict(**kw)

class TemplateEngine(object):
    '''
    Base template engine.
    '''
    def __call__(self, path, model):
        return '<!-- override this method to render template -->'

class Jinja2TemplateEngine(TemplateEngine):

    '''
    Render using jinja2 template engine.

    >>> templ_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test')
    >>> engine = Jinja2TemplateEngine(templ_path)
    >>> engine.add_filter('datetime', lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S'))
    >>> engine('jinja2-test.html', dict(name='Michael', posted_at=datetime.datetime(2014, 6, 1, 10, 11, 12)))
    '<p>Hello, Michael.</p><span>2014-06-01 10:11:12</span>'
    '''

    def __init__(self, templ_dir, **kw):
        from jinja2 import Environment, FileSystemLoader
        if not 'autoescape' in kw:
            kw['autoescape'] = True
        self._env = Environment(
            variable_start_string = '{{{{',
            variable_end_string = '}}}}',
            loader=FileSystemLoader(templ_dir), **kw)

    def add_filter(self, name, fn_filter):
        self._env.filters[name] = fn_filter

    def __call__(self, path, model):
        return self._env.get_template(path).render(**model).encode('utf-8')

_RE_INTERCEPTROR_STARTS_WITH = re.compile(r'^([^\*\?]+)\*?$')
_RE_INTERCEPTROR_ENDS_WITH = re.compile(r'^\*([^\*\?]+)$')

def _build_pattern_fn(pattern):
    m = _RE_INTERCEPTROR_STARTS_WITH.match(pattern)
    if m:
        return lambda p: p.startswith(m.group(1))
    m = _RE_INTERCEPTROR_ENDS_WITH.match(pattern)
    if m:
        return lambda p: p.endswith(m.group(1))
    raise ValueError('Invalid pattern definition in interceptor.')

def interceptor(pattern='/'):
    '''
    An @interceptor decorator.

    @interceptor('/admin/')
    def check_admin(req, resp):
        pass
    '''
    def _decorator(func):
        func.__interceptor__ = _build_pattern_fn(pattern)
        return func
    return _decorator

def _build_interceptor_fn(func, next):
    def _wrapper():
        if func.__interceptor__(ctx.request.path_info):
            return func(next)
        else:
            return next()
    return _wrapper

def _build_interceptor_chain(last_fn, *interceptors):
    '''
    Build interceptor chain.

    >>> def target():
    ...     print 'target'
    ...     return 123
    >>> @interceptor('/')
    ... def f1(next):
    ...     print 'before f1()'
    ...     return next()
    >>> @interceptor('/test/')
    ... def f2(next):
    ...     print 'before f2()'
    ...     try:
    ...         return next()
    ...     finally:
    ...         print 'after f2()'
    >>> @interceptor('/')
    ... def f3(next):
    ...     print 'before f3()'
    ...     try:
    ...         return next()
    ...     finally:
    ...         print 'after f3()'
    >>> chain = _build_interceptor_chain(target, f1, f2, f3)
    >>> ctx.request = Dict(path_info='/test/abc')
    >>> chain()
    before f1()
    before f2()
    before f3()
    target
    after f3()
    after f2()
    123
    >>> ctx.request = Dict(path_info='/api/')
    >>> chain()
    before f1()
    before f3()
    target
    after f3()
    123
    '''
    L = list(interceptors)
    L.reverse()
    fn = last_fn
    for f in L:
        fn = _build_interceptor_fn(f, fn)
    return fn

class WSGIApplication(object):

    def __init__(self, document_root, **kw):
        '''
        Init a WSGIApplication.

        Args:
          document_root: document root path.
        '''
        self._running = False
        self._document_root = document_root
        self._template_engine = None

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

        self.template_engine = Jinja2TemplateEngine(os.path.join(document_root, 'views'))
        self.template_engine.add_filter('datetime', datetime_filter)
        self.middleware = []

    def _check_not_running(self):
        if self._running:
            raise RuntimeError('Cannot modify WSGIApplication when running.')

    @property
    def template_engine(self):
        return self._template_engine

    @template_engine.setter
    def template_engine(self, engine):
        self._check_not_running()
        self._template_engine = engine

    def init_middlewares(self):
        for f in os.listdir(self._document_root + r'/middlewares'):
            if f.endswith('.py'):
                import_module = f.replace(".py", "")
                m = __import__('middlewares', globals(), locals(), [import_module])
                s_m = getattr(m, import_module)
                fn = getattr(s_m, import_module, None)
                if fn is not None and callable(fn) and not import_module.endswith('__'):
                    self.middleware.append(fn())
        def take_second(elem):
            return elem[1]
        self.middleware.sort(key=take_second)

    def run(self, port=9000, host='127.0.0.1'):
        from wsgiref.simple_server import make_server
        logging.info('application (%s) will start at %s:%s...' % (self._document_root, host, port))
        server = make_server(host, port, self.get_wsgi_application())
        server.serve_forever()

    def get_wsgi_application(self):
        self._check_not_running()
        self._running = True

        _application = Dict(document_root=self._document_root)

        def fn_route():
            def route_entry(context,next):
                def dispatch(i):
                    fn = self.middleware[i][0]
                    if i == len(self.middleware):
                        fn = next
                    return fn(context,lambda : dispatch(i+1))

                return dispatch(0)
            return route_entry
        fn_exec = fn_route()

        def wsgi(env, start_response):
            ctx.application = _application
            ctx.request = Request(env)
            response = ctx.response = Response()
            try:
                r = fn_exec(ctx,None)
                if isinstance(r, Template):
                    tmp = []
                    tmp.append(self._template_engine(r.template_name, r.model))
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
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=fp)
                stacks = fp.getvalue()
                fp.close()
                start_response('500 Internal Server Error', [])
                return [
                    r'''<html><body><h1>500 Internal Server Error</h1><div style="font-family:Monaco, Menlo, Consolas, 'Courier New', monospace;"><pre>''',
                    stacks.replace('<', '&lt;').replace('>', '&gt;'),
                    '</pre></div></body></html>']
            finally:
                del ctx.application
                del ctx.request
                del ctx.response

        return wsgi

if __name__=='__main__':
    sys.path.append('.')
    import doctest
    doctest.testmod()
