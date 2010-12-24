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
        'related_id': fields.integer( 'Related ID', readonly=True, help='Related partner sale order'),
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
        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'ruid:%s'%ruid)
        return ruid
    
    def _getuid(self, cr, uid, partnerid, context=None):
        """根据partnerid返回数据库中的uid,如果没有则返回uid"""
        ruid = uid 
        uidlist = self._getuidlist(cr, uid, partnerid, context=context)
        if uidlist:
            ruid = uidlist[0] #取第一个UID可能不准确，建议新建一个角色，用于自动创建订单
        return ruid    

    
    def action_wait(self, cr, uid, ids, *args):
        res = super(sale_order, self).action_wait(cr, uid, ids, *args)  #完成父类动作
        #for to sale_order
        for o in self.browse(cr, uid, ids):
            purchase_order_obj = self.pool.get('purchase.order')
            buy_partner = self.pool.get('res.partner').browse(cr, uid, o.partner_id.id)
            if buy_partner and buy_partner.createpurchase:
                #通过业务员或uid的公司的partner作为供应商supplier
                if o.user_id:
                    supplier = o.user_id
                else:
                    supplier = self.pool.get('res.users').browse(cr, uid, uid)
                
                buy_uid = self._getuid(cr, uid, buy_partner.id)
                
                partner = self.pool.get('res.partner').browse(cr, uid, supplier.company_id.partner_id.id)
                partner_id = partner.id
                address_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])['delivery']
                pricelist_id = partner.property_product_pricelist_purchase.id
                context = {}
                context.update({'lang':partner.lang, 'partner_id':partner_id})
                #company = self.pool.get('res.users').browse(cr, uid, buy_uid, context).company_id
                whid = self.pool.get('stock.warehouse').search(cr, uid, [('partner_address_id','=',address_id)])
                if not whid:
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
                #这里能否在当前销售订单的 客户参考: 字段记录一下此so对应的客户po号？        
    
