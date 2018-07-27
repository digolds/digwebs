#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'SLZ'

from .model import Model, StringField, IntegerField, FloatField

class Gold(Model):
    __table__ = 'golds'

    user_id = StringField(updatable=False, ddl='varchar(50)')
    gold_type = IntegerField()
    price = FloatField()
    original_price = FloatField()
    image_url = StringField(ddl='varchar(1000)')
    detail_url = StringField(ddl='varchar(1000)')
    content_id = StringField(ddl='varchar(50)')
    title = StringField(ddl='varchar(1000)')
    number_of_order = IntegerField()
    number_of_vote = IntegerField()