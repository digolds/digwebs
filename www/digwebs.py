#!/usr/bin/env python

__author__ = 'SLZ'

'''
digwebs framework entry.
'''

import logging, functools
logging.basicConfig(level=logging.INFO)

from .web import WSGIApplication

def get(path):
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

def post(path):
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

def put(path):
    '''
    A @put decorator.
    '''
    def _decorator(func):
        func.__web_route__ = path
        func.__web_method__ = 'PUT'
        return func
    return _decorator

def delete(path):
    '''
    A @delete decorator.
    '''
    def _decorator(func):
        func.__web_route__ = path
        func.__web_method__ = 'DELETE'
        return func
    return _decorator

def view(path):
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
            raise ValueError('Expect return a dict when using @view() decorator.')
        return _wrapper
    return _decorator

digolds = WSGIApplication(root_path)
digolds.init_middlewares()

if __name__ == '__main__':
    digolds.run(9000, host='0.0.0.0')
else:
    application = digolds.get_wsgi_application()
