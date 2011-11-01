# encoding: utf-8

from osv import osv, fields
import time
from datetime import datetime
import decimal_precision as dp

class account_report_wizard_cf(osv.osv_memory):
    _name='oecn_account_report.report_wizard_cf'

    _columns = {
        'period': fields.many2one('account.period', 'Period', required=True),
    }
    _defaults = {
        'period': 12,
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['period'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return { 'type': 'ir.actions.report.xml',
            'report_name': 'oecn_account_report.cf',
            'datas': datas, }
            
account_report_wizard_cf()

class account_report_wizard_pl(osv.osv_memory):
    _name='oecn_account_report.report_wizard_pl'

    _columns = {
        'period': fields.many2one('account.period', 'Period', required=True),
    }
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['period'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return { 'type': 'ir.actions.report.xml',
            'report_name': 'oecn_account_report.pl',
            'datas': datas, }
            
account_report_wizard_pl()

class account_report_wizard_cogs(osv.osv_memory):
    _name='oecn_account_report.report_wizard_cogs'

    _columns = {
        'period': fields.many2one('account.period', 'Period', required=True),
    }
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['period'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return { 'type': 'ir.actions.report.xml',
            'report_name': 'oecn_account_report.cogs',
            'datas': datas, }
            
account_report_wizard_cogs()
