# -*- coding: utf-8 -*-

#https://blog.csdn.net/hello_world_zhou/article/details/54782980

import requests,random,os,time
import logging; logging.basicConfig(level=logging.INFO)
import json
import sys
import pickle

from io import BytesIO
from PIL import Image

from qqbot.qrcodemanager import QrcodeManager
from qqbot.utf8logger import CRITICAL, ERROR, WARN, INFO, DEBUG
from qqbot.utf8logger import DisableLog, EnableLog
from qqbot.common import PY3, Partition, JsonLoads, JsonDumps,StartDaemonThread
from qqbot.facemap import FaceParse, FaceReverseParse
from qqbot.mainloop import Put

from login import QLogin

def disableInsecureRequestWarning():
    try:
        try:
            urllib3 = requests.packages.urllib3
        except AttributeError:
            import urllib3    
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception as e:
        ERROR('无法禁用 InsecureRequestWarning ，原因：%s', e)


class RequestError(Exception):
    pass

class QQBot:

    def Login(self):
        session = QLogin()
        self.session = session

        #child thread 1
        self.poll = session.Copy().Poll

    def Run(self):
        StartDaemonThread(self.pollForever)

    # child thread 1
    def pollForever(self):
        while True:
            try:
                result = self.poll()
            except RequestError:
                Put(sys.exit, LOGIN_EXPIRE)
                break
            except:
                ERROR('qsession.Poll 方法出错', exc_info=True)
            else:
                Put(self.onPollComplete, *result)

    def onPollComplete(self, ctype, fromUin, membUin, content):
        if ctype == 'timeout':
            return

        contact, member, nameInGroup = \
            self.findSender(ctype, fromUin, membUin, self.conf.qq, content)
        
        if contact.ctype == 'group' and member == 'SYSTEM-MESSAGE':
            INFO('来自 %s 的系统消息： "%s"', contact, content)
            return

        if self.detectAtMe(nameInGroup, content):
            INFO('有人 @ 我：%s[%s]' % (contact, member))
            content = '[@ME] ' + content.replace('@'+nameInGroup, '')
        else:
            content = content.replace('@ME', '@Me')
                
        if ctype == 'buddy':
            INFO('来自 %s 的消息: "%s"' % (contact, content))
        else:
            INFO('来自 %s[%s] 的消息: "%s"' % (contact, member, content))


if __name__ == '__main__':
    
    qqbot = QQBot()
    qqbot.Login()
    qqbot.Run()


        








