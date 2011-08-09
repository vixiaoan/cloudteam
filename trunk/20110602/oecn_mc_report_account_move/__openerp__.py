# -*- encoding: utf-8 -*-

{
    'name': 'OECN mc report account move report',
    'version': '1.0',
    'category' : "Generic Modules/Sales & Purchases",
    'description': """
    PO报表模块
    需要版本：
    relatorio version 5.5以上
    genshi version 6.0
    
     """,
    'author': 'Joshua<popkar77@gmail.com>',
    'depends': ['base','account','relatorio_report'],
    'init_xml': [],
    'update_xml': [
        'account_move_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'website':'www.openerp-china.org'
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
