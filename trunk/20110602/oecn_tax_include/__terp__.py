# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Sell and buy prices with taxes included',
    'version': '1.0',
    'category': 'Generic Modules/Accounting',
    'description': """Allow the user to work tax included prices.
Especially useful for b2c businesses.
    
This module implement the enhancement on the sale and purchase
order line form. If user input a tax with tax_include flag checked, 
the unit price of this order line will be replaced by untaxed price.

Attention:
  you can use only one type tax( include or not) in a order line
  for openerp don't support calculate taxes one by one
""",
    'author': 'Jeff@CloudTeam',
    'website': 'http://openerp-china.org',
    'depends': ['account','sale'],
    'init_xml': [],
    'update_xml': [],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'certificate': '',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
