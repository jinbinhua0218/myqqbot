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
        self.waitForAuth()

    def prepareLogin(self):

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent':('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/68.0.3440.106 Safari/537.36'),
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer':'https://pub.alimama.com/',
            'Origin' :'https://pub.alimama.com'
        })

        result =self.session.get('https://pub.alimama.com')
        try:
            result = result.content
            print(self.session.cookies)
        except Exception:
            print('It is failed')

    def getAuthStatus(self):
        ksTS_time = time.time()
        _ksTS='%s_%s' %(int(ksTS_time*1000),str(ksTS_time)[-3:])
        callback='jsonp%s' %(int(str(ksTS_time)[-3:])+1)
        print(_ksTS,callback)
            
        result = self.session.get(
            url = 'https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?' +
            'lgToken='+str(self.lgToken) +
            '&defaulturl=http%3A%2F%2Fwww.alimama.com' +
            '&_ksTS=%s' %(_ksTS) +
            '&callback=%s' %(callback)
        ).content
        result = result.decode('utf-8')
        return result

    def getQrcode(self):
        logging.info('获取二维码')
        result = self.session.get('https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do'
                                  ).json()
        print(result)
        
        #获取lgToken、adToken、二维码的url
        self.lgToken = result['lgToken']
        self.adToken = result['adToken']
        qr_url = 'https:'+result['url']
        print('qr_url....', qr_url)
        
        qrcode = self.session.get(qr_url).content
        self.im = Image.open(BytesIO(qrcode))
        self.im.show()

    def waitForAuth(self):
        while True:
            time.sleep(5)
            authStatus = self.getAuthStatus()

            if '"code":"10000"' in authStatus:
                logging.info('请扫描二维码...')
            elif '"code":"10001"' in authStatus:
                logging.info('已扫描二维码,等待授权')
            elif '"code":"10004"' in authStatus:
                logging.info('二维码过期，请重新获取二维码')
                self.getQrcode()
                
            #扫描成功的支路
            elif '"code":"10006"'in authStatus:
                logging.info('登录成功，正在跳转')
                items = authStatus.split(',')          
                qr2_url = items[-1].split('"')[3]
                print('qr2.........',qr2_url)
                break
            else:
                logging.info('未知错误，退出执行')
                sys.exit(0)
                
        #登录成功后操作
        result = self.session.get(url=qr2_url)
        print('url ', result.url)
        print('cookies ', result.cookies)
        print(result.cookies.keys())

        print('headers ', result.headers)

                             
if __name__ == '__main__':
    ali = ali_Login()
    ali.Login()











    
    
