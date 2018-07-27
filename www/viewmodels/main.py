#!/usr/bin/env python

__author__ = 'SLZ'

import os, re, time, hashlib, json

import requests
import random

from digwebs.web import get, post, view, view1, ctx
from digwebs.errors import  seeother

from models.gold import Gold
from config import configs
from apis import api, APIError, APIValueError
from constants import UserRole, GoldType, InteractionType

@view('golds.html')
@get('/')
def index():
    return dict()