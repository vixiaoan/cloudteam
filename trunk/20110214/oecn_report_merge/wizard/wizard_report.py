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


import wizard
from osv import osv
import pooler
from tools.translate import _
import netsvc

_report_form = '''<?xml version="1.0"?>
<form string="请选择">
    <field name="organizational_structure"/>
    <newline/>
    <field name="report_type"/>
    <newline/>
    <field name="period"/>
</form>'''

def _period_get(self, cr, uid, datas, ctx={}):
    try:
        pool = pooler.get_pool(cr.dbname)
        ids = pool.get('report.period').find(cr, uid, context=ctx)
        return {'period': ids[0]}
    except:
        return {}

_report_fields = {
    'organizational_structure': {'string':'组织结构', 'type':'many2one', 'relation':'organizational.structure', 'required':True},
    'report_type': {'string':'报表类型', 'type':'many2one', 'relation':'report.type', 'required':True},
    'period': {'string':'期间', 'type':'many2one', 'relation':'report.period', 'required':True,
    }
}

def _action_open_window(self, cr, uid, data, context):
    form = data['form']
    cr.execute('select id,name from ir_ui_view where model=%s and type=%s', ('report', 'tree'))
    view_res = cr.fetchone()
    
    r =  pooler.get_pool(cr.dbname).get('report')
    report_ids = r.search(cr, uid , [('organizational_structure','=',form['organizational_structure']), ('report_type','=',form['report_type']),('period','=',form['period'])])
    if not len(report_ids):
    #如果不存在报表的记录,则根据报表类型找出相应的报表行
        rl = pooler.get_pool(cr.dbname).get('report.line')
        report_line_ids = rl.search(cr, uid, [('report_type','=',form['report_type'])])
        
        for report_line_id in report_line_ids:
            r.create(cr, uid, {'organizational_structure':form['organizational_structure'], 'report_type': form['report_type'],'period':form['period'],'report_line':report_line_id})
    return {
        'domain': "[('organizational_structure','=',%d), ('report_type','=',%d),('period','=',%d)]" % (form['organizational_structure'],form['report_type'],form['period']),
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'report',
        'view_id': view_res,
        'context': "{'organizational_structure':%d, 'report_type':%d, 'period':%d}" % (form['organizational_structure'],form['report_type'] ,form['period']),
        'type': 'ir.actions.act_window'
    }

class wiz_report(wizard.interface):
    states = {
        'init': {
            'actions': [_period_get],
            'result': {'type': 'form', 'arch':_report_form, 'fields':_report_fields, 'state':[('end','取消'),('open','打开报表')]}
        },
        'open': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_window, 'state':'end'}
        }
    }
wiz_report('report.move')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

