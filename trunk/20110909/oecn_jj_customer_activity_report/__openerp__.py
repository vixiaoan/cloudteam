# -*- coding: utf-8 -*-

{
    'name': 'Customer Activity',
    'version': '1.0',
    'category': 'Generic Modules/Others',
    'description': """
Customer Activity Chart
    """,
    'author': 'Joshua<popkar77@gmail.com>',
    'website': 'http://www.openerp-china.org',
    'depends': ['oecn_jj_customer_activity',],
    'web_depends': [''],
    'init_xml': [],
    'update_xml': [
        'customer_activity_report_view.xml','wizard/customer_activity_wizard.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}