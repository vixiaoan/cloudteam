# -*- encoding: utf-8 -*-

import time 
from report import report_sxw

class account_move_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(account_move_report_parser, self).__init__(cr, uid, name, context)
        self.cr = cr
        self.uid = uid
        self.localcontext.update({
            'time':time,
            'total':self._get_total,
            })
            
    def _get_total(self, id):
        am_obj = self.pool.get('account.move')
        result = {
            'total_debit':0.00,
            'total_credit':0.00,
        }
        if id:
            for line in am_obj.browse(self.cr, self.uid, id).line_id:
                result['total_debit'] += line.debit or 0.00
                result['total_credit'] += line.credit or 0.00
        return result
        
        
report_sxw.report_sxw('report.oecn_mc_report_account_move','account.move','addon/oecn_mc_report_account_move/report/report/account_move_report.odt',parser=account_move_report_parser)