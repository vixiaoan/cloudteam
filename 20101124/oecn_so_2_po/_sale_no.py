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
    #related_id销售订单的关联副本
    _columns = {
        'related_id': fields.many2one('sale.order', 'Related ID', readonly=True, help='Related partner sale order'),
    }  

    def _getuidlist(self, cr, uid, partnerid, context=None):
        """根据partnerid返回数据库中的uid[]"""
        ruid = []
        partner_obj =  self.pool.get('res.partner').browse(cr, uid, partnerid, context=context)
        if partner_obj:
            company_id = self.pool.get('res.company').search(cr, uid, [('partner_id','=',partnerid)])
            #如果没有多公司则返回第一个
            if not company_id:
                company_id = self.pool.get('res.company').search(cr, uid, [])[0]
            if company_id:
               ruid = self.pool.get('res.users').search(cr, uid, [('company_id','=',company_id)])

        return ruid
    
    def _getuid(self, cr, uid, partnerid, context=None):
        """根据partnerid返回数据库中的uid,如果没有则返回uid"""
        ruid = uid 
        uidlist = self._getuidlist(cr, uid, partnerid, context=context)
        if uidlist:
            ruid = uidlist[0] #取第一个UID可能不准确，建议新建一个角色，用于自动创建订单
        return ruid    
        
    """
    def _getuid(self, cr, uid, partnerid, context=None)
        ruid = uid 
        partner_obj =  self.pool.get('res.partner').browse(cr, uid, partnerid, context=context)
        if partner_obj:
            company_id = self.pool.get('res.company').search(cr, uid, [('partner_id','=',partnerid)])
            if company_id:
               uids = self.pool.get('res.users').search(cr, uid, [('company_id','=',company_id)])
               if uids:
                ruid = uids[0] #取第一个UID可能不准确，建议新建一个角色，用于自动创建订单
        return ruid
    """    
        
    
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
                        

    def write(self, cr, uid, ids, vals, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            runflag = False        
            if o.state=='draft' and o.related_id and o.related_id.state=='draft':
                if 'partner_id' in vals:
                    #伙伴改变,
                    buy_partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
                    if buy_partner and (not buy_partner.createpurchase):
                        #如果新的伙伴不需要自动创建order则删除关联订单,并continue
                        self.pool.get('sale.order').unlink(cr, uid, [o.related_id.id])
                        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'o.id:%s'%o.id)                        
                        #self.pool.get('sale.order').write(cr, uid, [o.id], {'related_id':None}, context)
                        vals.update({'related_id':None})
                        res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                        runflag = True
                        continue
                    else:    
                        #如果新的伙伴需要自动创建order则修改关联订单USER_ID，并更新关联订单内容
                        res = super(sale_order, self).write(cr, uid, o.id, vals, context=context)  
                        runflag = True
                        new_uid_l = self._getuidlist(cr, uid, vals['partner_id'], context=context)
                        if new_uid_l:
                            new_uid = self._getuid(cr, uid, vals['partner_id'], context=context)
                            #('createpurchase','=',False)防止进入死循环， order='create_date desc':按创建日期降序
                            partnet_id_list = self.pool.get('res.partner').search(cr, uid, [('createpurchase','=',False),('create_uid','in',new_uid_l)], order='create_date desc')
                            user_obj = self.pool.get('res.users').browse(cr, uid, new_uid, context=context)
                            #取最新的partner
                            partner = self.pool.get('res.partner').browse(cr, uid, partnet_id_list[0], context=context)
                            partner_id = partner.id
                            #联系人
                            partner_order_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact'])['contact']
                            #发票地址
                            partner_invoice_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['invoice'])['invoice']
                            #送货地址
                            partner_shipping_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])['delivery']
                            pricelist_id = partner.property_product_pricelist_purchase.id
                            #shop是否也得改?
                            update_vals = {
                                'user_id':new_uid,
                                'partner_id':partner_id,
                                'partner_order_id':partner_order_id,
                                'partner_invoice_id':partner_invoice_id,
                                'partner_shipping_id':partner_shipping_id
                            }                        
                            new_vals = vals.copy()
                            new_vals.update(update_vals)
                            #更新订单主表
                            self.write(cr, uid,o.related_id.id, new_vals, context)
                            
                            
                            #如果存在明细修改，则删除后重建
                            if order_line in vals:
                                #删除明细，再添加
                                del_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',o.related_id.id)])
                                self.pool.get('sale.order.line').unlink(cr, uid, del_ids)
                                for o_line in o.order_line:
                                    #结构说明:1=?,5=orderid         'order_line': [(1, 5, {'product_id': 16 ...})]:
                                    lines = {
                                        'order_id': o.id,
                                        'name': o_line.name,
                                        'sequence': o_line.sequence,
                                        'delay': o_line.delay,
                                        'product_id': o_line.product_id.id,
                                        'property_ids': o_line.property_ids,
                                        'price_unit': o_line.price_unit,
                                        'product_uom_qty': o_line.product_uom_qty,
                                        'product_uom': o_line.product_uom.id,
                                        'product_uos': o_line.product_uos.id,
                                        'discount': o_line.discount,
                                        'th_weight': o_line.th_weight,
                                        'product_packaging': o_line.product_packaging.id,
                                        #'address_allotment_id': o_line.address_allotment_id.id,
                                        #'notes': o_line.notes,
                                        'type': o_line.type
                                    }
                                    self.pool.get('sale.order.line').create(cr, new_uid, lines, context)
                if not runflag:
                    res = super(sale_order, self).write(cr, uid, o.id, vals, context=context)                            
        return res 
        
    def create(self, cr, uid, vals, context={}):
        res = super(sale_order, self).create(cr, uid, vals, context=context)
        if res:
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'start1')
            buy_partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
            if buy_partner and buy_partner.createpurchase:
                #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'start2')
                new_uid_l = self._getuidlist(cr, uid, vals['partner_id'], context=context)
                #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'error%s'%new_uid_l)
                if new_uid_l:
                    new_uid = self._getuid(cr, uid, vals['partner_id'], context=context)
                    #('createpurchase','=',False)防止进入死循环， order='create_date desc':按创建日期降序
                    partnet_id_list = self.pool.get('res.partner').search(cr, uid, [('createpurchase','=',False),('create_uid','in',new_uid_l)], order='create_date desc')
                    user_obj = self.pool.get('res.users').browse(cr, uid, new_uid, context=context)
                    #取最新的partner
                    partner = self.pool.get('res.partner').browse(cr, uid, partnet_id_list[0], context=context)
                    partner_id = partner.id
                    #联系人
                    partner_order_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['contact'])['contact']
                    #发票地址
                    partner_invoice_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['invoice'])['invoice']
                    #送货地址
                    partner_shipping_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])['delivery']
                    pricelist_id = partner.property_product_pricelist_purchase.id
                    #shop是否也得改?
                    update_vals = {
                        'user_id':new_uid,
                        'partner_id':partner_id,
                        'partner_order_id':partner_order_id,
                        'partner_invoice_id':partner_invoice_id,
                        'partner_shipping_id':partner_shipping_id
                    }
                    new_vals = vals.copy()
                    new_vals.update(update_vals)
                    if new_vals.has_key('name'):
                        new_vals.update({'name':'from '+vals['name']})
                        #del new_vals['name']
                    res2 = self.create(cr, new_uid, new_vals, context=context)
                    if res2:
                        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'res2:%s'%res2)
                        #写入关联单号
                        self.write(cr, uid, res, {'related_id':res2}, context=context)
        return res


sale_order()
