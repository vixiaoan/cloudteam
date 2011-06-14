# encoding: utf-8

from osv import osv, fields
import time
from datetime import datetime
import decimal_precision as dp

class ar_ap_report_wizard(osv.osv_memory):
    _name='oecn_mc_report_ar_ap.ar_ap_report_wizard'

    def _get_default_start_date(self, cr, uid, context=None):
        dt = datetime.now()
        return dt.strftime("%Y-%m-01")

    def _get_default_end_date(self, cr, uid, context=None):
        dt = datetime.now()
        return dt.strftime("%Y-%m-%d")

    _columns = {
        'date_start' : fields.date(u'开始日期', required=True),
        'date_end' : fields.date(u'结束日期', required=True),
    }
    _defaults = {
        'date_start': _get_default_start_date,
        'date_end': _get_default_end_date
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
        res = self.read(cr, uid, ids, ['date_start', 'date_end'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return { 'type': 'ir.actions.report.xml',
            'report_name': 'oecn_mc_report_ar_ap.ar_ap_report',
            'datas': datas, }
            
ar_ap_report_wizard()
