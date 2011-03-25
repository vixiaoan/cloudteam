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
        'is_template':fields.boolean('模板'),
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
        'merge_column': fields.char('合并列', size=128, required=True)
    }
report_type()

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
    _rec_name = 'report_company'
    
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
        res = {
            #result是否成功插入数据 delete_num 删除重复数据的数量 create_num:创建重复数据的数量
            'result':True,
            'delete_num':0,
            'create_num':0,
        }
        #验证输入数据是否合法
        result = {}
        result = self.check_input(cr, uid, company, report_type, year, month)
        company_obj = self.pool.get('report.company').read(cr, uid ,result['company_id'],['is_template'])
        if len(result['msg']):
            return result['msg']
        for i in range(0,len(report_deta_objs)):
        #循环输入全部的report_data_objs
            report_data_ids = self.pool.get('report.data').search(cr, uid , [('report_company','=',result['company_id']), ('report_type','=',result['report_type_id']),('year','=',result['year']),('month','=',result['month'])])
            if report_data_ids:
            #先删除已有的相同key（company\report_type\year\month）的report_data
                self.pool.get('report.data').unlink(cr, uid, report_data_ids)
                res['delete_num'] = res['delete_num']+1
            if company_obj[0]['is_template']:
            #如果company是模版公司，年和月设置为0000年1月
                id  = self.pool.get('report.data').create(cr, uid, {'report_company': result['company_id'][0],'report_type':result['report_type_id'][0],'year':'0000','month':'1','row':report_deta_objs[i]['row'],'column':report_deta_objs[i]['column'],'text':report_deta_objs[i]['text'],'value':report_deta_objs[i]['value']})
                res['create_num'] = res['create_num']+1
            else:
                id  = self.pool.get('report.data').create(cr, uid, {'report_company': result['company_id'][0],'report_type':result['report_type_id'][0],'year':result['year'],'month':result['month'],'row':report_deta_objs[i]['row'],'column':report_deta_objs[i]['column'],'text':report_deta_objs[i]['text'],'value':report_deta_objs[i]['value']})
                res['create_num'] = res['create_num']+1
        if id:
            res['result'] = True
        return res
        

report_data()

#----------------------------------------------------------
#    报表数据表格
#----------------------------------------------------------

class report_data_grid(osv.osv):
    _name = 'report.data.grid'
    _description = 'Report Data Grid'
    _inherit='report.data'
    _table = 'report_data'
    
    def create(self, cr, uid, vals, cotext=None):
        raise osv.except_osv('Error !','You cannot add an entry to this view!')
    
    def unlink(self, *args, **argv):
        raise osv.except_osv('Error !', 'You cannot delete an entry of this view !')
    
    def write(self, cr, uid, ids, vals, context=None):
        raise osv.except_osv('Error !', 'You cannot write an entry of this view !')
    
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        logger = netsvc.Logger()
        cr.execute("SELECT DISTINCT  cast(row as int) FROM report_data WHERE report_company='%s' and report_type='%s' and year = '%s' and month = '%s'  order by cast(row as int) "%(context['report_company'], context['report_type'],context['year'],context['month']))
        rows = cr.dictfetchall()
        cr.execute('''SELECT DISTINCT  "column" FROM report_data WHERE report_company='%s' and report_type='%s' and year = '%s' and month = '%s'  order by "column" '''%(context['report_company'], context['report_type'],context['year'],context['month']))
        columns = cr.dictfetchall()
        if not isinstance(rows,list):
            rows=[rows]
        for row in rows:
            for column in columns:
                text_value_id = self.pool.get('report.data').search(cr, uid, [('report_company', '=', context['report_company']),('report_type', '=',  context['report_type']),('year', '=', context['year']),('month', '=', context['month']),('column', '=', column['column']),('row', '=', row['row'])])
                text_value = self.pool.get('report.data').read(cr, uid,text_value_id,['text','value','id'])
                if text_value:
                 #如果text或者value存在即赋值
                    if text_value[0]['value']:
                        row['column_'+str(column['column'])] =  text_value[0]['value']
                    elif text_value[0]['text']:
                        row['column_'+str(column['column'])] =  text_value[0]['text']
                    else:
                        row['column_'+str(column['column'])] = ''
                    row['id'] = text_value[0]['id']
            row['line_num'] = str(row['row'])
        return rows
        
    def fields_get(self, cr, uid, fields=None, context=None, read_access=True):
        result = super(report_data_grid, self).fields_get(cr, uid, fields, context)
        if context.get('report_company',False):
            cr.execute('''SELECT DISTINCT  "column" FROM report_data WHERE report_company='%s' and report_type='%s' and year = '%s' and month = '%s'  order by "column" '''%(context['report_company'], context['report_type'],context['year'],context['month']))
            columns = cr.dictfetchall()
            result['line_num'] = {'string': '行号/列号','type': 'char','size': 7}
            for column in columns:
                result['column_'+str(column['column'])] = {'string': '%s'%column['column'],'type': 'char','size': 7}
        return result
        
    def fields_view_get(self, cr, uid, view_id=None,view_type='form',context={},toolbar=False):
        logger = netsvc.Logger()
        logger.notifyChannel('addon:'+self._name,netsvc.LOG_INFO,'context_get:%s'%(context))
        result = super(report_data_grid, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar)
        if context.get('report_company',False):
            cr.execute('''SELECT DISTINCT  "column" FROM report_data WHERE report_company='%s' and report_type='%s' and year = '%s' and month = '%s'  order by "column" '''%(context['report_company'], context['report_type'],context['year'],context['month']))
            columns = cr.dictfetchall()
            if not columns:
                raise osv.except_osv('Error !','No data!')
            xml = '''<?xml version="1.0"?>
            <%s>
            <field name="line_num"/>
        ''' % (view_type,)
            for column in columns:
                #logger.notifyChannel('addon:'+self._name,netsvc.LOG_INFO,'_columns:%s'%(columns))
                xml +='''<field name="column_%s"/>'''%(str(column['column']))
            xml += '''</%s>'''% (view_type,)
            result['arch'] = xml
            result['fields'] = self.fields_get(cr, uid,'line',context = context)
        logger.notifyChannel('addon:'+self._name,netsvc.LOG_INFO,'report_data_grid_result:%s'%(result))
        return result
