# -*- encoding: utf-8 -*-

{
    "name": "OpenERP-China MC Report",
    "author": "CloudTeam",
    "Description": u"""
    A long description

    """,
    "version": "0.1",
    "depends": ['base', 'report_relatorio', 'account', 'account_accountant'],
    "category" : u"Reporting",
    'description': u"""
    A long description
    """,
    "init_xml": [],
    "update_xml": [
#        'security/ir.model.access.csv',
        'mc_wizard.xml',
        'mc_report.xml',
    ],
    "demo_xml": [],
#    "test": ['test/test_lunch.yml', 'test/lunch_report.yml'],
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
