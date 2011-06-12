# encoding: utf-8

import time 
import datetime
from report import report_sxw
from osv import osv

class ar_ap_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ar_ap_report_parser, self).__init__(cr, uid, name, context=context)
        self.cr = cr
        self.uid = uid
        self.localcontext.update({
            'time':time,
            'cr': cr,
            'uid': uid,
            'current':self._get_current,
            'main_currency':self._get_main_currency,
        })
        self.context = context
        
    def _get_main_currency(self,old_currency,new_currency,from_amount):
        currency_pool = self.pool.get('res.currency')
        if old_currency == new_currency:
        #相同即返回
            return False

        old_currency_id =currency_pool.search(self.cr, self.uid,[('name','=',old_currency)])
        new_currency_id =currency_pool.search(self.cr, self.uid,[('name','=',new_currency)])

        a =  currency_pool.compute(self.cr, self.uid, old_currency_id[0], new_currency_id[0], from_amount)
        return a
    
    def get_date_diff(self, data1, data2):
        '''计算date1与date2的日期差'''
        date_diff = 0
        if data1 and data2:
            data1 = datetime.datetime(int(data1[0:4]),int(data1[5:7]),int(data1[8:10]))
            data2 = datetime.datetime(int(data2[0:4]),int(data2[5:7]),int(data2[8:10]))
            date_diff = (data1 - data2).days
        return date_diff
        
    def _get_current(self,amount,date_due = False):
        '''按日期差获取应收账款'''
        res = {
            'current':'',
            '1_30':'',
            '31_60':'',
            '61_90':'',
            '90':'',
            }
        date_diff = self.get_date_diff(date_due or self.date_end,self.date_end)
        if date_diff <= 0:
            res['current'] = amount
        elif 1 <= date_diff <= 30:
            res['1_30'] = amount
        elif 31 <= date_diff <= 60:
            res['31_60'] = amount
        elif 61 <= date_diff <= 90:
            res['61_90'] = amount
        elif date_diff > 90:
            res['90'] = amount
        return res
    
    def set_context(self, objects, data, ids, report_type=None):
        super(ar_ap_report_parser, self).set_context(objects, data, ids, report_type)
        form = self.localcontext['data']['form']
        self.user = self.localcontext['user']
        self.date_start = data['form']['date_start']
        self.date_end = data['form']['date_end']
        self.localcontext['date_end'] = self.date_end
        
        user_pool = self.pool.get('res.users')
        user_obj = user_pool.browse(self.cr, self.uid, self.user, context=None)
        
        currencys = []
        currency_pool = self.pool.get('res.currency')
        currency_ids = currency_pool.search(self.cr, self.uid, [])
        currency_objs = currency_pool.browse(self.cr, self.uid, currency_ids, context=None)
        
        
        account_invoice_pool = self.pool.get('account.invoice')

        for currency_obj in currency_objs:
            currency = {'out_invoices':False,
                        'in_invoices':False,
                        'out_invoice_current_total':False,
                        'out_invoice_1_30_total':False,
                        'out_invoice_31_60_total':False,
                        'out_invoice_61_90_total':False,
                        'out_invoice_90_total':False,
                        'out_invoice_amount_total':False,
                        'in_invoice_current_total':False,
                        'in_invoice_1_30_total':False,
                        'in_invoice_31_60_total':False,
                        'in_invoice_61_90_total':False,
                        'in_invoice_90_total':False,
                        'in_invoice_amount_total':False,
                        
                        'currency_name':''}
            
            account_out_invoice_by_currency_ids = account_invoice_pool.search(self.cr, self.uid, [('currency_id','=',currency_obj.id),('state','=','open'),('type','=','out_invoice')],order="date_due")
            if account_out_invoice_by_currency_ids:
                out_invoices = account_invoice_pool.browse(self.cr, self.uid, account_out_invoice_by_currency_ids, context=None)
                currency['out_invoices'] = out_invoices
                for out_invoice in out_invoices:
                    date_diff = self.get_date_diff(out_invoice.date_due or self.date_end,self.date_end)
                    if date_diff <=0:
                        currency['out_invoice_current_total'] = currency['in_invoice_current_total'] + out_invoice.amount_total
                    elif 1 <= date_diff <= 30:
                        currency['out_invoice_1_30_total'] = currency['out_invoice_1_30_total'] + out_invoice.amount_total
                    elif 31 <= date_diff <= 60:
                        currency['out_invoice_31_60_total'] = currency['out_invoice_31_60_total'] + out_invoice.amount_total
                    elif 61 <= date_diff <= 90:
                        currency['out_invoice_61_90_total'] = currency['out_invoice_61_90_total'] + out_invoice.amount_total
                    elif date_diff > 90:
                        currency['out_invoice_90_total'] = currency['out_invoice_90_total'] + out_invoice.amount_total
                    currency['out_invoice_amount_total'] = currency['out_invoice_amount_total'] + out_invoice.amount_total
            account_in_invoice_by_currency_ids = account_invoice_pool.search(self.cr, self.uid, [('currency_id','=',currency_obj.id),('state','=','open'),('type','=','in_invoice')],order="date_due")
            if account_in_invoice_by_currency_ids:
                in_invoices = account_invoice_pool.browse(self.cr, self.uid, account_in_invoice_by_currency_ids, context=None)
                currency['in_invoices'] = in_invoices
                for in_invoice in in_invoices:
                    date_diff = self.get_date_diff(in_invoice.date_due or self.date_end,self.date_end)
                    if date_diff <=0:
                        currency['in_invoice_current_total'] = currency['in_invoice_current_total'] + in_invoice.amount_total
                    elif 1 <= date_diff <= 30:
                        currency['in_invoice_1_30_total'] = currency['in_invoice_1_30_total'] + in_invoice.amount_total
                    elif 31 <= date_diff <= 60:
                        currency['in_invoice_31_60_total'] = currency['in_invoice_31_60_total'] + in_invoice.amount_total
                    elif 61 <= date_diff <= 90:
                        currency['in_invoice_61_90_total'] = currency['in_invoice_61_90_total'] + in_invoice.amount_total
                    elif date_diff > 90:
                        currency['in_invoice_90_total'] = currency['in_invoice_90_total'] + in_invoice.amount_total
                    currency['in_invoice_amount_total'] = currency['in_invoice_amount_total'] + in_invoice.amount_total
                    
            if currency['out_invoices'] or currency['in_invoices']:
                currency['currency_name'] = currency_obj.name
                currencys.append(currency)
        self.localcontext['currencys'] = currencys
        #pre-order
        pre_order_ids = account_invoice_pool.search(self.cr, self.uid, [('state','=','draft'),('type','=','in_invoice')],order="date_due")
        pre_orders = account_invoice_pool.browse(self.cr, self.uid, pre_order_ids, context=None)
        self.localcontext['pre_orders'] = pre_orders
        
report_sxw.report_sxw('report.oecn_mc_report_ar_ap.ar_ap_report',
                      'account.invoice',
                      'addons/oecn_mc_report_ar_ap/report/ar_ap_report.odt',parser=ar_ap_report_parser)