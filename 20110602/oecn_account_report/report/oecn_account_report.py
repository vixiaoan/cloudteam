# encoding: utf-8

import time 
import datetime
from report import report_sxw
from osv import osv
import re

class oecn_account_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(oecn_account_report_parser, self).__init__(cr, uid, name, context=context)
        self.cr = cr
        self.uid = uid
        self.localcontext.update({
            'time':time,
            'cr': cr,
            'uid': uid,
            'get':self.get,
            'get_text':self.get_text,
            'get_year':self.get_year,
        })
        self.context = context
        
    def get_text(self,period_offset=0,context={}):
        period_object = self.pool.get('account.period')
        for_period = self.localcontext['data']['form'].get('period', False)+period_offset
        if for_period <= 0:
            txt = 'Not Found Period'
        else:
            txt = period_object.browse(self.cr, self.uid, [for_period], context)[0].name
        return txt
    
    def get(self,code,period_offset=0,company_id=1,balance_mode='1',context={}):
        """
        It returns the (debit, credit, balance*) tuple for a account with the
        given code, or the sum of those values for a set of accounts
        when the code is in the form "400,300,(323)"

        Depending on the balance_mode, the balance is calculated as follows:
          Mode 0: debit-credit for all accounts (default);
          Mode 1: debit-credit, credit-debit for accounts in brackets;
          Mode 2: credit-debit for all accounts;
          Mode 3: credit-debit, debit-credit for accounts in brackets.

        Also the user may specify to use only the debit or credit of the account
        instead of the balance writing "debit(551)" or "credit(551)".
        """
        acc_facade = self.pool.get('account.account')
        ammount = 0.00
        uid = self.uid
        for_period = self.localcontext['data']['form'].get('period', False)+period_offset
        if for_period <= 0:
            return ammount
        context['periods'] = [for_period]

        assert balance_mode in ('0','1','2','3'), "balance_mode should be in [0..3]"

        # We iterate over the accounts listed in "code", so code can be
        # a string like "430+431+432-438"; accounts split by "+" will be added,
        # accounts split by "-" will be substracted.
        #
        # We also take in consideration the balance_mode:
        #   Mode 0: credit-debit for all accounts
        #   Mode 1: debit-credit, credit-debit for accounts in brackets
        #   Mode 2: credit-debit, debit-credit for accounts in brackets
        #   Mode 3: credit-debit, debit-credit for accounts in brackets.
        #
        # And let the user get just the credit or debit if he specifies so.
        #
        for account_code in re.findall('(-?\w*\(?[0-9a-zA-Z_]*\)?)', code):
            # Check if the code is valid (findall might return empty strings)
            if len(account_code) > 0:
                #
                # Check the sign of the code (substraction)
                #
                if account_code.startswith('-'):
                    sign = -1.0
                    account_code = account_code[1:] # Strip the sign
                else:
                    sign = 1.0


                if re.match(r'^debit\(.*\)$', account_code):
                    # Use debit instead of balance
                    mode = 'debit'
                    account_code = account_code[6:-1] # Strip debit()
                elif re.match(r'^credit\(.*\)$', account_code):
                    # Use credit instead of balance
                    mode = 'credit'
                    account_code = account_code[7:-1] # Strip credit()
                else:
                    mode = 'balance'
                    #
                    # Calculate the balance, as given by the balance mode
                    #
                    if balance_mode == '1':
                        # We use debit-credit as default balance,
                        # but for accounts in brackets we use credit-debit
                        if account_code.startswith('(') and account_code.endswith(')'):
                            sign = -1.0 * sign
                    elif balance_mode == '2':
                        # We use credit-debit as the balance,
                        sign = -1.0 * sign
                    elif balance_mode == '3':
                        # We use credit-debit as default balance,
                        # but for accounts in brackets we use debit-credit
                        if not account_code.startswith('(') and account_code.endswith(')'):
                            sign = -1.0 * sign
                    # Strip the brackets (if there are brackets)
                    if account_code.startswith('(') and account_code.endswith(')'):
                        account_code = account_code[1:-1]

                # Search for the account (perfect match)
                account_ids = acc_facade.search(self.cr, uid, [
                        ('code', '=', account_code),
                        ('company_id','=', company_id)
                    ], context=context)
                if not account_ids:
                    # We didn't find the account, search for a subaccount ending with '0'
                    account_ids = acc_facade.search(self.cr, uid, [
                            ('code', '=like', '%s%%0' % account_code),
                            ('company_id','=', company_id)
                        ], context=context)

                if len(account_ids) > 0:
                    if mode == 'debit':
                        ammount += acc_facade.browse(self.cr, uid, account_ids, context)[0].debit
                    elif mode == 'credit':
                        ammount += acc_facade.browse(self.cr, uid, account_ids, context)[0].credit
                    else:
                        ammount += acc_facade.browse(self.cr, uid, account_ids, context)[0].balance * sign
        return ammount
    
    def get_year(self,code,company_ids=[1],balance_mode='1',context={}):
        n = 0
        amt = 0.0
        while n < 12:
            for company in company_ids:
                amt += self.get(code,period_offset=n,company_id=company,balance_mode=balance_mode,context=context)
            n += 1
        return amt
report_sxw.report_sxw('report.oecn_account_report.cf',
                      'account.account',
                      'addons/oecn_account_report/report/cashflow.odt',parser=oecn_account_report_parser)
report_sxw.report_sxw('report.oecn_account_report.pl',
                      'account.account',
                      'addons/oecn_account_report/report/pl.odt',parser=oecn_account_report_parser)
report_sxw.report_sxw('report.oecn_account_report.cogs',
                      'account.account',
                      'addons/oecn_account_report/report/cogs.odt',parser=oecn_account_report_parser)
