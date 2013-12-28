#/usr/bin/env python
#-*-coding:utf-8-*-

#import ScanSend
import WaitTimer
import Portprobe
import Sniffer
import TcpClient
import xml.dom.minidom
import ExecuteInterfaceServer
from socket import socket,inet_ntoa,gethostname,AF_INET,SOCK_DGRAM
from struct import pack
from fcntl import ioctl
from time import strftime,localtime,time

class General:
   """
   nothing to do
   """
   def __init__(self):
      """
      nothing
      """
  #from XMLGengerator
  # def ScanAction(self):
  #     while True:
  #           Scan=ScanSend.ScanGenerator('eth0')
  #           IP=Scan.get_ip_address()
  #           print IP
  #           Scan.Scan()
   def TS(self):
       ts = ExecuteInterfaceServer.MultControl()  
       ts.ListenServer()  

   def PortCheck(self):
   
       def GetPlist(PROTO):
           LUI = Sniffer.ParseNetstat()
           LUIDICT = LUI.GetListenPortUidInode()
           #get listen port and get unique port list
           LPORT = {}.fromkeys(LUIDICT[PROTO+'4'].keys()+LUIDICT[PROTO+'6'].keys()).keys()
           #print LPORT
           return  LPORT

       def GetInitDict(PROTO):
           INITVALUE = 3
	   PLIST = GetPlist(PROTO)
           INITDICT = {}
           for KEYPORT in PLIST:
   	       INITDICT[KEYPORT] = INITVALUE
           return INITDICT


      #原来客户端的逻辑移交到服务端
      # def Check(PROTO,TYPE,ORGINDIC):
      #     #check port
      #     #define state code
      #     DOWN = 0
      #     CRITICAL = 1
      #     WARNNING = 2
      #     NORMAL = 3
      #     TIMESTAMP = strftime('%Y-%m-%d-%H:%M:%S',localtime(time()))
      #     Send = TcpClient.Tclient()
      #     #打印原始字典
      #     print  "%s,%s" % (PROTO,ORGINDIC)

      #     #扫描一次端口
      #     NEWLIST =  GetPlist(PROTO)
      #     #打印出扫描出的列表
      #     print  "%s,%s" % (PROTO,NEWLIST)

      #     for port in NEWLIST:
      #         if port in ORGINDIC.keys():
      #  	  ORGINDIC[port] = NORMAL
      #         elif port not in ORGINDIC.keys():
      #  	  ORGINDIC[port] = NORMAL 
      #            print '%s:[%s] %s port added!' % (TIMESTAMP,PROTO,port)
      #     
      #     #get down port 
      #     DIFFELEMENT = list(set(ORGINDIC.keys()).difference(set(NEWLIST)))
      #     if len(DIFFELEMENT) == 0:
      #        print '%s:[%s]:check over,no port down!' % (TIMESTAMP,PROTO)
      #     else:
      #        for downport in DIFFELEMENT:
      #            if ORGINDIC[downport] == DOWN:
      #               SEND_CO =  TYPE+':'+downport+':'+'0'
      #               print '%s:%s' % (TIMESTAMP,SEND_CO)
      #               Send.TcpSender(SEND_CO,str((1<<0)|(1<<8)))
      #            else:
      #                ORGINDIC[downport] -= 1
       def Main():
          def send(PROTO,PRO):
	      CONTENT = ''
              TIMESTAMP = strftime('%Y-%m-%d-%H:%M:%S',localtime(time()))
	      for PORTLIST in PROTO.keys():
		  CONTENT += ':'+PORTLIST

              SEND_CO = PRO+CONTENT
              print '%s:%s' % (TIMESTAMP,SEND_CO)
              Send.TcpSender(SEND_CO,str((1<<0)|(1<<8)))

          while True:
	      #实例化发送客户端
              Send = TcpClient.Tclient()
              #得到原始监听端口号
   	      #UDPORGINDIC = GetInitDict('udp')
   	      TCPORGINDIC = GetInitDict('tcp')
	      print '------------'
	      print  'tcp:%s' % TCPORGINDIC
	      #print  'udp:%s' % UDPORGINDIC
	      print '------------'
   	      for x in xrange(2):
   	          S = WaitTimer.Waiter(5)
	      #	  send(UDPORGINDIC,'udp')
		  send(TCPORGINDIC,'tcp')
   	          S.Sleep()
   
       Main()

if __name__=='__main__':
   test = General()
   test.PortCheck()

