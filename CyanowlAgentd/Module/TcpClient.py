#!/usr/bin/env python
#-*- coding:utf-8 -*-

import xml.dom.minidom
import WaitTimer
import socket

class Tclient:
     """ tcp client """
     def __init__(self):
         SERVEROBJ = xml.dom.minidom.parse('../conf/server.xml')
         self.serverip = SERVEROBJ.getElementsByTagName('info')[0].attributes['ip'].value
         self.port = int(SERVEROBJ.getElementsByTagName('info')[0].attributes['port'].value)

     def TcpSender(self,TEXT,FLAG):
         #传送文件类校验码
	 WATIME = 5
	 while True:
             try:
                 #连接服务端
	         TC = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	         TC.settimeout(2)
                 TC.connect((self.serverip,self.port))
		 break
             except socket.error:
                 print "%s:%s Connection refused! retry after 5 seconds" % (self.serverip,self.port)
		 S = WaitTimer.Waiter(WATIME)
		 S.Sleep()

         while True:
             try:
                TC.send(FLAG+':'+TEXT)
		break
             except socket.error:
                print "Broken pipe ,because of port refused! retry after 5 seconds!"
		S = WaitTimer.Waiter(WATIME)
		S.Sleep()

         print "Information has been send !"
         TC.close()
    
if __name__ == '__main__':
    t = Tclient()
    t.TcpSender('TestMessage','1')
