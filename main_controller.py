#!/usr/bin/env python

__author__ = 'SLZ'

from www.web import digwebs_app

@digwebs_app.get('/')
def hello_world():
    return """<html>
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
    </body></html>"""