report_data_grid()

#----------------------------------------------------------
#    合并项目
#----------------------------------------------------------
class merge_entry(osv.osv):
    _description = '合并项目'
    _name = 'merge.entry'
    _columns = {
        'name': fields.char('名字', size=128, required=True),
        'active': fields.boolean('Active'),
        'report_type':fields.many2one('report.type','报表类型',required=True),
        'row':fields.char('行号',size=25,required=True),
    }
    
    _defaults = {
        'active':lambda *a:1,
     }
merge_entry()

#----------------------------------------------------------
#    抵消分录
#----------------------------------------------------------
class report_offsetting_entry(osv.osv):
    _description = "抵消分录"
    _name = "report.offsetting_entry"
    _columns = {
        'code': fields.char('编号', size=64, required=True),
        'year':fields.char('年',size=10,required=True),
        'month':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')],'月份',required=True),
        'report_company':fields.many2one('report.company','公司',required=True),
        'line_ids':fields.one2many('report.offsetting_entry.line','offsetting_entry_line','报表格式'),
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'create_date': fields.date('Creation date', readonly=True),
    }
report_offsetting_entry()

#----------------------------------------------------------
#    抵消分录行
#----------------------------------------------------------
class report_offsetting_entry_line(osv.osv):
    _description = "抵消分录行"
    _name = "report.offsetting_entry.line"
    _columns = {
        'offsetting_entry_line':fields.many2one('report.offsetting_entry','分录',),
        'merge_entry':fields.many2one('merge.entry','合并项目',required=True),
        'report_company':fields.many2one('report.company','对方公司',required=True),
        'amount':fields.float('金额',required=True),
    }
report_offsetting_entry_line()

