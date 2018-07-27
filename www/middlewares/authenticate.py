#!/usr/bin/env python

__author__ = 'SLZ'

def authenticate():
    def user_interceptor(ctx, next):
        #you can write logic to handle http request at this place
        return next()
    return (user_interceptor, 0)