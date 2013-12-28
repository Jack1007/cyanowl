#!/usr/bin/env python 
#-*-coding:utf-8 -*-
#这是发送文件客户端
import os
import struct
import sys,time
import socket,fcntl,struct 
import xml.dom.minidom
sys.path.append('../Scanmodule')
#导入xml目录解析模块类
import XMLGenerator
#导入等待器
import WaitTimer

#存放xml的根目录
ROOT_FILE_DIR = '../box/'

class ScanGenerator:
    """
	this clasee will be creat directory,file,which contain server infomation,web detail.
    """
    def __init__(self,IFNAME='eth0'):
       """
	   no idea
       """
       self.IFNAME=IFNAME
       self.HOSTNAME=socket.gethostname()

    def get_ip_address(self): 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        try:
           return socket.inet_ntoa(fcntl.ioctl( 
           s.fileno(), 
           0x8915, # SIOCGIFADDR 
           struct.pack('256s', self.IFNAME[:15]) 
           )[20:24]) 
        except IOError:
            print "%s : is disconnect,cable right?" % self.IFNAME		
        except TypeError:
            print "%s : is disconnect,cable right?" % self.IFNAME		
         #print get_ip_address('lo')
         #print get_ip_address('wlan0')
         #print get_ip_address('eth0')

    def connector(self):   
	 SERVEROBJ = xml.dom.minidom.parse('../conf/server.xml')
         SERVER_IP=SERVEROBJ.getElementsByTagName('info')[0].attributes['ip'].value
         SERVER_PORT=SERVEROBJ.getElementsByTagName('info')[0].attributes['port'].value
         FLAG =str(1<<0)+':'
         ETH_IP=self.get_ip_address()
         HOSTNAME=self.HOSTNAME
         
         #新目录名
         DIR_TIME=time.strftime('%Y-%m-%d',time.localtime(time.time()))
         #新文件名
         FILE_NAME=ETH_IP+HOSTNAME+'.xml'
         #创建存放目录

         #BUFSIZE = 1024
         #FILEINFO_SIZE = struct.calcsize('128s32sI8s')
         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
	 while True:
	     try:
                 #连接服务端
                 sock.connect((SERVER_IP,int(SERVER_PORT)))
		 break
             except socket.error:
                 print "%s:%s Connection refused!" % (SERVER_IP,SERVER_PORT)
                 #sleep time
                 s=WaitTimer.Waiter(5)
                 s.Sleep()
		 continue
         try:
            #FHEAD = struct.pack('128s11I',ROOT_FILE_DIR+FILE_NAME,0,0,0,0,0,0,0,0,os.stat(ROOT_FILE_DIR+FILE_NAME).st_size,0,0)
            FHEAD = open(ROOT_FILE_DIR+FILE_NAME,'r')
            TEXT=FHEAD.read()
         except OSError:
            print '"%s" file does not exsit!' % ROOT_FILE_DIR+FILE_NAME
            sys.exit() 
         try:
            #sock.send(FHEAD)
            sock.send(FLAG+TEXT)
         except socket.error:
            print "Broken pipe ,because of port refused!"
            sys.exit(112)
         #准备要传输的文件目录和文件名
         #FILE_OPEN= open(ROOT_FILE_DIR+FILE_NAME,'rb')

         #while True:
         #   FILEDATA =FILE_OPEN.read(BUFSIZE)
         #  
         #   if not FILEDATA:
         #      break
         #      sock.send(FILEDATA)
    				  
         print "file has been send"
         #FILE_OPEN.close()
         sock.close()
         FHEAD.close()
         print "disconnected"

    def Scan(self):
        #生成xml文件
        TIME = 60
        ETH0_IP=self.get_ip_address()
        NEW_PATH=ROOT_FILE_DIR
        xmldoc = XMLGenerator.ScanLoop(ETH0_IP, self.HOSTNAME)
        xmldoc.XMLGenerator(True)
        xmldoc.XMLGenerator(False)
        f = open(NEW_PATH+ETH0_IP+self.HOSTNAME+'.xml', 'w')
        f.write(xmldoc.XMLDoc.toprettyxml(indent = '    ', newl = '\n', encoding = 'utf-8'))
        f.close()
        
        #调用客户端发送文件
        self.connector()
        #sleep time
        s=WaitTimer.Waiter(TIME)
        s.Sleep()
            
if __name__ == '__main__':
     test=ScanGenerator('wlan0')
     IP=test.get_ip_address()
     print IP
     test.Scan()
