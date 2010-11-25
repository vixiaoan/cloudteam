# -*- encoding: utf-8 -*-
##############################################################################
#
#    Created on 2010-11-25
#    @author: stbrine@yahoo.com.cn
#
##############################################################################

import time
from mx import DateTime
import netsvc
from osv import fields, osv
from tools.translate import _

class sale_order(osv.osv):
    _name = "sale.order"
    _description = "Sale Order"
    _inherit = 'sale.order'
    logger = netsvc.Logger()
    def action_wait(self, cr, uid, ids, *args):
        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'start')
        res = super(sale_order, self).action_wait(cr, uid, ids, *args)  #完成父类动作
        #for to sale_order
        for o in self.browse(cr, uid, ids):
            purchase_order_obj = self.pool.get('purchase.order')
            #purchase_order_line_obj = self.pool.get('purchase.order_line')
            buy_partner = self.pool.get('res.partner').browse(cr, uid, o.partner_id.id)
            if buy_partner and buy_partner.createpurchase:
                #通过业务员或uid的公司的partner作为供应商supplier
                if o.user_id:
                    supplier = o.user_id
                else:
                    supplier = self.pool.get('res.users').browse(cr, uid, uid)
                
                buy_uid = uid #采购单的uid,此处以uid可能不准确,需完善
                
                partner = self.pool.get('res.partner').browse(cr, uid, supplier.company_id.partner_id.id)
                partner_id = partner.id
                address_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])['delivery']
                pricelist_id = partner.property_product_pricelist_purchase.id
                context = {}
                context.update({'lang':partner.lang, 'partner_id':partner_id})
                company = self.pool.get('res.users').browse(cr, uid, buy_uid, context).company_id
                whid = self.pool.get('stock.warehouse').search(cr, uid, [])
                wh = self.pool.get('stock.warehouse').browse(cr, uid, whid, context)[0]
                
                #参考D:\Program Files\OpenERP AllInOne\Server\addons\mrp\mrp.py 1055行,添加采购单
                #参考D:\Program Files\OpenERP AllInOne\Server\addons\mrp\wizard\make_procurement.py 37行取warehouse
                
                #生成采购明细
                lines = []
                for o_line in o.order_line:
                    product = self.pool.get('product.product').browse(cr,uid,o_line.product_id.id,context=context)
                    taxes_ids = product.product_tmpl_id.supplier_taxes_id
                    taxes = self.pool.get('account.fiscal.position').map_tax(cr, uid, partner.property_account_position, taxes_ids)
                    newdate = DateTime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S') #明细计划时间
                    #newdate = newdate - DateTime.RelativeDateTime(days=company.po_lead)
                    #newdate = newdate - product.seller_ids[0].delay
                    lines.append((0,0,{
                        'name': product.partner_ref,
                        'product_qty': o_line.product_uom_qty,
                        'product_id': product.id,
                        'product_uom': o_line.product_uom.id,
                        'price_unit': o_line.price_unit,
                        'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                        'notes':product.description_purchase,    
                        #'move_dest_id': res_id,
                        'taxes_id':[(6,0,taxes)]                        
                    }))
                
                #'name':self.pool.get('ir.sequence').get(cr, uid, 'purchase.order'),
                purchase_order_id = purchase_order_obj.create(cr, buy_uid, 
                    {
                        'origin':'sale order:%s'%o.name,
                        'partner_id': partner_id,
                        'partner_address_id': address_id,
                        'location_id': wh.lot_stock_id.id,
                        'pricelist_id': pricelist_id,
                        'order_line': lines,
                        'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                        'date_order':time.strftime('%Y-%m-%d %H:%M:%S'),
                    })

sale_order()
