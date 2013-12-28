#! /usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from tornado.netutil import bind_sockets
from tornado.process import fork_processes
from tornado.options import options, define
from tornado import log
#from pyxmpp2.simple import send_message
#from pyxmpp2.settings import XMPPSettings
import logging
#from pyxmpp2.jid import JID
#from pyxmpp2.message import Message
#from pyxmpp2.client import Client
#from pyxmpp2.settings import XMPPSettings
#from pyxmpp2.interfaces import EventHandler, event_handler, QUIT
#from pyxmpp2.streamevents import AuthorizedEvent, DisconnectedEvent
import os, sys
import socket
import time
import string
import random
import Queue
import threading
import traceback
#import objgraph
import gc

#### use sleekxmpp as xmpp client ###
import ssl
import sleekxmpp
from sleekxmpp.util.misc_ops import setdefaultencoding
setdefaultencoding('utf8')

### custom modules
import config
import simpleutil

#queue = Queue.Queue()

options.parse_command_line()
options.parse_config_file("config.json")

class SendMsgBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, recipient, message):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.recipient = recipient
        self.msg = message
        self.add_event_handler("session_start", self.start, threaded=True)

    def start(self, event):
        self.send_presence()
        self.get_roster()

        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')

        self.disconnect(wait=True)



class HandleStream(object):
    def __init__(self, stream, address):
        self._stream = stream
        self._address = str(address[0])
        self._buffer = ""
        self._xmldir = options.xmldir
        log.gen_log.info("init addr: %s" % (str(address)))
    def read_data(self):
        log.gen_log.info("recving data from %s" % (self._address))
        self._stream.read_until_close(self.callback_data, self.streaming_callback_data)
    def callback_data(self, data):
        log.gen_log.info("Handle Stream Over and Closed The Stream Now!")
        del data
        self._stream.close()
        #IOLoop.instance().stop()
    def streaming_callback_data(self, data):
        #print "streaming_callback data: ", data
        self._buffer = data.strip()
        log.gen_log.info("recv data: <%s> over", len(data))
        #self._stream.close()
        hb = HandleBuffer(self._stream, self._address, self._buffer)
        hb.handlebuffer()
        del hb
        #mbt = simpleutil.MainBuffThread(hb.handlebuffer)
        #mbt.start()
        log.gen_log.info("close stream now")
        #objgraph.show_most_common_types(limit=20)
        #gc.set_debug(gc.DEBUG_LEAK)
        return 0
        #self.handlebuffer()
