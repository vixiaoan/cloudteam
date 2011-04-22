# -*- encoding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
#    Created on 2011-04-21
#    author:Joshua  
##############################################################################

from osv import fields, osv
from osv import osv

class product_product(osv.osv):
    _inherit = 'product.product'

    def search(self, cr, user, args, offset= 0, limit=None, order=None, context=None, count=False):
        if context and context.get('srtock_alarm'):
            #mrp/scheduler.py
            orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
            location_obj = self.pool.get('stock.location')
            ids = orderpoint_obj.search(cr, user, [
                ('product_id.active', '=', True),
                ('product_id.purchase_ok', '=', True),
            ], offset=offset, limit=100)
            for op in orderpoint_obj.browse(cr, user, ids):
                if op.procurement_id and op.procurement_id.purchase_id and op.procurement_id.purchase_id.state in ('draft', 'confirmed'):
                    continue
                prods = location_obj._product_virtual_get(cr, user,
                        op.location_id.id, [op.product_id.id],
                        {'uom': op.product_uom.id})[op.product_id.id]
                if prods < op.product_min_qty:
                    args.append(('id','in',str(op.product_id.id)))
            if len(args) <= 0:
               args = [('id','in','0')]
        return super(product_product, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)
product_product()