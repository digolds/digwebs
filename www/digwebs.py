#!/usr/bin/env python

__author__ = 'SLZ'

'''
digwebs framework entry.
'''

import logging
logging.basicConfig(level=logging.INFO)

from .web import WSGIApplication

digolds = WSGIApplication(root_path)
digolds.init_middlewares()

if __name__ == '__main__':
    digolds.run(9000, host='0.0.0.0')
else:
    application = digolds.get_wsgi_application()
