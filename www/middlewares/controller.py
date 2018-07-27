#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'SLZ'

import os
from digwebs.router import Router

r = Router()
from constants import root_path
for f in os.listdir(root_path + r'/viewmodels'):
    if f.endswith('.py') and f != '__init__.py':
        import_module = f.replace(".py", "")
        m = __import__('viewmodels', globals(), locals(), [import_module])
        s_m = getattr(m, import_module)
        r.add_module(s_m)
def controller():
    def handle_route(ctx, next):
        request_method = ctx.request.request_method
        path_info = ctx.request.path_info
        f, arg = r.route_to(request_method,path_info)
        return f(*arg)

    return (handle_route,3)