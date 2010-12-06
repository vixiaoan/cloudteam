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
        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'start1')
        if context.has_key('only_update_p') and context['only_update_p']:
            return super(sale_order, self).write(cr, uid,  ids, vals, context=context)  
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'start2')
        
        for o in self.browse(cr, uid, ids, context=context):
            runflag = False        
            if o.state=='draft':
                if not o.related_id:#1. 原order.related_id为空
                    if not ('partner_id' in vals):#1.1 无业务伙伴更新
                        res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                        runflag = True
                    #end if not ('partner_id' in vals)
                    else:
                        buy_partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
                        if buy_partner and (not buy_partner.createpurchase):#1.2 新业务伙伴不需auto create
                            res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                            runflag = True
                        else:#1.3 新业务伙伴需auto create 
                            
                            #取要新建的order数据
                            new_data = self.copy_data(cr, uid, o.id, default=None, context=context)[0]
                            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'new_data:%s'%new_data)
                            if new_data.has_key('name'):
                                del new_data['name']
                                
                            #更新new_data
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
                                new_data.update(update_vals)
                                #创建副本
                                new_id = self.create(cr, new_uid, new_data, context)

                                new_vals = vals.copy()
                                new_vals.update({'related_id':new_id})
                                
                                #如果在创建之前执行，会出现已被更新提示
                                res = super(sale_order, self).write(cr, uid,  o.id, new_vals, context=context)                            
                                runflag = True
                                
                                #保存order后再更新副本
                                new_vals = vals.copy()
                                #不更新明细
                                if new_vals.has_key('order_line'):
                                    del new_vals['order_line']
                                if new_vals.has_key('name'):
                                    del new_vals['name']
                                #不更新partner相关
                                if new_vals.has_key('user_id'):
                                    del new_vals['user_id']
                                if new_vals.has_key('partner_id'):
                                    del new_vals['partner_id']
                                if new_vals.has_key('partner_order_id'):
                                    del new_vals['partner_order_id']
                                if new_vals.has_key('partner_invoice_id'):
                                    del new_vals['partner_invoice_id']
                                if new_vals.has_key('partner_shipping_id'):
                                    del new_vals['partner_shipping_id']
                                
                                if context:
                                    new_context =  context.copy()
                                    new_context.update({'only_update_p':True})
                                else:
                                    new_context = {'only_update_p':True}
                                
                                #更新订单主表
                                self.write(cr, uid, [new_id], new_vals, context=new_context)
                                
                                #如果存在明细修改，则删除后重建
                                if 'order_line' in vals:
                                    #删除明细，再添加
                                    del_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',new_id)])
                                    self.pool.get('sale.order.line').unlink(cr, uid, del_ids)
                                    for o_line in o.order_line:
                                        #结构说明:1=?,5=orderid         'order_line': [(1, 5, {'product_id': 16 ...})]:
                                        lines = {
                                            'order_id': new_id,
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
                                
                                
                                

                            #end if new_uid_l
                        #end else if buy_partner and (not buy_partner.createpurchase)
                    #end else if not ('partner_id' in vals):#1.1 无业务伙伴更新
                #end if not o.related_id
                else:#2. 原order.related_id不为空
                    if not ('partner_id' in vals):#2.1 无业务伙伴更新
                        res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                        runflag = True
                        
                        #副本主表内容不用更新?
                        
                        #如果存在明细修改，则删除后重建
                        if 'order_line' in vals:
                            #删除明细，再添加
                            del_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',o.related_id.id)])
                            self.pool.get('sale.order.line').unlink(cr, uid, del_ids)
                            new_uid = self._getuid(cr, uid, o.partner_id.id, context=context)
                            for o_line in o.order_line:
                                #结构说明:1=?,5=orderid         'order_line': [(1, 5, {'product_id': 16 ...})]:
                                lines = {
                                    'order_id': o.related_id.id,
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
                        
                    #end if not ('partner_id' in vals):#2.1 无业务伙伴更新
                    else:
                        buy_partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
                        if buy_partner and (not buy_partner.createpurchase):#2.2 新业务伙伴不需auto create
                            #如果新的伙伴不需要自动创建order则删除关联订单
                            self.pool.get('sale.order').unlink(cr, uid, [o.related_id.id])
                            vals.update({'related_id':None})
                            res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                            runflag = True
                        else:#3.3 新业务伙伴需auto create 
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
                                
                                #不更新明细
                                if new_vals.has_key('order_line'):
                                    del new_vals['order_line']
                                if new_vals.has_key('name'):
                                    del new_vals['name']

                                if context:
                                    new_context =  context.copy()
                                    new_context.update({'only_update_p':True})
                                else:
                                    new_context = {'only_update_p':True}                                    
                                    
                                #更新订单主表
                                self.write(cr, uid, [o.related_id.id], new_vals, context=new_context)
                                
                                #如果存在明细修改，则删除后重建
                                if 'order_line' in vals:
                                    #删除明细，再添加
                                    del_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',o.related_id.id)])
                                    self.pool.get('sale.order.line').unlink(cr, uid, del_ids)
                                    for o_line in o.order_line:
                                        #结构说明:1=?,5=orderid         'order_line': [(1, 5, {'product_id': 16 ...})]:
                                        lines = {
                                            'order_id': o.related_id.id,
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
                            
                        #end else if buy_partner and (not buy_partner.createpurchase)    
                    #end else if not ('partner_id' in vals):#2.1 无业务伙伴更新
                #end else if not o.related_id
            #end if o.state=='draft':
            
            if not runflag:
                res = super(sale_order, self).write(cr, uid, o.id, vals, context=context)                            
        #end for o in self.browse(cr, uid, ids, context=context):    
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
                        #new_vals.update({'name':'from '+vals['name']})
                        del new_vals['name']
                    res2 = self.create(cr, new_uid, new_vals, context=context)
                    if res2:
                        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'res2:%s'%res2)
                        #写入关联单号
                        if context:
                            new_context =  context.copy()
                            new_context.update({'only_update_p':True})
                        else:
                            new_context = {'only_update_p':True}
                        self.write(cr, uid, res, {'related_id':res2}, context=new_context)
        return res


sale_order()
