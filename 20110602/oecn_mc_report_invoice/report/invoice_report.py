# encoding: utf-8

import time
from report import report_sxw
from osv import osv

LINES_PER_PAGE = 17

class invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'lines': self._lines
        })

    def _lines(self, invoice):
        lines = []
        for il in invoice.invoice_line:
            note_lines = il.note.split('\n')            
            if len(note_lines) > 0:
                line = (il.quantity, note_lines[0], self.formatLang(il.price_unit), self.formatLang(il.price_subtotal))
                lines.append(line)
            else:
                line = (il.quantity, '<EMPTY>', self.formatLang(il.price_unit), self.formatLang(il.price_subtotal))
                lines.append(line)

            if len(note_lines) > 1:
                for nl in note_lines[1:]:
                    line = ('', nl, '', '')
                    lines.append(line)

            #插入一个空行分隔
            line = ('', '', '' , '')
            lines.append(line)
        
        sum_height = 3
        mod = len(lines) % LINES_PER_PAGE
        free_lines = LINES_PER_PAGE - mod

        empty_lines = 0
        if free_lines - mod > sum_height: #如果在一页里面够放汇总
            empty_lines = free_lines - sum_height
        else: #不够放汇总
            empty_lines = free_lines + (LINES_PER_PAGE - sum_height)

        for n in range(0, empty_lines):
            line = ('', '', '' , '')
            lines.append(line)

        return lines

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
