# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution   
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import pooler
import netsvc
import re

import time


  

def make_update(obj, cr, uid, data, context=None):
    ''''''
    pool = pooler.get_pool(cr.dbname)
    m=pool.get('hr.department').read(cr, uid, data['id'],['member_ids'], context)

    for user_id in m['member_ids']:

 
        change_id = pool.get('res.users').write(cr, uid,user_id, {'department_id':data['id']}, context=context)

    

    return {
         }


class Makeupdatelist(wizard.interface):
    '''Wizard that update the department to user '''

    done_form = """<?xml version="1.0"?>
<form string="UPdate">
    <label string="DONE !"/>
</form>"""
    update_form = """<?xml version="1.0"?>
<form string="update">
  <label string="this wizard help you update the department inf to the user form,just press the update button!"/>
 </form>"""
    update_fields = {
       
       
    }

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': update_form, 'fields': update_fields,
                'state': [
                    ('end', 'Cancel'),


                    ('create', 'update')
                ]
            }
        },
        'done': {
            'actions': [],
            'result': {'type': 'form', 'arch': done_form, 'fields': {},
                'state': [
                    ('end', 'Close'),
                ]
            }
        },
        'create': {
            'actions': [],
            'result': {'type': 'action', 'action': make_update, 'state': 'done'}
        }
    }

Makeupdatelist('hr.updatetouser')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

