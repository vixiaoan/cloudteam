# -*- coding: utf-8 -*-
{
    'name': 'oecn Account Report',
    'version': '1.0',
    'category': 'Custom',
    'description': """
    Module used by MC to print P&L, cash flow and COGS report
    
    User need input last period of a year in the wizard
    
    User can change the report templates (.odt files) to set up the logic:
    in any cell, menu insert->hyperlink, input methods begin with relatorio:// 
    
    get_text(period_offset) 
        ---- default value of period_offset is 0
        ---- to get the name of period,for example,
             get_text(-1) can return last period's name
    
    get(code,period_offset,company_id) 
        ---- default value of period_offset is 0
        ---- default value of company_id is 1
        ---- to get the value of an account code list, for example,
             get('debit(1001),1002,-1003',-1,1) return 
                  debit of account code 1001 
                + debit-credit of acount code 1002
                - debit-credit of acount code 1003
                  in last period in main company
    
    get_year(code,period_offset,company_ids)
        ---- default value of period_offset is 0
        ---- default value of company_ids is [1]
        ---- to get the value of an account code list, for example,
             get('debit(1001),1002,-1003',-1,1) return 
                  debit of account code 1001 
                + debit-credit of acount code 1002
                - debit-credit of acount code 1003
                  in last 12 periods(including current) in main company
    """,
    'author': 'Jeff Wang',
    'website': 'http://openerp-china.org/',
    'depends': [
        'account',
    ],
    'init_xml': [],
    'update_xml': [
        'oecn_account_report.xml'
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'certificate' : '',
}
