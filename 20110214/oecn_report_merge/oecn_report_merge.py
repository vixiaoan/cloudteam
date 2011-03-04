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
#    报表类型
#----------------------------------------------------------

class report_type(osv.osv):
    _description = "报表类型"
    _name = "report.type"
    _columns = {
        'code': fields.char('编号', size=64, required=True),
        'name': fields.char('名字', size=128, required=True),
        'report_format': fields.one2many('report.format','report_type','报表格式')
    }
report_type()

#----------------------------------------------------------
#    报表格式
#----------------------------------------------------------
    
class report_format(osv.osv):
    _description = "报表格式"
    _name = "report.format"
    _columns = {
        'report_type':fields.many2one('report.type','报表类型'),
        'row':fields.char('行号',size=25,required=True),
        'column':fields.char('列号',size=25,required=True),
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
        'year':fields.char('年',size=10,required=True),
        'month':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')],'月份',required=True),
        'row':fields.char('行号',size=25,required=True),
        'column':fields.char('列号',size=25,required=True),
        'text':fields.char('文本',size=128),
        'value':fields.float('数值'),
    }
    
    def check_input(self, cr, uid, comapny, report_type, year, month):
        """
        验证输入数据是否合法,合法则返回相应ID
        """
        msg=''
        company_id = self.pool.get('report.company').search(cr, uid ,[('name','=',comapny)])
        if not company_id:
            msg = 'company'
        report_type_id = self.pool.get('report.type').search(cr, uid ,[('name','=',report_type)])
        if not report_type_id:
            msg = msg + ' report_type'
        try:
            int(year)
        except ValueError:
            msg = msg + ' year'
        try:
            int(month)
            if not 0 < int(month) < 13:
                msg = msg + ' month'
        except ValueError:
            msg = msg + ' month'
        if len(msg):
            msg = msg + ' error!'
        return {
            'company_id':company_id,
            'report_type_id':report_type_id,
            'year':year,
            'month':month,
            'msg':msg,
            }
    
    def get_report_data(self, cr, uid, company, report_type, year, month):
        """
        传入 company,report_type,year,month 传出row,column,text,value四列的list
        """
        #验证输入数据是否合法
        result = {}
        result = self.check_input( cr, uid, company, report_type, year, month)
        if len(result['msg']):
            return result['msg']
        report_data_ids = self.pool.get('report.data').search(cr, uid , [('report_company','=',result['company_id']), ('report_type','=',result['report_type_id']),('year','=',result['year']),('month','=',result['month'])])
        report_deta_objs = self.pool.get('report.data').read(cr, uid ,report_data_ids,['row','column','text','value'])
        #不输出ID
        for report_deta_obj in report_deta_objs:
            del report_deta_obj['id']
        return report_deta_objs
    
    def set_report_data(self, cr, uid,company,report_type,year,month,report_deta_objs):
        """
        传入company,report_type,year,month，还有report_deta_objs是包含row,column,text,value四列的list，传出成功或失败的信息
        """
        res = False
        #验证输入数据是否合法
        result = {}
        result = self.check_input(cr, uid, company, report_type, year, month)
        if len(result['msg']):
            return result['msg']
        for i in range(0,len(report_deta_objs)):
            id  = self.pool.get('report.data').create(cr, uid, {'report_company': result['company_id'][0],'report_type':result['report_type_id'][0],'year':result['year'],'month':result['month'],'row':report_deta_objs[i]['row'],'column':report_deta_objs[i]['column'],'text':report_deta_objs[i]['text'],'value':report_deta_objs[i]['value']})
        if id:
            res = True
        return res
report_data()