class HandleBuffer:

    _BOTMASK = (1<<8)
    _XMLMASK = (1<<9)
    _DBMASK = (1<<10)

    _PORTMASK = (1<<0)
    _CKPORTMASK = (1<<1)
    _BOTHMASK = _XMLMASK | _BOTMASK

    def __init__(self, stream, address, data):
        self._stream = stream
        self._address = address
        self._buffer = data
        self._xmldir = options.xmldir
    def handlebuffer(self):
        #time.sleep(10000)
        buf = self._buffer
        try:
            split_list = buf.split(':', 1)
            mask = int(split_list[0])
            buf = split_list[1]
        except:
            mask = None
        if mask == HandleBuffer._XMLMASK:
            action = "xml"
        elif mask == HandleBuffer._BOTMASK | HandleBuffer._PORTMASK:
            action = "bot"
        elif mask == HandleBuffer._BOTMASK | HandleBuffer._CKPORTMASK:
            action = 'ckportbot'
        elif mask == HandleBuffer._DBMASK:
            action = 'dbthreads'
        elif mask == HandleBuffer._BOTHMASK:
            action = "both"
        else:
            action = "reportlog"
        handle_func = getattr(self, "handle_%s" % action)
        return handle_func(buf, mask)
    def handle_xml(self, buf, mask):
        xmlfile = os.path.join(self._xmldir, self._address + ".xml")
        fh = open(xmlfile, 'w')
        #log.gen_log.info("sleep 10.0 secs...")
        #time.sleep(10.0)
        log.gen_log.info("buf_to_file: %s" % xmlfile)
        fh.write(buf)
        fh.close()
    def handle_ckportbot(self, buf, mask):
        #gc.enable()
        #gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)
        """
        argparser = XMPPSettings.get_arg_parser(add_help = True)
        settings = XMPPSettings()
        settings.load_arguments(argparser.parse_args())
        
        random_resource = string.join(random.sample((string.lowercase + string.digits), 6)).replace(" ", "")
        bot_jid = config.BOT_JID + "/" + random_resource
        bot_passwd = config.BOT_PASSWD
        target_jid = config.ROBOT
        """
        #self._stream.write("Test check port function=========")
        #return 0
        agent_ip, agent_data = tuple(buf.split(":", 1))
        rdbh = simpleutil.RedisHandler.init_exist()
        ip_exist = rdbh.exists_one(agent_ip, tcprdb = "tcp", udprdb = "udp")
        if not ip_exist:
            portmsg = "The ip you specified seem not in my cached, the Client may not run on this server, or it's an invalid server"
            try:
                self._stream.write(portmsg)
            except:
                loginfo = "Bot have closed, msg send back failed! " + portmsg
                log.gen_log.info(loginfo)
            return 0
                
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        is_mgs = 0
        try:
            sock.connect((agent_ip, config.AGENT_PORT))
            sock.send(agent_data)
            recv_data = sock.recv(2048)
            sock.close()
            is_msg = 1
        except:
            portmsg = "Time out from Agent"
            is_msg = 0
        if is_msg:
            portstring = recv_data.split(':', 1)[1]
            tcpport, udpport = tuple(portstring.split('|'))
            portstat = portstring.split(',')
            portmsg = agent_ip + ":\n" + tcpport + "\n" + udpport
            """
            for p in portstat:
                if int(p.split(':')[1]) == 104:
                    portline =  p.split(":")[0] + "off" + "\n"
                    portmsg += portline
                elif int(p.split(":")[1]) == 0:
                    portline = p.split(":")[0] + "listening" + "\n"
                    portmsg += portline
                else:
                    pass
            """
            portmsg += "\n ---- port check over -----\n"
            #simpleutil.SendMsgThread(send_message, bot_jid, bot_passwd, target_jid, portmsg, settings = settings).start()
        else:
            pass
        try:
            self._stream.write(portmsg)
        except:
            log.gen_log.info("Bot have closed, msg send back failed!")

        #print 'begin collect...'
        #_unreachable = gc.collect()
        #print 'unreachable object num:%d' % _unreachable
        #print 'garbage object num:%d' % len(gc.garbage)
    def handle_bot(self, buf, mask):
        #gc.enable()
        #gc.set_debug(gc.DEBUG_COLLECTABLE | gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS)

        porttype, strports = tuple(buf.split(":", 1))
        rdbh = simpleutil.RedisHandler.init_storedb(self._address, strports)
        sendports = rdbh.storedb(porttype)
        com_list = ['prot_type', 'port', 'ip']
        for s in sendports:
            #msg_list = [porttype, s, self._address]
            #item = dict(zip(com_list, msg_list))
            #items = []
            #items.append(item)
            #dbh = simpleutil.DBHandler()
            #dbthread = simpleutil.DBThread(dbh.add_portmonit, simpleutil.PortMonit, items, queue)
            #dbthread.start()
            #dbh.add_portmonit(simpleutil.PortMonit, items, queue)
            #if_send = queue.get()
            rdbchk = simpleutil.RedisHandler.init_exist()
            if_send = rdbchk.check_monitport(self._address, porttype, s)
            if if_send == 1:
                msg_list = [porttype, s, self._address]
                item = dict(zip(com_list, msg_list))
                dbh = simpleutil.DBHandler()
                dbthread = simpleutil.DBThread(dbh.add_portoff, simpleutil.PortMonit, item)
                dbthread.start()
                #dbh.add_portoff(simpleutil.PortMonit, item)

                #argparser = XMPPSettings.get_arg_parser(add_help = True)
                #settings = XMPPSettings()
                #settings.load_arguments(argparser.parse_args())
                random_resource = string.join(random.sample((string.lowercase + string.digits), 6)).replace(" ", "")
                bot_jid = config.BOT_JID + "/" + random_resource
                bot_passwd = config.BOT_PASSWD
                target_jid = config.ROBOT
                #message = "IP: {0}:{1} {2} off".format(self._address, msg_list[1], msg_list[0])
                message = "IP: {0}:{1} {2} off".format(self._address, s, porttype)
                #smt = simpleutil.SendMsgThread(send_message, bot_jid, bot_passwd, target_jid, message, settings = settings)
                #smt.start()
                #send_message(bot_jid, bot_passwd, target_jid, message, settings = settings)
                #send_message(bot_jid, bot_passwd, target_jid, message)
                xmpp = SendMsgBot(bot_jid, bot_passwd, target_jid, message)
                xmpp.ssl_version = ssl.PROTOCOL_SSLv3
                if xmpp.connect():
                    xmpp.process(block=False)
                    log.gen_log.info("XMPP Client: Message Send Over.")
                else:
                    log.gen_log.info("XMPP Client: Unable to connect.")
        '''msg_list = buf.split(':', buf)
        message = "IP: {0}:{1} off".format(self._address, msg_list[1])
        msg_list[-1] = self._address
        com_list = ['prot_type', 'port', 'ip']
        item = dict(zip(com_list, msg_list))
        items = []
        items.append(item)
        dbh = simpleutil.DBHandler()
        if_send = dbh.add_portmonit(simpleutil.PortMonit, items)
        if if_send == 1:
            send_message(bot_jid, bot_passwd, target_jid, message, settings = settings)
        '''
        #print 'begin collect...'
        #_unreachable = gc.collect()
        #print 'unreachable object num:%d' % _unreachable
        #print 'garbage object num:%d' % len(gc.garbage)
        #print 'garbage object is: %s' % str(gc.garbage)
    def handle_db(self, buf, mask):
        xmlstrust = simpleutil.XmlbufToStruct()
        items = xmlstrust.get_strust(buf, mask)
        dbh = simpleutil.DBHandler()
        dbh.add_appitems(simpleutil.AppItems, items)
    def handle_dbthreads(self, buf, mask):
        simpleutil.DBThread(self.handle_db, buf, mask).start()
    def handle_both(self, buf, mask):
        self.handle_xml(buf, mask)
        self.handle_bot(buf, mask)
    def handle_reportlog(self, buf, mask):
        log.gen_log.info("Invalid data from %s" % (self._address))



class MasterServer(TCPServer):
    def handle_stream(self, stream, address):
        handler = HandleStream(stream, address)
        #simpleutil.MainBuffThread(handler.read_data)
        handler.read_data()
        #handler._stream.write("File Trans OK")

        

def main():
    sockets = bind_sockets(options.port)
    #fork_processes(options.worker)
    server = MasterServer()
    server.add_sockets(sockets)
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        print >>sys.stderr, "MasterServer Exiting..."
        sys.exit(-2)
    except:
        traceback.print_exc()
        log.gen_log.info("MasterServer aborted unexpectedly")
    finally:
        IOLoop.instance().stop()
        

if __name__ == '__main__':
    main()
