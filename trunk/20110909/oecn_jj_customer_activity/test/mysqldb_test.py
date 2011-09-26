#!/usr/bin/env python
# -*- coding:utf-8 -*-
import MySQLdb

#----mysql 配置信息----
#mysql 服务器地址
HOST = 'localhost'
#数据库名字
DB = 'jjdb'
#数据库用户名
USER = 'root'
#数据库密码
PASSWD = '1'

db=MySQLdb.connect(host=HOST,db=DB,user=USER,passwd=PASSWD)
c=db.cursor()
c.execute("show tables;")
res = c.fetchall()
print res

