#!/usr/bin/env python

__author__ = 'SLZ'

from web import digwebs_app

@digwebs_app.get('/')
def hello_world():
    return 'hello world'