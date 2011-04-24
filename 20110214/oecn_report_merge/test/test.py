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
DB = 'test'
#uid
USERID = 1
#密码
USERPASS = 'admin'
res = ''
report_data_obj = [
{'column': 'A', 'text': u'\\u9879\\u76ee', 'value': 0.0, 'row': '1'},
{'column': 'B', 'text': u'\\u884c\\u6b21', 'value': 0.0, 'row': '1'},
{'column': 'C', 'text': u'\\u52171', 'value': 0.0, 'row': '1'},
{'column': 'D', 'text': u'\\u52172', 'value': 0.0, 'row': '1'},
{'column': 'E', 'text': u'\\u52173', 'value': 0.0, 'row': '1'},
{'column': 'F', 'text': u'\\u62b5\\u6d88\\u5206\\u5f55', 'value': 0.0, 'row': '1'},
{'column': 'G', 'text': u'\\u5408\\u8ba1', 'value': 0.0, 'row': '1'},
{'column': 'A', 'text': u'\\u9500\\u552e\\u6536\\u5165', 'value': 0.0, 'row': '2'},
{'column': 'B', 'text': '', 'value': 1.0, 'row': '2'},
{'column': 'C', 'text': '', 'value': 3000.0, 'row': '2'},
{'column': 'D', 'text': '', 'value': 2000000.0, 'row': '2'},
{'column': 'F', 'text': '', 'value': 100.0, 'row': '2'},
{'column': 'G', 'text': '', 'value': 2002900.0, 'row': '2'},
{'column': 'A', 'text': u'\\u9500\\u552e\\u6210\\u672c', 'value': 0.0, 'row': '3'},
{'column': 'B', 'text': '', 'value': 2.0, 'row': '3'},
{'column': 'C', 'text': '', 'value': 2000.0, 'row': '3'},
{'column': 'D', 'text': '', 'value': 1000.0, 'row': '3'},
{'column': 'E', 'text': '', 'value': 10.0, 'row': '3'},
{'column': 'F', 'text': '', 'value': 10000.0, 'row': '3'},
{'column': 'G', 'text': '', 'value': -7000.0, 'row': '3'},
{'column': 'A', 'text': u'\\u9879\\u76ee1', 'value': 0.0, 'row': '4'},
{'column': 'C', 'text': '', 'value': 2001.0, 'row': '4'},
{'column': 'D', 'text': '', 'value': 1001.0, 'row': '4'},
{'column': 'A', 'text': u'\\u9879\\u76ee2', 'value': 0.0, 'row': '5'},
{'column': 'C', 'text': '', 'value': 2002.0, 'row': '5'},
{'column': 'D', 'text': '', 'value': 1002.0, 'row': '5'},
{'column': 'E', 'text': '', 'value': 20.0, 'row': '5'},
{'column': 'A', 'text': u'\\u9879\\u76ee3', 'value': 0.0, 'row': '6'},
{'column': 'C', 'text': '', 'value': 2003.0, 'row': '6'},
{'column': 'D', 'text': '', 'value': 1003.0, 'row': '6'},
{'column': 'A', 'text': u'\\u9879\\u76ee4', 'value': 0.0, 'row': '7'},
{'column': 'C', 'text': '', 'value': 2004.0, 'row': '7'},
{'column': 'D', 'text': '', 'value': 1004.0, 'row': '7'},
{'column': 'E', 'text': '', 'value': 30.0, 'row': '7'},
{'column': 'A', 'text': u'\\u9879\\u76ee5', 'value': 0.0, 'row': '8'},
{'column': 'C', 'text': '', 'value': 2005.0, 'row': '8'},
{'column': 'D', 'text': '', 'value': 1005.0, 'row': '8'},
{'column': 'E', 'text': '', 'value': 40.0, 'row': '8'},
{'column': 'A', 'text': u'\\u9879\\u76ee6', 'value': 0.0, 'row': '9'},
{'column': 'C', 'text': '', 'value': 2006.0, 'row': '9'},
{'column': 'D', 'text': '', 'value': 1006.0, 'row': '9'},
{'column': 'A', 'text': u'\\u9879\\u76ee7', 'value': 0.0, 'row': '10'},
{'column': 'C', 'text': '', 'value': 2007.0, 'row': '10'},
{'column': 'D', 'text': '', 'value': 1007.0, 'row': '10'},
{'column': 'E', 'text': '', 'value': 50.0, 'row': '10'},
{'column': 'A', 'text': u'\\u9879\\u76ee8', 'value': 0.0, 'row': '11'},
{'column': 'C', 'text': '', 'value': 2008.0, 'row': '11'},
{'column': 'D', 'text': '', 'value': 1008.0, 'row': '11'},
{'column': 'A', 'text': u'\\u9879\\u76ee9', 'value': 0.0, 'row': '12'},
{'column': 'C', 'text': '', 'value': 2009.0, 'row': '12'},
{'column': 'D', 'text': '', 'value': 1009.0, 'row': '12'},
{'column': 'E', 'text': '', 'value': 60.0, 'row': '12'},
{'column': 'A', 'text': u'\\u9879\\u76ee10', 'value': 0.0, 'row': '13'},
{'column': 'C', 'text': '', 'value': 2010.0, 'row': '13'},
{'column': 'D', 'text': '', 'value': 1010.0, 'row': '13'},
{'column': 'E', 'text': '', 'value': 70.0, 'row': '13'},
{'column': 'A', 'text': u'\\u9879\\u76ee11', 'value': 0.0, 'row': '14'},
{'column': 'C', 'text': '', 'value': 2011.0, 'row': '14'},
{'column': 'D', 'text': '', 'value': 1011.0, 'row': '14'},
{'column': 'A', 'text': u'\\u9879\\u76ee12', 'value': 0.0, 'row': '15'},
{'column': 'C', 'text': '', 'value': 2012.0, 'row': '15'},
{'column': 'D', 'text': '', 'value': 1012.0, 'row': '15'},
{'column': 'A', 'text': u'\\u9879\\u76ee13', 'value': 0.0, 'row': '16'},
{'column': 'C', 'text': '', 'value': 2013.0, 'row': '16'},
{'column': 'D', 'text': '', 'value': 1013.0, 'row': '16'},
{'column': 'A', 'text': u'\\u9879\\u76ee14', 'value': 0.0, 'row': '17'},
{'column': 'C', 'text': '', 'value': 2014.0, 'row': '17'},
{'column': 'D', 'text': '', 'value': 1014.0, 'row': '17'},
{'column': 'A', 'text': u'\\u9879\\u76ee15', 'value': 0.0, 'row': '18'},
{'column': 'C', 'text': '', 'value': 2015.0, 'row': '18'},
{'column': 'D', 'text': '', 'value': 1015.0, 'row': '18'},
{'column': 'A', 'text': u'\\u9879\\u76ee16', 'value': 0.0, 'row': '19'},
{'column': 'C', 'text': '', 'value': 2016.0, 'row': '19'},
{'column': 'D', 'text': '', 'value': 1016.0, 'row': '19'},
{'column': 'A', 'text': u'\\u9879\\u76ee17', 'value': 0.0, 'row': '20'},
{'column': 'C', 'text': '', 'value': 2017.0, 'row': '20'},
{'column': 'D', 'text': '', 'value': 1017.0, 'row': '20'},
{'column': 'A', 'text': u'\\u9879\\u76ee18', 'value': 0.0, 'row': '21'},
{'column': 'C', 'text': '', 'value': 2018.0, 'row': '21'},
{'column': 'D', 'text': '', 'value': 1018.0, 'row': '21'},
{'column': 'A', 'text': u'\\u9879\\u76ee19', 'value': 0.0, 'row': '22'},
{'column': 'C', 'text': '', 'value': 2019.0, 'row': '22'},
{'column': 'D', 'text': '', 'value': 1019.0, 'row': '22'},
{'column': 'A', 'text': u'\\u9879\\u76ee20', 'value': 0.0, 'row': '23'},
{'column': 'C', 'text': '', 'value': 2020.0, 'row': '23'},
{'column': 'D', 'text': '', 'value': 1020.0, 'row': '23'},
{'column': 'A', 'text': u'\\u9879\\u76ee21', 'value': 0.0, 'row': '24'},
{'column': 'C', 'text': '', 'value': 2021.0, 'row': '24'},
{'column': 'D', 'text': '', 'value': 1021.0, 'row': '24'}
]
sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % ('localhost',8069))
res1 = sock.execute(DB, USERID, USERPASS, 'report.data','set_report_data','子公司','利润表','2011','1',report_data_obj)
res2 = sock.execute(DB, USERID, USERPASS, 'report.data', 'get_report_data','子公司','利润表','2011','1')
print res1
print res2

