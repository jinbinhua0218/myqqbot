# -*- coding: utf-8 -*-

#https://blog.csdn.net/hello_world_zhou/article/details/54782980

import logging
import sys
import threading

from login import QLogin

logging.basicConfig(level=logging.INFO)


class QQBot:

    def Login(self):
        self.session = QLogin()
        #child thread 1
        self.poll = self.session.Poll

    def Run(self):
        #StartDaemonThread(self.pollForever)
        t = threading.Thread(target=self.pollForever)
        t.daemon = True
        t.start()

    # child thread 1
    def pollForever(self):
        while True:
            try:
                result = self.poll()
            except:
                print('qsession.Poll 方法出错')
                break
            '''else:
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
            INFO('来自 %s[%s] 的消息: "%s"' % (contact, member, content))'''


if __name__ == '__main__':
    
    qqbot = QQBot()
    qqbot.Login()
    qqbot.Run()


        








