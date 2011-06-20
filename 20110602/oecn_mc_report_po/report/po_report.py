# -*- encoding: utf-8 -*-

import time 
import  report
from report import report_sxw

class po_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(po_report_parser, self).__init__(cr, uid, name, context)
        self.cr = cr
        self.uid = uid
        self.localcontext.update({
            'time':time,
            })
        self.context = context
    
    def set_context(self, objects, data, ids, report_type=None):
        super(po_report_parser, self).set_context(objects,data, ids, report_type)
        purchase_pool = self.pool.get('purchase.order')
        purchases = purchase_pool.browse(self.cr, self.uid, ids, context=None)

        self.localcontext['purchases'] = purchases
        
report_sxw.report_sxw('report.oecn_mc_report_po','purchase.order','addon/oecn_mc_report_po/report/po_report.odt',parser=po_report_parser)