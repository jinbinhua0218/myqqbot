# -*- coding: utf-8 -*-

#https://blog.csdn.net/hello_world_zhou/article/details/54782980

import requests,random,os,sys,time
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)
    
import logging; 
import json
import pickle
import threading
from io import BytesIO
from PIL import Image

from qqbot.utf8logger import DisableLog, EnableLog
from qqbot.mainloop import Put

logging.basicConfig(level=logging.INFO)

def disableInsecureRequestWarning():
    try:
        try:
            urllib3 = requests.packages.urllib3
        except AttributeError:
            import urllib3    
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception as e:
        logging.error('无法禁用 InsecureRequestWarning ，原因：%s', e)


class RequestError(Exception):
    pass

class QQBot_Login:

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
        self.TestLogin()

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

    def TestLogin(self):
        print('TestLogin',self.session.verify)
        if not self.session.verify:
            disableInsecureRequestWarning()
        try:
            DisableLog()
            # 请求一下 get_online_buddies 页面，避免103错误。
            # 若请求无错误发生，则表明登录成功
            self.smartRequest(
                url = ('http://d1.web2.qq.com/channel/get_online_buddies2?'
                       'vfwebqq=%s&clientid=%d&psessionid=%s&t={rand}') %
                      (self.vfwebqq, self.clientid, self.psessionid),
                Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                           'callback=1&id=2'),
                Origin = 'http://d1.web2.qq.com',
                repeatOnDeny = 0
            )
        finally:
            EnableLog()
        
        logging.info('登录成功。登录账号：%s(%s)', self.nick, self.qq)


    def urlGet(self, url, data=None, Referer=None, Origin=None):
        Referer and self.session.headers.update( {'Referer': Referer} )
        Origin and self.session.headers.update( {'Origin': Origin} )
        timeout = 30 if url != 'https://d1.web2.qq.com/channel/poll2' else 120
            
        try:
            if data is None:
                return self.session.get(url, timeout=timeout)
            else:
                return self.session.post(url, data=data, timeout=timeout)
        except (requests.exceptions.SSLError, AttributeError):
            # by @staugur, @pandolia
            if self.session.verify:
                time.sleep(5)
                logging.error('无法和腾讯服务器建立私密连接，'
                      ' 5 秒后将尝试使用非私密连接和腾讯服务器通讯。'
                      '若您不希望使用非私密连接，请按 Ctrl+C 退出本程序。')
                try:
                    time.sleep(5)
                except KeyboardInterrupt:
                    Put(sys.exit, 0)
                    sys.exit(0)
                logging.warning('开始尝试使用非私密连接和腾讯服务器通讯。')
                self.session.verify = False
                disableInsecureRequestWarning()
                return self.urlGet(url, data, Referer, Origin)
            else:
                raise


    def smartRequest(self, url, data=None, Referer=None, Origin=None,
                     expectedCodes=(0,100003,100100), expectedKey=None,
                     timeoutRetVal=None, repeatOnDeny=2):
        nCE, nTO, nUE, nDE = 0, 0, 0, 0
        while True:
            url = url.format(rand=repr(random.random()))
            html = ''
            errorInfo = ''
            try:
                resp = self.urlGet(url, data, Referer, Origin)
            except (requests.ConnectionError,
                    requests.exceptions.ReadTimeout) as e:
                nCE += 1
                errorInfo = '网络错误 %s' % e
            else:
                html =resp.content.decode('utf8')                    
                if resp.status_code in (502, 504, 404):
                    self.session.get(
                        ('http://pinghot.qq.com/pingd?dm=w.qq.com.hot&'
                         'url=/&hottag=smartqq.im.polltimeout&hotx=9999&'
                         'hoty=9999&rand=%s') % random.randint(10000, 99999)
                    )
                    if url == 'https://d1.web2.qq.com/channel/poll2':
                        return {'errmsg': ''}
                    nTO += 1
                    errorInfo = '超时'
                else:
                    try:
                        rst = json.loads(html)
                    except ValueError:
                        nUE += 1
                        errorInfo = ' URL 地址错误'
                    else:
                        result = rst.get('result', rst)
                        
                        if expectedKey:
                            if expectedKey in result:
                                return result
                        else:                        
                            if 'retcode' in rst:
                                retcode = rst['retcode']
                            elif 'errCode' in rst:
                                retcode = rst['errCode']
                            elif 'ec' in rst:
                                retcode = rst['ec']
                            else:
                                retcode = -1
    
                            if (retcode in expectedCodes):
                                return result

                        nDE += 1
                        errorInfo = '请求被拒绝错误'
            
            n = nCE + nTO + nUE+ nDE
            
            if len(html) > 40:
                html = html[:20] + '...' + html[-20:]

            # 出现网络错误、超时、 URL 地址错误可以多试几次 
            # 若网络没有问题但 retcode 有误，一般连续 3 次都出错就没必要再试了
            if nCE < 5 and nTO < 20 and nUE < 5 and nDE <= repeatOnDeny:
                logging.debug('第%d次请求“%s”时出现 %s，html=%s',
                      n, url.split('?', 1)[0], errorInfo, repr(html))
                time.sleep(0.5)
            elif nTO == 20 and timeoutRetVal: # by @killerhack
                return timeoutRetVal
            else:
                logging.error('第%d次请求“%s”时出现 %s, html=%s',
                      n, url.split('?', 1)[0], errorInfo, repr(html))
                raise RequestError

    def Poll(self):
        
        try:
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
            self.session.headers.update({'Referer':Referer})
            result = self.session.post(
                url = 'https://d1.web2.qq.com/channel/poll2',
                data = {
                    'r': json.dumps({
                        'ptwebqq':self.ptwebqq, 'clientid':self.clientid,
                        'psessionid':self.psessionid, 'key':''
                    })
                }
            ).json()
            # "{'retcode': 0, 'retmsg': 'ok', 'errmsg': 'error'}"
            print(result)
            if type(result) is dict and \
                    result.get('retcode', 1) == 0 and \
                    result.get('errmsg', '') == 'error':
                logging.debug(result)
                raise RequestError
        except RequestError:
            logging.error('接收消息出错，开始测试登录 cookie 是否过期...')
            return 'timeout', '', '', ''
        else:
            if (not result) or (not isinstance(result, list)):
                logging.debug(result)
                return 'timeout', '', '', ''
            else:
                result = result[0]
                ctype = {
                    'message': 'buddy',
                    'group_message': 'group',
                    'discu_message': 'discuss'
                }[result['poll_type']]
                fromUin = str(result['value']['from_uin'])
                memberUin = str(result['value'].get('send_uin', ''))
                content = result['value']['content']
                return ctype, fromUin, memberUin, content
            
    def Copy(self):
        c = self.__class__()
        c.__dict__.update(self.__dict__)
        c.session = pickle.loads(pickle.dumps(c.session))
        return c


def QLogin():
    session = QQBot_Login()
    session.Login()
    return session
   

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

if __name__ == '__main__':
    qqbot = QQBot_Login()
    qqbot.Login()




        








