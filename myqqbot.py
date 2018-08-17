# -*- coding: utf-8 -*-

#https://blog.csdn.net/hello_world_zhou/article/details/54782980

import requests,random,os,time
import logging; logging.basicConfig(level=logging.INFO)
import json
import sys

from io import BytesIO
from PIL import Image

class QQBot:

    def __init__(self):
        pass

    def Login(self):
        self.prepareLogin()
        self.getQrcode()
        self.waitForAuth()
        self.getPtwebqq()
        self.getVfwebqq()
        self.getUinAndPsessionid()
        self.fetchBuddy()
        self.fetchGroup()
        self.fetchDiscuss()

    def prepareLogin(self):
        self.clientid = 53999199
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent':('Mozilla/5.0 (Macintosh;Intel Mac OS X 10.9;'
                          ' rv:27.0) Gecko/20100101 Firefox/27.0'),
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
        })

        self.session.get(
            'https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&'
            'style=16&mibao_css=m_webqq&appid=501004106&enable_qlogin=0&'
            'no_verifyimg=1&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&'
            'f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001'
        )

        self.session.cookies.update({
            'RK': 'OfeLBai4FB',
            'pgv_pvi': '911366144',
            'pgv_info': 'ssid pgv_pvid=1051433466',
            'ptcz': ('ad3bf14f9da2738e09e498bfeb93dd9da7'
                    '540dea2b7a71acfb97ed4d3da4e277'),
            'qrsig': ('hJ9GvNx*oIvLjP5I5dQ19KPa3zwxNI'
                    '62eALLO*g2JLbKPYsZIRsnbJIxNe74NzQQ')
        })

        self.getAuthStatus()
        self.session.cookies.pop('qrsig')

    def getAuthStatus(self):
        Referer=('https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&'
                'target=self&style=16&mibao_css=m_webqq&appid=501004106&'
                'enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2F'
                'w.qq.com%2Fproxy.html&f_url=loginerroralert&'
                'strong_login=1&login_state=10&t=20131024001')
        self.session.headers.update({'Referer':Referer})
        
        result = self.session.get(
            url='https://ssl.ptlogin2.qq.com/ptqrlogin?ptqrtoken=' + 
                str(bknHash(self.session.cookies['qrsig'], init_str=0)) +
                '&webqq_type=10&remember_uin=1&login2qq=1&aid=501004106' +
                '&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26' +
                'webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&' +
                'from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-' +
                repr(random.random() * 900000 + 1000000) +
                '&mibao_css=m_webqq&t=undefined&g=1&js_type=0' +
                '&js_ver=10141&login_sig=&pt_randsalt=0'
            ).content
        return result.decode('utf-8')
            

    def getQrcode(self):
        logging.info('登录 Step-1 获取二维码')

        qrcode = self.session.get(
            'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&'
            's=5&d=72&v=4&t='+ repr(random.random()),timeout=10
        ).content
        self.im = Image.open(BytesIO(qrcode))
        self.im.show()

    def waitForAuth(self):

        while True:
            time.sleep(3)
            authStatus = self.getAuthStatus()

            if '二维码未失效' in authStatus:
                logging.info('登录 Step2 - 等待二维码扫描及授权')
            elif '二维码认证中' in authStatus:
                logging.info('二维码已扫描，等待授权')
            elif '二维码已失效' in authStatus:
                logging.info('二维码已失效，重新获取二维码')
                self.getQrcode()
            elif '登录成功' in authStatus:
                logging.info('已获取授权')
                items = authStatus.split(',')

                self.nick = items[-1].split("'")[1]
                self.qq = int(self.session.cookies['superuin'][1:])
                self.urlPtwebqq = items[2].strip().strip("'")
                break
            else:
                print('I have no ideal')

    def getPtwebqq(self):
        logging.info('登录 Step3 - 获取ptwebqq')
        self.session.get(self.urlPtwebqq,timeout=10)
        self.ptwebqq = self.session.cookies['ptwebqq']
        print(self.ptwebqq)

    def getVfwebqq(self):
        logging.info('登录 Step4 - 获取vfwebqq')
        
        Referer = 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
        Origin = 'http://s.web2.qq.com'
        self.session.headers.update({'Referer':Referer,'Origin':Origin})
        result = self.session.get(
            url = 'http://s.web2.qq.com/api/getvfwebqq?ptwebqq=%s&clientid=%s&psessionid=&t=%s' % \
                  (self.ptwebqq,self.clientid,repr(random.random()))
        ).json()
        for k,v in result['result'].items():
            print(k,v)
        self.vfwebqq = result['result']['vfwebqq']

    def getUinAndPsessionid(self):
        logging.info('登录 Step5 - 获取uin和psessionid')
        
        Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        Origin =  'http://d1.web2.qq.com'
        self.session.headers.update({'Referer':Referer,'Origin':Origin})

        result = self.session.post(
            url='http://d1.web2.qq.com/channel/login2',
            data = {
                'r':json.dumps({
                    'ptwebqq':self.ptwebqq, 'clientid':self.clientid, 'psessionid':'','status':'online'
                })
            }
        ).json()['result']
        self.uin = result['uin']
        print('uin:',self.uin)
        self.psessionid = result['psessionid']
        print('psessionid:', self.psessionid)
        self.hash = qHash(self.uin,self.ptwebqq)
        self.bkn = bknHash(self.session.cookies['skey'])

    def fetchBuddy(self):
        logging.info('登录 Step6 - 获取好友列表')

        Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        self.session.headers.update({'Referer':Referer})

        result=self.session.post(
            url = 'http://s.web2.qq.com/api/get_user_friends2',
            data = {'r':json.dumps({'vfwebqq':self.vfwebqq,'hash':self.hash})}
        ).json()
        print(result)

        if result['retcode'] == 0:
            buddies = result['result']['info']
            self.buddy = tuple((buddy['uin'],buddy['nick'].encode('utf-8')) for buddy in buddies)

            logging.info('获取朋友列表成功，共%d 个朋友' %len(self.buddy))
        else:
            raise Exception("reason='获取好友列表',errInfo="+ str(result))

    def fetchGroup(self):
        logging.info('登录 Step7 - 获取群列表')

        Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        Origin = 'http://d1.web2.qq.com'
        self.session.headers.update({'Referer':Referer,'Origin':Origin})

        result = self.session.post(
            url='http://s.web2.qq.com/api/get_group_name_list_mask2',
            data = {'r':json.dumps({'vfwebqq':self.vfwebqq,'hash':self.hash})}
        ).json()

        if result['retcode'] == 0:
            groups = result['result']['gnamelist']
            self.group = tuple((group['gid'],group['name']) for group in groups)

            logging.info('获取群列表成功，共%d个群' %len(self.group))
            '''i = 0
            for group in groups:
                try:
                    print(i,group)
                except UnicodeEncodeError:
                    non_bmp_map = dict.fromkeys(range(0x10000,sys.maxunicode+1),0xfffd)
                    group['name'] = group['name'].translate(non_bmp_map)
                    print(group)
                i += 1'''
                
        else:
            raise Exception("reason='获取群列表'errInfo=" + str(result))
        

    def fetchDiscuss(self):
        logging.info('登录 Step8 - 获取讨论组列表')
        Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        self.session.headers.update({'Referer':Referer})
        result = self.session.get(
            url = 'http://s.web2.qq.com/api/get_discus_list?clientid=%s&psessionid=%s'
                  '&vfwebqq=%s&t=%s' %(self.clientid,self.psessionid,self.vfwebqq,repr(random.random()))
        ).json()

        if result['retcode'] == 0:
            discusses = result['result']['dnamelist']
            self.discuss = tuple((discuss['did'],discuss['name']) for discuss in discusses)
            logging.info('获取讨论组列表成功，共%d个讨论组' %len(self.discuss))
        else:
            raise Exception("reason='获取讨论组列表,errInfo="+str(result))

    def poll(self):

        Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        expectedCodes = (0,100003,100100,100012)
        self.session.headers.update({'Referer':Referer,'expectedCodes':expectedCodes})
        result = self.session.post(
            url = 'http://d1.web2.qq.com/channel/poll2',
            data = {
                'r': json.dumps({
                    'ptwebqq':self.ptwebqq,'clientid':self.clientid,
                    'psessionid':self.psessionid,'key':''
                })
            }
        ).json()
        print('poll',result)

        if result['retcode'] == 0:
            if 'errmsg' in result:
                return ('',0,0,'')
            result = result['result'][0]
            msgType = {'message':'buddy','group_message':'group','discu_message':'discuss'}[result['poll_type']]
            msg = result['value']['from_uin']
            from_uin = result['value']['from_uin']
            buddy_uin = result['value'].get('send_uin',from_uin)
            pollResult = msgType,from_uin,buddy_uin,msg
            if msgType =='buddy':
                logging.info('收到一条来自%s%d的消息：<%s>' %(msgType,from_uin,msg))
            else:
                logging.info('收到一条来自%s%d（buddy%d)消息:<%s>' %pollResult)
            return pollResult
        else:
            raise Exception('errInfo=<%s>' % result)


    def PollForever(self):
        logging.info('QQBot已启动，请用其他QQ号码向本QQ %s<%d> 发送命令来操作QQBot。%s' % \
                     (self.nick,self.qq,self.helpInfo)
        )
        self.stopped = False
        while not self.stopped:
            time.sleep(0.2)
            pullResult = self.poll()
            try:
                print('pullResult',pullResult)
                #self.onPollComplete(*pullResult)
            except Exception:
                logging.info(' onPollComplete函数出现错误，已忽略',exc_info=True)
        logging.info('QQBot已停止')

    def onPollComplete(self,msgType,from_uin,buddy_uin,message):
        targets = ('buddy','group','discuss')
        reply = ''
        if message == '-help':
            reply = '欢迎使用QQBot，使用方法：\r\n' + \
                    '      -help\r\n' + \
                    '      -list buddy|group|discuss\r\n' + \
                    '      -send buddy/group/discuss uin message\r\n' + \
                    '      -stop'
        elif message[:6] == '-list':
            target = message[6:].strip()
            reply = getattr(self,target+'Str','')
        elif message[:6] == '-send':
            args = message[6:].split(' ',2)
            if len(args) == 3 and args[0] in targets and args[1].isdigit():
                reply = self.send(args[0],int(args[1]),args[2].strip())
        elif message == '-stop':
            self.stopped = True
            reply = 'QQBot 已停止'
        self.sendLongMsg(msgType,from_uin,reply)
        
            

