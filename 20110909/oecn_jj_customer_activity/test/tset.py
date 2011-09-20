# -*- encoding:utf-8 -*-
import xmlrpclib

USERNAME = 'admin'
PWD = 'admin'
DBNAME = 'jj1'
URL = 'http://localhost'

sock_common = xmlrpclib.ServerProxy(URL+':8069/xmlrpc/common')
uid = sock_common.login(DBNAME, USERNAME, PWD)
sock = xmlrpclib.ServerProxy(URL+':8069/xmlrpc/object')
sock.execute(DBNAME, uid, PWD, 'customer.activity', 'download_data',10000)
