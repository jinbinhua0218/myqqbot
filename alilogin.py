# -*- coding: utf-8 -*-

import logging; logging.basicConfig(level=logging.INFO)
import os,sys,time
from io import BytesIO

import requests
from PIL import Image

class ali_Login:

    def __init__(self):
        pass

    def Login(self):
        self.prepareLogin()
        self.getQrcode()

    def prepareLogin(self):

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent':('Mozilla/5.0 (Macintosh;Intel Mac OS X 10.9;'
                          ' rv:27.0) Gecko/20100101 Firefox/27.0'),
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
        })

        result =self.session.get('https://pub.alimama.com')
        try:
            result = result.content
            print(self.session.cookies)
        except Exception:
            print('It is failed')

    def getQrcode(self):
        logging.info('获取二维码')
        '''qrcode = self.session.get('https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do?'
                                  'from=alimama&appkey=00000000'
                                  '&umid_token=C1535877302705343818768411535897741046165'
                                  '&_ksTS=1535897741510_46&callback=jsonp47').content'''
        qrcode = self.session.get('https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do?'
                                  'from=alimama&appkey=00000000'
                                  '&umid_token=C1535877302705343818768411535897741046165'
                                  '&_ksTS=1535897741507_28&callback=jsonp29').content
                                  
        qrcode = qrcode.decode('utf-8')
        print(type(qrcode))
        print(qrcode)


        
        self.im = Image.open(BytesIO(qrcode))
        self.im.show()
                                  

if __name__ == '__main__':
    ali = ali_Login()
    ali.Login()











    
    
