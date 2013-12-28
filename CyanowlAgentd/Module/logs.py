#!/usr/bin/env python 
#-*-coding:utf-8 -*-
#
import xml.dom.minidom as xmldom

class Logs:
    """
    here is logs class
    """
    
    def __init__(self):
        #print "logs"
	pass
    def Get(self):
	LOGOBJ = xmldom.parse('../conf/logs.xml')
        CHILDLOGFILE=LOGOBJ.getElementsByTagName('file')[0].attributes['path'].value
        return CHILDLOGFILE

if __name__ == "__main__":
    a=Logs()
    b=a.Get()
    print b
