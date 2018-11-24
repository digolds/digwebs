#!/usr/bin/env python

__author__ = 'SLZ'

'''
digwebs framework demo.
'''

import logging
logging.basicConfig(level=logging.INFO)

from web import get_app

digwebs_app = get_app('')

if __name__ == '__main__':
    digwebs_app.run(9999, host='0.0.0.0')
else:
    wsgi_app = digwebs_app.get_wsgi_application()
