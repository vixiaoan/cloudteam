# -*- encoding: utf-8 -*-###############################################################################    OpenERP, Open Source Management Solution#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).##    This program is free software: you can redistribute it and/or modify#    it under the terms of the GNU Affero General Public License as#    published by the Free Software Foundation, either version 3 of the#    License, or (at your option) any later version.##    This program is distributed in the hope that it will be useful,#    but WITHOUT ANY WARRANTY; without even the implied warranty of#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the#    GNU Affero General Public License for more details.##    You should have received a copy of the GNU Affero General Public License#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     ##    Created on 2011-02-14#    author:Joshua  ##############################################################################import wizardfrom osv import osvimport poolerfrom tools.translate import __report_grid_from = '''<?xml version="1.0"?><form string = "请选择">       <field name="report_company"/>       <field name="report_type"/>       <field name="year"/>       <field name="month"/></form>'''_report_grid_fields = {        'report_company': {            'string':'组织结构',             'type':'many2one',            'relation':'report.company',             'required':True        },        'report_type': {            'string':'报表类型',             'type':'many2one',            'relation':'report.type',             'required':True        },        'year': {            'string':'年',             'type':'char',             'size':'4',             'required':True        },        'month':{            'string':'月份',            'type':'selection',            'selection':[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')],            'required':True        },}def _action_open_window(self, cr, uid, data, context):    form = data['form']    #cr.execute('select id,name from ir_ui_view where model=%s and type=%s', ('report.data', 'form'))    #view_res = cr.fetchone()    return{        'view_type':'form',        'view_mode':'tree,form',        'res_model': 'report.data.grid',        'view_id':False,        'type':'ir.actions.act_window',        'context':"{'report_company':%d,'report_type':%d, 'year':%s,'month':%s}"%(form['report_company'],form['report_type'],form['year'],form['month']),    }    class wiz_report_grid(wizard.interface):    states = {        'init': {            'actions': [],            'result': {'type': 'form', 'arch':_report_grid_from, 'fields':_report_grid_fields, 'state':[('end','取消'),('open','打开报表')]}        },        'open': {            'actions': [],            'result': {'type': 'action', 'action': _action_open_window, 'state':'end'}        }    }wiz_report_grid('report.data.grid')      