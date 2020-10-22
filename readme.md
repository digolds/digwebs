# Digolds web framework

A tiny web framework called **digwebs** which is developed by Python. You can checkout the detail design of **digwebs** in [www.digolds.cn](https://www.digolds.cn/article/00153708688234475cbc5a7d7994e8ebc8b8df6d33a12a1000). The following steps will guide you quickly build a web service using digwebs.

* Install digwebs by `pip`

```bash
pip install digwebs
```

* Create a web service project, for example, my project name is "hello-world"

```bash
digwebs hello-world
```

After succesfully create the project, `cd` to it, you will see the following contents:

```
|____favicon.ico
|____wsgiapp.py
|____test
|____middlewares
|____static
| |____css
| |____images
| |____js
| |____fonts
|____controllers
| |____main_controller.py
|____views
```

* **controllers** is where you put controller script
* **middlewares** is where you put middlewares script
* **static** is where you put front end script such as css file, javascript file, font, image etc
* **test** is where you put the test script for your web app
* **views** is where you put the html file

The content in `wsgiapp.py` is shown below:

```python
#!/usr/bin/env python

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

```

The content in `main_controller.py` is shown below:

```python
#!/usr/bin/env python

__author__ = 'SLZ'

'''
digwebs framework controller.
'''

from digwebs.web import current_app

@current_app.get('/')
def hello_world():
    return """
<html>
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
```

* Run `python wsgiapp.py`, you can see the following output:

```bash                                            
INFO:root:Add module: controllers.main_controller
INFO:root:Add route: Route(static,GET,path=/)
INFO:root:application (/Users/slz/dev/src/digwebs/hello-world) will start at 0.0.0.0:9999..
```
* Open your browser and enter `localhost:9999`, you see the content `"digwebs - A Minimal Web Framework!"`

**Note**: if you want to learn more about `digwebs`, head over [here](https://www.digolds.cn/article/001553757423266a02c9e9f7bc44159829e2db86d0d076d000).

# Contribution

We are looking for contributors. Please check open issues in the above repos if you think you could help, or open a new one if you have an idea you'd like to discuss.

# License

This project is licensed under the MIT open source license.
