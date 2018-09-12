#!/usr/bin/env python

__author__ = 'SLZ'

def make_signed_cookie(id, email, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [
        id, expires,
        hashlib.md5('{id}-{email}-{expires}-{secret}'.format(
            id=id, email=email, expires=expires,
            secret=configs.session.secret).encode('utf-8')).hexdigest()
    ]
    return '-'.join(L)

if __name__ == '__main__':
    import doctest
    doctest.testmod()