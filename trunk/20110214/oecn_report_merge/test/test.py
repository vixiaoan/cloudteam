# -*- encoding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
#    Created on 2011-02-14
#    author:Joshua  
##############################################################################
import xmlrpclib
#数据库
DB = 'orm'
#uid
USERID = 1
#密码
USERPASS = 'admin'
cteate_obj={
'company': 1,'report_type':1,'year':1,'month':1,'row':2,'column':2,'text':'22222','value':'1212121212'
}
sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % ('localhost',8069))

res = sock.execute(DB, USERID, USERPASS, 'report.data','set_report_data',1,1,1,'1','2','2','2222','12121')
res = sock.execute(DB, USERID, USERPASS, 'report.data', 'get_report_data',1,1,1,1)

print res