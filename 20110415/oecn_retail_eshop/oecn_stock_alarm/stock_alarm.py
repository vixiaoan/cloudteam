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
import netsvc

class stock_warehouse_orderpoint(osv.osv):
    _inherit = 'stock.warehouse.orderpoint'
    
    def _get_virtual_available(self, cr, uid, ids, name, arg,context={}):
        product_obj = self.pool.get('product.product')
        if not ids:
            ids = self.search(cr, uid, [])
        if not ids:
            return res
        res = {}.fromkeys(ids, 0.0)
        for id in ids:
            orderpoint_obj = self.browse(cr, uid, id)
            res[id] = product_obj.browse(cr, uid, orderpoint_obj.id).virtual_available
        return res
        
    _columns = {
                'virtual_available':fields.function(_get_virtual_available,method = True, type='float', string = 'Virtual Stock'),
    }

    def search(self, cr, user, args, offset= 0, limit=None, order=None, context=None, count=False):
        if context and context.get('srtock_alarm'):
            #mrp/scheduler.py
            op_ids = []
            location_obj = self.pool.get('stock.location')
            ids = self.search(cr, user, [
                ('product_id.active', '=', True),
                ('product_id.purchase_ok', '=', True),
            ], offset=offset, limit=limit)
            for op in self.browse(cr, user, ids):
                if op.procurement_id and op.procurement_id.purchase_id and op.procurement_id.purchase_id.state in ('draft', 'confirmed'):
                    continue
                prods = location_obj._product_virtual_get(cr, user,
                        op.location_id.id, [op.product_id.id],
                        {'uom': op.product_uom.id})[op.product_id.id]
                if prods < op.product_min_qty:
                    op_ids.append(op.id)
                args.append(('id','in',op_ids))
            if len(args) <= 0:
               args = [('id','in','0')]
        return super(stock_warehouse_orderpoint, self).search(cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)
stock_warehouse_orderpoint()