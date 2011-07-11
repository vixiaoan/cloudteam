# encoding: utf-8

from osv import osv, fields
import time
from datetime import datetime
import decimal_precision as dp
import netsvc

class invoice_report_wizard(osv.osv_memory):
    _name='oecn_mc_report_invoice.invoice_report_wizard'

    def _get_bankaccount(self, cr, uid, context=None):
        bank_ids =self.pool.get('res.users').browse(cr, uid, uid, context).company_id.partner_id.bank_ids
        #netsvc.Logger().notifyChannel('A:wizard(bank_ids):',netsvc.LOG_INFO,bank_ids)
        bank = self.pool.get('res.partner.bank')
        res = []
        dup = []
        ins = []
        for b in bank_ids:
            #dup += [r.bank.code for r in bank.browse(cr, uid, [b['id']], context)]
            for r in bank.browse(cr, uid, [b['id']], context):
                dup += [r.bank.code]

        for b in bank_ids:            
            for r in bank.browse(cr, uid, [b['id']], context):
                #raise osv.except_osv(str(dup.count(r.bank.code)),str(res.count((r.id,r.bank.code))))
                if dup.count(r.bank.code) > 1:
                    if ins.count(r.bank.code) < 1:
                        ins += [r.bank.code]
                        res +=[ (r.bank.code, r.bank.code)]
                else:
                    res +=[ (r.bank.name, r.bank.name)]
        #raise osv.except_osv(str(res),str(ins))
        return res

    _columns = {
        'bank_account' : fields.selection(_get_bankaccount, 'Bank Account', required=True),
	#'add_msg':fields
    }
    
    def print_report(self, cr, uid, ids, context=None):
        """
        print the report
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['bank_account'], context=context)
	#netsvc.Logger().notifyChannel('A:print_report(res):',netsvc.LOG_INFO,res)
	#raise osv.except_osv(str(res),str(res))
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return { 'type': 'ir.actions.report.xml',
            'report_name': 'oecn_mc_report_invoice.invoice_report',
            'datas': datas, }
            
invoice_report_wizard()
