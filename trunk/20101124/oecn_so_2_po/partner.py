# -*- encoding: utf-8 -*-
##############################################################################
#
#    Created on 2010-11-24
#    @author: stbrine@yahoo.com.cn
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'
    _columns = {
        'createpurchase': fields.boolean('Auto Purchase Order', help="Create purchase of sale order Confirmation"),
    }    
res_partner()
