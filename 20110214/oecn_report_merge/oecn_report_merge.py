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

from osv import fields, osv
from osv import osv
import netsvc

#----------------------------------------------------------
#    组织结构
#----------------------------------------------------------

class report_company(osv.osv):
    _description = "组织结构"
    _name = "report.company"
    _columns = {
        'code': fields.char('编号', size=64, required=True),
        'name': fields.char('名字', size=128, required=True),
        'parent_id': fields.many2one('report.company', '上级', ondelete='cascade'),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
    }
report_company()

#----------------------------------------------------------
#    年
#----------------------------------------------------------

class report_fiscalyear(osv.osv):
    _name = "report.fiscalyear"
    _description = "年"
    _columns = {
        'name': fields.char('Fiscal Year', size=64, required=True),
        'code': fields.char('Code', size=6, required=True),
    }
report_fiscalyear()


#----------------------------------------------------------
#    报表类型
#----------------------------------------------------------

class report_type(osv.osv):
    _description = "报表类型"
    _name = "report.type"
    _columns = {
        'code': fields.char('编号', size=64, required=True),
        'name': fields.char('名字', size=128, required=True),
    }
report_type()

#----------------------------------------------------------
#    报表格式
#----------------------------------------------------------
    
class report_format(osv.osv):
    _description = "报表行"
    _name = "report.format"
    _columns = {
        'name': fields.char('名称', size=128, required=True),
        'report_type':fields.many2one('report.type','报表类型'),
        'row':fields.integer('行号'),
        'column':fields.integer('列号'),
        'text':fields.char('文本',size=128),
        'value':fields.float('数值'),
    }
report_format()



#----------------------------------------------------------
#    报表数据
#----------------------------------------------------------

class report_data(osv.osv):
    _description = "报表数据"
    _name = "report.data"
    _columns = {
        'report_company':fields.many2one('report.company','组织结构',required=True),
        'report_type':fields.many2one('report.type','报表类型',required=True),
        'year':fields.many2one('report.fiscalyear','年',required=True),
        'month':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')],'月份',required=True),
        'row':fields.integer('行号'),
        'column':fields.integer('列号'),
        'text':fields.char('文本',size=128),
        'value':fields.float('数值'),
    }
    
    def get_report_data(self, cr, uid, comapny, report_type, year,month):
        """
        传入company,report_type,year,month 传出id,row,column,text,value五列的list
        """
        report_data_ids = self.pool.get('report.data').search(cr, uid , [('report_company','=',comapny), ('report_type','=',report_type),('year','=',year),('month','=',month)])
        report_deta_objs = self.pool.get('report.data').read(cr, uid ,report_data_ids,['report_data_id','row','column','text','value'])
        return report_deta_objs
    
    def set_report_data(self, cr, uid,company,report_type,year,month,row,column,text,value):
        """
        传入company,report_type,year,month，row,column,text,value九列的list，传出成功或失败的信息
        """
        res = False
        id  = self.pool.get('report.data').create(cr, uid, {'report_company': company,'report_type':report_type,'year':year,'month':month,'row':row,'column':column,'text':text,'value':value})
        if id:
            res = True
        return res
report_data()