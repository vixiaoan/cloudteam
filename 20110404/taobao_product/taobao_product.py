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
import netsvc
from osv import fields, osv
	
class taobao_description_template(osv.osv):
	_name='product.description.template'
	_description='淘宝说明模板'
	_columns={
		'name': fields.char('模板名',size=128,required=True),
		'template':fields.text('模板',required=True),
	}
	_sql_constraints = [('unique_description_template_name', 'unique(name)', '模板名不能重复。')]
taobao_description_template()


class taobao_product(osv.osv):
	_inherit = "product.product"
	_columns = {
		'default_code' : fields.char('Code', size=64, required=True),
		'tb_picture':    	fields.binary('图片'),
		'tb_dimension':    fields.char('规格尺寸', size=100),
		'tb_material':     fields.char('材质', size=100),
		'tb_itemid':   fields.char('淘宝产品ID', size=100),
		'tb_description':  fields.text('产品描述'),
		'tb_online':       fields.boolean('上线'),
		'tb_onshelf':      fields.boolean('上架'),
		'tb_synchronized': fields.boolean('已同步'),
		'tb_picture_urls': fields.one2many('product.picture.url', 'product_id', '图片地址'),
		'tb_description_template':fields.many2one('product.description.template','描述模板',required=True),
		'tb_instock':      fields.boolean('有货')
	}
        _sql_constraints = [('default_code_key', 'unique(default_code)', '产品编码必须是唯一的。')]
        
taobao_product()


class taobao_picture_url(osv.osv):
	_name = 'product.picture.url'
	_description = '淘宝图片地址'

	_columns = {
                'product_id': fields.many2one('product.product', '产品ID', select=1, ondelete='cascade', required=True),
		'picture_url': fields.char('图片地址', size=200),
		}
taobao_picture_url()

