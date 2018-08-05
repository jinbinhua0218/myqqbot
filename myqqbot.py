# -*- coding: utf-8 -*-

#https://blog.csdn.net/hello_world_zhou/article/details/54782980

import requests,random,os,time
import logging; logging.basicConfig(level=logging.INFO)

from io import BytesIO
from PIL import Image

def create_default_path():
    #创建图片文件夹
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'pic')
    if not os.path.exists(path):
        os.mkdir(path)
        logging.info('[New] Create file folder %s' %path)
    else:
        logging.info('[Old] Already exists file folder %s' %path)
    return path

#设置默认路径
path = create_default_path()

#获得登录的二维码 保存到默认文件里。水平不够，见谅
def getQrcode():
    
    global Qrsession
    Qrsession = requests.Session()
    Qrsession.headers.update({
        'User-Agent':('Mozilla/5.0 (Macintosh;Intel Mac OS X 10.9;'
                      ' rv:27.0) Gecko/20100101 Firefox/27.0'),
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
    })

    Qrurl = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&' + \
          's=5&d=72&v=4&t='+ repr(random.random())
    
          
    Qrcontent = Qrsession.get(Qrurl,timeout=30).content
    filename = os.path.join(path,'erweima.jpg')
    with open(filename,'wb') as f:
        f.write(Qrcontent)
    logging.info('It has download QR pic')
    

    im = Image.open(BytesIO(Qrcontent))
    #im.show()
    logging.info('已获取二维码')

getQrcode()


def getAuthStatus():


    p =     'https://ssl.ptlogin2.qq.com/ptqrlogin?ptqrtoken=1178303247' +  \
            '&webqq_type=10&remember_uin=1&login2qq=1&aid=501004106' + \
            '&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26' + \
            'webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&' + \
            'from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-' + \
            repr(random.random() * 900000 + 1000000) + \
            '&mibao_css=m_webqq&t=undefined&g=1&js_type=0' + \
            '&js_ver=10141&login_sig=&pt_randsalt=0'

    

    ASurl = 'https://ssl.ptlogin2.qq.com/ptqrlogin?ptqrtoken=1178303247' + \
            '&webqq_type=10&remember_uin=1&login2qq=1&aid=501004106' + \
            '&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26' + \
            'webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&' +  \
            'from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-' + \
            repr(random.random() *900000+1000000) + \
            '&mibao_css=m_webqq&t=undefined&g=1&js_type=0'+ \
            'js_ver =10141&login_sig=&pt_randsalt=0'
    
    print(p==ASurl)
    
    Referer =('https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&'
            'target=self&style=16&mibao_css=m_webqq&appid=501004106&'
            'enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2F'
            'w.qq.com%2Fproxy.html&f_url=loginerroralert&'
            'strong_login=1&login_state=10&t=20131024001')
    Referer and Qrsession.headers.update({'Referer':Referer})
    
    result = Qrsession.get(ASurl,timeout=30).content.decode('utf-8')
    print(result)
    

def waitForAuth():
    
    time.sleep(1)
    authStatus = getAuthStatus()
    return authStatus

waitForAuth()
        

    















































