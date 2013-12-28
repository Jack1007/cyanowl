#import os
#import json
from tornado.options import define, options

DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "cyanowl"
DB_PASSWD = "123456"
DB_NAME = "cyanowl"

RDB_HOST = '127.0.0.1'
RDB_PORT = 6379
TCPPORT_DB = 0
UDPPORT_DB = 1
OFFTCPPORT_DB = 2
OFFUDPPORT_DB = 3

AGENT_PORT = 6000

BOT_JID = 'master@cyanowl.org'
BOT_PASSWD = '123456'
ROBOT = 'robots@cyanowl.org'

define("port", default=9000, metavar="9000", help="run on the given port", type=int)
define("worker", default=1, metavar="1", help="number of subworker work", type=int)
define("xmldir", default="/tmp/collections", metavar="/tmp/collections", help="the dir where the xml files store in", type=str)

 
