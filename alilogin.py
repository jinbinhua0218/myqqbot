# -*- coding: utf-8 -*-

import logging; logging.basicConfig(level=logging.INFO)
import os,sys,time
from io import BytesIO
import random
import datetime
import json
import re

import requests
from PIL import Image

class ali_Login:

    def __init__(self):
        pass

    def Login(self):
        self.prepareLogin()
        self.getQrcode()
        self.waitForAuth()
        self.get_taoke_order_list()

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
        self.session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
           
        })




        result =self.session.get('https://pub.alimama.com')
        try:
            result = result.content
            print('初步尝试链接成功')
        except Exception:
            print('It is failed')
            
        self.session.headers.update({
            'Content-Type':'application/javascript'})
        result2 = self.session.get(
            url = 'https://g.alicdn.com/mm/tanx-cdn/t/tanxssp.js?v=2%20HTTP/1.1')
        #print(result2.status_code)
        #print(result2.cookies)

    def getAuthStatus(self):
        ksTS_time = time.time()
        _ksTS='%s_%s' %(int(ksTS_time*1000),str(ksTS_time)[-3:])
        callback='jsonp%s' %(int(str(ksTS_time)[-3:])+1)
        #print(_ksTS,callback)
            
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

        #获取随机umid_token
        date = ''.join(str(time.time()).split('.'))[0:13]

        r_11 = ''.join(str(random.random()).split('.'))[1:12]

        r_3 =  ''.join(str(random.random()).split('.'))[-3:]

        umid_token = 'C' + date + r_11 + date + r_3
        print(umid_token)

        #找不到好的数据传递方式，先这么用
        self.umid_token = umid_token
        
        logging.info('获取二维码')
        result = self.session.get('https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do'
                                  '?from=alimama&appkey=00000000&umid_token=' + str(umid_token)
                                  ).json()
        #print(result)
        
        #获取lgToken、adToken、二维码的url
        self.lgToken = result['lgToken']
        self.adToken = result['adToken']
        qr_url = 'https:'+result['url']

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
                '''for item in items:
                    print(item)'''
                lg_url = items[-1].split('"')[3]
                break
            else:
                logging.info('未知错误，退出执行')
                sys.exit(0)
                
        #登录成功后操作
        lg_url = lg_url + '&umid_token=' + str(self.umid_token)   
        result = self.session.get(url=lg_url)


    #获取淘客订单列表
    def get_taoke_order_list(self):
        logging.info('获取淘客订单')
        print(type(self.session.cookies))
        '''for k,v in self.session.cookies.items():
            print(k,v)'''

        re_tb_token = re.compile(r'(<Cookie _tb_token_=)(.+?)( for .alimama.com/>)')
        self._tb_token_ = re.findall(re_tb_token,str(self.session.cookies))[0][1]
        print(self._tb_token_)
        
        s_day = datetime.date.today() - datetime.timedelta(days=90)
        e_day = datetime.date.today() - datetime.timedelta(days=1)
        t = ''.join(str(time.time()).split('.'))[0:13]
        
        url = 'http://pub.alimama.com/report/getTbkPaymentDetails.json?startTime=' + s_day.strftime(
                "%Y-%m-%d") + '&endTime=' + e_day.strftime(
                "%Y-%m-%d") + '&payStatus=&queryType=1&toPage=1&perPageSize=20' \
                '&total=&t='+ str(t) + '&pvid=&_tb_token_=' + str(self._tb_token_) + '&_input_charset=utf-8'
        print(url)
        
        '''web_data = self.session.get(url)
        data = json.loads(web_data.text)'''

        result = self.session.get(url).json()
        data = result['data']['paymentList']

        '''for i in range(len(data)):
            for k,v in data[i].items():
                print('序号'+str(i)+'-----> ',k,'>>>>>',v)
            print('----------------------------------------------------')'''

        return data


    #转换链接获取口令
    def get_goods_list(self):
        logging.info('开始转换口令............................')

        siteid   = '125900089'
        adzoneid = '30875200022'

        t = ''.join(str(time.time()).split('.'))[0:13]

        url = 'http://pub.alimama.com/urltrans/urltrans.json?_input_charset=utf-8'\
              '&promotionURL=https://item.taobao.com/item.htm?id=559103665936' \
              '&siteid=' + siteid +'&adzoneid='+adzoneid+ '&t=' + t + '&_tb_token_=' + self._tb_token_

        '''proxies = {
            'http': 'http://10.10.1.10:80'
        }'''
        time.sleep(2)
     
        print('url',url)
        result = self.session.get(url)
        
        print(result.json())
        print('22222222222222222222222')
        print(result.text)
        
                             
if __name__ == '__main__':
    ali = ali_Login()
    ali.Login()
    ali.get_goods_list()







































    
    
