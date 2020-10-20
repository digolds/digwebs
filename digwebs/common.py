#!/usr/bin/env python

__author__ = 'SLZ'

import urllib

class Dict(dict):
    '''
    Simple dict but support access as x.y style.

    >>> d1 = Dict()
    >>> d1['x'] = 100
    >>> d1.x
    100
    >>> d1.y = 200
    >>> d1['y']
    200
    >>> d2 = Dict(a=1, b=2, c='3')
    >>> d2.c
    '3'
    >>> d2['empty']
    Traceback (most recent call last):
        ...
    KeyError: 'empty'
    >>> d2.empty
    Traceback (most recent call last):
        ...
    AttributeError: 'Dict' object has no attribute 'empty'
    >>> d3 = Dict(('a', 'b', 'c'), (1, 2, 3))
    >>> d3.a
    1
    >>> d3.b
    2
    >>> d3.c
    3
    '''
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

def quote(s, encoding='utf-8',safe='/'):
    '''
    Url quote as str.

    >>> quote('http://example/test?a=1+')
    'http%3A//example/test%3Fa%3D1%2B'
    >>> quote(u'hello world!')
    'hello%20world%21'
    '''
    return urllib.parse.quote(s.encode(encoding),safe)

def unquote(s, encoding='utf-8'):
    '''
    Url unquote as unicode.

    >>> unquote('http%3A//example/test%3Fa%3D1+')
    u'http://example/test?a=1+'
    '''
    return urllib.parse.unquote(s)

def to_str(s, encoding='utf-8'):
    '''
    Convert to str.

    >>> to_str('挖矿') == '挖矿'
    True
    >>> to_str(b'\xe6\x8c\x96\xe7\x9f\xbf') == '挖矿'
    True
    >>> to_str(-43) == '-43'
    True
    '''
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        return s.decode(encoding)
    return str(s)

if __name__=='__main__':
    import doctest
    doctest.testmod()