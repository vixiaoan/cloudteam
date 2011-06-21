# encoding: utf-8

import time
import datetime
from report import report_sxw
from osv import osv
import calendar

class cash_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        '''构造函数'''
        super(cash_report_parser, self).__init__(cr, uid, name, context=context)
        self.cr = cr
        self.uid = uid
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        super(cash_report_parser, self).set_context(objects, data, ids, report_type)
        form = self.localcontext['data']['form']
        self.user = self.localcontext['user']
        self.date_start = data['form']['date_start']
        self.date_end = data['form']['date_end']
        self.localcontext['duration'] = self.date_start + u' To ' + self.date_end
        self.localcontext['subcompanies'] = self.load_companies_data()


    def load_companies_data(self):
        # 设置子公司数据
        res_company = self.pool.get('res.company')
        ids = res_company.search(self.cr, self.uid, []) #[('id', '<>', self.user.company_id.id)]) 
        company_records = res_company.browse(self.cr, self.uid, ids, context=None)
        subcompanies = []
        for crecord in company_records:
            subcompany = {}
            subcompany['company_object'] = crecord
            #已收已付
            receipt_info = self.get_receipts(crecord.id)
            subcompany['receipts_total'] = receipt_info[0]
            subcompany['receipts'] = receipt_info[1]
            payment_info = self.get_payments(crecord.id)
            subcompany['payments_total'] = payment_info[0]
            subcompany['payments'] = payment_info[1]

            # 现金科目汇总
            cash_accounts_info = self.get_cash_accounts_info(crecord.id)
            subcompany['cash_balance'] = cash_accounts_info[0]
            subcompany['cash_accounts'] = cash_accounts_info[1]
            subcompany['receipts_total_balance'] = cash_accounts_info[0] + subcompany['receipts_total']
            subcompany['surplus'] = subcompany['receipts_total_balance'] - subcompany['payments_total']

            # 应收发票
            recv_invoice = self.get_receivable_invoices(crecord.id)
            subcompany['receivable_total'] = recv_invoice[0]
            subcompany['receivable_invoices'] = recv_invoice[1]

            # 应付发票
            repay_invoice = self.get_repayable_invoices(crecord.id)
            subcompany['repayable_total'] = repay_invoice[0]
            subcompany['repayable_invoices'] = repay_invoice[1]

            subcompanies.append(subcompany)

        return subcompanies

    def __sum_account_balance(self, company_id, account_id):
        params = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': company_id,
            'account_id': account_id,
        }
        sql = '''
            SELECT  (SUM(l.debit) - SUM(l.credit)) AS balance 
            FROM account_move_line l
            INNER JOIN account_move am ON (am.id = l.move_id)
            WHERE am.date < %(date_start)s AND am.state = 'posted'
                AND l.account_id = %(account_id)s AND am.company_id = %(company_id)s 
            '''
        self.cr.execute(sql, params)
        return self.cr.fetchone()[0] or 0.0


    def get_cash_accounts_info(self, company_id):
        account_account = self.pool.get('account.account')
        filters = [('type', '=', 'liquidity'), ('company_id', '=', company_id) ]
        #TODO 这里需要重新搞一下考虑时间区间
        account_ids = account_account.search(self.cr, self.uid, filters)
        accounts = account_account.browse(self.cr, self.uid, account_ids, context=None)
        total_balance = 0
        real_accounts = []
        for a in accounts:
            balance = self.__sum_account_balance(company_id, a.id)
            if abs(balance) > 0.0001:
                account_info = { 'name': a.name, 'code': a.code, 'balance': balance }
                real_accounts.append(account_info)
                total_balance += balance
        return total_balance, real_accounts


    def get_receipts(self, company_id):
        params = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': company_id,
        }
        sql = r'''
            SELECT l.date AS date, p.name AS partner_name, l.name AS name, i."number" AS invoice, l.debit - l.credit AS amount
            FROM account_move_line AS l
            INNER JOIN account_account AS a ON (l.account_id = a.id)
            INNER JOIN account_move AS am ON (am.id = l.move_id)
            LEFT JOIN res_partner AS p ON l.partner_id = p.id
            LEFT JOIN account_invoice AS i ON l.move_id = i.move_id
            where l.debit > l.credit AND (am.date BETWEEN %(date_start)s AND %(date_end)s) 
                AND a.type = 'liquidity' AND am.state = 'posted'
                AND am.company_id = %(company_id)s 
        '''
        self.cr.execute(sql, params)
        receipts = self.cr.dictfetchall()
        total = 0
        for r in receipts:
            total = total + r['amount']

        return (total, receipts)

    def get_payments(self, company_id):
        params = {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'company_id': company_id,
        }
        sql = r'''
            SELECT l.date AS date, p.name AS partner_name, l.name AS name, i."number" AS invoice, l.credit - l.debit AS amount
            FROM account_move_line AS l
            INNER JOIN account_account AS a ON (l.account_id = a.id)
            INNER JOIN account_move AS am ON (am.id = l.move_id)
            LEFT JOIN res_partner AS p ON l.partner_id = p.id
            LEFT JOIN account_invoice AS i ON l.move_id = i.move_id
            where l.credit > l.debit AND (am.date BETWEEN %(date_start)s AND %(date_end)s) 
                AND a.type = 'liquidity' AND am.state = 'posted'
                AND am.company_id = %(company_id)s 
        '''
        self.cr.execute(sql, params)
        payments = self.cr.dictfetchall()
        total = 0
        for p in payments:
            total = total + p['amount']
        return (total, payments)

    def __get_invoice_end_date(self):
        t = time.strptime(self.date_end, '%Y-%m-%d')
        day = calendar.monthrange(t.tm_year, t.tm_mon)[1]
        return datetime.datetime(t.tm_year, t.tm_mon, day) 

    def get_receivable_invoices(self, company_id):
        date_end = self.__get_invoice_end_date()
        account_invoice = self.pool.get('account.invoice')
        conds = [("state", "=", "open"),
                ("type", "=", "in_invoice"), 
                ("date_invoice", "<=", date_end),
                ("company_id", "=", company_id) ]
        ids = account_invoice.search(self.cr, self.uid, conds)
        invoices = account_invoice.browse(self.cr, self.uid, ids, context=None)
        total_amount = 0.0
        for i in invoices:
            total_amount = total_amount + i.amount_total
        return (total_amount, invoices)

    def get_repayable_invoices(self, company_id):
        date_end = self.__get_invoice_end_date()
        account_invoice = self.pool.get('account.invoice')
        conds = [("state", "=", "open"), 
                ("type", "=", "out_invoice"), 
                ("date_invoice", "<=", date_end),
                ("company_id", "=", company_id) ]
        ids = account_invoice.search(self.cr, self.uid, conds)
        invoices = account_invoice.browse(self.cr, self.uid, ids, context=None)
        total_amount = 0.0
        for i in invoices:
            total_amount = total_amount + i.amount_total
        return (total_amount, invoices)

        
report_sxw.report_sxw('report.oecn_mc_report.cash_report',
                       'res.partner', 
                       'addons/oecn_mc_report/report/cash_report.odt',
                       parser=cash_report_parser)
