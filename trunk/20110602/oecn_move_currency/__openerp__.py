# -*- encoding: utf-8 -*-

{
    'name': 'OECN Move Currency',
    'version': '1.0',
    "category" : "Generic Modules/Accounting",
    'description': """
    When create journal entry manaually, after user change the currency, 
    we can convert foriegn currency amount to local currency amount.
     """,
    'author': 'Jeff',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': [
        'oecn_move_currency.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