def qHash(x,K):
    N = [0] * 4
    for T in range(len(K)):
        N[T%4] ^= ord(K[T])

    U,V  = 'ECOK', [0]*4
    V[0] = ((x >>24) & 255) ^ord(U[0])
    V[1] = ((x >>16) & 255) ^ord(U[1])
    V[2] = ((x >> 8) & 255) ^ord(U[2])
    V[3] = ((x >> 0) & 255) ^ord(U[3])

    U1 = [0] *8
    for T in range(8):
        U1[T] = N[T>> 1] if T%2==0 else V[T >>1]
    N1,V1 = '0123456789ABCDEF',''
    for aU1 in U1:
        V1 += N1[((aU1 >> 4) & 15)]
        V1 += N1[((aU1 >> 0) & 15)]

    return V1
    
        
def bknHash(skey, init_str=5381):
    hash_str = init_str
    for i in skey:
        hash_str += (hash_str << 5) + ord(i)
    hash_str = int(hash_str & 2147483647)
    return hash_str

def utf8Partition(msg,n):
    if n >=len(msg):
        return msg,''

    while n > 0:
        ch = ord(msg[n])
        if (ch>>7 == 0) or (ch >> 6 ==3):
            break
        n -=1
    return msg[:n],msg[n:]

if __name__ == '__main__':
    qqbot = QQBot()
    qqbot.Login()
    qqbot.PollForever()

        












