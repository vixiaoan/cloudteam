# encoding: utf-8

import time
from report import report_sxw
from osv import osv

class invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
        })

    def _get_bankaccounts(self):
        bank_ids =self.pool.get('res.users').browse(self.cr, self.uid, self.uid, {}).company_id.partner_id.bank_ids
        bank = self.pool.get('res.partner.bank')
        res = []
        bkname = self.localcontext['bank_account']
        for b in bank_ids:            
            for r in bank.browse(self.cr, self.uid, [b['id']], {}):
                #raise osv.except_osv(str(dup.count(r.bank.code)),str(res.count((r.id,r.bank.code))))
                if r.bank.code == bkname or r.bank.name == bkname:
                    res += [(r.bank.name,r.bank.bic or '',r.acc_number, r.name and '(' + r.name + ')' or '', r.bank.city or '', r.bank.street or '')]
        #raise osv.except_osv(str(res),str(bkname))
        return res

    def set_context(self, objects, data, ids, report_type=None):
        super(invoice_report, self).set_context(objects, data, ids, report_type)
        form = self.localcontext['data']['form']
        self.user = self.localcontext['user']
        self.localcontext['bank_account'] = data['form']['bank_account']
        self.localcontext['invoice_title'] = 'Invoice'
        if self.localcontext['company'].id == 3:
            #3,'MASTER CONCEPT SINGAPORE PTE LTD':
            self.localcontext['invoice_title'] = 'Tax Invoice'
        self.localcontext['bank_accounts'] = self._get_bankaccounts()
        #raise osv.except_osv(str(self.localcontext['company'].name ),str(self.localcontext['invoice_title']))
        
report_sxw.report_sxw('report.oecn_mc_report_invoice.invoice_report',
                      'account.invoice',
                      'addons/oecn_mc_report_invoice/report/invoice_report.odt',parser=invoice_report)
