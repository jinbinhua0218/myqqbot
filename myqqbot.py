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
        self.send = self.session.send

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
            else:
                self.onPollComplete(*result)

    def onPollComplete(self, ctype, fromUin, membUin, content):
        if ctype == 'timeout':
            return
        #发送者是自己就不回复(1545055584)
        if fromUin == '1545055584':
            return 
        print('ctype ', ctype)
        print('fromUin ', fromUin)
        print('memberUin ', membUin)
        print('content ', content)

        #个人消息
        if ctype == 'buddy':
            logging.info('来自%s(uin)的消息: %s' %(fromUin,content))
        #群消息，但没写完
        elif ctype == 'group_message' and  True == True:
            logging.info('来自%s[%s](uin)的消息:%s' %(fromUin,membUin,content))
        #系统消息，但没写完
        elif ctype == 'group_message' and True == True:
            logging.info('来自%s(uin)的系统消息: %s' %(fromUin,content))
        #讨论组消息
        elif ctype =='discu_message':
            logging.info('来自%s[%s](uin)的消息:%s' %(fromUin,membUin,content))
        else:
            print('发生了什么？谁发了什么消息？')
        self.send(ctype,fromUin,membUin,content)


if __name__ == '__main__':
    
    qqbot = QQBot()
    qqbot.Login()
    qqbot.Run()










    


        








