# -*- encoding: utf-8 -*-

import os
import shutil


import base64
import struct
import urllib
import urllib2
import urllib3
import string
import time
import md5
import re
import types
import logging
import sys
from xml.dom import minidom


import wizard
from tools.translate import _
from osv import fields, osv
import pooler

#--第一屏：显示选项，准备开始
_output_form = '''<?xml version="1.0"?>
<form string="导出产品清单">
    <field name="include_zero" colspan="4"/>
    <field name="include_nopic" colspan="4"/>
    <field name="sort_by_cate" colspan="4"/>
</form>'''

_output_form_fields = {
    'include_zero': {'string':'包括无库存', 'type':'boolean',
        'default': lambda *a:False},
    'include_nopic': {'string':'包括无图', 'type':'boolean',
        'default': lambda *a:False},
    'sort_by_cate': {'string':'按产品分类归类', 'type':'boolean',
        'default': lambda *a:False},    
    }

#--第二屏：执行结果提示
_success_form = '''<?xml version="1.0"?>
<form string="完成">
    <label string="成功完成。" colspan="4" />
    <label string="输出文件保存在“公共文件夹\临时\产品列表.html”" colspan="4" />
</form>'''

_fail_form = '''<?xml version="1.0"?>
<form string="失败">
    <label string="对不起，出错了。" colspan="4" />
</form>'''

_success_fields ={}
_fail_fields ={}


def _output_product_list(self, cr, uid, data, context):
    
    if os.path.exists(u'D:\PUBLIC\临时\产品列表'):
        shutil.rmtree(u'D:\PUBLIC\临时\产品列表')

    os.mkdir(u'D:\PUBLIC\临时\产品列表') 
    saveout = sys.stdout
    fsock = open(u'D:\PUBLIC\临时\产品列表.html','w')
    sys.stdout = fsock

    print '''<html>

<head>
<meta http-equiv="Content-Language" content="zh-cn">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>暹艺工贸产品清单</title>
</head>

<body>

<p align="center"><font face="黑体" size="5">暹艺工贸有限公司产品清单</font></p>
<p align="center">输出日期：'''
    t=time.localtime()
    print time.strftime('%Y-%m-%d %X', t),"</p>"
    print '''<table border="0" width="1000" id="table1" cellpadding="0">  <tr>'''
    
    
    recs = pooler.get_pool(cr.dbname).get('product.product').browse(cr,uid,data['ids'])
    
    counter = 0
    no_pic_counter = 0
    no_stk_counter = 0
    for rec in recs:
        if (not data['form']['include_zero']) and rec.virtual_available<=0:
            continue
        if (not data['form']['include_nopic']) and not rec.tb_picture:
            continue
        
        counter = counter + 1
        if not rec.tb_picture:
            no_pic_counter = no_pic_counter + 1
        if rec.virtual_available<=0:
            no_stk_counter = no_stk_counter + 1
        
        
        #save pic file
        pic_name = rec.default_code+".jpg"
        pic_abslute_name = u"D:\PUBLIC\临时\产品列表\\" + pic_name
        pic_relative_name = u".\产品列表\\" + pic_name
        if rec['tb_picture']:
            fout = open(pic_abslute_name, "wb")
            fout.write(base64.decodestring(rec['tb_picture']))
            fout.close()
        
        print '<td>'
        print '<a target="_blank" href="' , pic_relative_name.encode('utf8') , '">'
        print '<img border="0" src="' , pic_relative_name.encode('utf8') , '" width="100" height="100"></a><br>'
        print "【编号】" + rec.default_code.encode('utf8') + "<br>"
        print "【名称】" , rec.product_tmpl_id.name.encode('utf8') , "<br>"
        if rec.tb_dimension:
            print "【尺寸】" , rec.tb_dimension.encode('utf8') , "<br>"
        print "【单位】" , rec.product_tmpl_id.uom_id.name.encode('utf8') , "<br>"
        print "【单价】" , str(rec.product_tmpl_id.list_price).encode('utf8') , "<br>"
        #print "【数量】" , str(rec.virtual_available).encode('utf8') , "<br><br>"
        print "</td>"
        
        if counter%5==0:
            print "</tr><tr>"
        
    print "</table></p>"
    print "共导出产品：",counter,"件<br>"
    print "无图产品：",no_pic_counter,"件<br>"
    #print "无库存产品：",no_stk_counter,"件<br>"


    sys.stdout=saveout
    fsock.close()

    return 'success'
    

class product_list(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_output_form, 'fields':_output_form_fields, 'state':[('end','取消'),('output','导出')]}
            },
        'output': {
            'action': [],
            'result': {'type':'choice', 'next_state':_output_product_list}
            },
        'success' : {
            'actions': [],
            'result': {'type': 'form', 'arch':_success_form, 'fields':_success_fields, 'state':[('end','关闭')]}
            },
        'fail':{
            'actions': [],
            'result': {'type': 'form', 'arch':_fail_form, 'fields':_fail_fields, 'state':[('end','关闭')]}
            }
        }
            
product_list('product.list')


