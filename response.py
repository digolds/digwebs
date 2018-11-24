#!/usr/bin/env python

__author__ = 'SLZ'

import datetime, re

from .common import quote, unquote, to_str
from .response_code import RESPONSE_STATUSES, RESPONSE_HEADER_DICT, HEADER_X_POWERED_BY, RE_RESPONSE_STATUS

_TIMEDELTA_ZERO = datetime.timedelta(0)

# timezone as UTC+8:00, UTC-10:00

_RE_TZ = re.compile('^([\+\-])([0-9]{1,2})\:([0-9]{1,2})$')

class UTC(datetime.tzinfo):
    '''
    A UTC tzinfo object. 

    >>> tz0 = UTC('+00:00')
    >>> tz0.tzname(None)
    'UTC+00:00'
    >>> tz8 = UTC('+8:00')
    >>> tz8.tzname(None)
    'UTC+8:00'
    >>> tz7 = UTC('+7:30')
    >>> tz7.tzname(None)
    'UTC+7:30'
    >>> tz5 = UTC('-05:30')
    >>> tz5.tzname(None)
    'UTC-05:30'
    >>> from datetime import datetime
    >>> u = datetime.utcnow().replace(tzinfo=tz0)
    >>> l1 = u.astimezone(tz8)
    >>> l2 = u.replace(tzinfo=tz8)
    >>> d1 = u - l1
    >>> d2 = u - l2
    >>> d1.seconds
    0
    >>> d2.seconds
    28800
    '''

    def __init__(self, utc):
        utc = str(utc.strip().upper())
        mt = _RE_TZ.match(utc)
        if mt:
            minus = mt.group(1)=='-'
            h = int(mt.group(2))
            m = int(mt.group(3))
            if minus:
                h, m = (-h), (-m)
            self._utcoffset = datetime.timedelta(hours=h, minutes=m)
            self._tzname = 'UTC%s' % utc
        else:
            raise ValueError('bad utc time zone')

    def utcoffset(self, dt):
        return self._utcoffset

    def dst(self, dt):
        return _TIMEDELTA_ZERO

    def tzname(self, dt):
        return self._tzname

    def __str__(self):
        return 'UTC tzinfo object (%s)' % self._tzname

    __repr__ = __str__

UTC_0 = UTC('+00:00')

