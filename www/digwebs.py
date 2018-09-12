#!/usr/bin/env python

__author__ = 'SLZ'

'''
digwebs framework entry.
'''

import logging
logging.basicConfig(level=logging.INFO)

from web import digwebs

digwebs_app = digwebs()

@digwebs_app.view('d.html')
@digwebs_app.get('/')
def hello_world():
    pass

if __name__ == '__main__':
    digwebs_app.run(9999, host='0.0.0.0')
else:
    application = digwebs_app.get_wsgi_application()
