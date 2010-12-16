# -*- encoding: utf-8 -*-
##############################################################################
# By Jeff Wang
# Email wjfonhand@gmail.com
##############################################################################

from osv import fields,osv

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
    }
    def write(self, cr, uid, ids, vals, context=None):
        if 'shop_id' in vals:
            shop = self.pool.get('sale.shop').browse(cr, uid, vals['shop_id'])
            company = shop.warehouse_id.company_id.id
            vals.update({'company_id': company})
        return super(sale_order, self).write(cr, uid, ids, vals, context=context)
    
    def create(self, cr, uid, vals, context={}):
        if 'shop_id' in vals:
            shop = self.pool.get('sale.shop').browse(cr, uid, vals['shop_id'])
            company = shop.warehouse_id.company_id.id
            vals.update({'company_id': company})
        return super(sale_order, self).create(cr, uid, vals, context=context)
    
sale_order()  
class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
    }
    def write(self, cr, uid, ids, vals, context=None):
        if 'warehouse_id' in vals:
            company = self.pool.get('stock.warehouse').browse(cr, uid, vals['warehouse_id']).company_id.id
            vals.update({'company_id': company})
        return super(purchase_order, self).write(cr, uid, ids, vals, context=context)
    
    def create(self, cr, uid, vals, context={}):
        if 'warehouse_id' in vals:
            company = self.pool.get('stock.warehouse').browse(cr, uid, vals['warehouse_id']).company_id.id
            vals.update({'company_id': company})
        return super(purchase_order, self).create(cr, uid, vals, context=context)
    
purchase_order()
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
res_partner()
         