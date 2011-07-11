# -*- encoding: utf-8 -*-

{
    'name': 'OECN mc INVOICE report',
    'version': '1.0',
    "category" : u"Reporting",
    'description': """
    Custom Invoice Report for Master Concept (Hong Kong) Limited
     """,
    'author': 'CloudTeam<Hifly,csnlca@gmail.com>',
    'depends': ['base','account','relatorio_report'],
    'init_xml': [],
    'update_xml': [
        'invoice_report.xml',
        'wizard/invoice_report_wizard.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
