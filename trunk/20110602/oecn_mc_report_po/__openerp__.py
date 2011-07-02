# -*- encoding: utf-8 -*-

{
    'name': 'OECN mc report PO report',
    'version': '1.0',
    "category" : "Generic Modules/Sales & Purchases",
    'description': """
    PO报表模块
    需要版本：
    relatorio version 5.5以上
    genshi version 6.0
    
     """,
    'author': 'Joshua',
    'depends': ['base','account','relatorio_report','purchase'],
    'init_xml': [],
    'update_xml': [
        'po_report_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
