from osv import osv, fields
from urllib2 import Request, urlopen
import base64
import re
class product_template_img(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'
    _description = 'Product Extra Image'

    def is_url(self, url):
        regexStr = '^((https|http|ftp|rtsp|mms)?://)+'
        regex = re.compile(regexStr)
        print regex.match(url)
        return regex.match(url)
        
    def _get_image(self, cursor, user, ids, name, arg, context=None):
        image = {}
        res = self.read(cursor, user, ids, ['image_link'])
        image_link = res[0]['image_link']
        if image_link:
            if not self.is_url(image_link):
                raise osv.except_osv('URL Error','URL should start with https|http|ftp|rtsp|mms.')
            req = Request(image_link)
            try:
                respose = urlopen(req)
            except IOError, e:
                if hasattr(e, 'reason'):
                    raise osv.except_osv('URL Error','We failed to reach a server.' + 'Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    raise osv.except_osv('URL Error','The server couldn\'t fulfill the request.\n' + 'Error code: ', e.code)
            pic = base64.encodestring(respose.read())
            for id in ids:
                image[id] = pic
        return image

    _columns = {
        'image_link' : fields.char('Image Link', size=180),
        'image' : fields.function(_get_image, method=True, string='Product Image', type='binary', store=False), 
    }

product_template_img()