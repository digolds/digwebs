#!/usr/bin/env python

__author__ = 'SLZ'

'''
A WSGI application entry.
'''

import logging
logging.basicConfig(level=logging.INFO)

from config import configs
configs['debug'] = __name__ == '__main__'
from models import db
from digwebs.web import WSGIApplication

# init db:
db.create_engine(**configs.db)

# init digolds app:
from constants import root_path
digolds = WSGIApplication(root_path)
digolds.init_middlewares()

if __name__ == '__main__':
    digolds.run(9000, host='0.0.0.0')
else:
    application = digolds.get_wsgi_application()
