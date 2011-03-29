# -*- encoding: utf-8 -*-

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


def _get_author_address(uid, data, state):
    return 'http://auth.open.taobao.com/?appkey='+data['form']['app_key']


#--第一屏：输入key和secret
_appkey_form = '''<?xml version="1.0"?>
<form string="淘宝app key和app secret">
    <field name="app_key"  colspan="4"/>
    <field name="app_secret"  colspan="4"/>
</form>'''
_appkey_fields = {
    'app_key': {'string':'淘宝App Key', 'type':'char', 'size':128,'required':True, 
        'default': lambda *a:"12136311"},
    'app_secret': {'string':'淘宝App Secret', 'type':'char', 'size':128,'required':True, 
        'default': lambda *a:"9489e242771aa3b63df71d8f5372ff66"},
}

#--第二屏：取得授权码
_synchronize_form = '''<?xml version="1.0"?>
<form string="淘宝产品同步">
    <label string="1. 登录取得授权码：" colspan="4" />
    <field name="auther_address" nolabel="1" readonly="1" colspan="4" widget='url'/>
    <label string="2. 填入授权码：" colspan="4" />
    <field name="auther_code" nolabel="1" colspan="4"/>
    <field name="force_upload" colspan="4"/>
</form>'''

_synchronize_fields = {
    'force_upload':{'string':'不检查图片和库存，无条件上传', 'type':'boolean'},
    'auther_address': {'string':'授权码地址', 'type':'char', 'size':128,'required':True, 
        'default': _get_author_address},
    'auther_code': {'string':'授权码', 'type':'char',  'size':128, 'required':True},
}

#--第三屏：执行结果提示
_success_form = '''<?xml version="1.0"?>
<form string="完成">
    <label string="工作完成。请查看log文件。" colspan="4" />
</form>'''

_fail_form = '''<?xml version="1.0"?>
<form string="失败">
    <label string="同步出错。" colspan="4" />
</form>'''

_success_fields ={}
_fail_fields ={}


