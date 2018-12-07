#!/usr/bin/env python

__author__ = 'SLZ'

import cgi, urllib

from .common import to_str, unquote, Dict
from .body_parser import get_parser
import urllib.parse

class MultipartFile(object):
    '''
    Multipart file storage get from request input.

    f = ctx.request['file']
    f.filename # 'test.png'
    f.file # file-like object
    '''
    def __init__(self, storage):
        self.filename = to_str(storage.filename)
        self.file = storage.file
        self.data = storage.file.read()

import tempfile
from email.parser import FeedParser
class CustomFieldStorage(cgi.FieldStorage):
    def __init__(self, *args, **kwargs):
        cgi.FieldStorage.__init__(self, *args, **kwargs)

    def make_file(self):
        if self._binary_file or self.length >= 0:
            return tempfile.TemporaryFile("wb+")
        else:
            return tempfile.TemporaryFile("w+",
                encoding=self.encoding, newline = '\n')
    
    def __getattr__(self, name):
        if name != 'value':
            raise AttributeError(name)
        if self.file:
            self.file.seek(0)
            value = self.file.read()
            self.file.seek(0)
        elif self.list is not None:
            value = self.list
        else:
            value = None
        return value

import json

class Request(object):
    '''
    Request object for obtaining all http request information.
    '''

    def __init__(self, environ):
        self._environ = environ

    def _parse_input(self):
        def _convert(item):
            if isinstance(item, list):
                return [to_str(i.value) for i in item]
            if item.filename:
                return MultipartFile(item)
            return to_str(item.value)
        fs = CustomFieldStorage(fp=self._environ['wsgi.input'], environ=self._environ, keep_blank_values=True)
        received_data = fs.value
        if isinstance(received_data,list):
            inputs = dict()
            for key in fs:
                inputs[key] = _convert(fs[key])
        else:
            raise ValueError('unknown received data type')
        return inputs

    def _get_raw_input(self):
        '''
        Get raw input as dict containing values as unicode, list or MultipartFile.
        '''
        if not hasattr(self, '_raw_input'):
            self._raw_input = self._parse_input()
        return self._raw_input

    def __getitem__(self, key):
        '''
        Get input parameter value. If the specified key has multiple value, the first one is returned.
        If the specified key is not exist, then raise KeyError.

        >>> from StringIO import StringIO
        >>> r = Request({'REQUEST_METHOD':'POST', 'wsgi.input':StringIO('a=1&b=M%20M&c=ABC&c=XYZ&e=')})
        >>> r['a']
        u'1'
        >>> r['c']
        u'ABC'
        >>> r['empty']
        Traceback (most recent call last):
            ...
        KeyError: 'empty'
        >>> b = '----WebKitFormBoundaryQQ3J8kPsjFpTmqNz'
        >>> pl = ['--%s' % b, 'Content-Disposition: form-data; name=\\"name\\"\\n', 'Scofield', '--%s' % b, 'Content-Disposition: form-data; name=\\"name\\"\\n', 'Lincoln', '--%s' % b, 'Content-Disposition: form-data; name=\\"file\\"; filename=\\"test.txt\\"', 'Content-Type: text/plain\\n', 'just a test', '--%s' % b, 'Content-Disposition: form-data; name=\\"id\\"\\n', '4008009001', '--%s--' % b, '']
        >>> payload = '\\n'.join(pl)
        >>> r = Request({'REQUEST_METHOD':'POST', 'CONTENT_LENGTH':str(len(payload)), 'CONTENT_TYPE':'multipart/form-data; boundary=%s' % b, 'wsgi.input':StringIO(payload)})
        >>> r.get('name')
        u'Scofield'
        >>> r.gets('name')
        [u'Scofield', u'Lincoln']
        >>> f = r.get('file')
        >>> f.filename
        u'test.txt'
        >>> f.file.read()
        'just a test'
        '''
        r = self._get_raw_input()[key]
        if isinstance(r, list):
            return r[0]
        return r

    def get(self, key, default=None):
        '''
        The same as request[key], but return default value if key is not found.

        >>> from StringIO import StringIO
        >>> r = Request({'REQUEST_METHOD':'POST', 'wsgi.input':StringIO('a=1&b=M%20M&c=ABC&c=XYZ&e=')})
        >>> r.get('a')
        u'1'
        >>> r.get('empty')
        >>> r.get('empty', 'DEFAULT')
        'DEFAULT'
        '''
        r = self._get_raw_input().get(key, default)
        if isinstance(r, list):
            return r[0]
        return r

    def gets(self, key):
        '''
        Get multiple values for specified key.

        >>> from StringIO import StringIO
        >>> r = Request({'REQUEST_METHOD':'POST', 'wsgi.input':StringIO('a=1&b=M%20M&c=ABC&c=XYZ&e=')})
        >>> r.gets('a')
        [u'1']
        >>> r.gets('c')
        [u'ABC', u'XYZ']
        >>> r.gets('empty')
        Traceback (most recent call last):
            ...
        KeyError: 'empty'
        '''
        r = self._get_raw_input()[key]
        if isinstance(r, list):
            return r[:]
        return [r]

    def input(self, **kw):
        '''
        Get input as dict from request, fill dict using provided default value if key not exist.

        i = ctx.request.input(role='guest')
        i.role ==> 'guest'

        >>> from StringIO import StringIO
        >>> r = Request({'REQUEST_METHOD':'POST', 'wsgi.input':StringIO('a=1&b=M%20M&c=ABC&c=XYZ&e=')})
        >>> i = r.input(x=2008)
        >>> i.a
        u'1'
        >>> i.b
        u'M M'
        >>> i.c
        u'ABC'
        >>> i.x
        2008
        >>> i.get('d', u'100')
        u'100'
        >>> i.x
        2008
        '''
        copy = Dict(**kw)
        raw = self._get_raw_input()
        for k, v in raw.items():
            copy[k] = v[0] if isinstance(v, list) else v
        return copy

    def get_body(self):
        fp = self._environ['wsgi.input']
        return get_parser(self._environ['CONTENT_TYPE'])(fp.read())

    @property
    def remote_addr(self):
        '''
        Get remote addr. Return '0.0.0.0' if cannot get remote_addr.

        >>> r = Request({'REMOTE_ADDR': '192.168.0.100'})
        >>> r.remote_addr
        '192.168.0.100'
        '''
        return self._environ.get('REMOTE_ADDR', '0.0.0.0')

    @property
    def document_root(self):
        '''
        Get raw document_root as str. Return '' if no document_root.

        >>> r = Request({'DOCUMENT_ROOT': '/srv/path/to/doc'})
        >>> r.document_root
        '/srv/path/to/doc'
        '''
        return self._environ.get('DOCUMENT_ROOT', '')

    def get_query_string(self,to_json=False):
        '''
        Get raw query string as str. Return '' if no query string.

        >>> r = Request({'QUERY_STRING': 'a=1&c=2'})
        >>> r.get_query_string()
        'a=1&c=2'
        >>> r = Request({})
        >>> r.get_query_string()
        ''
        >>> r = Request({'QUERY_STRING': 'a=1&b=2&b=3'})
        >>> r.get_query_string(to_json=True)
        {'a': ['1'], 'b': ['2','3']}
        '''
        if to_json:
            return urllib.parse.parse_qs(self._environ.get('QUERY_STRING', '')) 
        return self._environ.get('QUERY_STRING', '')

    @property
    def environ(self):
        '''
        Get raw environ as dict, both key, value are str.

        >>> r = Request({'REQUEST_METHOD': 'GET', 'wsgi.url_scheme':'http'})
        >>> r.environ.get('REQUEST_METHOD')
        'GET'
        >>> r.environ.get('wsgi.url_scheme')
        'http'
        >>> r.environ.get('SERVER_NAME')
        >>> r.environ.get('SERVER_NAME', 'unamed')
        'unamed'
        '''
        return self._environ

    @property
    def request_method(self):
        '''
        Get request method. The valid returned values are 'GET', 'POST', 'HEAD'.

        >>> r = Request({'REQUEST_METHOD': 'GET'})
        >>> r.request_method
        'GET'
        >>> r = Request({'REQUEST_METHOD': 'POST'})
        >>> r.request_method
        'POST'
        '''
        return self._environ['REQUEST_METHOD']

    @property
    def path_info(self):
        '''
        Get request path as str.

        >>> r = Request({'PATH_INFO': '/test/a%20b.html'})
        >>> r.path_info
        '/test/a b.html'
        '''
        return urllib.parse.unquote(self._environ.get('PATH_INFO', ''))

    @property
    def host(self):
        '''
        Get request host as str. Default to '' if cannot get host..

        >>> r = Request({'HTTP_HOST': 'localhost:8080'})
        >>> r.host
        'localhost:8080'
        '''
        return self._environ.get('HTTP_HOST', '')

    def _get_headers(self):
        if not hasattr(self, '_headers'):
            hdrs = {}
            for k, v in self._environ.items():
                if k.startswith('HTTP_'):
                    # convert 'HTTP_ACCEPT_ENCODING' to 'ACCEPT-ENCODING'
                    hdrs[k[5:].replace('_', '-').upper()] = v
            self._headers = hdrs
        return self._headers

    @property
    def headers(self):
        '''
        Get all HTTP headers with key as str and value as unicode. The header names are 'XXX-XXX' uppercase.

        >>> r = Request({'HTTP_USER_AGENT': 'Mozilla/5.0', 'HTTP_ACCEPT': 'text/html'})
        >>> H = r.headers
        >>> H['ACCEPT']
        u'text/html'
        >>> H['USER-AGENT']
        u'Mozilla/5.0'
        >>> L = H.items()
        >>> L.sort()
        >>> L
        [('ACCEPT', u'text/html'), ('USER-AGENT', u'Mozilla/5.0')]
        '''
        return dict(**self._get_headers())

    def header(self, header, default=None):
        '''
        Get header from request as unicode, return None if not exist, or default if specified. 
        The header name is case-insensitive such as 'USER-AGENT' or u'content-Type'.

        >>> r = Request({'HTTP_USER_AGENT': 'Mozilla/5.0', 'HTTP_ACCEPT': 'text/html'})
        >>> r.header('User-Agent')
        u'Mozilla/5.0'
        >>> r.header('USER-AGENT')
        u'Mozilla/5.0'
        >>> r.header('Accept')
        u'text/html'
        >>> r.header('Test')
        >>> r.header('Test', u'DEFAULT')
        u'DEFAULT'
        '''
        return self._get_headers().get(header.upper(), default)

    def _get_cookies(self):
        if not hasattr(self, '_cookies'):
            cookies = {}
            cookie_str = self._environ.get('HTTP_COOKIE')
            if cookie_str:
                for c in cookie_str.split(';'):
                    pos = c.find('=')
                    if pos>0:
                        cookies[c[:pos].strip()] = unquote(c[pos+1:])
            self._cookies = cookies
        return self._cookies

    @property
    def cookies(self):
        '''
        Return all cookies as dict. The cookie name is str and values is unicode.

        >>> r = Request({'HTTP_COOKIE':'A=123; url=http%3A%2F%2Fwww.example.com%2F'})
        >>> r.cookies['A']
        u'123'
        >>> r.cookies['url']
        u'http://www.example.com/'
        '''
        return Dict(**self._get_cookies())

    def cookie(self, name, default=None):
        '''
        Return specified cookie value as unicode. Default to None if cookie not exists.

        >>> r = Request({'HTTP_COOKIE':'A=123; url=http%3A%2F%2Fwww.example.com%2F'})
        >>> r.cookie('A')
        u'123'
        >>> r.cookie('url')
        u'http://www.example.com/'
        >>> r.cookie('test')
        >>> r.cookie('test', u'DEFAULT')
        u'DEFAULT'
        '''
        return self._get_cookies().get(name, default)

if __name__=='__main__':
    import doctest
    doctest.testmod()