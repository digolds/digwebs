#!/usr/bin/env python

__author__ = 'SLZ'

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(dir_path, '..'))

def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def make_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)

contorller_dir = os.path.join(parent_dir,'controllers')
make_dir(contorller_dir)
make_dir(os.path.join(parent_dir,'middlewares'))
make_dir(os.path.join(parent_dir,'views'))
make_dir(os.path.join(parent_dir,'test'))

make_dir(os.path.join(parent_dir,'static'))
static_dir = os.path.join(parent_dir,'static')
make_dir(os.path.join(static_dir,'css'))
make_dir(os.path.join(static_dir,'js'))
make_dir(os.path.join(static_dir,'images'))
make_dir(os.path.join(static_dir,'fonts'))

boost_content = \
"""#!/usr/bin/env python

__author__ = 'SLZ'

'''
digwebs framework demo.
'''

import logging
logging.basicConfig(level=logging.INFO)

from digwebs.web import get_app
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
digwebs_app = get_app({'root_path':dir_path})
digwebs_app.init_all()
if __name__ == '__main__':
    digwebs_app.run(9999, host='0.0.0.0')
else:
    wsgi_app = digwebs_app.get_wsgi_application()
"""

make_file(os.path.join(parent_dir,'digwebs.py'),boost_content)

html_content = \
"""<html>
    <style>
    html,body{
  height:100%;
  padding:0;
  margin:0;
}
*{
  box-sizing:border-box;
}

.container{
  
  width:100%;
  height:100%;
  
  display:flex;
  justify-content:center;
  align-items:center;
  
}
    </style>
    <body>
    <div class="container">
  <h1>digwebs - A Minimal Web Framework!</h1>
</div>
    </body></html>
"""

main_controller_content = \
"""#!/usr/bin/env python

__author__ = 'SLZ'

'''
digwebs framework controller.
'''

from digwebs.web import current_app

@current_app.get('/')
def hello_world():
    return %s
""" % '"""'+ html_content + '"""'
make_file(os.path.join(contorller_dir,'main_controller.py'),main_controller_content)

import shutil
shutil.copyfile(os.path.join(dir_path,'favicon.ico'), os.path.join(parent_dir,'favicon.ico'))