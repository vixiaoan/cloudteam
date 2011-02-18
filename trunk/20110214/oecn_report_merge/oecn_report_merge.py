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

#----------------------------------------------------------
#    组织结构
#----------------------------------------------------------

class organizational_structure(osv.osv):
    _description = "组织结构"
    _name = "organizational.structure"
    _columns = {
        'code': fields.char('编号', size=64, required=True),
        'name': fields.char('名字', size=128, required=True),
        'parent_id': fields.many2one('organizational.structure', '上级', ondelete='cascade'),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
    }
organizational_structure()
#----------------------------------------------------------
#    报表类型
#----------------------------------------------------------

class report_type(osv.osv):
    _description = "报表类型"
    _name = "report.type"
    _columns = {
        'code': fields.char('编号', size=64, required=True),
        'name': fields.char('名字', size=128, required=True),
        #行格式 暂时不需要
    }
report_type()
#----------------------------------------------------------
#    报表行
#----------------------------------------------------------
    
class report_line(osv.osv):
    _description = "报表行"
    _name = "report.line"
    _columns = {
        'report_type':fields.many2one('report.type','报表类型'),
        'name': fields.char('名称', size=128, required=True),
        'line_number':fields.integer('行号'),
    }
report_line()

#----------------------------------------------------------
#    年
#----------------------------------------------------------

class report_fiscalyear(osv.osv):
    _name = "report.fiscalyear"
    _description = "年"
    _columns = {
        'name': fields.char('Fiscal Year', size=64, required=True),
        'code': fields.char('Code', size=6, required=True),
        'date_start': fields.date('Start Date', required=True),
        'date_stop': fields.date('End Date', required=True),
        'period_ids': fields.one2many('report.period', 'fiscalyear_id', 'Periods'),
        'state': fields.selection([('draft','Draft'), ('done','Done')], 'Status', readonly=True),
    }
report_fiscalyear()

#----------------------------------------------------------
#    期间
#----------------------------------------------------------

class report_period(osv.osv):
    _name = "report.period"
    _description = "期间"
    _columns = {
        'name': fields.char('Period Name', size=64, required=True),
        'code': fields.char('Code', size=12),
        'special': fields.boolean('Opening/Closing Period', size=12,
            help="These periods can overlap."),
        'date_start': fields.date('Start of Period', required=True, states={'done':[('readonly',True)]}),
        'date_stop': fields.date('End of Period', required=True, states={'done':[('readonly',True)]}),
        'fiscalyear_id': fields.many2one('report.fiscalyear', 'Fiscal Year', required=True, states={'done':[('readonly',True)]}, select=True),
    }
report_period()

#----------------------------------------------------------
#    报表
#----------------------------------------------------------

class report(osv.osv):
    _name = "report"
    _description = "报表"
    _columns = {
        'organizational_structure':fields.many2one('organizational.structure','组织结构'),
        'report_type':fields.many2one('report.type','报表类型'),
        'period':fields.many2one('report.period','期间'),
    }
report()

#----------------------------------------------------------
#    报表明细
#----------------------------------------------------------

class report_detail(osv.osv):
    _description = "报表明细"
    _name = "report.detail"
    _columns = {
        'report_id':fields.many2one('report','报表'),
        'report_line':fields.many2one('report.line','报表行'),
        'beginning_balance':fields.float('年初金额'),
        'ending_balance':fields.float('期末金额'),
        'this_year_amount':fields.float('本年金额'),
        'last_year_amount':fields.float('上年金额'),
        'last_year_paid_up_capital':fields.float('上年实收资本'),
        'this_year_paid_up_capital':fields.float('本年实收资本'),
        'last_year_additional_paid_in_capital':fields.float('上年资本公积'),
        'this_year_additional_paid_in_capital':fields.float('本年资本公积'),
        'last_year_treasury_share':fields.float('上年库存股'),
        'this_year_treasury_share':fields.float('本年库存股'),
        'last_year_legal_reserve':fields.float('上年盈余公积'),
        'this_year_legal_reserve':fields.float('本年盈余公积'),
        'last_year_balance_of_retained_earnings':fields.float('上年未分配利润'),
        'this_year_balance_of_retained_earnings':fields.float('本年未分配利润'),
    }
report_detail()