#    def _partner_change_u_line(self, cr, uid, saleorder, context=None):
#        """"partner改变时，更新订单明细价格"""
#        for line in saleorder.order_line:
#            r_v = self.pool.get('sale.order.line').product_id_change(cr, uid, [line.id],
#                vals.get('pricelist_id', o.pricelist_id.id), line.product_id.id, qty=line.product_uom_qty,
#                partner_id=vals['partner_id'],
#                packaging=line.product_packaging.id, fiscal_position=True
#            )
#            self.pool.get('sale.order.line').write(cr, uid, line.id, r_v['value'], context=context)        

    def _partner_change_u_line(self, cr, uid, vals, saleorder, context=None):
        """partner改变时，更新订单明细价格"""
        for line in saleorder.order_line:
            r_v = self.pool.get('sale.order.line').product_id_change(cr, uid, [line.id],
                vals.get('pricelist_id', saleorder.pricelist_id.id), line.product_id.id, qty=line.product_uom_qty,
                partner_id=vals['partner_id'],
                packaging=line.product_packaging.id, fiscal_position=True
            )
            self.pool.get('sale.order.line').write(cr, uid, line.id, r_v['value'], context=context)        
    
    def _create_order_to_buypartner(self, cr, uid, vals, o, context=None):
        """为buy_partner创健一个临时订单,
        参数:
        vals=sale_order更新的内容
        o=要复制的sale_order，
        """
        #取要新建的order数据
        new_data = self.copy_data(cr, uid, o.id, default=None, context=context)[0]
        if new_data.has_key('name'):
            del new_data['name']
        
        #更新new_data
        res = 0 
        new_uid_l = self._getuidlist(cr, uid, vals['partner_id'], context=context)
        if new_uid_l:
            new_uid = self._getuid(cr, uid, vals['partner_id'], context=context)
            #('createpurchase','=',False)防止进入死循环， order='create_date desc':按创建日期降序
            partnet_id_list = self.pool.get('res.partner').search(cr, new_uid, [('createpurchase','=',False),('create_uid','in',new_uid_l)], order='create_date desc')
            if not partnet_id_list:
                #业务伙伴不存在客户，引发异常,终于有机会用到翻译了.
                raise osv.except_osv(_('Error !'), _('Partners do not exist.'))
            user_obj = self.pool.get('res.users').browse(cr, new_uid, new_uid, context=context)
            #取最新的partner
            partner = self.pool.get('res.partner').browse(cr, new_uid, partnet_id_list[0], context=context)
            partner_id = partner.id
            #联系人
            partner_order_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['contact'])['contact']
            #发票地址
            partner_invoice_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['invoice'])['invoice']
            #送货地址
            partner_shipping_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id
            #shop是否也得改?
            shop_id = self.pool.get('sale.shop').search(cr, new_uid, [('warehouse_id.company_id.id','=',partner.company_id.id)])
            update_vals = {
                'user_id':new_uid,
                'partner_id':partner_id,
                'partner_order_id':partner_order_id,
                'partner_invoice_id':partner_invoice_id,
                'partner_shipping_id':partner_shipping_id,
                'shop_id':shop_id[0]
                
            }                        
            new_data.update(update_vals)
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, '175_new_data:%s'%new_data)
            res = self.create(cr, new_uid, new_data, context)#创建副本
            #end if new_uid_l                    
        return res
        
    def _update_order_to_buypartner(self, cr, uid, vals, o, context=None):
        """为buy_partner更新订单主单,
        参数:
        vals=sale_order更新的内容
        o=要复制的sale_order，
        """
        new_uid_l = self._getuidlist(cr, uid, vals['partner_id'], context=context)
        if new_uid_l:
            new_uid = self._getuid(cr, uid, vals['partner_id'], context=context)
            #('createpurchase','=',False)防止进入死循环， order='create_date desc':按创建日期降序
            partnet_id_list = self.pool.get('res.partner').search(cr, new_uid, [('createpurchase','=',False),('create_uid','in',new_uid_l)], order='create_date desc')
            if not partnet_id_list:
                raise osv.except_osv(_('Error !'), _('Partners do not exist.'))            
            user_obj = self.pool.get('res.users').browse(cr, new_uid, new_uid, context=context)
            #取最新的partner
            partner = self.pool.get('res.partner').browse(cr, new_uid, partnet_id_list[0], context=context)
            partner_id = partner.id
            #联系人
            partner_order_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['contact'])['contact']
            #发票地址
            partner_invoice_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['invoice'])['invoice']
            #送货地址
            partner_shipping_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id
            #shop是否也得改?
            shop_id = self.pool.get('sale.shop').search(cr, new_uid, [('warehouse_id.company_id.id','=',partner.company_id.id)])
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'shop_id:%s partner:%s'%(shop_id,partner))
            update_vals = {
                'user_id':new_uid,
                'partner_id':partner_id,
                'partner_order_id':partner_order_id,
                'partner_invoice_id':partner_invoice_id,
                'partner_shipping_id':partner_shipping_id,
                'shop_id':shop_id[0]
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
            self.write(cr, new_uid, [o.related_id], new_vals, context=new_context)        


    def _update_orderline_to_buypartner(self, cr, uid, orderid, o, context=None):        
        """创建副本明细，先删除明细，再添加"""
        del_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',orderid)])
        self.pool.get('sale.order.line').unlink(cr, uid, del_ids)
        new_uid = self._getuid(cr, uid, o.partner_id.id, context=context)
        for o_line in o.order_line:
            #结构说明:1=(0=添加,1=更新,2=删除),5=orderid         'order_line': [(1, 5, {'product_id': 16 ...})]:
            lines = {
                'order_id': orderid,
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
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, '---259---')
            self.pool.get('sale.order.line').create(cr, new_uid, lines, context)       
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, '---261---')            

            
    def write(self, cr, uid, ids, vals, context=None):
        #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'vals:%s'%vals)
        if context.get('only_update_p',False):
            return super(sale_order, self).write(cr, uid,  ids, vals, context=context)  
            #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'vals:%s'%s)
        
        for o in self.browse(cr, uid, ids, context=context):
            runflag = False        
            if o.state=='draft':
                if not o.related_id:#1. 原order.related_id为空
                    if not ('partner_id' in vals):#1.1 无业务伙伴更新
                        res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                        runflag = True
                    #end if not ('partner_id' in vals)
                    else:
                        #如果partner更新,则更新明细价格
                        self._partner_change_u_line(cr, uid, vals, o, context=context)

                        buy_partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
                        if buy_partner and (not buy_partner.createpurchase):#1.2 新业务伙伴不需auto create
                            res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                            runflag = True
                        else:#1.3 新业务伙伴需auto create 
                            new_id = self._create_order_to_buypartner(cr, uid, vals, o, context=None)
                            if new_id:
                                new_vals = vals.copy()
                                new_vals.update({'related_id':new_id})
                                #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'newI_id:%s o.id:%s new_vals:%s'%(new_id,o.id,new_vals))
                                #如果在创建之前执行，会出现已被更新提示
                                #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, '---291---')
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
                                self.write(cr, 1, [new_id], new_vals, context=new_context)
                                #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, '---321---')
                                #如果存在明细修改
                                if 'order_line' in vals:
                                    self._update_orderline_to_buypartner(cr, 1, new_id, o, context=context)
                                #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, '---325---')
                        #end else if buy_partner and (not buy_partner.createpurchase)
                    #end else if not ('partner_id' in vals):#1.1 无业务伙伴更新
                #end if not o.related_id
                else:#2. 原order.related_id不为空
                    if not ('partner_id' in vals):#2.1 无业务伙伴更新
                        res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                        runflag = True
                        #副本主表内容不用更新?
                        
                        #如果存在明细修改
                        if 'order_line' in vals:
                            _update_orderline_to_buypartner(cr, uid, o.related_id, o, context=context)
                        
                    #end if not ('partner_id' in vals):#2.1 无业务伙伴更新
                    else:
                        #如果partner更新,则更新明细价格
                        self._partner_change_u_line(cr, uid, vals, o, context=context)
                        buy_partner = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'], context=context)
                        if buy_partner and (not buy_partner.createpurchase):#2.2 新业务伙伴不需auto create
                            #如果新的伙伴不需要自动创建order则删除关联订单
                            self.pool.get('sale.order').unlink(cr, uid, [o.related_id])
                            vals.update({'related_id':None})
                            res = super(sale_order, self).write(cr, uid,  o.id, vals, context=context)                            
                            runflag = True
                        else:#3.3 新业务伙伴需auto create 
                            res = super(sale_order, self).write(cr, uid, o.id, vals, context=context)  
                            runflag = True
                            _update_order_to_buypartner(cr, uid, vals, o, context=None)                            
                            #如果存在明细修改
                            if 'order_line' in vals:
                                _update_orderline_to_buypartner(cr, uid, o.related_id, o, context=context)                         

                                #end else if buy_partner and (not buy_partner.createpurchase)    
                    #end else if not ('partner_id' in vals):#2.1 无业务伙伴更新
                #end else if not o.related_id
            #end if o.state=='draft':
            
            if not runflag:
                #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, '---366---')
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
                #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'new_uid_l:%s'%new_uid_l)
                if new_uid_l:
                    new_uid = self._getuid(cr, uid, vals['partner_id'], context=context)
                    #('createpurchase','=',False)防止进入死循环， order='create_date desc':按创建日期降序
                    partnet_id_list = self.pool.get('res.partner').search(cr, new_uid, [('createpurchase','=',False)], order='create_date desc')
                    #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'partnet_id_list:%s'%partnet_id_list)
                    user_obj = self.pool.get('res.users').browse(cr, new_uid, new_uid, context=context)
                    #取最新的partner
                    partner = self.pool.get('res.partner').browse(cr, new_uid, partnet_id_list[0], context=context)
                    partner_id = partner.id
                    #联系人
                    partner_order_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['contact'])['contact']
                    #发票地址
                    partner_invoice_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['invoice'])['invoice']
                    #送货地址
                    partner_shipping_id = self.pool.get('res.partner').address_get(cr, new_uid, [partner_id], ['delivery'])['delivery']
                    pricelist_id = partner.property_product_pricelist_purchase.id
                    #shop是否也得改?
                    shop_id = self.pool.get('sale.shop').search(cr, new_uid, [('warehouse_id.company_id.id','=',partner.company_id.id)])
                    #self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_INFO, 'shop_id:%s partner:%s'%(shop_id,partner))
                    update_vals = {
                        'user_id':new_uid,
                        'partner_id':partner_id,
                        'partner_order_id':partner_order_id,
                        'partner_invoice_id':partner_invoice_id,
                        'partner_shipping_id':partner_shipping_id,
                        'shop_id':shop_id[0],
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
