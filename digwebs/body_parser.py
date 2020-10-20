#!/usr/bin/env python

__author__ = 'SLZ'

import json

def get_parser(file_type):
    return _parse_map.get(file_type,_default_parser)

_parse_map= {}

def _default_parser(data_in_bytes):
    return data_in_bytes

def _parse_to_json(data_in_bytes,encoding='utf-8'):
    return json.loads(data_in_bytes.decode(encoding))

_parse_map['application/json'] = _parse_to_json