#!/usr/bin/env python

__author__ = 'SLZ'

import re, logging, mimetypes, os, types, importlib

from errors import notfound, badrequest

def _static_file_generator(fpath):
    BLOCK_SIZE = 8192
    with open(fpath, 'rb') as f:
        block = f.read(BLOCK_SIZE)
        while block:
            yield block
            block = f.read(BLOCK_SIZE)

class StaticFileRoute(object):
    def __init__(self):
        self.method = 'GET'
        self.is_static = False

    def match(self, url):
        if url.startswith('/static/'):
            return (url[1:], )
        return None

    def __call__(self, context, *args):
        fpath = os.path.join(context.application.document_root, args[0])
        if not os.path.isfile(fpath):
            raise notfound()
        fext = os.path.splitext(fpath)[1]
        context.response.content_type = mimetypes.types_map.get(fext.lower(), 'application/octet-stream')
        return _static_file_generator(fpath)

class FaviconFileRoute(object):

    def __init__(self):
        self.method = 'GET'
        self.is_static = False

    def match(self, url):
        if url == '/favicon.ico':
            return ('favicon.ico', )
        return None

    def __call__(self, context, *args):
        fpath = os.path.join(context.application.document_root, args[0])
        if not os.path.isfile(fpath):
            raise notfound()
        fext = os.path.splitext(fpath)[1]
        context.response.content_type = mimetypes.types_map.get(fext.lower(), 'application/octet-stream')
        return _static_file_generator(fpath)

_re_route = re.compile(r'(\:[a-zA-Z_]\w*)')

def _build_regex(path):
    r'''
    Convert route path to regex.

    >>> _build_regex('/path/to/:file')
    '^\\/path\\/to\\/(?P<file>[^\\/]+)$'
    >>> _build_regex('/:user/:comments/list')
    '^\\/(?P<user>[^\\/]+)\\/(?P<comments>[^\\/]+)\\/list$'
    >>> _build_regex(':id-:pid/:w')
    '^(?P<id>[^\\/]+)\\-(?P<pid>[^\\/]+)\\/(?P<w>[^\\/]+)$'
    '''
    re_list = ['^']
    var_list = []
    is_var = False
    for v in _re_route.split(path):
        if is_var:
            var_name = v[1:]
            var_list.append(var_name)
            re_list.append(r'(?P<%s>[^\/]+)' % var_name)
        else:
            s = ''
            for ch in v:
                if ch>='0' and ch<='9':
                    s = s + ch
                elif ch>='A' and ch<='Z':
                    s = s + ch
                elif ch>='a' and ch<='z':
                    s = s + ch
                else:
                    s = s + '\\' + ch
            re_list.append(s)
        is_var = not is_var
    re_list.append('$')
    return ''.join(re_list)

class Route(object):
    '''
    A Route object is a callable object.
    '''

    def __init__(self, func):
        self.path = func.__web_route__
        self.method = func.__web_method__
        self.is_static = _re_route.search(self.path) is None
        if not self.is_static:
            self.route = re.compile(_build_regex(self.path))
        self.func = func

    def match(self, url):
        m = self.route.match(url)
        if m:
            return m.groups()
        return None

    def __call__(self, context, *args):
        return self.func(*args)

    def __str__(self):
        if self.is_static:
            return 'Route(static,%s,path=%s)' % (self.method, self.path)
        return 'Route(dynamic,%s,path=%s)' % (self.method, self.path)

    __repr__ = __str__

def _load_module(module_name):
    '''
    Load module from name as str.

    >>> m = _load_module('xml')
    >>> m.__name__
    'xml'
    >>> m = _load_module('xml.sax')
    >>> m.__name__
    'xml.sax'
    >>> m = _load_module('xml.sax.handler')
    >>> m.__name__
    'xml.sax.handler'
    '''
    last_dot = module_name.rfind('.')
    if last_dot==(-1):
        return __import__(module_name, globals(), locals())
    from_module = module_name[:last_dot]
    import_module = module_name[last_dot+1:]
    m = __import__(from_module, globals(), locals(), [import_module])
    return getattr(m, import_module)

class Router(object):

    def __init__(
        self,
        is_develop_mode):
        self.static_method_to_route = {'GET':{},'POST':{},'PUT':{},'DELETE':{}}
        self.dynamic_method_to_route ={'GET':[],'POST':[],'PUT':[],'DELETE':[]}
        if is_develop_mode:
            self.dynamic_method_to_route['GET'].append(StaticFileRoute())
            self.dynamic_method_to_route['GET'].append(FaviconFileRoute())

    def create_route(self, func):
        route = Route(func)
        if route.is_static:
            self.static_method_to_route[route.method][route.path] = route
        else:
            self.dynamic_method_to_route[route.method].append(route)
        logging.info('Add route: %s' % str(route))

    def add_module(self, mod):
        m = mod if type(mod)==types.ModuleType else _load_module(mod)
        logging.info('Add module: %s' % m.__name__)
        for name in dir(m):
            fn = getattr(m, name)
            if callable(fn) and hasattr(fn, '__web_route__') and hasattr(fn, '__web_method__'):
                self.create_route(fn)

    def route_to(self, request_method,path_info):
        fn = self.static_method_to_route[request_method].get(path_info, None)
        if fn:
            return (fn, [])
        for fn in self.dynamic_method_to_route[request_method]:
            args = fn.match(path_info)
            if args:
                return (fn, args)
        raise notfound()

def create_controller(root_path, controller_folder, is_develop_mode):
    r = Router(is_develop_mode)
    controller_modules_path = os.path.join(root_path, controller_folder)
    for f in os.listdir(controller_modules_path):
        if f.endswith('controller.py') and f != '__init__.py':
            import_module = f.replace(".py", "")
            m = importlib.import_module(import_module)
            #s_m = getattr(m, import_module)
            r.add_module(m)

    def handle_route(ctx, next):
        request_method = ctx.request.request_method
        path_info = ctx.request.path_info
        f, arg = r.route_to(request_method,path_info)
        return f(ctx, *arg)
    return (handle_route,10000)