#----------------------------------------------------------
#    合并报表底稿
#----------------------------------------------------------
class merge_report(osv.osv):
    _name = 'merge.report'
    _description = 'Merge Report'
    _inherit='report.data'
    _table = 'report_data'
    
    def create(self, cr, uid, vals, cotext=None):
        raise osv.except_osv('Error !','You cannot add an entry to this view!')
    
    def unlink(self, *args, **argv):
        raise osv.except_osv('Error !', 'You cannot delete an entry of this view !')
    
    def write(self, cr, uid, ids, vals, context=None):
        raise osv.except_osv('Error !', 'You cannot write an entry of this view !')
    
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        column_name = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        if context.get('report_company',False) and context.get('report_type',False):
            #找出相关的公司
            report_company_objs = self.pool.get('report.company').browse(cr, uid,context['report_company'], context = context)
            #找出相关报表类型
            report_type_obj = self.pool.get('report.type').browse(cr, uid,context['report_type'], context = context)
            #找出合并行
            merge_entry_ids = self.pool.get('merge.entry').search(cr, uid,[('report_type','=',context['report_type'])])
            merge_entry_objs = self.pool.get('merge.entry').browse(cr, uid,merge_entry_ids)
            i = 0
            result = []
            #首行
            row={
                 'id':i+1,
                 'line_num':i+1,
                 'merge_entry_name':'项目',
                 'merge_entry_line_num':'行次',
                 'merge_column':'合计',
                 'offsetting_entry':'抵消分录',
                 }
            #生成新的报表对象
            create_report_data_obj = {
                'report_company':context['parent_company'],
                'report_type':context['report_type'],
                'year':context['year'],
                'month':context['month'],
                'row':'1',
                }
            create_report_data_obj['text'] = '项目'
            create_report_data_obj['column'] = 'A'
            self.pool.get('report.data').create(cr, uid,create_report_data_obj)
            create_report_data_obj['text'] = '行号'
            create_report_data_obj['column'] = 'B'
            self.pool.get('report.data').create(cr, uid,create_report_data_obj)      
            j = 2
            for report_company_obj in report_company_objs:        
                row['company_'+str(report_company_obj.id)] = report_company_obj.name
                create_report_data_obj['column'] = column_name[j]
                create_report_data_obj['text'] = report_company_obj.name
                self.pool.get('report.data').create(cr, uid,create_report_data_obj)
            result.append(row)
            i = i+1
            #第二行
            for merge_entry_obj in merge_entry_objs: 
                row={
                     #合并项，抵消分录清零
                     'merge_column':0,
                     'offsetting_entry':0,
                     }
                create_report_data_obj['row'] = i+1
                j = 2
                for report_company_obj in report_company_objs:
                    create_report_data_obj['column'] = column_name[j]
                    j=j+1
                    #找出相应列数值或者字符
                    text_value_id = self.pool.get('report.data').search(cr, uid, [('report_company', '=', report_company_obj.id),('report_type', '=',  context['report_type']),('year', '=', context['year']),('month', '=', context['month']),('column', '=', report_type_obj.merge_column),('row', '=', merge_entry_obj.row)])
                    text_value = self.pool.get('report.data').read(cr, uid,text_value_id,['text','value','id'])
                    if text_value:
                    #如果text或者value存在即赋值
                        if text_value[0]['value']:
                            row['company_'+str(report_company_obj.id)] =  text_value[0]['value']
                            row['merge_column'] = row['merge_column'] + text_value[0]['value']
                            #保存
                            del create_report_data_obj['text']
                            create_report_data_obj['value'] = text_value[0]['value']
                            self.pool.get('report.data').create(cr, uid,create_report_data_obj)
                        elif text_value[0]['text']:
                            row['company_'+str(report_company_obj.id)] =  text_value[0]['text']
                            #保存
                            del create_report_data_obj['value']
                            create_report_data_obj['text'] = text_value[0]['text']                     
                    else:
                        row['company_'+str(report_company_obj.id)] = ''
                        #保存
                        del create_report_data_obj['value']
                        del create_report_data_obj['text']
                        create_report_data_obj['text'] = text_value[0]['text']
                        self.pool.get('report.data').create(cr, uid,create_report_data_obj)
                #通过公司、年、月 找出抵消分录
                offsetting_entry_ids = self.pool.get('report.offsetting_entry').search(cr, uid, [('report_company', 'in', context['report_company']),('year', '=', context['year']),('month', '=', context['month'])]) 
                #通过抵消分录、公司、合并项目  找出抵消分录行
                offsetting_entry_line_ids = self.pool.get('report.offsetting_entry.line').search(cr, uid,[('offsetting_entry_line','in',offsetting_entry_ids),('report_company', 'in', context['report_company']),('merge_entry','=',merge_entry_obj.id)])
                if offsetting_entry_line_ids:
                    offsetting_entry_line_amounts = self.pool.get('report.offsetting_entry.line').read(cr, uid , offsetting_entry_line_ids, ['amount'])
                    for offsetting_entry_line_amount in offsetting_entry_line_amounts:
                        #求出抵消分录的总数
                        row['offsetting_entry'] = row['offsetting_entry']+offsetting_entry_line_amount['amount']
                row['merge_column'] = row['merge_column']-row['offsetting_entry']
                row['id'] = i+1
                row['line_num'] = i+1
                #项目名称
                merge_entry_name_id = self.pool.get('report.data').search(cr, uid,[('report_company', '=', report_company_objs[0].id),('report_type', '=',  context['report_type']),('year', '=', context['year']),('month', '=', context['month']),('row','=',merge_entry_obj.row),('column','=','A')])
                merge_entry_name = self.pool.get('report.data').read(cr, uid, merge_entry_name_id,['text'])
                row['merge_entry_name'] = merge_entry_name[0]['text']
                #保存
                create_report_data_obj['text'] = merge_entry_name[0]['text']
                create_report_data_obj['column']='A'
                del create_report_data_obj['value']
                self.pool.get('report.data').create(cr, uid,create_report_data_obj)
                #行次
                merge_entry_line_num_id = self.pool.get('report.data').search(cr, uid,[('report_company', '=', report_company_objs[0].id),('report_type', '=',  context['report_type']),('year', '=', context['year']),('month', '=', context['month']),('row','=',merge_entry_obj.row),('column','=','B')])
                merge_entry_line_num = self.pool.get('report.data').read(cr, uid, merge_entry_line_num_id,['text'])
                row['merge_entry_line_num'] =merge_entry_line_num[0]['text']
                #保存
                create_report_data_obj['column']='B'
                del create_report_data_obj['value']
                self.pool.get('report.data').create(cr, uid,create_report_data_obj)
                i = i+1
                result.append(row)
        #删除旧的报表
        old_report_ids = self.pool.get('report.data').search(cr, uid,[('report_company', '=', context['parent_company']),('report_type', '=',  context['report_type']),('year', '=', context['year']),('month', '=', context['month'])])
        self.pool.get('report.data').unlink(cr, uid,old_report_ids)
        #生成新的报表
        create_report_data_obj = {
                'report_company':context['parent_company'],
                'report_type':context['report_type'],
                'year':context['year'],
                'month':context['month'],
                'row':res['line_num'],
                }
        #生成首行
        for report_company_obj in report_company_objs:
            create_report_data_obj['text'] = report_company_obj.name
            self.pool.get('report.data').create(cr, uid,create_report_data_obj)
        for res in result:
            create_report_data_obj['text']
            self.pool.get('report.data').create(cr, uid,create_report_data_obj)
            res
        return result
        
    def fields_get(self, cr, uid, fields=None, context=None, read_access=True):
       result = super(merge_report, self).fields_get(cr, uid, fields, context)
       column_name = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
       i = 0
       if context.get('report_company',False) and context.get('report_type',False):
           #找出相关的公司
           report_company_objs = self.pool.get('report.company').browse(cr, uid,context['report_company'], context = context)
           #找出相关报表类型
           report_type_obj = self.pool.get('report.type').browse(cr, uid,context['report_type'], context = context)
           result['line_num'] = {'string': '行号/列号','type': 'char','size': 7}
           result['merge_entry_name'] = {'string':column_name[i],'type': 'char','size': 7}
           result['merge_entry_line_num'] = {'string':column_name[i+1],'type': 'char','size': 7}
           for report_company_obj in report_company_objs:
               #如果超过26列可能会出现问题
               result['company_'+ str(report_company_obj.id)] = {'string': '%s'%column_name[i+2],'type': 'char','size': 7}
               i=i+1
           result['offsetting_entry'] = {'string':column_name[i+3],'type': 'char','size': 7}
           result['merge_column'] = {'string':column_name[i+4],'type': 'char','size': 7}
       return result
   
    def fields_view_get(self, cr, uid, view_id=None,view_type='form',context={},toolbar=False):
        '''
        根据 公司，年，月，报表类型，生成合并报表底稿
        '''
        logger = netsvc.Logger()
        result = super(merge_report, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar)
        if context.get('report_company',False) and context.get('report_type',False):
           #找出相关的公司
           report_company_objs = self.pool.get('report.company').browse(cr, uid,context['report_company'], context = context)
           #找出相关报表类型
           #report_type_obj = self.pool.get('report.type').browse(cr, uid,context['report_type'], context = context)
           xml = '''<?xml version="1.0"?>
           <%s>
           <field name="line_num"/>
           '''%(view_type)
           #项目名称
           xml +='''<field name="merge_entry_name"/>'''
           #行次
           xml +='''<field name="merge_entry_line_num"/>'''
           for report_company_obj in report_company_objs:
               xml +='''<field name="company_%s"/>'''%(report_company_obj.id)
           #抵消分录
           xml +='''<field name="offsetting_entry"/>'''
           #合并列
           xml +='''<field name="merge_column"/>'''
           xml +='''</%s>'''%(view_type)
           result['arch'] = xml
           result['fields'] = self.fields_get(cr, uid,'xxx',context = context)
           logger.notifyChannel('addon:'+self._name,netsvc.LOG_INFO,'merge_report_result:%s'%(result))
        return result
         
merge_report()

