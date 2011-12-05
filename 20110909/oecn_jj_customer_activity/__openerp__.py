# -*- coding: utf-8 -*-
{
    'name': 'Customer Activity',
    'version': '1.0',
    'category': 'Generic Modules/Others',
    'description': """
     从网站下载前一天的用户活跃度数据并写入客户主数据。如果剩余point或money数量低于预设值，发邮件给计划任务的用户。

该模块功能由scheduler触发。

增加了一个菜单用于显示取到的活跃度数据""",
    'author': 'Joshua<popkar77@gmail.com>',
    'depends': ['base'],
    'init_xml': [],
    'update_xml': ['customer_activity_view.xml','customer_activity_data.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
