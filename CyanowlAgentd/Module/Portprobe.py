#!/usr/bin/env python 
#-*- coding:utf-8 -*-
#this module manage warinning data and send to center 
import xml.dom.minidom as Dom
import socket
import WaitTimer


class MixInfo:
     def __init__(self):
         """hello boy"""
	 pass

     def __doc__(self):

         """
         GetPortList
         CheckPort
	 GetDetail4Port
	 """
     
     def GetPortList(self,XMLFILE):
         """返回端口列表"""
         TAG = 'port'
         PORTLIST = [22,80]
         XMLF = Dom.parse(XMLFILE)
         PL = XMLF.getElementsByTagName(TAG)
	 for PORTNUM in PL:
	     P = PORTNUM.childNodes[0].nodeValue
	     PORTLIST.append(P)
	 return PORTLIST

     def GetDetail4Port(self,DOWNPORT,XMLFILE):
         """返回app_item 节点下的所有内容"""
	 TAG = 'port'
         DWXML = Dom.parse(XMLFILE)
	 GD = DWXML.getElementsByTagName(TAG)
	 for GDPL in GD:
	     if int(DOWNPORT) == int(GDPL.childNodes[0].nodeValue):
                APP_ITEM = GDPL.parentNode.parentNode
		break
	 return APP_ITEM
    
     def CheckPort(self,PORT,PROTOCOL,IP='localhost'):
         CKWATIME = 5.0
         CKNORMAL = 0
	 ERROR = 104
	 while True:
	     if PROTOCOL == 'tcp':
                CK = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	        CK.settimeout(CKWATIME)
		break
	     elif PROTOCOL == 'udp':
                CK = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	        CK.settimeout(CKWATIME)
		break
	     else:
	         print "warnnig: network protocol is wrong,you will be modify!"
		 sp = WaitTimer.Waiter(1)
		 sp.Sleep()

         #如果端口为0,则直接通过,并返回正常值
	 if int(PORT) == 0:
	     pass
             return CKNORMAL
	 else:
             CK_ADDR= (str(IP),int(PORT))
             RETURN_CODE = CK.connect_ex(CK_ADDR) 
             if RETURN_CODE != CKNORMAL:
                return ERROR 
             else:
                return CKNORMAL
         CK.close()

if __name__ == '__main__':
    import time
    import TcpClient

    test = MixInfo()

    while True:
       """ 如果文件更新会自动重载"""
       F = '../conf/test.xml'
       POL = test.GetPortList(F)
       sender = TcpClient.Tclient()
       print POL
       for i in POL:
	   #print i
	   STA = test.CheckPort(int(i),'tcp')
	   if int(STA) == 104 and int(i) == 80:
	      SEND_CO = 'http port 80 has been down'
	      print SEND_CO
	      sender.TcpSender(SEND_CO,str(1<<1))
	   elif int(STA) == 104 and int(i) == 22: 
	      SEND_CO = 'sshd port 22 has been down'
	      print SEND_CO
	      sender.TcpSender(SEND_CO,str(1<<1))
	   elif int(STA) == 104: 
	      Content =  test.GetDetail4Port(int(i),F)
	      SEND_CO = Content.toxml()
	      sender.TcpSender(SEND_CO,str(1<<1))
       time.sleep(3)   