class Response(object):

    def __init__(self):
        self._status = '200 OK'
        self._headers = {'CONTENT-TYPE': 'text/html; charset=utf-8'}

    @property
    def headers(self):
        '''
        Return response headers as [(key1, value1), (key2, value2)...] including cookies.

        >>> r = Response()
        >>> r.headers
        [('Content-Type', 'text/html; charset=utf-8'), ('X-Powered-By', 'transwarp/1.0')]
        >>> r.set_cookie('s1', 'ok', 3600)
        >>> r.headers
        [('Content-Type', 'text/html; charset=utf-8'), ('Set-Cookie', 's1=ok; Max-Age=3600; Path=/; HttpOnly'), ('X-Powered-By', 'transwarp/1.0')]
        '''
        L = [(RESPONSE_HEADER_DICT.get(k, k), v) for k, v in self._headers.items()]
        if hasattr(self, '_cookies'):
            for v in self._cookies.values():
                L.append(('Set-Cookie', v))
        L.append(HEADER_X_POWERED_BY)
        return L

    def header(self, name):
        '''
        Get header by name, case-insensitive.

        >>> r = Response()
        >>> r.header('content-type')
        'text/html; charset=utf-8'
        >>> r.header('CONTENT-type')
        'text/html; charset=utf-8'
        >>> r.header('X-Powered-By')
        '''
        key = name.upper()
        if not key in RESPONSE_HEADER_DICT:
            key = name
        return self._headers.get(key)

    def unset_header(self, name):
        '''
        Unset header by name and value.

        >>> r = Response()
        >>> r.header('content-type')
        'text/html; charset=utf-8'
        >>> r.unset_header('CONTENT-type')
        >>> r.header('content-type')
        '''
        key = name.upper()
        if not key in RESPONSE_HEADER_DICT:
            key = name
        if key in self._headers:
            del self._headers[key]

    def set_header(self, name, value):
        '''
        Set header by name and value.

        >>> r = Response()
        >>> r.header('content-type')
        'text/html; charset=utf-8'
        >>> r.set_header('CONTENT-type', 'image/png')
        >>> r.header('content-TYPE')
        'image/png'
        '''
        key = name.upper()
        if not key in RESPONSE_HEADER_DICT:
            key = name
        self._headers[key] = to_str(value)

    @property
    def content_type(self):
        '''
        Get content type from response. This is a shortcut for header('Content-Type').

        >>> r = Response()
        >>> r.content_type
        'text/html; charset=utf-8'
        >>> r.content_type = 'application/json'
        >>> r.content_type
        'application/json'
        '''
        return self.header('CONTENT-TYPE')

    @content_type.setter
    def content_type(self, value):
        '''
        Set content type for response. This is a shortcut for set_header('Content-Type', value).
        '''
        if value:
            self.set_header('CONTENT-TYPE', value)
        else:
            self.unset_header('CONTENT-TYPE')

    @property
    def content_length(self):
        '''
        Get content length. Return None if not set.

        >>> r = Response()
        >>> r.content_length
        >>> r.content_length = 100
        >>> r.content_length
        '100'
        '''
        return self.header('CONTENT-LENGTH')

    @content_length.setter
    def content_length(self, value):
        '''
        Set content length, the value can be int or str.

        >>> r = Response()
        >>> r.content_length = '1024'
        >>> r.content_length
        '1024'
        >>> r.content_length = 1024 * 8
        >>> r.content_length
        '8192'
        '''
        self.set_header('CONTENT-LENGTH', str(value))

    def delete_cookie(self, name):
        '''
        Delete a cookie immediately.

        Args:
          name: the cookie name.
        '''
        self.set_cookie(name, '__deleted__', expires=0)

    def set_cookie(self, name, value, max_age=None, expires=None, path='/', domain=None, secure=False, http_only=True):
        '''
        Set a cookie.

        Args:
          name: the cookie name.
          value: the cookie value.
          max_age: optional, seconds of cookie's max age.
          expires: optional, unix timestamp, datetime or date object that indicate an absolute time of the 
                   expiration time of cookie. Note that if expires specified, the max_age will be ignored.
          path: the cookie path, default to '/'.
          domain: the cookie domain, default to None.
          secure: if the cookie secure, default to False.
          http_only: if the cookie is for http only, default to True for better safty 
                     (client-side script cannot access cookies with HttpOnly flag).

        >>> r = Response()
        >>> r.set_cookie('company', 'Abc, Inc.', max_age=3600)
        >>> r._cookies
        {'company': 'company=Abc%2C%20Inc.; Max-Age=3600; Path=/; HttpOnly'}
        >>> r.set_cookie('company', r'Example="Limited"', expires=1342274794.123, path='/sub/')
        >>> r._cookies
        {'company': 'company=Example%3D%22Limited%22; Expires=Sat, 14-Jul-2012 14:06:34 GMT; Path=/sub/; HttpOnly'}
        >>> dt = datetime.datetime(2012, 7, 14, 22, 6, 34, tzinfo=UTC('+8:00'))
        >>> r.set_cookie('company', 'Expires', expires=dt)
        >>> r._cookies
        {'company': 'company=Expires; Expires=Sat, 14-Jul-2012 14:06:34 GMT; Path=/; HttpOnly'}
        '''
        if not hasattr(self, '_cookies'):
            self._cookies = {}
        L = ['%s=%s' % (quote(name), quote(value))]
        if expires is not None:
            if isinstance(expires, (float, int)):
                L.append('Expires=%s' % datetime.datetime.fromtimestamp(expires, UTC_0).strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
            if isinstance(expires, (datetime.date, datetime.datetime)):
                L.append('Expires=%s' % expires.astimezone(UTC_0).strftime('%a, %d-%b-%Y %H:%M:%S GMT'))
        elif isinstance(max_age, (int)):
            L.append('Max-Age=%d' % max_age)
        L.append('Path=%s' % path)
        if domain:
            L.append('Domain=%s' % domain)
        if secure:
            L.append('Secure')
        if http_only:
            L.append('HttpOnly')
        self._cookies[name] = '; '.join(L)

    def unset_cookie(self, name):
        '''
        Unset a cookie.

        >>> r = Response()
        >>> r.set_cookie('company', 'Abc, Inc.', max_age=3600)
        >>> r._cookies
        {'company': 'company=Abc%2C%20Inc.; Max-Age=3600; Path=/; HttpOnly'}
        >>> r.unset_cookie('company')
        >>> r._cookies
        {}
        '''
        if hasattr(self, '_cookies'):
            if name in self._cookies:
                del self._cookies[name]

    @property
    def status_code(self):
        '''
        Get response status code as int.

        >>> r = Response()
        >>> r.status_code
        200
        >>> r.status = 404
        >>> r.status_code
        404
        >>> r.status = '500 Internal Error'
        >>> r.status_code
        500
        '''
        return int(self._status[:3])

    @property
    def status(self):
        '''
        Get response status. Default to '200 OK'.

        >>> r = Response()
        >>> r.status
        '200 OK'
        >>> r.status = 404
        >>> r.status
        '404 Not Found'
        >>> r.status = '500 Oh My God'
        >>> r.status
        '500 Oh My God'
        '''
        return self._status

    @status.setter
    def status(self, value):
        '''
        Set response status as int or str.

        >>> r = Response()
        >>> r.status = 404
        >>> r.status
        '404 Not Found'
        >>> r.status = '500 ERR'
        >>> r.status
        '500 ERR'
        >>> r.status = u'403 Denied'
        >>> r.status
        '403 Denied'
        >>> r.status = 99
        Traceback (most recent call last):
          ...
        ValueError: Bad response code: 99
        >>> r.status = 'ok'
        Traceback (most recent call last):
          ...
        ValueError: Bad response code: ok
        >>> r.status = [1, 2, 3]
        Traceback (most recent call last):
          ...
        TypeError: Bad type of response code.
        '''
        if isinstance(value, int):
            if value>=100 and value<=999:
                st = RESPONSE_STATUSES.get(value, '')
                if st:
                    self._status = '%d %s' % (value, st)
                else:
                    self._status = str(value)
            else:
                raise ValueError('Bad response code: %d' % value)
        elif isinstance(value, str):
            value = value.encode('utf-8')
            if RE_RESPONSE_STATUS.match(value):
                self._status = value
            else:
                raise ValueError('Bad response code: %s' % value)
        else:
            raise TypeError('Bad type of response code.')

if __name__=='__main__':
    import doctest
    doctest.testmod()