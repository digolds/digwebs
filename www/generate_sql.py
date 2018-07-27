#!/usr/bin/env python

__author__ = 'SLZ'

import os
current_path = os.path.dirname(os.path.abspath(__file__))+'/models'
from models import model
import importlib
import mysql.connector
from .config import configs
def generate_sql():
    cnx = mysql.connector.Connect(host=configs.host,user=configs.user,password=configs.password)
    cursor = cnx.cursor()
    cursor.execute("drop database if exists %s;" % configs.database)
    cursor.execute("create database %s;" % configs.database)
    cursor.execute("use %s;" % configs.database)
    cursor.execute("""grant select, insert, update, delete on %s.* to '%s'@'%s' identified by '%s';""" % (configs.database,configs.database.user,configs.host,configs.database.password))
    
    for pyf in os.listdir(current_path):
        if pyf.endswith('.py') and pyf != '__init__.py':
            module_name = pyf.replace(".py", "")
            m = __import__('models.'+module_name, globals(), locals(), ["Model"])
            for name in dir(m):
                attr = getattr(m, name)
                if hasattr(attr, '__table__'):
                    sql_start = 'create table %s (' % getattr(attr, '__table__')
                    am = attr.__dict__['__mappings__']
                    sql_middle = ''
                    sql_primary_key = ',PRIMARY KEY (%s)'
                    for k,v in am.items():
                        fv = {}
                        fv['field_name'] = v.name
                        fv['type'] = model.get_sql_type(v)
                        tmp = """{field_name} {type}"""
                        tmp = tmp.format(**fv)
                        if not v.nullable:
                             tmp = tmp + ' NOT NULL'
                        if v.primary_key:
                            sql_primary_key = sql_primary_key % v.name
                        sql_middle = sql_middle + tmp + ','
                    sql_end = """) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
                    sql_for_create_table = sql_start+sql_middle[:-1]+sql_primary_key+sql_end
                    cursor.execute(sql_for_create_table)
    
    cnx.commit() # when insert data to sql, you should call commit or nothing will insert to db
    cursor.close()  # you can omit in most cases as the destructor will call it

if __name__ == '__main__':
    generate_sql()