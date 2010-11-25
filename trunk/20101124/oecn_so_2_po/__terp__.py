# -*- encoding: utf-8 -*-
##############################################################################
#
#    Created on 2010-11-24
#    @author: stbrine@yahoo.com.cn
#
##############################################################################
{
    "name": "sale order to purchase ordre",
    "author": "stbrine@yahoo.com.cn",
    "version": "0.1",
    "depends": ["sale","purchase"],
    "description": """Recognized on the sale of certain business partners in order to automatically generate purchase orders""",
    "init_xml": [],
    "update_xml": [
		'partner_view.xml',
    ],
    "demo_xml": [],
    "installable": True,
}

