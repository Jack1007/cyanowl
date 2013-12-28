#!/usr/bin/env python
#-*- conding:utf-8 -*-

import sys
from socket import *

serverHost = 'localhost'
serverPort = 6000

#message = ['Hello network world']
#message = ['java']
message = sys.argv[1]
if len(sys.argv) > 1:
    serverHost = sys.argv[1]
    if len(sys.argv) > 2:
        message = sys.argv[2:]

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.connect((serverHost, serverPort))
for line in message:
    print line
    sockobj.send(line)
    data = sockobj.recv(1024)
    print 'Client received:', str(data)

sockobj.close( )
