# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Luke Meng(Coldfire) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
{
	"name" : "Taobao Product",
	"version" : "0.2",
	"author" : "Luke Meng(Coldfire)",
	"website" : "",
	"category" : "Generic Modules/Others",
	"depends" : ["product"],
	"description" : """This is a product managment module.
	Which enchances OprnERP's built-in product module to
	manage the products on a popular Chinese Web store:
	Taobao.com from local computer.
        """,
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : ["taobao_product_view.xml", "taobao_product_wizard.xml"],
	"active": False,
	"installable": True
}
