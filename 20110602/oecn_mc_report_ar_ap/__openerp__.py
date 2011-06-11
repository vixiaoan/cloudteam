# -*- encoding: utf-8 -*-

{
    'name': 'OECN mc report AR & AP report',
    'version': '1.0',
    "category" : u"Reporting",
    'description': """
    AR AP报表模块
     """,
    'author': 'CloudTeam',
    'depends': ['base','account','relatorio_report'],
    'init_xml': [],
    'update_xml': [
        'ar_ap_report.xml',
        'wizard/ar_ap_wizard.xml'
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
