#!/usr/bin/env python 
#-*- coding:utf-8 -*-
from config import tcpstate
class ParseNetstat:
     """This moudule can analyse four files:
     /proc/net/tcp
     /proc/net/tcp6
     /proc/net/udp
     /proc/net/udp6
     and will  get ListenPort,uid,inode num,foreigner IP ,connection status.
     tcp state:
     00  "ERROR_STATUS",
     01  "TCP_ESTABLISHED",
     02  "TCP_SYN_SENT",
     03  "TCP_SYN_RECV",
     04  "TCP_FIN_WAIT1",
     05  "TCP_FIN_WAIT2",
     06  "TCP_TIME_WAIT",
     07  "TCP_CLOSE",
     08  "TCP_CLOSE_WAIT",
     09  "TCP_LAST_ACK",
     0A  "TCP_LISTEN",
     0B  "TCP_CLOSING",     
     Introduction:

     ESTABLISHED
            The socket has an established connection.
     SYN_SENT
            The socket is actively attempting to establish a connection.
     SYN_RECV
            A connection request has been received from the network.
     FIN_WAIT1
            The socket is closed, and the connection is shutting down.
     FIN_WAIT2
            Connection is closed, and the socket is waiting for a shutdown from the remote end.
     TIME_WAIT
            The socket is waiting after close to handle packets still in the network.
     CLOSE  The socket is not being used.
     CLOSE_WAIT
            The remote end has shut down, waiting for the socket to close.
     LAST_ACK
            The remote end has shut down, and the socket is closed. Waiting for acknowledgement.
     LISTEN The socket is listening for incoming connections.
     CLOSING
            Both sockets are shut down but we still don't have all our data sent.
     UNKNOWN
            The state of the socket is unknown.
     """

     def __init__(self,BUFFER = 2048,TCP = '/proc/net/tcp',TCP6 = '/proc/net/tcp6',UDP = '/proc/net/udp',UDP6 = '/proc/net/udp6'):
        self.buff = BUFFER
        self.tcp = TCP
	self.tcp6 = TCP6
	self.udp = UDP
	self.udp6 = UDP6
        self.tcpstate = tcpstate

	self.need = {'LPIU':1,'CSC':2,'FC':3}

        # LPIU : Get listen port for inode adn uid.
        # CSC  : Get per  state  count for connections.
        # FC   : Get per foreigner IP  count  which connected  localhost.

	self.tupletcp = (self.tcp,self.tcp6)
	self.tupleudp = (self.udp,self.udp6)

     def hex2dec(self,STRING_NUM):
         return str(int(STRING_NUM.upper(), 16))

     # ipv4数字地址 
     # dec2ipv4
     def Getipv4addr_from_decnum(self,decipv4):
         ipv4_n = socket.htonl(decipv4)
         data = struct.pack('I', ipv4_n)
         ipv4_addr= socket.inet_ntop(socket.AF_INET, data)
         return ipv4_addr
     
     # ipv6用四个整数(tuple或用,分开的字符串)表示
     #dec2ipv6
     def Getipv6_from_decnum(self,decipv6):
         ipv6_n = (socket.htonl(ipv6[0]),
                   socket.htonl(ipv6[1]),
                   socket.htonl(ipv6[2]),
                   socket.htonl(ipv6[3]))
         data = struct.pack('IIII', ipv6_n[0], ipv6_n[1], ipv6_n[2], ipv6_n[3])
         ipv6_addr= socket.inet_ntop(socket.AF_INET6, data)
         return ipv6_addr
     
     def openfile(self,F):
         opfile = open(F)
	 filelist = opfile.readlines()
	 opfile.close()
	 #delete first line
	 del filelist[0]
	 return filelist

     def getprotocoldic(self,protocolfile,statecode):
         PROTOCOLDIC = {}
	 for eachprotocolline in protocolfile:
	     protocolfields = eachprotocolline.split()
	     #print  statecode
	     if protocolfields[3] == statecode:
                #print  'PROTOCOL:listen port:%s, uid:%s, inode:%s' % (self.hex2dec(tcpfields[1].split(':')[1]),tcpfields[7],tcpfields[9])
		TMP = (protocolfields[7],protocolfields[9])
                PROTOCOLDIC[self.hex2dec(protocolfields[1].split(':')[1])] = TMP
	        del TMP
	 return PROTOCOLDIC

     def GetListenPortUidInode(self):
         LISTENINFO = {}

         alltcp4file = self.openfile(self.tupletcp[0])
	 tcp4 = self.getprotocoldic(alltcp4file,self.tcpstate.get('TCP_LISTEN'))

         alltcp6file = self.openfile(self.tupletcp[1])
	 tcp6 = self.getprotocoldic(alltcp6file,self.tcpstate.get('TCP_LISTEN'))
              
         alludp4file = self.openfile(self.tupleudp[0])
	 udp4 = self.getprotocoldic(alludp4file,self.tcpstate.get('TCP_CLOSE'))

         alludp6file = self.openfile(self.tupleudp[1])
	 udp6 = self.getprotocoldic(alludp6file,self.tcpstate.get('TCP_CLOSE'))
         
	 LISTENTCP ={}
	 LISTENTCP['tcp4'] = tcp4
	 LISTENTCP['tcp6'] = tcp6

	 LISTENUDP ={}
         LISTENUDP['udp4'] = udp4
	 LISTENUDP['udp6'] = udp6

         #LISTENINFO['listentcp'] = LISTENTCP
	 #LISTENINFO['listenudp'] = LISTENUDP
	 #merge dict
	 LISTENINFO = dict(LISTENTCP,**LISTENUDP)
         #clear memory
	 for var in [alltcp4file,alltcp6file,alludp4file,alludp6file,LISTENTCP,LISTENUDP]:
             del var

         return LISTENINFO

     def GetTcpConnectionsStateCount(self):
         #使用多线程方式处理每种状态统计
         pass  

     def GetTCPForeignerIpCount(self):
         #使用多线程方式处理每个ip的数量
        pass

if __name__ == '__main__':
    test = ParseNetstat()
    q = test.GetListenPortUidInode()
    print q

