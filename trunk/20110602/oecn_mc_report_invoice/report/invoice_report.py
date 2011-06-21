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
        
report_sxw.report_sxw('report.oecn_mc_report_invoice.invoice_report',
                      'account.invoice',
                      'addons/oecn_mc_report_invoice/report/invoice_report.odt',parser=invoice_report)