def _product_synchronize(self, cr, uid, data, context):

    #签名函数
    def _sign(param,sercetCode):
        src = sercetCode + ''.join(["%s%s" % (k, v) for k, v in sorted(param.items())])
        return md5.new(src).hexdigest().upper()
    
    
    
    debugmode = True  #调试动态
    if debugmode: #调试输出
        saveout = sys.stdout
        fsock = open('my_openrp_log.txt','w')
        sys.stdout = fsock
        print '-------------测试输出-------------'
        print  time.localtime()
        print '----------------------------------'
        print data['form']['auther_code']
        print '---context---'
        print context
        print '---data---'
        print data
        print '---self---'
        print self
        print '---cr---'
        print cr
        
    #取得session key
    urlopen = urllib2.urlopen('http://container.open.taobao.com/container?authcode=' + data['form']['auther_code'])
    rsp = urlopen.read();
    start_pos = rsp.find('&top_session=')
    end_pos = rsp.find('&top_sign=')
    if start_pos==-1 or end_pos==-1:
        obj = pooler.get_pool(cr.dbname).get('product.product')
        res = obj.read(cr, uid, data['ids'], \
             [ \
             'id',\
             'default_code',\
             'product_tmpl_id', \
             'tb_online',\
             'tb_onshelf',\
             'tb_itemid',\
             'tb_dimension',\
             'tb_material',\
             'tb_description',\
             'tb_synchronized',\
             'tb_description_template',\
             'virtual_available'\
             ], \
             context )
         
        print '---ids---'
        print data['ids']
        print '---res---'
        print res
        if debugmode: #调试输出
            print '========================='
            print '获取session key出错'
            print '========================='
            sys.stdout=saveout
            fsock.close()
        return 'fail'
    session_key = rsp[start_pos+13:end_pos]
    
    #获得当前时间
    t = time.localtime()
    tb_time_str = str(t[0])+'-'+str(t[1]).rjust(2,'0')+'-'+str(t[2]).rjust(2,'0')+' '+str(t[3]).rjust(2,'0')+':'+str(t[4]).rjust(2,'0')+':'+str(t[5]).rjust(2,'0')

    #取得数据库记录
    obj = pooler.get_pool(cr.dbname).get('product.product')
    res = obj.read(cr, uid, data['ids'], \
        [ \
        'id',\
        'default_code',\
        'product_tmpl_id', \
        'tb_picture',\
        'tb_online',\
        'tb_onshelf',\
        'tb_itemid',\
        'tb_dimension',\
        'tb_material',\
        'tb_description',\
        'tb_synchronized',\
        'tb_description_template',\
        'virtual_available'\
        ], \
        context )
    
    #读取所有的产品
    upload_counter=0
    for rec in res:
        amount = str(int(rec['virtual_available']))
        
        if not data['form']['force_upload']:
            #如果没有图片，跳过
            if not rec['tb_picture']:
                continue
            #数量
            if amount <= '0':
                continue
            
        
        upload_counter=upload_counter+1
        
        #读product_template
        obj_template = pooler.get_pool(cr.dbname).get('product.template')
        res_template = obj_template.read(cr, uid, [rec['product_tmpl_id'][0]], ['list_price','name'],context)
        rec_template = res_template[0]
        
        #读product_description_template
        obj_description = pooler.get_pool(cr.dbname).get('product.description.template')
        res_description = obj_description.read(cr, uid, [rec['tb_description_template'][0]], ['template'],context)
        rec_description = res_description[0]
        
        #读product_picture_url
        obj_url = pooler.get_pool(cr.dbname).get('product.picture.url')
        ids_url = obj_url.search(cr, uid, [('product_id','=',rec['id'])])
        res_url = obj_url.read(cr, uid, ids_url, ['picture_url'],context)
        
        print "图片地址：" 
        print res_url
        
        #图片
        if not rec['tb_picture']:
            pic = ''
        else:
            pic = base64.decodestring(rec['tb_picture'])
        #数量
        if amount<='0':
            amount = '999'
        #标价
        price = str(rec_template['list_price'])
        #标题
        title = rec_template['name'].encode('utf8')
        #描述
        description = rec_description['template'].encode('utf8')
        description = description.replace('[SS-标题]',rec_template['name'].encode('utf8'))
        description = description.replace('[SS-货号]',rec['default_code'].encode('utf8'))
        if rec['tb_dimension']:
            description = description.replace('[SS-规格]',rec['tb_dimension'].encode('utf8'))
        else:
            description = description.replace('[SS-规格]','')
        if rec['tb_material']:
            description = description.replace('[SS-材质]',rec['tb_material'].encode('utf8'))        
        else:
            description = description.replace('[SS-材质]','')        
        if rec['tb_description']:
            description = description.replace('[SS-描述]',rec['tb_description'].encode('utf8'))
        else:
            description = description.replace('[SS-描述]','')
        picture_urls =''
        for rec_url in res_url:
            if rec_url['picture_url']:
                picture_urls = picture_urls+'<img src="'+rec_url['picture_url'].encode('utf8')+'" alt="细节图片" /><br><br>'
        description = description.replace('[SS-图片]',picture_urls)
        #产品编码
        code = rec['default_code'].encode('utf8')
        
        print '[',code,']', title
        
        
        #
        #判断产品是否存在
        #
        
        #参数数组
        param_array_get={
            'session': session_key,
            'app_key':data['form']['app_key'],
            'method':'taobao.items.custom.get',
            'format':'xml',
            'v':'2.0',
            'timestamp':tb_time_str,
            'outer_id':code,
            'fields':'outer_id, num_iid',
        }
        #生成签名
        sign = _sign(param_array_get, data['form']['app_secret']);
        param_array_get['sign'] = sign
        #组装参数
        form_data = urllib.urlencode(param_array_get)
        #访问服务
        urlopen = urllib2.urlopen('http://gw.api.taobao.com/router/rest', form_data)
        rsp = urlopen.read();
        #xml解码
        xmldoc = minidom.parseString(rsp)
        node_error_response = xmldoc.getElementsByTagName('error_response')
        if node_error_response:
            node_error_code = node_error_response[0].getElementsByTagName('code')[0]
            node_error_msg = node_error_response[0].getElementsByTagName('msg')[0]
            print '---上传失败---'
            print '错误代码:',node_error_code.firstChild.data
            print '错误信息:',node_error_msg.firstChild.data
            sys.stdout=saveout
            fsock.close()
            return 'fail'
                
        node_item_rsponse = xmldoc.getElementsByTagName('items_custom_get_response')
        node_num_iid = xmldoc.getElementsByTagName('num_iid')
        
        if node_num_iid:
            #
            #产品存在，更新产品资料
            #
            
            #参数数组
            paramArray = {
                'session': session_key,
                'app_key':data['form']['app_key'],
                'method':'taobao.item.update',
                'format':'xml',
                'v':'2.0',
                'timestamp':tb_time_str,
                'num_iid':node_num_iid[0].firstChild.data.encode('utf8'),
                'num':amount,
                'price':price,
                'title':title,
                'desc':description,
                'auto_repost':'true',
                'outer_id':code
            }
            #生成签名
            sign = _sign(paramArray, data['form']['app_secret']);
            paramArray['sign'] = sign
            paramArray['image'] = ('image.jpg', pic)
            #上传
            API_URL = 'http://gw.api.taobao.com/router/rest'
            http_pool = urllib3.connection_from_url(API_URL)
            r = http_pool.post_url(API_URL, paramArray)
            
            xmldoc = minidom.parseString(r.data)
            node_error_response = None
            node_error_response = xmldoc.getElementsByTagName('error_response')
            if node_error_response:
                node_error_code = node_error_response[0].getElementsByTagName('code')[0]
                node_error_msg = node_error_response[0].getElementsByTagName('msg')[0]
                node_error_subcode = node_error_response[0].getElementsByTagName('sub_code')[0]
                node_error_submsg = node_error_response[0].getElementsByTagName('sub_msg')[0]
                print '------更新出错:',node_error_code.firstChild.data, ' ', node_error_msg.firstChild.data
                print '               ', node_error_subcode.firstChild.data.encode('utf8'), ' ', node_error_submsg.firstChild.data.encode('utf8')
                
            else:
                print '------更新成功!'
            
        else:
            #
            #产品不存在，增加新产品
            #
        
            #参数数组
            paramArray = {
                'session': session_key,
                'app_key':data['form']['app_key'],
                'method':'taobao.item.add',
                'format':'xml',
                'v':'2.0',
                'timestamp':tb_time_str,
                'num':amount,
                'price':price,
                'type':'fixed',
                'stuff_status':'new',
                'title':title,
                'desc':description,
                'location.state':'云南',
                'location.city':'昆明',
                'approve_status':'onsale',
                'cid':'50022006',   #泰国特色手工艺
                'props':'20380:113325;',
                'valid_thru':'7',
                'auto_repost':'true',
                'outer_id':code
            }
            #生成签名
            sign = _sign(paramArray,data['form']['app_secret']);
            paramArray['sign'] = sign
            paramArray['image'] = ('image.jpg', pic)
            #上传
            API_URL = 'http://gw.api.taobao.com/router/rest'
            http_pool = urllib3.connection_from_url(API_URL)
            r = http_pool.post_url(API_URL, paramArray)
    
            xmldoc = minidom.parseString(r.data)
            node_error_response = None
            node_error_response = xmldoc.getElementsByTagName('error_response')
            if node_error_response:
                node_error_code = node_error_response[0].getElementsByTagName('code')[0]
                node_error_msg = node_error_response[0].getElementsByTagName('msg')[0]
                #node_error_subcode = node_error_response[0].getElementsByTagName('sub_code')[0]
                #node_error_submsg = node_error_response[0].getElementsByTagName('sub_msg')[0]
                
                print '------新增出错:', node_error_code.firstChild.data, ' ', node_error_msg.firstChild.data
                #print '               ', node_error_subcode.firstChild.data.encode('utf8'), ' ', node_error_submsg.firstChild.data.encode('utf8')
            else:
                print '------新增成功!'

    if debugmode: #调试输出
        print '============================================'
        print '总共上传产品：',upload_counter,'个'
        print '============================================'
        sys.stdout=saveout
        fsock.close()
    return 'success'



    

class taobao_product_synchronize(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_appkey_form, 'fields':_appkey_fields, 'state':[('end','取消'),('author','确定')]}
            },
        'author': {
            'actions': [],
            'result': {'type': 'form', 'arch':_synchronize_form, 'fields':_synchronize_fields, 'state':[('end','取消'),('synchronize','同步')]}
            },
        'synchronize': {
            'actions': [],
            'result': {'type':'choice', 'next_state':_product_synchronize}
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
            
taobao_product_synchronize('taobao.product.synchronize')


